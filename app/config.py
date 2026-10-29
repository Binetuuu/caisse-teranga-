"""Configuration lue depuis l'environnement, avec des valeurs par défaut sûres.

Aucun secret n'est codé en dur : tout vient de .env (non versionné) ou est
généré au premier démarrage en mode démo.
"""
from __future__ import annotations

import base64
import logging
import os
import secrets
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger("caisse.config")


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "oui", "on"}


def _int(name: str, default: int, lo: int, hi: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} doit être un entier") from exc
    if not lo <= value <= hi:
        raise RuntimeError(f"{name} doit être entre {lo} et {hi}")
    return value


@dataclass(frozen=True)
class Settings:
    app_env: str
    data_dir: Path
    database_path: Path
    secret_key: bytes
    cookie_secure: bool
    session_cookie: str
    trust_proxy: bool
    allowed_hosts: frozenset
    public_url: str
    session_hours: int

    lightning_backend: str  # "fake" | "lnbits"
    lnbits_url: str
    lnbits_invoice_key: str
    lnbits_allow_http: bool
    nwc_allow_private: bool

    payout_fee_pct: float
    payout_daily_max_xof: int

    invoice_expiry_seconds: int
    min_amount_xof: int
    max_amount_xof: int

    rate_source: str  # "coingecko" | "static"
    btc_xof_static: int

    anthropic_api_key_set: bool
    ai_model: str

    seed_demo: bool
    support_phone: str
    metrics_token: str

    @property
    def is_demo(self) -> bool:
        return self.app_env != "production"

    @property
    def simulate_allowed(self) -> bool:
        # Le bouton « simuler le paiement » n'existe qu'avec le portefeuille factice.
        return self.lightning_backend == "fake"


def _load_secret(app_env: str, data_dir: Path) -> bytes:
    raw = os.getenv("SECRET_KEY", "").strip()
    if raw:
        try:
            key = base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4))
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError("SECRET_KEY doit être en base64 (voir README)") from exc
        if len(key) < 32:
            raise RuntimeError("SECRET_KEY doit faire au moins 32 octets")
        return key
    if app_env == "production":
        raise RuntimeError("SECRET_KEY est obligatoire en production")
    # Mode démo : clé générée une fois et gardée dans le volume de données (0600).
    path = data_dir / "secret.key"
    if path.exists():
        return base64.urlsafe_b64decode(path.read_bytes())
    key = secrets.token_bytes(32)
    path.write_bytes(base64.urlsafe_b64encode(key))
    try:
        path.chmod(0o600)
    except OSError:
        pass
    log.warning("SECRET_KEY absente : clé de démo générée dans le dossier de données")
    return key


def load_settings() -> Settings:
    app_env = os.getenv("APP_ENV", "demo").strip().lower()
    data_dir = Path(os.getenv("DATA_DIR", "./data")).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    backend = os.getenv("LIGHTNING_BACKEND", "fake").strip().lower()
    if backend not in {"fake", "lnbits"}:
        raise RuntimeError("LIGHTNING_BACKEND doit être 'fake' ou 'lnbits'")
    if backend == "fake" and app_env == "production":
        raise RuntimeError("Le portefeuille factice est interdit en production")

    lnbits_url = os.getenv("LNBITS_URL", "").strip().rstrip("/")
    lnbits_key = os.getenv("LNBITS_INVOICE_KEY", "").strip()
    allow_http = _bool("LNBITS_ALLOW_HTTP", False)
    if backend == "lnbits":
        if not lnbits_url:
            raise RuntimeError("LNBITS_URL est obligatoire avec LIGHTNING_BACKEND=lnbits")
        if lnbits_url.startswith("http://") and not allow_http:
            raise RuntimeError("LNBITS_URL doit être en https (ou LNBITS_ALLOW_HTTP=true sur un réseau privé)")

    min_xof = _int("MIN_AMOUNT_XOF", 100, 1, 10_000_000)
    max_xof = _int("MAX_AMOUNT_XOF", 500_000, min_xof, 100_000_000)

    rate_source = os.getenv("RATE_SOURCE", "coingecko").strip().lower()
    if rate_source not in {"coingecko", "static"}:
        raise RuntimeError("RATE_SOURCE doit être 'coingecko' ou 'static'")

    return Settings(
        app_env=app_env,
        data_dir=data_dir,
        database_path=Path(os.getenv("DATABASE_PATH", str(data_dir / "caisse.db"))),
        secret_key=_load_secret(app_env, data_dir),
        cookie_secure=_bool("COOKIE_SECURE", app_env == "production"),
        # Firebase Hosting ne transmet à Cloud Run qu'un seul cookie, nommé « __session ».
        session_cookie=os.getenv("SESSION_COOKIE_NAME", "ct_session").strip() or "ct_session",
        # Derrière Firebase Hosting / Cloud Run : l'IP du client est dans X-Forwarded-For.
        trust_proxy=_bool("TRUST_PROXY", False),
        # Domaines publics autorisés pour l'en-tête Origin (ex. monprojet.web.app).
        # Adresse publique (https://…) utilisée dans le QR de l'affiche. Vide = déduite de la requête.
        public_url=os.getenv("PUBLIC_URL", "").strip().rstrip("/"),
        allowed_hosts=frozenset(h.strip().lower() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()),
        session_hours=_int("SESSION_HOURS", 12, 1, 24 * 30),
        lightning_backend=backend,
        lnbits_url=lnbits_url,
        lnbits_invoice_key=lnbits_key,
        lnbits_allow_http=allow_http,
        # Tests uniquement : autorise un relais NWC local (ws://127.0.0.1). Interdit en production.
        nwc_allow_private=_bool("NWC_ALLOW_PRIVATE", False) and app_env != "production",
        payout_fee_pct=_int("PAYOUT_FEE_BPS", 100, 0, 1000) / 100,
        payout_daily_max_xof=_int("PAYOUT_DAILY_MAX_XOF", 300_000, 1_000, 100_000_000),
        invoice_expiry_seconds=_int("INVOICE_EXPIRY_SECONDS", 600, 60, 3600),
        min_amount_xof=min_xof,
        max_amount_xof=max_xof,
        rate_source=rate_source,
        btc_xof_static=_int("BTC_XOF_STATIC", 62_500_000, 1_000_000, 1_000_000_000),
        anthropic_api_key_set=bool(os.getenv("ANTHROPIC_API_KEY", "").strip()),
        ai_model=os.getenv("AI_MODEL", "claude-opus-5-5").strip(),
        seed_demo=_bool("SEED_DEMO", app_env != "production"),
        support_phone=os.getenv("SUPPORT_PHONE", "").strip(),
        metrics_token=os.getenv("METRICS_TOKEN", "").strip(),
    )
