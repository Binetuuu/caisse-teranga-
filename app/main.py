"""Caisse Teranga — API et service des fichiers de l'interface."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import logging
import re
import secrets
import statistics
import threading
import time
import unicodedata
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import segno
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.gzip import GZipMiddleware

from . import db, security
from .ai import AI, local_summary
from .config import Settings, load_settings
import bech32

from .lightning import INVOICE_KEY_RE, FakeWallet, LightningError, build_wallet, verify_preimage
from .nwc import NWCWallet, parse_uri
from .rates import RateProvider, xof_to_sat

# ---------------------------------------------------------------- journaux sans données personnelles

_handler = logging.StreamHandler()
_handler.addFilter(security.RedactFilter())
_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[_handler], force=True)
log = logging.getLogger("caisse")


class State:
    settings: Settings
    crypto: security.Crypto
    wallet: object
    rates: RateProvider
    ai: AI
    stop: threading.Event


S = State()


def now() -> int:
    return int(time.time())


def day_start(ts: int, offset_days: int = 0) -> int:
    # Dakar est à GMT toute l'année : le jour UTC est le jour local.
    d = datetime.fromtimestamp(ts, tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return int(d.timestamp()) + offset_days * 86_400


def hhmm(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%H:%M")


# ---------------------------------------------------------------- paiements


def merchant_ln_key(merchant_id: int) -> str | None:
    with db.connect() as conn:
        row = conn.execute("SELECT ln_key_enc FROM merchants WHERE id=?", (merchant_id,)).fetchone()
    if row and row["ln_key_enc"]:
        return S.crypto.decrypt(row["ln_key_enc"])
    return None


def merchant_nwc(merchant_id: int) -> NWCWallet | None:
    with db.connect() as conn:
        row = conn.execute("SELECT nwc_enc FROM merchants WHERE id=?", (merchant_id,)).fetchone()
    if row and row["nwc_enc"]:
        return NWCWallet(parse_uri(S.crypto.decrypt(row["nwc_enc"]), S.settings.nwc_allow_private))
    return None


def merchant_training(merchant_id: int) -> bool:
    with db.connect() as conn:
        row = conn.execute("SELECT training FROM merchants WHERE id=?", (merchant_id,)).fetchone()
    return bool(row and row["training"])


def wallet_for(merchant_id: int, backend: str | None = None):
    """Portefeuille à utiliser : entraînement (faux bitcoins), celui du commerçant (NWC), ou celui par défaut."""
    if backend == "training" or (backend is None and merchant_training(merchant_id)):
        return S.training_wallet, None, "training"
    if backend in (None, "nwc"):
        nwc = merchant_nwc(merchant_id)
        if nwc:
            return nwc, None, "nwc"
        if backend == "nwc":
            return None, None, "nwc"  # connexion supprimée depuis : état non vérifiable
    return S.wallet, merchant_ln_key(merchant_id), "default"


def mark_paid(invoice_id: str, preimage: str | None = None) -> None:
    """Enregistre le paiement (et sa preuve) et attribue le numéro de vente du jour (sans doublon)."""
    with db.transaction() as conn:
        inv = conn.execute("SELECT merchant_id, status FROM invoices WHERE id=?", (invoice_id,)).fetchone()
        if not inv or inv["status"] == "paid":
            return
        t = now()
        sale_no = conn.execute(
            "SELECT COUNT(*) FROM invoices WHERE merchant_id=? AND status='paid' AND paid_at>=?",
            (inv["merchant_id"], day_start(t)),
        ).fetchone()[0] + 1
        conn.execute(
            "UPDATE invoices SET status='paid', paid_at=?, sale_no=?, preimage=? WHERE id=?",
            (t, sale_no, preimage, invoice_id),
        )
    log.info("paiement confirmé")


def refresh_invoice(row) -> str:
    """Interroge le service Lightning pour une facture en attente."""
    status = row["status"]
    if status not in ("pending", "cancelled"):
        return status
    wallet, key, _ = wallet_for(row["merchant_id"], row["backend"])
    try:
        paid, preimage = wallet.status(row["payment_hash"], key) if wallet else (False, None)
    except LightningError:
        paid, preimage = False, None
    if paid:
        # Même annulée à l'écran, une facture payée est une vente : l'argent est arrivé.
        # La préimage n'est conservée que si elle prouve vraiment le paiement.
        mark_paid(row["id"], preimage if verify_preimage(preimage, row["payment_hash"]) else None)
        return "paid"
    if status == "pending" and row["expires_at"] <= now():
        with db.connect() as conn:
            conn.execute("UPDATE invoices SET status='expired' WHERE id=? AND status='pending'", (row["id"],))
        return "expired"
    return status


def process_payouts() -> None:
    """Démo : le partenaire Mobile Money simulé confirme le transfert après quelques secondes."""
    with db.connect() as conn:
        conn.execute(
            "UPDATE payouts SET status='completed', completed_at=? WHERE status='pending' AND created_at<=?",
            (now(), now() - 5),
        )


def poller() -> None:
    """Surveille les factures en attente, même si le téléphone du commerçant a perdu le réseau."""
    while not S.stop.wait(4):
        try:
            with db.connect() as conn:
                rows = conn.execute(
                    "SELECT * FROM invoices WHERE status='pending' OR "
                    "(status='cancelled' AND expires_at > ?) ORDER BY created_at DESC LIMIT 50",
                    (now(),),
                ).fetchall()
            for row in rows:
                refresh_invoice(row)
            process_payouts()
        except Exception:  # noqa: BLE001 — la boucle ne doit jamais mourir
            log.exception("erreur du surveillant de paiements")


# ---------------------------------------------------------------- démarrage


@asynccontextmanager
async def lifespan(app: FastAPI):
    S.settings = load_settings()
    S.crypto = security.Crypto(S.settings.secret_key)
    security.SESSION_COOKIE = S.settings.session_cookie
    db.init_db(S.settings.database_path)
    S.wallet = build_wallet(S.settings)
    # Mode entraînement : toujours un portefeuille factice (faux bitcoins), quel que soit le réglage.
    S.training_wallet = S.wallet if isinstance(S.wallet, FakeWallet) else FakeWallet()
    S.rates = RateProvider(S.settings.rate_source, S.settings.btc_xof_static)
    S.ai = AI(S.settings.anthropic_api_key_set, S.settings.ai_model)
    S.stop = threading.Event()
    if S.settings.seed_demo:
        from .seed import seed_if_empty

        seed_if_empty(S.crypto, S.settings, S.wallet)
    ensure_public_ids()
    thread = threading.Thread(target=poller, name="poller", daemon=True)
    thread.start()
    log.info(
        "Caisse Teranga démarrée (env=%s, lightning=%s, ia=%s)",
        S.settings.app_env, S.settings.lightning_backend, "oui" if S.ai.enabled else "non",
    )
    yield
    S.stop.set()


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(GZipMiddleware, minimum_size=500)

MAX_BODY = 16 * 1024
CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
    "connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'none'; "
    "frame-ancestors 'none'; form-action 'self'; manifest-src 'self'; worker-src 'self'"
)


def allowed_origin_hosts(request: Request) -> set[str]:
    """Hôtes légitimes : celui de la requête, les domaines publics configurés,
    et, derrière un proxy de confiance (Firebase Hosting), l'hôte d'origine transmis."""
    hosts = {(request.headers.get("host") or "").lower()} | set(S.settings.allowed_hosts)
    if S.settings.trust_proxy and request.headers.get("x-forwarded-host"):
        hosts.add(request.headers["x-forwarded-host"].split(",")[0].strip().lower())
    return hosts


@app.middleware("http")
async def guard(request: Request, call_next):
    started = time.perf_counter()
    path = request.url.path
    if path.startswith("/api/") and request.method not in ("GET", "HEAD", "OPTIONS"):
        # Anti-CSRF : en-tête personnalisé (impossible à poser depuis un autre site sans CORS)
        # + vérification de l'origine quand le navigateur la fournit.
        if request.headers.get("x-requested-with") != "caisse":
            return JSONResponse({"error": "csrf"}, status_code=403)
        origin = request.headers.get("origin")
        if origin and origin.split("://", 1)[-1].lower() not in allowed_origin_hosts(request):
            return JSONResponse({"error": "csrf"}, status_code=403)
        if int(request.headers.get("content-length") or 0) > MAX_BODY:
            return JSONResponse({"error": "too_large"}, status_code=413)
    response: Response = await call_next(request)
    h = response.headers
    h["Content-Security-Policy"] = CSP
    h["X-Content-Type-Options"] = "nosniff"
    h["X-Frame-Options"] = "DENY"
    h["Referrer-Policy"] = "no-referrer"
    h["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
    h["Cross-Origin-Opener-Policy"] = "same-origin"
    if S.settings.cookie_secure:
        h["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    if path.startswith("/api/"):
        h.setdefault("Cache-Control", "no-store")
    # Journal minimal : méthode, gabarit de route, statut, durée. Pas d'IP, pas de paramètres.
    route = request.scope.get("route")
    log.info("%s %s %s %dms", request.method, getattr(route, "path", "static"),
             response.status_code, (time.perf_counter() - started) * 1000)
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    fields = sorted({str(e["loc"][-1]) for e in exc.errors() if e.get("loc")})
    return JSONResponse({"error": "invalid", "fields": fields}, status_code=422)


def fail(status: int, code: str, **extra) -> HTTPException:
    return HTTPException(status_code=status, detail={"error": code, **extra})


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, dict) else {"error": "http_%d" % exc.status_code}
    return JSONResponse(detail, status_code=exc.status_code)


def client_ip(request: Request) -> str:
    if S.settings.trust_proxy:
        forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        if forwarded:
            return forwarded[:64]
    return request.client.host if request.client else "?"


def current_merchant(request: Request) -> int:
    merchant_id = security.session_merchant(request.cookies.get(security.SESSION_COOKIE))
    if merchant_id is None:
        raise fail(401, "auth")
    return merchant_id


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        security.SESSION_COOKIE, token,
        max_age=S.settings.session_hours * 3600,
        httponly=True, secure=S.settings.cookie_secure, samesite="strict", path="/",
    )


# ---------------------------------------------------------------- schémas d'entrée (stricts)


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_max_length=200)


class SignupIn(Strict):
    name: str = Field(max_length=60)
    shop_name: str = Field(max_length=60)
    area: str = Field(max_length=60)
    phone: str = Field(max_length=20)
    pin: str = Field(min_length=4, max_length=4)
    accept_terms: bool


class LoginIn(Strict):
    phone: str = Field(max_length=20)
    pin: str = Field(min_length=4, max_length=4)


class PrefsIn(Strict):
    lang: Literal["fr", "wo"] | None = None
    training: bool | None = None


class WalletIn(Strict):
    invoice_key: str = Field(max_length=64)


class NWCIn(Strict):
    uri: str = Field(max_length=1000)


class PinChangeIn(Strict):
    current_pin: str = Field(min_length=4, max_length=4)
    new_pin: str = Field(min_length=4, max_length=4)


class InvoiceIn(Strict):
    amount_xof: int
    note: str | None = Field(default=None, max_length=60)


class CashSaleIn(Strict):
    amount_xof: int
    method: Literal["cash", "mobile"]
    note: str | None = Field(default=None, max_length=60)


class PosterSimIn(Strict):
    amount_xof: int


class OnrampIn(Strict):
    operator: Literal["orange", "free", "wave"]


class PayoutIn(Strict):
    operator: Literal["wave", "orange", "free"]
    amount_xof: int
    pin: str = Field(min_length=4, max_length=4)


class ChatTurn(Strict):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=1200)


class AssistantIn(Strict):
    message: str = Field(min_length=1, max_length=500)
    history: list[ChatTurn] = Field(default_factory=list, max_length=6)
    lang: Literal["fr", "wo"] = "fr"


# ---------------------------------------------------------------- authentification


@app.post("/api/auth/signup", status_code=201)
def signup(body: SignupIn, request: Request, response: Response):
    if not security.limiter.allow(f"signup:{client_ip(request)}", 10, 3600):
        raise fail(429, "too_many")
    if not body.accept_terms:
        raise fail(422, "terms")
    phone = security.normalize_phone(body.phone)
    if not phone:
        raise fail(422, "phone_invalid")
    problem = security.pin_problem(body.pin)
    if problem:
        raise fail(422, problem)
    name = security.clean_text(body.name, 60)
    shop = security.clean_text(body.shop_name, 60)
    area = security.clean_text(body.area, 60)
    if not (name and shop and area):
        raise fail(422, "invalid", fields=[f for f, v in (("name", name), ("shop_name", shop), ("area", area)) if not v])
    phone_hash = S.crypto.blind("phone:" + phone)
    with db.connect() as conn:
        if conn.execute("SELECT 1 FROM merchants WHERE phone_hash=?", (phone_hash,)).fetchone():
            raise fail(409, "phone_taken")
        cur = conn.execute(
            "INSERT INTO merchants(name, shop_name, area, phone_hash, phone_enc, pin_hash, created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (name, shop, area, phone_hash, S.crypto.encrypt(phone), security.hash_pin(body.pin), now()),
        )
        merchant_id = cur.lastrowid
        conn.execute("UPDATE merchants SET public_id=? WHERE id=?", (make_public_id(shop), merchant_id))
    set_session_cookie(response, security.create_session(merchant_id, S.settings.session_hours))
    log.info("nouveau commerçant inscrit")
    return {"ok": True}


@app.post("/api/auth/login")
def login(body: LoginIn, request: Request, response: Response):
    if not security.limiter.allow(f"login-ip:{client_ip(request)}", 30, 900):
        raise fail(429, "too_many")
    phone = security.normalize_phone(body.phone) or "invalid"
    lock_key = S.crypto.blind("lock:" + phone)
    remaining = security.lock_remaining(lock_key)
    if remaining:
        raise fail(429, "locked", minutes=max(1, remaining // 60))
    with db.connect() as conn:
        row = conn.execute(
            "SELECT id, pin_hash FROM merchants WHERE phone_hash=?", (S.crypto.blind("phone:" + phone),)
        ).fetchone()
    if not security.verify_pin(row["pin_hash"] if row else None, body.pin):
        security.record_failure(lock_key)
        # Même message que le numéro existe ou non : pas d'énumération des comptes.
        raise fail(401, "bad_credentials")
    security.clear_failures(lock_key)
    set_session_cookie(response, security.create_session(row["id"], S.settings.session_hours))
    return {"ok": True}


@app.post("/api/auth/logout")
def logout(request: Request, response: Response):
    security.delete_session(request.cookies.get(security.SESSION_COOKIE))
    response.delete_cookie(security.SESSION_COOKIE, path="/")
    return {"ok": True}


def mask_phone(phone: str) -> str:
    return f"{phone[:4]} {phone[4:6]} *** ** {phone[-2:]}"


@app.get("/api/me")
def me(merchant_id: int = Depends(current_merchant)):
    with db.connect() as conn:
        m = conn.execute("SELECT * FROM merchants WHERE id=?", (merchant_id,)).fetchone()
    st = S.settings
    return {
        "name": m["name"],
        "shop_name": m["shop_name"],
        "area": m["area"],
        "phone": mask_phone(S.crypto.decrypt(m["phone_enc"])),
        "lang": m["lang"],
        "wallet_linked": m["ln_key_enc"] is not None,
        "nwc_linked": m["nwc_enc"] is not None,
        "training": bool(m["training"]),
        "public_id": m["public_id"],
        "config": {
            "min_xof": st.min_amount_xof,
            "max_xof": st.max_amount_xof,
            "expiry_s": st.invoice_expiry_seconds,
            "simulate": st.simulate_allowed,
            "backend": st.lightning_backend,
            "ai": S.ai.enabled,
            "support_phone": st.support_phone,
        },
    }


@app.patch("/api/me")
def update_prefs(body: PrefsIn, merchant_id: int = Depends(current_merchant)):
    with db.connect() as conn:
        if body.lang is not None:
            conn.execute("UPDATE merchants SET lang=? WHERE id=?", (body.lang, merchant_id))
        if body.training is not None:
            conn.execute("UPDATE merchants SET training=? WHERE id=?", (int(body.training), merchant_id))
    return {"ok": True}


@app.delete("/api/me/training-sales")
def clear_training(merchant_id: int = Depends(current_merchant)):
    """Efface les ventes d'entraînement (les vraies ventes ne sont jamais touchées)."""
    with db.connect() as conn:
        n = conn.execute("DELETE FROM invoices WHERE merchant_id=? AND backend='training'", (merchant_id,)).rowcount
    return {"deleted": n}


