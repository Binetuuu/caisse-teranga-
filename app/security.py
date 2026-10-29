"""Briques de sécurité : chiffrement, code secret, sessions, anti-force brute, journaux sans données perso."""
from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import re
import secrets
import threading
import time
from collections import defaultdict, deque

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from . import db

# ---------------------------------------------------------------- clés dérivées


class Crypto:
    """Une seule clé maîtresse (SECRET_KEY), des sous-clés séparées par usage (HKDF)."""

    def __init__(self, master: bytes) -> None:
        def derive(label: bytes) -> bytes:
            return HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=label).derive(master)

        self._fernet = Fernet(base64.urlsafe_b64encode(derive(b"caisse/fernet/v1")))
        self._hmac_key = derive(b"caisse/hmac/v1")

    def encrypt(self, value: str) -> bytes:
        return self._fernet.encrypt(value.encode())

    def decrypt(self, token: bytes) -> str:
        try:
            return self._fernet.decrypt(token).decode()
        except InvalidToken as exc:
            raise ValueError("donnée chiffrée illisible") from exc

    def blind(self, value: str) -> str:
        """Empreinte HMAC : permet de chercher un numéro sans le stocker en clair."""
        return hmac.new(self._hmac_key, value.encode(), hashlib.sha256).hexdigest()


# ---------------------------------------------------------------- validations

_PHONE_RE = re.compile(r"^(?:\+?221)?(7[05678]\d{7}|3[03]\d{7})$")


def normalize_phone(raw: str) -> str | None:
    """Numéro sénégalais → format +221XXXXXXXXX, sinon None."""
    digits = re.sub(r"[\s.\-()]", "", raw or "")
    if digits.startswith("00"):
        digits = "+" + digits[2:]
    m = _PHONE_RE.match(digits)
    return f"+221{m.group(1)}" if m else None


_WEAK_PINS = {
    "1234", "4321", "0123", "3210", "2345", "5432", "3456", "6543", "4567", "7654",
    "5678", "8765", "6789", "9876", "7890", "0987", "1212", "2121", "1122", "2211",
    "6969", "1004", "2000", "2580", "0852", "1010", "0101", "1313", "2222",
}


def pin_problem(pin: str) -> str | None:
    """Renvoie une clé de message d'erreur si le code est refusé."""
    if not re.fullmatch(r"\d{4}", pin or ""):
        return "pin_format"
    if len(set(pin)) == 1 or pin in _WEAK_PINS:
        return "pin_weak"
    if 1940 <= int(pin) <= 2030:  # ressemble à une année de naissance
        return "pin_weak"
    return None


_TEXT_RE = re.compile(r"^[\w\s'’.,\-&/()éèêëàâäîïôöûüçñÉÈÊÀÂÎÔÛÇ]+$", re.UNICODE)


def clean_text(raw: str, max_len: int) -> str | None:
    value = re.sub(r"\s+", " ", (raw or "").strip())
    if not 2 <= len(value) <= max_len or not _TEXT_RE.match(value):
        return None
    return value


# ---------------------------------------------------------------- code secret

# Argon2id, paramètres adaptés à un petit serveur (≈50 ms).
_hasher = PasswordHasher(time_cost=3, memory_cost=64 * 1024, parallelism=2)
_DUMMY_HASH = _hasher.hash("0000-dummy")


def hash_pin(pin: str) -> str:
    return _hasher.hash(pin)


def verify_pin(pin_hash: str | None, pin: str) -> bool:
    try:
        # Toujours vérifier un hash, même si le compte n'existe pas : même durée de réponse.
        return _hasher.verify(pin_hash or _DUMMY_HASH, pin) and pin_hash is not None
    except (VerificationError, InvalidHashError):
        return False


# ---------------------------------------------------------------- sessions

SESSION_COOKIE = "ct_session"


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_session(merchant_id: int, hours: int) -> str:
    token = secrets.token_urlsafe(32)
    now = int(time.time())
    with db.connect() as conn:
        conn.execute("DELETE FROM sessions WHERE expires_at < ?", (now,))
        conn.execute(
            "INSERT INTO sessions(token_hash, merchant_id, created_at, expires_at) VALUES (?,?,?,?)",
            (_token_hash(token), merchant_id, now, now + hours * 3600),
        )
    return token


def session_merchant(token: str | None) -> int | None:
    if not token or len(token) > 100:
        return None
    with db.connect() as conn:
        row = conn.execute(
            "SELECT merchant_id FROM sessions WHERE token_hash=? AND expires_at > ?",
            (_token_hash(token), int(time.time())),
        ).fetchone()
    return row["merchant_id"] if row else None


def delete_other_sessions(merchant_id: int, keep_token: str | None) -> None:
    keep = _token_hash(keep_token) if keep_token else ""
    with db.connect() as conn:
        conn.execute("DELETE FROM sessions WHERE merchant_id=? AND token_hash!=?", (merchant_id, keep))


def delete_session(token: str | None) -> None:
    if token:
        with db.connect() as conn:
            conn.execute("DELETE FROM sessions WHERE token_hash=?", (_token_hash(token),))


# ---------------------------------------------------------------- anti-force brute

MAX_FAILURES = 5
LOCK_SECONDS = 15 * 60


def lock_remaining(key: str) -> int:
    with db.connect() as conn:
        row = conn.execute("SELECT locked_until FROM login_attempts WHERE key=?", (key,)).fetchone()
    return max(0, (row["locked_until"] if row else 0) - int(time.time()))


def record_failure(key: str) -> None:
    now = int(time.time())
    with db.connect() as conn:
        row = conn.execute("SELECT failures FROM login_attempts WHERE key=?", (key,)).fetchone()
        failures = (row["failures"] if row else 0) + 1
        locked = 0
        if failures >= MAX_FAILURES:
            # Blocage progressif : 15 min, puis 30, 60... (plafonné à 24 h)
            locked = now + min(LOCK_SECONDS * 2 ** (failures - MAX_FAILURES), 86_400)
        conn.execute(
            "INSERT INTO login_attempts(key, failures, locked_until, updated_at) VALUES (?,?,?,?) "
            "ON CONFLICT(key) DO UPDATE SET failures=excluded.failures, "
            "locked_until=excluded.locked_until, updated_at=excluded.updated_at",
            (key, failures, locked, now),
        )


def clear_failures(key: str) -> None:
    with db.connect() as conn:
        conn.execute("DELETE FROM login_attempts WHERE key=?", (key,))


class RateLimiter:
    """Limiteur en mémoire (fenêtre glissante) pour les appels coûteux."""

    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str, limit: int, window: float) -> bool:
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] > window:
                hits.popleft()
            if len(hits) >= limit:
                return False
            hits.append(now)
            if len(self._hits) > 10_000:  # borne mémoire
                for k in [k for k, v in self._hits.items() if not v][:5_000]:
                    del self._hits[k]
            return True


limiter = RateLimiter()

# ---------------------------------------------------------------- journaux

_REDACT = [
    (re.compile(r"\+?\d[\d\s.\-]{7,}\d"), "[num]"),            # numéros de téléphone
    (re.compile(r"\bln(?:bc|tb|tbs|bcrt)[0-9a-z]{20,}\b", re.I), "[facture]"),
    (re.compile(r"\b[0-9a-f]{32,}\b", re.I), "[clé]"),           # clés API, hash
]


class RedactFilter(logging.Filter):
    """Filet de sécurité : efface numéros, factures et clés de tout message de journal."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for pattern, repl in _REDACT:
            msg = pattern.sub(repl, msg)
        record.msg, record.args = msg, None
        return True
