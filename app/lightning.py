"""Accès Lightning en lecture/encaissement uniquement.

Principe du moindre privilège : l'application ne détient JAMAIS de clé capable
de dépenser. Avec LNbits on utilise la clé « Invoice/read » (créer des factures,
lire leur état), jamais la clé « Admin ».

Chaque facture renvoyée par le service est décodée et vérifiée avec la
bibliothèque `bolt11` (celle utilisée par LNbits) : montant et empreinte de
paiement doivent correspondre à ce qui a été demandé.
"""
from __future__ import annotations

import hashlib
import logging
import re
import secrets
import time
from dataclasses import dataclass

import httpx
from bolt11 import Bolt11, MilliSatoshi, TagChar, Tags, decode, encode

log = logging.getLogger("caisse.lightning")

INVOICE_KEY_RE = re.compile(r"^[0-9a-f]{32}$")


class LightningError(Exception):
    """Le service Lightning est injoignable ou a répondu de façon incohérente."""


@dataclass(frozen=True)
class NewInvoice:
    payment_hash: str
    bolt11: str


def verify_preimage(preimage: str | None, payment_hash: str) -> bool:
    """Preuve de paiement : seul celui qui a été payé connaît s tel que SHA256(s) = empreinte."""
    if not preimage or not re.fullmatch(r"[0-9a-fA-F]{64}", preimage):
        return False
    return hashlib.sha256(bytes.fromhex(preimage)).hexdigest() == payment_hash


def verify_bolt11(bolt11: str, amount_sat: int, payment_hash: str | None = None) -> str:
    """Décode la facture et vérifie montant (+ empreinte). Renvoie l'empreinte."""
    try:
        decoded = decode(bolt11)
    except Exception as exc:  # noqa: BLE001 — toute facture illisible est refusée
        raise LightningError("facture illisible") from exc
    if decoded.amount_msat is None or int(decoded.amount_msat) != amount_sat * 1000:
        raise LightningError("montant de la facture incorrect")
    if payment_hash and decoded.payment_hash != payment_hash:
        raise LightningError("empreinte de paiement incorrecte")
    return decoded.payment_hash


class FakeWallet:
    """Portefeuille de démonstration : vraies factures BOLT11 signées, réseau « regtest ».

    Les factures sont au format réel (décodables par tout portefeuille) mais sur
    le réseau de test `lnbcrt` : impossible de les payer avec de vrais bitcoins
    par erreur. Le paiement est simulé depuis l'écran de démo.
    """

    name = "fake"

    def __init__(self) -> None:
        self._privkey = secrets.token_hex(32)
        self._paid: set[str] = set()
        self._preimages: dict[str, str] = {}

    def create_invoice(self, amount_sat: int, memo: str, expiry: int, api_key: str | None = None,
                       description_hash: str | None = None) -> NewInvoice:
        preimage = secrets.token_bytes(32)
        payment_hash = hashlib.sha256(preimage).hexdigest()
        self._preimages[payment_hash] = preimage.hex()
        tags = Tags()
        tags.add(TagChar.payment_hash, payment_hash)
        tags.add(TagChar.payment_secret, secrets.token_hex(32))
        if description_hash:
            tags.add(TagChar.description_hash, description_hash)
        else:
            tags.add(TagChar.description, memo)
        tags.add(TagChar.expire_time, expiry)
        invoice = Bolt11(
            currency="bcrt",
            amount_msat=MilliSatoshi(amount_sat * 1000),
            date=int(time.time()),
            tags=tags,
        )
        return NewInvoice(payment_hash=payment_hash, bolt11=encode(invoice, self._privkey))

    def status(self, payment_hash: str, api_key: str | None = None) -> tuple[bool, str | None]:
        paid = payment_hash in self._paid
        return paid, self._preimages.get(payment_hash) if paid else None

    def is_paid(self, payment_hash: str, api_key: str | None = None) -> bool:
        return self.status(payment_hash, api_key)[0]

    def simulate_payment(self, payment_hash: str) -> None:
        self._paid.add(payment_hash)

    def check_key(self, api_key: str) -> bool:
        return True


class LNbitsWallet:
    """Client minimal de l'API LNbits (v0.12 et v1.x)."""

    name = "lnbits"

    def __init__(self, base_url: str, default_key: str) -> None:
        self._base = base_url
        self._default_key = default_key
        self._client = httpx.Client(
            timeout=httpx.Timeout(10.0, connect=5.0),
            follow_redirects=False,  # pas de redirection vers un hôte inattendu
            headers={"User-Agent": "caisse-teranga/1.0"},
        )

    def _key(self, api_key: str | None) -> str:
        key = api_key or self._default_key
        if not key:
            raise LightningError("aucun portefeuille configuré")
        return key

    def create_invoice(self, amount_sat: int, memo: str, expiry: int, api_key: str | None = None,
                       description_hash: str | None = None) -> NewInvoice:
        body = {"out": False, "amount": amount_sat, "unit": "sat", "memo": memo, "expiry": expiry}
        if description_hash:
            body["description_hash"] = description_hash
        try:
            r = self._client.post(
                f"{self._base}/api/v1/payments",
                headers={"X-Api-Key": self._key(api_key)},
                json=body,
            )
        except httpx.HTTPError as exc:
            raise LightningError("service Lightning injoignable") from exc
        if r.status_code not in (200, 201):
            log.warning("LNbits création facture : statut %s", r.status_code)
            raise LightningError("le service Lightning a refusé la facture")
        data = r.json()
        bolt11 = data.get("bolt11") or data.get("payment_request") or ""
        payment_hash = str(data.get("payment_hash", ""))
        if not re.fullmatch(r"[0-9a-f]{64}", payment_hash):
            raise LightningError("réponse Lightning inattendue")
        verify_bolt11(bolt11, amount_sat, payment_hash)
        return NewInvoice(payment_hash=payment_hash, bolt11=bolt11)

    def status(self, payment_hash: str, api_key: str | None = None) -> tuple[bool, str | None]:
        try:
            r = self._client.get(
                f"{self._base}/api/v1/payments/{payment_hash}",
                headers={"X-Api-Key": self._key(api_key)},
            )
        except httpx.HTTPError as exc:
            raise LightningError("service Lightning injoignable") from exc
        if r.status_code != 200:
            raise LightningError("état du paiement indisponible")
        data = r.json()
        preimage = data.get("preimage") or (data.get("details") or {}).get("preimage")
        return data.get("paid") is True, preimage if isinstance(preimage, str) else None

    def is_paid(self, payment_hash: str, api_key: str | None = None) -> bool:
        return self.status(payment_hash, api_key)[0]

    def check_key(self, api_key: str) -> bool:
        """Vérifie qu'une clé ouvre bien un portefeuille (sans rien dépenser)."""
        try:
            r = self._client.get(f"{self._base}/api/v1/wallet", headers={"X-Api-Key": api_key})
        except httpx.HTTPError as exc:
            raise LightningError("service Lightning injoignable") from exc
        return r.status_code == 200


def build_wallet(settings) -> FakeWallet | LNbitsWallet:
    if settings.lightning_backend == "lnbits":
        return LNbitsWallet(settings.lnbits_url, settings.lnbits_invoice_key)
    return FakeWallet()