@app.put("/api/me/wallet")
def link_wallet(body: WalletIn, merchant_id: int = Depends(current_merchant)):
    key = body.invoice_key.strip().lower()
    if not INVOICE_KEY_RE.match(key):
        raise fail(422, "wallet_key_format")
    if S.settings.lightning_backend != "lnbits":
        raise fail(409, "wallet_not_supported")
    if not security.limiter.allow(f"wallet:{merchant_id}", 5, 3600):
        raise fail(429, "too_many")
    try:
        ok = S.wallet.check_key(key)
    except LightningError:
        raise fail(502, "lightning_down")
    if not ok:
        raise fail(422, "wallet_key_rejected")
    with db.connect() as conn:
        conn.execute("UPDATE merchants SET ln_key_enc=? WHERE id=?", (S.crypto.encrypt(key), merchant_id))
    return {"ok": True}


def check_pin(merchant_id: int, pin: str) -> None:
    """Re-vérifie le code secret avant une action sensible (même verrouillage que la connexion)."""
    with db.connect() as conn:
        m = conn.execute("SELECT pin_hash, phone_enc FROM merchants WHERE id=?", (merchant_id,)).fetchone()
    lock_key = S.crypto.blind("lock:" + S.crypto.decrypt(m["phone_enc"]))
    remaining = security.lock_remaining(lock_key)
    if remaining:
        raise fail(429, "locked", minutes=max(1, remaining // 60))
    if not security.verify_pin(m["pin_hash"], pin):
        security.record_failure(lock_key)
        raise fail(403, "bad_pin")
    security.clear_failures(lock_key)


@app.post("/api/me/pin")
def change_pin(body: PinChangeIn, request: Request, merchant_id: int = Depends(current_merchant)):
    check_pin(merchant_id, body.current_pin)
    problem = security.pin_problem(body.new_pin)
    if problem:
        raise fail(422, problem)
    with db.connect() as conn:
        conn.execute("UPDATE merchants SET pin_hash=? WHERE id=?", (security.hash_pin(body.new_pin), merchant_id))
    # Les autres appareils connectés sont déconnectés.
    security.delete_other_sessions(merchant_id, request.cookies.get(security.SESSION_COOKIE))
    log.info("code secret modifié")
    return {"ok": True}


@app.put("/api/me/nwc")
def link_nwc(body: NWCIn, merchant_id: int = Depends(current_merchant)):
    if not security.limiter.allow(f"nwc:{merchant_id}", 5, 3600):
        raise fail(429, "too_many")
    try:
        cfg = parse_uri(body.uri, S.settings.nwc_allow_private)
    except ValueError as exc:
        raise fail(422, str(exc))
    wallet = NWCWallet(cfg)
    try:
        # Test réel : une facture de 1 sat prouve que la connexion sait recevoir.
        wallet.create_invoice(1, "Caisse Teranga - test de connexion", 60)
    except LightningError:
        raise fail(502, "nwc_unreachable")
    can_spend = "pay_invoice" in wallet.permissions()
    with db.connect() as conn:
        conn.execute("UPDATE merchants SET nwc_enc=? WHERE id=?", (S.crypto.encrypt(body.uri.strip()), merchant_id))
    log.info("portefeuille NWC relié")
    return {"ok": True, "can_spend": can_spend}


@app.delete("/api/me/nwc")
def unlink_nwc(merchant_id: int = Depends(current_merchant)):
    with db.connect() as conn:
        conn.execute("UPDATE merchants SET nwc_enc=NULL WHERE id=?", (merchant_id,))
    return {"ok": True}


@app.delete("/api/me/wallet")
def unlink_wallet(merchant_id: int = Depends(current_merchant)):
    with db.connect() as conn:
        conn.execute("UPDATE merchants SET ln_key_enc=NULL WHERE id=?", (merchant_id,))
    return {"ok": True}


# ---------------------------------------------------------------- encaissement


@app.get("/api/rate")
def rate(merchant_id: int = Depends(current_merchant)):
    r = S.rates.current()
    return {"xof_per_btc": r.xof_per_btc, "source": r.source, "fetched_at": r.fetched_at}


def invoice_out(row, status: str | None = None) -> dict:
    return {
        "id": row["id"],
        "amount_xof": row["amount_xof"],
        "amount_sat": row["amount_sat"],
        "bolt11": row["bolt11"],
        "status": status or row["status"],
        "created_at": row["created_at"],
        "expires_at": row["expires_at"],
        "paid_at": row["paid_at"],
        "sale_no": row["sale_no"],
        "time": hhmm(row["paid_at"] or row["created_at"]),
        "date": datetime.fromtimestamp(row["paid_at"] or row["created_at"], tz=timezone.utc).strftime("%Y-%m-%d"),
        "real": row["backend"] == "nwc" or (row["backend"] == "default" and S.settings.lightning_backend != "fake"),
        "simulate": row["method"] == "lightning" and (
            row["backend"] == "training" or (row["backend"] == "default" and S.settings.simulate_allowed)),
        "training": row["backend"] == "training",
        "method": row["method"],
        "source": row["source"],
        "note": row["note"],
        "proof": proof_out(row),
        "confirm_s": (row["paid_at"] - row["created_at"]) if row["paid_at"] and row["method"] == "lightning" else None,
    }


def proof_out(row) -> dict | None:
    """Preuve de paiement Lightning : la préimage s, vérifiée par SHA256(s) = empreinte de la facture."""
    if row["method"] != "lightning" or row["status"] != "paid" or not row["preimage"]:
        return None
    return {"preimage": row["preimage"], "payment_hash": row["payment_hash"],
            "valid": verify_preimage(row["preimage"], row["payment_hash"])}


_NOTE_RE = re.compile(r"^[\w\s'’.,\-&/()+%:×]+$", re.UNICODE)


def clean_note(raw: str | None) -> str | None:
    if raw is None or not raw.strip():
        return None
    value = re.sub(r"\s+", " ", raw.strip())
    if len(value) > 60 or not _NOTE_RE.match(value):
        raise fail(422, "invalid", fields=["note"])
    return value


def own_invoice(invoice_id: str, merchant_id: int):
    if not (8 <= len(invoice_id) <= 40) or not invoice_id.replace("-", "").replace("_", "").isalnum():
        raise fail(404, "not_found")
    with db.connect() as conn:
        row = conn.execute(
            "SELECT * FROM invoices WHERE id=? AND merchant_id=?", (invoice_id, merchant_id)
        ).fetchone()
    if not row:  # même réponse pour « inexistante » et « appartient à un autre commerçant »
        raise fail(404, "not_found")
    return row


@app.post("/api/invoices", status_code=201)
def create_invoice(body: InvoiceIn, merchant_id: int = Depends(current_merchant)):
    st = S.settings
    if not st.min_amount_xof <= body.amount_xof <= st.max_amount_xof:
        raise fail(422, "amount_range", min=st.min_amount_xof, max=st.max_amount_xof)
    if not security.limiter.allow(f"invoice:{merchant_id}", 30, 60):
        raise fail(429, "too_many")
    note = clean_note(body.note)
    return invoice_out(new_invoice(merchant_id, body.amount_xof, note=note))


def new_invoice(merchant_id: int, amount_xof: int, note: str | None = None, source: str = "caisse",
                description_hash: str | None = None, amount_sat: int | None = None):
    """Crée la facture Lightning chez le bon portefeuille et l'enregistre."""
    st = S.settings
    r = S.rates.current()
    sats = amount_sat or xof_to_sat(amount_xof, r.xof_per_btc)
    with db.connect() as conn:
        shop = conn.execute("SELECT shop_name FROM merchants WHERE id=?", (merchant_id,)).fetchone()["shop_name"]
    wallet, key, backend = wallet_for(merchant_id)
    memo = f"{shop} - {amount_xof} FCFA" + (f" - {note}" if note else "")
    try:
        new = wallet.create_invoice(sats, memo, st.invoice_expiry_seconds, key, description_hash=description_hash)
    except LightningError:
        log.warning("création de facture impossible")
        raise fail(502, "lightning_down")
    t = now()
    invoice_id = secrets.token_urlsafe(12)
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO invoices(id, merchant_id, amount_xof, amount_sat, rate_xof_btc, payment_hash, bolt11, "
            "status, created_at, expires_at, backend, note, source) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (invoice_id, merchant_id, amount_xof, sats, r.xof_per_btc, new.payment_hash, new.bolt11,
             "pending", t, t + st.invoice_expiry_seconds, backend, note, source),
        )
        return conn.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,)).fetchone()


