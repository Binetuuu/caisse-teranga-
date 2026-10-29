"""Nostr Wallet Connect (NIP-47) — le commerçant relie SON portefeuille Lightning.

Pourquoi : un client qui scanne le QR avec n'importe quel portefeuille Lightning
paie directement le portefeuille du commerçant (Alby Hub, Coinos, Primal...).
Pas de nœud à gérer, et l'opérateur ne détient jamais les fonds.

Moindre privilège : la caisse n'utilise que `make_invoice` et `lookup_invoice`.
Si la connexion autorise aussi `pay_invoice`, on prévient le commerçant pour
qu'il crée une connexion « recevoir seulement ».

Cryptographie : `coincurve` (libsecp256k1, la bibliothèque de Bitcoin Core)
pour les signatures Schnorr BIP-340 et l'ECDH ; `cryptography` pour AES-256-CBC
(chiffrement NIP-04). Aucune primitive maison.
"""
from __future__ import annotations

import base64
import hashlib
import ipaddress
import json
import os
import re
import socket
import time
import uuid
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

from coincurve import PrivateKey, PublicKey, PublicKeyXOnly
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from websockets.sync.client import connect

from .lightning import LightningError, NewInvoice, verify_bolt11

HEX64 = re.compile(r"^[0-9a-f]{64}$")
REQUEST_KIND, RESPONSE_KIND, INFO_KIND = 23194, 23195, 13194


@dataclass(frozen=True)
class NWCConfig:
    wallet_pubkey: str
    relay: str
    secret: str


def parse_uri(uri: str, allow_private: bool = False) -> NWCConfig:
    """Valide une chaîne `nostr+walletconnect://<pubkey>?relay=wss://...&secret=<hex>`."""
    uri = (uri or "").strip()
    if len(uri) > 1000:
        raise ValueError("nwc_format")
    parsed = urlparse(uri)
    if parsed.scheme not in ("nostr+walletconnect", "nostrwalletconnect"):
        raise ValueError("nwc_format")
    pubkey = (parsed.netloc or parsed.path.lstrip("/")).lower()
    qs = parse_qs(parsed.query)
    relay = (qs.get("relay") or [""])[0]
    secret = (qs.get("secret") or [""])[0].lower()
    if not HEX64.match(pubkey) or not HEX64.match(secret):
        raise ValueError("nwc_format")
    check_relay(relay, allow_private)
    return NWCConfig(pubkey, relay, secret)


def check_relay(relay: str, allow_private: bool = False) -> None:
    """Anti-SSRF : relais en wss:// uniquement, jamais vers une adresse interne."""
    r = urlparse(relay)
    if r.scheme != "wss" and not (allow_private and r.scheme == "ws"):
        raise ValueError("nwc_relay")
    if not r.hostname:
        raise ValueError("nwc_relay")
    if allow_private:
        return
    try:
        infos = socket.getaddrinfo(r.hostname, r.port or 443, proto=socket.IPPROTO_TCP)
    except OSError as exc:
        raise ValueError("nwc_relay") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise ValueError("nwc_relay")


# ---------------------------------------------------------------- NIP-01 / NIP-04

def xonly(priv_hex: str) -> str:
    return PrivateKey(bytes.fromhex(priv_hex)).public_key_xonly.format().hex()


def _shared_x(priv_hex: str, pub_hex: str) -> bytes:
    # NIP-04 : la clé AES est la coordonnée x du point partagé (non hachée).
    point = PublicKey(b"\x02" + bytes.fromhex(pub_hex)).multiply(bytes.fromhex(priv_hex))
    return point.format(compressed=True)[1:]


def nip04_encrypt(priv_hex: str, pub_hex: str, text: str) -> str:
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    data = padder.update(text.encode()) + padder.finalize()
    enc = Cipher(algorithms.AES(_shared_x(priv_hex, pub_hex)), modes.CBC(iv)).encryptor()
    ct = enc.update(data) + enc.finalize()
    return f"{base64.b64encode(ct).decode()}?iv={base64.b64encode(iv).decode()}"


def nip04_decrypt(priv_hex: str, pub_hex: str, content: str) -> str:
    try:
        ct_b64, iv_b64 = content.split("?iv=")
        dec = Cipher(algorithms.AES(_shared_x(priv_hex, pub_hex)), modes.CBC(base64.b64decode(iv_b64))).decryptor()
        data = dec.update(base64.b64decode(ct_b64)) + dec.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return (unpadder.update(data) + unpadder.finalize()).decode()
    except Exception as exc:  # noqa: BLE001 — tout contenu illisible est rejeté
        raise LightningError("réponse NWC illisible") from exc


