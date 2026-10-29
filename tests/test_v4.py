"""Nouveautés : note, preuve de paiement, ventes en espèces, mode entraînement, affiche QR (LNURL), export CSV."""
import hashlib
import json

import bolt11
import pytest
from fastapi.testclient import TestClient

from app import security
from app.main import app

H = {"X-Requested-With": "caisse"}
_seq = iter(range(6000000, 6999999))


@pytest.fixture(autouse=True)
def reset_limits():
    security.limiter._hits.clear()


@pytest.fixture(scope="module", autouse=True)
def started():
    with TestClient(app):
        yield


def merchant():
    c = TestClient(app)
    r = c.post("/api/auth/signup", headers=H, json={
        "name": "Aïssatou Ba", "shop_name": "Épicerie Aïssatou", "area": "Rufisque",
        "phone": f"76{next(_seq)}", "pin": "4826", "accept_terms": True,
    })
    assert r.status_code == 201, r.text
    return c


def test_note_and_payment_proof():
    c = merchant()
    inv = c.post("/api/invoices", headers=H, json={"amount_xof": 1500, "note": "2 pains + sucre"}).json()
    assert inv["note"] == "2 pains + sucre"
    paid = c.post(f"/api/invoices/{inv['id']}/simulate", headers=H).json()
    proof = paid["proof"]
    # La preuve : SHA256(préimage) = empreinte de la facture.
    assert proof["valid"] is True
    assert hashlib.sha256(bytes.fromhex(proof["preimage"])).hexdigest() == proof["payment_hash"]
    assert c.post("/api/invoices", headers=H, json={"amount_xof": 1500, "note": "<script>"}).status_code == 422


def test_cash_sale_counts_but_not_withdrawable():
    c = merchant()
    sale = c.post("/api/sales/cash", headers=H, json={"amount_xof": 750, "method": "cash", "note": "Riz 1 kg"}).json()
    assert sale["status"] == "paid" and sale["method"] == "cash" and sale["sale_no"] == 1 and sale["proof"] is None
    today = c.get("/api/sales/today").json()
    assert today["total_xof"] == 750 and today["other_xof"] == 750 and today["lightning_xof"] == 0
    assert c.get("/api/payouts").json()["available_xof"] == 0  # les espèces ne sont pas dans le portefeuille


def test_training_mode():
    c = merchant()
    assert c.patch("/api/me", headers=H, json={"training": True}).status_code == 200
    assert c.get("/api/me").json()["training"] is True
    inv = c.post("/api/invoices", headers=H, json={"amount_xof": 2000}).json()
    assert inv["training"] is True and inv["simulate"] is True
    c.post(f"/api/invoices/{inv['id']}/simulate", headers=H)
    assert c.get("/api/payouts").json()["available_xof"] == 0       # faux bitcoins : rien à retirer
    assert c.delete("/api/me/training-sales", headers=H).json()["deleted"] == 1
    c.patch("/api/me", headers=H, json={"training": False})
    assert c.get("/api/me").json()["training"] is False


def test_poster_lnurl_flow():
    c = merchant()
    poster = c.get("/api/me/poster").json()
    assert poster["lnurl"].startswith("LNURL1") and "@" in poster["lightning_address"]
    pid = poster["lightning_address"].split("@")[0]
    assert pid.startswith("epicerie-aissatou-")

    anon = TestClient(app)  # le portefeuille du client : aucune session
    info = anon.get(f"/lnurlp/{pid}").json()
    assert info["tag"] == "payRequest" and info["minSendable"] <= 4_000_000 <= info["maxSendable"]
    assert anon.get(f"/.well-known/lnurlp/{pid}").json()["callback"] == info["callback"]

    pr = anon.get(f"/lnurlp/{pid}/callback", params={"amount": 4_000_000}).json()["pr"]
    decoded = bolt11.decode(pr)
    assert int(decoded.amount_msat) == 4_000_000
    # LUD-06 : la facture engage la description affichée au client.
    assert decoded.description_hash == hashlib.sha256(info["metadata"].encode()).hexdigest()

    bad = anon.get(f"/lnurlp/{pid}/callback", params={"amount": 1})
    assert bad.status_code == 400 and bad.json()["status"] == "ERROR"
    assert anon.get("/lnurlp/inconnu-0000").json()["status"] == "ERROR"
    assert anon.get("/lnurlp/..%2F..%2Fetc").status_code in (400, 404)

    sold = c.post("/api/me/poster/simulate", headers=H, json={"amount_xof": 2500}).json()
    assert sold["status"] == "paid" and sold["source"] == "affiche"


def test_csv_export_is_injection_safe():
    c = merchant()
    c.post("/api/sales/cash", headers=H, json={"amount_xof": 500, "method": "mobile", "note": "-promo"})
    r = c.get("/api/sales/export.csv")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/csv")
    text = r.content.decode("utf-8-sig")
    assert "Mobile Money" in text and ";'-promo;" in text  # cellule neutralisée pour Excel
    assert TestClient(app).get("/api/sales/export.csv").status_code == 401


def test_client_pays_with_mobile_money_onramp():
    c = merchant()
    inv = c.post("/api/invoices", headers=H, json={"amount_xof": 2000}).json()
    paid = c.post(f"/api/invoices/{inv['id']}/onramp", headers=H, json={"operator": "free"}).json()
    assert paid["status"] == "paid" and paid["source"] == "onramp-free"
    assert c.post(f"/api/invoices/{inv['id']}/onramp", headers=H, json={"operator": "inconnu"}).status_code == 422


def test_mixx_by_yas_label():
    c = merchant()
    c.post(f"/api/invoices/{c.post('/api/invoices', headers=H, json={'amount_xof': 5000}).json()['id']}/simulate", headers=H)
    p = c.post("/api/payouts", headers=H, json={"operator": "free", "amount_xof": 1000, "pin": "4826"}).json()
    assert p["operator_name"] == "Mixx by Yas"