@app.post("/api/sales/cash", status_code=201)
def cash_sale(body: CashSaleIn, merchant_id: int = Depends(current_merchant)):
    """Caisse unique : une vente payée en espèces ou en Mobile Money est aussi enregistrée."""
    st = S.settings
    if not 1 <= body.amount_xof <= st.max_amount_xof:
        raise fail(422, "amount_range", min=1, max=st.max_amount_xof)
    if not security.limiter.allow(f"cash:{merchant_id}", 60, 60):
        raise fail(429, "too_many")
    note = clean_note(body.note)
    t = now()
    invoice_id = secrets.token_urlsafe(12)
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO invoices(id, merchant_id, amount_xof, amount_sat, rate_xof_btc, payment_hash, bolt11, "
            "status, created_at, expires_at, backend, note, method) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (invoice_id, merchant_id, body.amount_xof, 0, S.rates.current().xof_per_btc, secrets.token_hex(32), "",
             "pending", t, t, "training" if merchant_training(merchant_id) else "default", note, body.method),
        )
    mark_paid(invoice_id)
    return invoice_out(own_invoice(invoice_id, merchant_id))


@app.get("/api/invoices/{invoice_id}")
def get_invoice(invoice_id: str, merchant_id: int = Depends(current_merchant)):
    row = own_invoice(invoice_id, merchant_id)
    if row["status"] == "pending":
        refresh_invoice(row)
        row = own_invoice(invoice_id, merchant_id)
    return invoice_out(row)