def _event_id(ev: dict) -> str:
    raw = json.dumps([0, ev["pubkey"], ev["created_at"], ev["kind"], ev["tags"], ev["content"]],
                     separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def sign_event(priv_hex: str, kind: int, content: str, tags: list) -> dict:
    ev = {"pubkey": xonly(priv_hex), "created_at": int(time.time()), "kind": kind, "tags": tags, "content": content}
    ev["id"] = _event_id(ev)
    ev["sig"] = PrivateKey(bytes.fromhex(priv_hex)).sign_schnorr(bytes.fromhex(ev["id"]), os.urandom(32)).hex()
    return ev


def verify_event(ev: dict) -> bool:
    try:
        if _event_id(ev) != ev["id"]:
            return False
        return PublicKeyXOnly(bytes.fromhex(ev["pubkey"])).verify(bytes.fromhex(ev["sig"]), bytes.fromhex(ev["id"]))
    except Exception:  # noqa: BLE001
        return False


# ---------------------------------------------------------------- NIP-47

class NWCWallet:
    name = "nwc"

    def __init__(self, cfg: NWCConfig, timeout: float = 12.0) -> None:
        self.cfg = cfg
        self.timeout = timeout

    def _request(self, method: str, params: dict) -> dict:
        cfg = self.cfg
        content = nip04_encrypt(cfg.secret, cfg.wallet_pubkey, json.dumps({"method": method, "params": params}))
        ev = sign_event(cfg.secret, REQUEST_KIND, content, [["p", cfg.wallet_pubkey]])
        sub = uuid.uuid4().hex[:16]
        deadline = time.monotonic() + self.timeout
        try:
            with connect(cfg.relay, open_timeout=6, close_timeout=2, max_size=256 * 1024) as ws:
                ws.send(json.dumps(["REQ", sub, {"kinds": [RESPONSE_KIND], "authors": [cfg.wallet_pubkey],
                                                  "#e": [ev["id"]], "since": ev["created_at"] - 10}]))
                ws.send(json.dumps(["EVENT", ev]))
                while (left := deadline - time.monotonic()) > 0:
                    msg = json.loads(ws.recv(timeout=left))
                    if not (isinstance(msg, list) and len(msg) >= 3 and msg[0] == "EVENT" and msg[1] == sub):
                        continue
                    resp = msg[2]
                    # On n'accepte qu'une réponse signée par le portefeuille, liée à notre requête.
                    if (resp.get("pubkey") != cfg.wallet_pubkey or resp.get("kind") != RESPONSE_KIND
                            or ["e", ev["id"]] not in [t[:2] for t in resp.get("tags", [])] or not verify_event(resp)):
                        continue
                    data = json.loads(nip04_decrypt(cfg.secret, cfg.wallet_pubkey, resp["content"]))
                    if data.get("error"):
                        raise LightningError(f"portefeuille : {str(data['error'].get('code', 'erreur'))[:40]}")
                    return data.get("result") or {}
        except LightningError:
            raise
        except (TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
            raise LightningError("portefeuille NWC injoignable") from exc
        except Exception as exc:  # noqa: BLE001 — erreurs websocket diverses
            raise LightningError("portefeuille NWC injoignable") from exc
        raise LightningError("le portefeuille n'a pas répondu à temps")

    def create_invoice(self, amount_sat: int, memo: str, expiry: int, api_key: str | None = None,
                       description_hash: str | None = None) -> NewInvoice:
        params = {"amount": amount_sat * 1000, "description": memo, "expiry": expiry}
        if description_hash:
            params["description_hash"] = description_hash
        res = self._request("make_invoice", params)
        bolt11 = str(res.get("invoice", ""))
        payment_hash = verify_bolt11(bolt11, amount_sat, res.get("payment_hash") or None)
        return NewInvoice(payment_hash=payment_hash, bolt11=bolt11)

    def status(self, payment_hash: str, api_key: str | None = None) -> tuple[bool, str | None]:
        res = self._request("lookup_invoice", {"payment_hash": payment_hash})
        paid = bool(res.get("settled_at")) or res.get("state") == "settled"
        preimage = res.get("preimage")
        return paid, preimage if paid and isinstance(preimage, str) else None

    def is_paid(self, payment_hash: str, api_key: str | None = None) -> bool:
        return self.status(payment_hash, api_key)[0]

    def permissions(self) -> list[str]:
        """Méthodes annoncées par le portefeuille (événement d'info NIP-47)."""
        sub = uuid.uuid4().hex[:16]
        try:
            with connect(self.cfg.relay, open_timeout=6, close_timeout=2, max_size=256 * 1024) as ws:
                ws.send(json.dumps(["REQ", sub, {"kinds": [INFO_KIND], "authors": [self.cfg.wallet_pubkey], "limit": 1}]))
                deadline = time.monotonic() + 6
                while (left := deadline - time.monotonic()) > 0:
                    msg = json.loads(ws.recv(timeout=left))
                    if isinstance(msg, list) and msg[:2] == ["EOSE", sub]:
                        return []
                    if isinstance(msg, list) and len(msg) >= 3 and msg[0] == "EVENT" and verify_event(msg[2]):
                        return str(msg[2].get("content", "")).split()
        except Exception:  # noqa: BLE001
            return []
        return []