@app.get("/api/invoices/{invoice_id}/qr.svg")
def invoice_qr(invoice_id: str, merchant_id: int = Depends(current_merchant)):
    row = own_invoice(invoice_id, merchant_id)
    # Majuscules : mode alphanumérique du QR, code plus petit et plus facile à scanner.
    qr = segno.make(f"lightning:{row['bolt11']}".upper(), error="q")  # 25 % de redondance : le logo au centre ne gêne pas la lecture
    buf = io.BytesIO()
    qr.save(buf, kind="svg", scale=6, border=3, xmldecl=False, dark="#141526")
    return Response(buf.getvalue(), media_type="image/svg+xml",
                    headers={"Cache-Control": "private, max-age=600"})


@app.post("/api/invoices/{invoice_id}/cancel")
def cancel_invoice(invoice_id: str, merchant_id: int = Depends(current_merchant)):
    row = own_invoice(invoice_id, merchant_id)
    with db.connect() as conn:
        conn.execute("UPDATE invoices SET status='cancelled' WHERE id=? AND status='pending'", (row["id"],))
    return {"ok": True}


@app.post("/api/invoices/{invoice_id}/simulate")
def simulate_payment(invoice_id: str, merchant_id: int = Depends(current_merchant)):
    """Démo et mode entraînement uniquement : jamais sur un vrai portefeuille."""
    row = own_invoice(invoice_id, merchant_id)
    if row["backend"] == "training":
        wallet = S.training_wallet
    elif row["backend"] == "default" and S.settings.simulate_allowed and isinstance(S.wallet, FakeWallet):
        wallet = S.wallet
    else:
        raise fail(404, "not_found")
    if row["status"] != "pending":
        raise fail(409, "not_pending")
    wallet.simulate_payment(row["payment_hash"])
    refresh_invoice(row)
    return invoice_out(own_invoice(invoice_id, merchant_id))


@app.post("/api/invoices/{invoice_id}/onramp")
def onramp(invoice_id: str, body: OnrampIn, merchant_id: int = Depends(current_merchant)):
    """Le client n'a pas de bitcoin : il paie en Mobile Money, un partenaire d'échange agréé
    règle la facture Lightning à sa place et le commerçant reçoit des sats.
    Démo / entraînement : le partenaire est simulé (même règle que la simulation de paiement)."""
    row = own_invoice(invoice_id, merchant_id)
    if row["method"] != "lightning":
        raise fail(404, "not_found")
    with db.connect() as conn:
        conn.execute("UPDATE invoices SET source=? WHERE id=? AND status='pending'", (f"onramp-{body.operator}", row["id"]))
    return simulate_payment(invoice_id, merchant_id)


# ---------------------------------------------------------------- ventes


def day_stats(merchant_id: int) -> tuple[dict, list]:
    t = now()
    start = day_start(t)
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT * FROM invoices WHERE merchant_id=? AND status='paid' AND paid_at>=? ORDER BY paid_at DESC",
            (merchant_id, start),
        ).fetchall()
        yesterday = conn.execute(
            "SELECT COALESCE(SUM(amount_xof),0) FROM invoices WHERE merchant_id=? AND status='paid' "
            "AND paid_at>=? AND paid_at<?",
            (merchant_id, day_start(t, -1), day_start(t, -1) + (t - start)),
        ).fetchone()[0]
    hours: dict[int, int] = {}
    for r in rows:
        h = int(hhmm(r["paid_at"])[:2])
        hours[h] = hours.get(h, 0) + 1
    biggest = max(rows, key=lambda r: r["amount_xof"]) if rows else None
    confirms = [r["paid_at"] - r["created_at"] for r in rows if r["method"] == "lightning"]
    stats = {
        "count": len(rows),
        "total_xof": sum(r["amount_xof"] for r in rows),
        "total_sat": sum(r["amount_sat"] for r in rows),
        "lightning_xof": sum(r["amount_xof"] for r in rows if r["method"] == "lightning"),
        "other_xof": sum(r["amount_xof"] for r in rows if r["method"] != "lightning"),
        "max_xof": biggest["amount_xof"] if biggest else 0,
        "max_time": hhmm(biggest["paid_at"]) if biggest else None,
        "peak_hour": max(hours, key=hours.get) if hours else None,
        "sales_by_hour": hours,
        "median_confirm_s": int(statistics.median(confirms)) if confirms else None,
        "yesterday_total_xof": yesterday,  # hier, à la même heure
    }
    return stats, rows


@app.get("/api/sales/today")
def sales_today(merchant_id: int = Depends(current_merchant)):
    stats, rows = day_stats(merchant_id)
    return {
        "count": stats["count"],
        "total_xof": stats["total_xof"],
        "total_sat": stats["total_sat"],
        "lightning_xof": stats["lightning_xof"],
        "other_xof": stats["other_xof"],
        "median_confirm_s": stats["median_confirm_s"],
        "yesterday_xof": stats["yesterday_total_xof"],
        "by_hour": by_hour_xof(rows),
        "sales": [invoice_out(r) for r in rows[:100]],
    }


def by_hour_xof(rows) -> list[int]:
    """Montant encaissé par heure (24 cases) pour le graphique du jour."""
    hours = [0] * 24
    for r in rows:
        hours[int(hhmm(r["paid_at"])[:2])] += r["amount_xof"]
    return hours


@app.get("/api/sales/history")
def sales_history(q: str = "", before: str = "", limit: int = 30, merchant_id: int = Depends(current_merchant)):
    """Historique de toutes les ventes, du plus récent au plus ancien, avec recherche.

    `q` : un montant (2500), un numéro de vente (n°17) ou une date (26/10, 2026-10-26).
    Pagination par curseur `before` = « horodatage:id » du dernier élément reçu.
    """
    q = q.strip()[:20]
    limit = max(1, min(limit, 50))
    sql = "SELECT * FROM invoices WHERE merchant_id=? AND status='paid'"
    args: list = [merchant_id]
    if before:
        ts, _, last_id = before.partition(":")
        if not ts.isdigit() or len(last_id) > 40:
            raise fail(422, "invalid")
        sql += " AND (paid_at < ? OR (paid_at = ? AND id < ?))"
        args += [int(ts), int(ts), last_id]
    if q:
        day = parse_day(q)
        digits = q.lstrip("nN°o# ").replace(" ", "")
        if day is not None:
            sql += " AND paid_at >= ? AND paid_at < ?"
            args += [day, day + 86_400]
        elif digits.isdigit() and len(digits) <= 9:
            n = int(digits)
            sql += " AND (amount_xof = ? OR sale_no = ?)"
            args += [n, n]
        else:
            return {"sales": [], "next_before": None}
    with db.connect() as conn:
        rows = conn.execute(sql + " ORDER BY paid_at DESC, id DESC LIMIT ?", (*args, limit)).fetchall()
    return {
        "sales": [invoice_out(r) for r in rows],
        "next_before": f"{rows[-1]['paid_at']}:{rows[-1]['id']}" if len(rows) == limit else None,
    }


_DAY_RE = re.compile(r"(\d{1,2})[/.-](\d{1,2})(?:[/.-](\d{4}))?")
_ISO_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def parse_day(q: str) -> int | None:
    """« 26/10 », « 26/10/2026 » ou « 2026-10-26 » → début de journée (UTC), sinon None."""
    if m := _ISO_RE.fullmatch(q):
        y, mo, d = int(m[1]), int(m[2]), int(m[3])
    elif m := _DAY_RE.fullmatch(q):
        d, mo, y = int(m[1]), int(m[2]), int(m[3] or datetime.now(timezone.utc).year)
    else:
        return None
    try:
        return int(datetime(y, mo, d, tzinfo=timezone.utc).timestamp())
    except ValueError:
        return None


# ---------------------------------------------------------------- retrait Mobile Money

# « free » est le code historique : Free Money s'appelle désormais Mixx by Yas.
OPERATORS = {"wave": "Wave", "orange": "Orange Money", "free": "Mixx by Yas"}
MIN_PAYOUT_XOF = 500


def payout_balance(conn, merchant_id: int) -> tuple[int, int]:
    """(disponible, déjà retiré aujourd'hui) en FCFA."""
    sales = conn.execute(
        # Seuls les vrais paiements Lightning sont dans le portefeuille (ni espèces, ni entraînement).
        "SELECT COALESCE(SUM(amount_xof),0) FROM invoices WHERE merchant_id=? AND status='paid' "
        "AND method='lightning' AND backend!='training'", (merchant_id,)
    ).fetchone()[0]
    out = conn.execute(
        "SELECT COALESCE(SUM(amount_xof),0) FROM payouts WHERE merchant_id=? AND status!='failed'", (merchant_id,)
    ).fetchone()[0]
    today = conn.execute(
        "SELECT COALESCE(SUM(amount_xof),0) FROM payouts WHERE merchant_id=? AND status!='failed' AND created_at>=?",
        (merchant_id, day_start(now())),
    ).fetchone()[0]
    return max(0, sales - out), today


def payout_out(row) -> dict:
    return {
        "id": row["id"], "operator": row["operator"], "operator_name": OPERATORS[row["operator"]],
        "amount_xof": row["amount_xof"], "fee_xof": row["fee_xof"], "net_xof": row["amount_xof"] - row["fee_xof"],
        "status": row["status"], "created_at": row["created_at"],
        "date": datetime.fromtimestamp(row["created_at"], tz=timezone.utc).strftime("%Y-%m-%d"),
        "time": hhmm(row["created_at"]),
    }


@app.get("/api/payouts")
def payouts(merchant_id: int = Depends(current_merchant)):
    st = S.settings
    with db.connect() as conn:
        available, today = payout_balance(conn, merchant_id)
        rows = conn.execute(
            "SELECT * FROM payouts WHERE merchant_id=? ORDER BY created_at DESC LIMIT 30", (merchant_id,)
        ).fetchall()
        phone_enc = conn.execute("SELECT phone_enc FROM merchants WHERE id=?", (merchant_id,)).fetchone()["phone_enc"]
    return {
        "available_xof": available,
        "daily_left_xof": max(0, st.payout_daily_max_xof - today),
        "fee_pct": st.payout_fee_pct,
        "min_xof": MIN_PAYOUT_XOF,
        "destination": mask_phone(S.crypto.decrypt(phone_enc)),
        "simulated": st.is_demo,
        "items": [payout_out(r) for r in rows],
    }


@app.post("/api/payouts", status_code=201)
def create_payout(body: PayoutIn, merchant_id: int = Depends(current_merchant)):
    """Retrait vers Mobile Money.

    Sécurité : code secret exigé, plafond quotidien, et destination imposée = numéro du
    commerçant (une session volée ne peut pas envoyer l'argent vers un autre numéro).
    """
    st = S.settings
    if not security.limiter.allow(f"payout:{merchant_id}", 5, 600):
        raise fail(429, "too_many")
    check_pin(merchant_id, body.pin)
    with db.transaction() as conn:
        available, today = payout_balance(conn, merchant_id)
        limit = min(available, st.payout_daily_max_xof - today)
        if body.amount_xof < MIN_PAYOUT_XOF or body.amount_xof > limit:
            raise fail(422, "payout_range", min=MIN_PAYOUT_XOF, max=max(0, limit))
        fee = round(body.amount_xof * st.payout_fee_pct / 100)
        payout_id = secrets.token_urlsafe(12)
        conn.execute(
            "INSERT INTO payouts(id, merchant_id, operator, amount_xof, fee_xof, status, created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (payout_id, merchant_id, body.operator, body.amount_xof, fee, "pending", now()),
        )
        row = conn.execute("SELECT * FROM payouts WHERE id=?", (payout_id,)).fetchone()
    log.info("retrait Mobile Money demandé")
    return payout_out(row)


@app.get("/api/sales/week")
def sales_week(merchant_id: int = Depends(current_merchant)):
    """Totaux des 7 derniers jours (aujourd'hui inclus)."""
    t = now()
    start = day_start(t, -6)
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT paid_at, amount_xof FROM invoices WHERE merchant_id=? AND status='paid' AND paid_at>=?",
            (merchant_id, start),
        ).fetchall()
    days = [{"day": datetime.fromtimestamp(start + i * 86_400, tz=timezone.utc).strftime("%Y-%m-%d"),
             "total_xof": 0, "count": 0} for i in range(7)]
    for r in rows:
        d = days[min(6, (r["paid_at"] - start) // 86_400)]
        d["total_xof"] += r["amount_xof"]
        d["count"] += 1
    return {"days": days}


@app.get("/api/sales/summary")
def sales_summary(merchant_id: int = Depends(current_merchant)):
    stats, _ = day_stats(merchant_id)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fingerprint = hashlib.sha256(json.dumps(stats, sort_keys=True).encode()).hexdigest()
    with db.connect() as conn:
        cached = conn.execute(
            "SELECT fingerprint, payload FROM ai_cache WHERE merchant_id=? AND day=?", (merchant_id, day)
        ).fetchone()
    if cached and cached["fingerprint"] == fingerprint:
        return json.loads(cached["payload"])
    if S.ai.enabled and not security.limiter.allow(f"ai:{merchant_id}", 20, 3600):
        return local_summary(stats)
    # Seules des statistiques agrégées partent vers l'IA (aucune donnée personnelle).
    result = S.ai.summary(stats)
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO ai_cache(merchant_id, day, fingerprint, payload) VALUES (?,?,?,?) "
            "ON CONFLICT(merchant_id, day) DO UPDATE SET fingerprint=excluded.fingerprint, payload=excluded.payload",
            (merchant_id, day, fingerprint, json.dumps(result, ensure_ascii=False)),
        )
    return result


@app.post("/api/assistant")
def assistant(body: AssistantIn, merchant_id: int = Depends(current_merchant)):
    if not security.limiter.allow(f"assistant:{merchant_id}", 15, 600):
        raise fail(429, "too_many")
    return S.ai.answer(body.message, [t.model_dump() for t in body.history], body.lang)


# ---------------------------------------------------------------- santé et indicateurs d'impact


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/public-config")
def public_config():
    """Infos non sensibles pour l'écran de connexion."""
    return {"demo": S.settings.is_demo and S.settings.seed_demo, "support_phone": S.settings.support_phone}


@app.get("/api/metrics")
def metrics(request: Request):
    """Indicateurs agrégés et anonymes. Désactivé sans METRICS_TOKEN."""
    token = S.settings.metrics_token
    given = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    if not token or not secrets.compare_digest(given.encode(), token.encode()):
        raise fail(404, "not_found")
    t = now()
    week = t - 7 * 86_400
    with db.connect() as conn:
        q = lambda sql, *a: conn.execute(sql, a).fetchone()[0]  # noqa: E731
        paid = conn.execute(
            "SELECT paid_at - created_at AS d FROM invoices WHERE status='paid' AND paid_at>=? "
            "AND backend!='training' AND method='lightning'", (week,)
        ).fetchall()
        created = q("SELECT COUNT(*) FROM invoices WHERE created_at>=? AND expires_at<?", week, t)
        expired = q("SELECT COUNT(*) FROM invoices WHERE status='expired' AND created_at>=?", week)
        data = {
            "merchants_total": q("SELECT COUNT(*) FROM merchants"),
            "merchants_active_7d": q("SELECT COUNT(DISTINCT merchant_id) FROM invoices WHERE status='paid' AND paid_at>=?", week),
            "sales_7d": len(paid),
            "volume_xof_7d": q("SELECT COALESCE(SUM(amount_xof),0) FROM invoices WHERE status='paid' AND paid_at>=?", week),
            "median_confirm_s_7d": int(statistics.median([r["d"] for r in paid])) if paid else None,
            "expired_rate_7d": round(expired / created, 3) if created else None,
        }
    return data


# ---------------------------------------------------------------- affiche QR à imprimer (LNURL-pay, LUD-06/16)

_PUBLIC_ID_RE = re.compile(r"^[a-z0-9-]{3,40}$")


def make_public_id(shop: str) -> str:
    """« Boutique Awa » → « boutique-awa-7k2f » (sert d'adresse Lightning : boutique-awa-7k2f@domaine)."""
    base = unicodedata.normalize("NFKD", shop).encode("ascii", "ignore").decode().lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")[:24] or "boutique"
    alphabet = "abcdefghijkmnpqrstuvwxyz23456789"
    return f"{base}-{''.join(secrets.choice(alphabet) for _ in range(4))}"


def ensure_public_ids() -> None:
    with db.connect() as conn:
        for m in conn.execute("SELECT id, shop_name FROM merchants WHERE public_id IS NULL").fetchall():
            conn.execute("UPDATE merchants SET public_id=? WHERE id=?", (make_public_id(m["shop_name"]), m["id"]))


def public_base(request: Request) -> str:
    if S.settings.public_url:
        return S.settings.public_url
    proto, host = request.url.scheme, request.headers.get("host", "localhost")
    if S.settings.trust_proxy:
        proto = request.headers.get("x-forwarded-proto", proto).split(",")[0].strip()
        host = request.headers.get("x-forwarded-host", host).split(",")[0].strip()
    return f"{proto}://{host}"


def merchant_by_public_id(public_id: str):
    if not _PUBLIC_ID_RE.match(public_id or ""):
        return None
    with db.connect() as conn:
        return conn.execute("SELECT id, shop_name FROM merchants WHERE public_id=?", (public_id,)).fetchone()


def lnurl_metadata(shop: str) -> str:
    return json.dumps([["text/plain", f"Paiement à {shop} (Caisse Teranga)"]], ensure_ascii=False)


def lnurl_encode(url: str) -> str:
    return bech32.bech32_encode("lnurl", bech32.convertbits(url.encode(), 8, 5)).upper()


def lnurl_bounds() -> tuple[int, int, int]:
    rate = S.rates.current().xof_per_btc
    lo = max(1, xof_to_sat(S.settings.min_amount_xof, rate)) * 1000
    hi = xof_to_sat(S.settings.max_amount_xof, rate) * 1000
    return lo, hi, rate


LNURL_HEADERS = {"Access-Control-Allow-Origin": "*", "Cache-Control": "no-store"}


def lnurl_error(reason: str) -> JSONResponse:
    return JSONResponse({"status": "ERROR", "reason": reason}, status_code=400, headers=LNURL_HEADERS)


@app.get("/lnurlp/{public_id}")
@app.get("/.well-known/lnurlp/{public_id}")
def lnurlp(public_id: str, request: Request):
    """Point d'entrée lu par le portefeuille du client quand il scanne l'affiche."""
    m = merchant_by_public_id(public_id)
    if not m:
        return lnurl_error("Boutique introuvable")
    lo, hi, _ = lnurl_bounds()
    return JSONResponse({
        "tag": "payRequest",
        "callback": f"{public_base(request)}/lnurlp/{public_id}/callback",
        "minSendable": lo, "maxSendable": hi,
        "metadata": lnurl_metadata(m["shop_name"]),
        "commentAllowed": 0,
    }, headers=LNURL_HEADERS)


def poster_invoice(merchant_id: int, shop: str, amount_msat: int):
    lo, hi, rate = lnurl_bounds()
    if amount_msat % 1000 or not lo <= amount_msat <= hi:
        raise fail(422, "amount_range", min=S.settings.min_amount_xof, max=S.settings.max_amount_xof)
    sats = amount_msat // 1000
    desc_hash = hashlib.sha256(lnurl_metadata(shop).encode()).hexdigest()
    return new_invoice(merchant_id, max(1, round(sats * rate / 100_000_000)), source="affiche",
                       description_hash=desc_hash, amount_sat=sats)


@app.get("/lnurlp/{public_id}/callback")
def lnurlp_callback(public_id: str, request: Request, amount: int = 0):
    """Le client a choisi un montant : on crée une facture chez le portefeuille du commerçant."""
    if not security.limiter.allow(f"lnurl-ip:{client_ip(request)}", 20, 60):
        return lnurl_error("Trop de demandes, réessayez dans une minute")
    m = merchant_by_public_id(public_id)
    if not m:
        return lnurl_error("Boutique introuvable")
    if not security.limiter.allow(f"lnurl:{m['id']}", 60, 60):
        return lnurl_error("Trop de demandes, réessayez dans une minute")
    try:
        row = poster_invoice(m["id"], m["shop_name"], amount)
    except HTTPException:
        return lnurl_error("Montant hors limites ou service indisponible")
    return JSONResponse({"pr": row["bolt11"], "routes": []}, headers=LNURL_HEADERS)


@app.get("/api/me/poster")
def poster(request: Request, merchant_id: int = Depends(current_merchant)):
    with db.connect() as conn:
        m = conn.execute("SELECT shop_name, area, public_id FROM merchants WHERE id=?", (merchant_id,)).fetchone()
    base = public_base(request)
    host = base.split("://", 1)[-1]
    return {
        "shop_name": m["shop_name"], "area": m["area"],
        "lightning_address": f"{m['public_id']}@{host}",
        "lnurl": lnurl_encode(f"{base}/lnurlp/{m['public_id']}"),
        # Un portefeuille ne joint l'affiche que si la caisse est en ligne en HTTPS.
        "reachable": base.startswith("https://"),
    }


@app.get("/api/me/poster-qr.svg")
def poster_qr(request: Request, merchant_id: int = Depends(current_merchant)):
    with db.connect() as conn:
        pid = conn.execute("SELECT public_id FROM merchants WHERE id=?", (merchant_id,)).fetchone()["public_id"]
    qr = segno.make(f"lightning:{lnurl_encode(f'{public_base(request)}/lnurlp/{pid}')}", error="q")
    buf = io.BytesIO()
    qr.save(buf, kind="svg", scale=8, border=2, xmldecl=False, dark="#141526")
    return Response(buf.getvalue(), media_type="image/svg+xml", headers={"Cache-Control": "private, max-age=300"})


@app.post("/api/me/poster/simulate", status_code=201)
def poster_simulate(body: PosterSimIn, merchant_id: int = Depends(current_merchant)):
    """Démo / entraînement : simule un client qui scanne l'affiche, choisit un montant et paie."""
    with db.connect() as conn:
        shop = conn.execute("SELECT shop_name FROM merchants WHERE id=?", (merchant_id,)).fetchone()["shop_name"]
    st = S.settings
    if not st.min_amount_xof <= body.amount_xof <= st.max_amount_xof:
        raise fail(422, "amount_range", min=st.min_amount_xof, max=st.max_amount_xof)
    sats = xof_to_sat(body.amount_xof, S.rates.current().xof_per_btc)
    row = poster_invoice(merchant_id, shop, sats * 1000)
    return simulate_payment(row["id"], merchant_id)


# ---------------------------------------------------------------- export comptable (CSV)

def csv_safe(value) -> str:
    """Anti-injection de formules : une cellule ne commence jamais par = + - @ dans Excel."""
    text = "" if value is None else str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


@app.get("/api/sales/export.csv")
def export_csv(merchant_id: int = Depends(current_merchant)):
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT * FROM invoices WHERE merchant_id=? AND status='paid' AND backend!='training' ORDER BY paid_at",
            (merchant_id,),
        ).fetchall()
    methods = {"lightning": "Lightning", "cash": "Espèces", "mobile": "Mobile Money"}
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(["Date", "Heure", "N° de vente", "Montant (FCFA)", "Montant (sats)", "Moyen", "Origine", "Note",
                "Preuve de paiement"])
    for r in rows:
        d = datetime.fromtimestamp(r["paid_at"], tz=timezone.utc)
        w.writerow([csv_safe(x) for x in (
            d.strftime("%d/%m/%Y"), d.strftime("%H:%M"), r["sale_no"], r["amount_xof"], r["amount_sat"],
            methods.get(r["method"], r["method"]), "Affiche QR" if r["source"] == "affiche" else "Caisse",
            r["note"], r["preimage"] or "")])
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return Response("\ufeff" + buf.getvalue(), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="ventes-{day}.csv"'})


# ---------------------------------------------------------------- interface

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
