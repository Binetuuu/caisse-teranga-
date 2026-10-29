"""Scénario nominal de bout en bout + tests de sécurité."""
import logging
import os
import sqlite3
import tempfile

# L'environnement de test est défini dans conftest.py.

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import security  # noqa: E402
from app.lightning import FakeWallet, LightningError, verify_bolt11  # noqa: E402
from app.main import S, app  # noqa: E402

H = {"X-Requested-With": "caisse"}
_phone_seq = iter(range(1000000, 9999999))


def new_phone() -> str:
    return f"77{next(_phone_seq)}"


@pytest.fixture(autouse=True)
def reset_rate_limits():
    security.limiter._hits.clear()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def signup(client, phone=None, pin="4826"):
    c = TestClient(app)  # client séparé = navigateur séparé (cookies distincts)
    phone = phone or new_phone()
    r = c.post("/api/auth/signup", headers=H, json={
        "name": "Awa Diop", "shop_name": "Boutique Awa", "area": "Médina, Dakar",
        "phone": phone, "pin": pin, "accept_terms": True,
    })
    assert r.status_code == 201, r.text
    return c, phone


# ------------------------------------------------------------------ scénario nominal

def test_nominal_flow(client):
    c, _ = signup(client)
    me = c.get("/api/me").json()
    assert me["shop_name"] == "Boutique Awa" and "***" in me["phone"]

    inv = c.post("/api/invoices", headers=H, json={"amount_xof": 2500}).json()
    assert inv["status"] == "pending" and inv["amount_sat"] == 4000  # 2 500 FCFA au taux 62,5 M
    assert inv["bolt11"].startswith("lnbcrt")                       # réseau de test : non payable en vrai
    verify_bolt11(inv["bolt11"], 4000)

    qr = c.get(f"/api/invoices/{inv['id']}/qr.svg")
    assert qr.status_code == 200 and qr.headers["content-type"].startswith("image/svg")

    paid = c.post(f"/api/invoices/{inv['id']}/simulate", headers=H).json()
    assert paid["status"] == "paid" and paid["sale_no"] == 1

    sales = c.get("/api/sales/today").json()
    assert sales["count"] == 1 and sales["total_xof"] == 2500

    summary = c.get("/api/sales/summary").json()
    assert "2 500 FCFA" in summary["fr"] and summary["wo"]


def test_sale_numbers_increment(client):
    c, _ = signup(client)
    for expected in (1, 2, 3):
        inv = c.post("/api/invoices", headers=H, json={"amount_xof": 500}).json()
        assert c.post(f"/api/invoices/{inv['id']}/simulate", headers=H).json()["sale_no"] == expected


def test_cancelled_then_paid_still_counts(client):
    c, _ = signup(client)
    inv = c.post("/api/invoices", headers=H, json={"amount_xof": 1000}).json()
    c.post(f"/api/invoices/{inv['id']}/cancel", headers=H)
    S.wallet.simulate_payment(_hash_of(inv["id"]))  # le client paie quand même après l'annulation
    from app.main import refresh_invoice, own_invoice
    me_id = security.session_merchant(c.cookies.get(security.SESSION_COOKIE))
    refresh_invoice(own_invoice(inv["id"], me_id))
    assert c.get(f"/api/invoices/{inv['id']}").json()["status"] == "paid"


def _hash_of(invoice_id):
    with sqlite3.connect(S.settings.database_path) as conn:
        return conn.execute("SELECT payment_hash FROM invoices WHERE id=?", (invoice_id,)).fetchone()[0]


# ------------------------------------------------------------------ sécurité

def test_csrf_header_required(client):
    c, _ = signup(client)
    assert c.post("/api/invoices", json={"amount_xof": 1000}).status_code == 403
    r = c.post("/api/invoices", headers={**H, "Origin": "https://evil.example"}, json={"amount_xof": 1000})
    assert r.status_code == 403


def test_session_cookie_flags(client):
    c = TestClient(app)
    r = c.post("/api/auth/signup", headers=H, json={
        "name": "Fatou Sow", "shop_name": "Chez Fatou", "area": "Pikine", "phone": new_phone(),
        "pin": "4826", "accept_terms": True,
    })
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=strict" in cookie


def test_security_headers(client):
    r = client.get("/")
    assert "default-src 'self'" in r.headers["content-security-policy"]
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["referrer-policy"] == "no-referrer"
    assert client.get("/api/health").headers["cache-control"] == "no-store"


def test_requires_auth(client):
    assert TestClient(app).get("/api/me").status_code == 401
    assert TestClient(app).get("/api/sales/today").status_code == 401


def test_merchants_are_isolated(client):
    a, _ = signup(client)
    b, _ = signup(client)
    inv = a.post("/api/invoices", headers=H, json={"amount_xof": 1500}).json()
    assert b.get(f"/api/invoices/{inv['id']}").status_code == 404
    assert b.get(f"/api/invoices/{inv['id']}/qr.svg").status_code == 404
    assert b.post(f"/api/invoices/{inv['id']}/simulate", headers=H).status_code == 404


@pytest.mark.parametrize("pin", ["1234", "0000", "1990", "abcd", "12"])
def test_weak_or_invalid_pin_rejected(client, pin):
    r = TestClient(app).post("/api/auth/signup", headers=H, json={
        "name": "Awa", "shop_name": "Boutique", "area": "Dakar", "phone": new_phone(), "pin": pin, "accept_terms": True,
    })
    assert r.status_code == 422


@pytest.mark.parametrize("phone", ["12345", "+33612345678", "771234567890", "<script>"])
def test_invalid_phone_rejected(client, phone):
    r = TestClient(app).post("/api/auth/signup", headers=H, json={
        "name": "Awa", "shop_name": "Boutique", "area": "Dakar", "phone": phone, "pin": "4826", "accept_terms": True,
    })
    assert r.status_code == 422


def test_unknown_fields_and_bad_text_rejected(client):
    base = {"name": "Awa", "shop_name": "Boutique", "area": "Dakar", "phone": new_phone(), "pin": "4826", "accept_terms": True}
    assert TestClient(app).post("/api/auth/signup", headers=H, json={**base, "is_admin": True}).status_code == 422
    assert TestClient(app).post("/api/auth/signup", headers=H, json={**base, "name": "<img src=x onerror=1>"}).status_code == 422


@pytest.mark.parametrize("amount", [0, -5, 99, 500_001, 10**12])
def test_amount_bounds(client, amount):
    c, _ = signup(client)
    assert c.post("/api/invoices", headers=H, json={"amount_xof": amount}).status_code == 422


def test_login_lockout_and_no_enumeration(client):
    _, phone = signup(client)
    c = TestClient(app)
    unknown = c.post("/api/auth/login", headers=H, json={"phone": new_phone(), "pin": "9999"})
    wrong = c.post("/api/auth/login", headers=H, json={"phone": phone, "pin": "9999"})
    assert unknown.status_code == wrong.status_code == 401
    assert unknown.json() == wrong.json()  # même réponse : on ne révèle pas si le compte existe
    for _ in range(4):
        c.post("/api/auth/login", headers=H, json={"phone": phone, "pin": "9999"})
    r = c.post("/api/auth/login", headers=H, json={"phone": phone, "pin": "4826"})
    assert r.status_code == 429 and r.json()["error"] == "locked"


def test_login_ok(client):
    _, phone = signup(client)
    c = TestClient(app)
    assert c.post("/api/auth/login", headers=H, json={"phone": phone, "pin": "4826"}).status_code == 200
    assert c.get("/api/me").status_code == 200
    c.post("/api/auth/logout", headers=H)
    assert c.get("/api/me").status_code == 401


def test_phone_and_session_not_stored_in_clear(client):
    c, phone = signup(client)
    token = c.cookies.get(security.SESSION_COOKIE)
    raw = open(S.settings.database_path, "rb").read()
    assert phone.encode() not in raw and ("+221" + phone).encode() not in raw
    assert token.encode() not in raw


def test_log_redaction():
    rec = logging.LogRecord("t", logging.INFO, "", 0, "tel %s facture %s", ("+221 77 123 45 67", "lnbcrt40u1" + "q" * 60), None)
    security.RedactFilter().filter(rec)
    assert "77 123" not in rec.getMessage() and "lnbcrt" not in rec.getMessage()


def test_bolt11_verification_rejects_wrong_amount():
    inv = FakeWallet().create_invoice(4000, "test", 600)
    verify_bolt11(inv.bolt11, 4000, inv.payment_hash)
    with pytest.raises(LightningError):
        verify_bolt11(inv.bolt11, 4001)
    with pytest.raises(LightningError):
        verify_bolt11(inv.bolt11, 4000, "0" * 64)
    with pytest.raises(LightningError):
        verify_bolt11("pas-une-facture", 4000)


def test_metrics_protected(client):
    assert client.get("/api/metrics").status_code == 404
    r = client.get("/api/metrics", headers={"Authorization": "Bearer test-metrics-token"})
    assert r.status_code == 200 and "merchants_active_7d" in r.json()


def test_assistant_local_answer(client):
    c, _ = signup(client)
    r = c.post("/api/assistant", headers=H, json={"message": "Le paiement n'arrive pas", "lang": "fr"})
    assert r.status_code == 200 and "10 minutes" in r.json()["reply"]


def test_week_and_hourly_totals(client):
    c, _ = signup(client)
    inv = c.post("/api/invoices", headers=H, json={"amount_xof": 3000}).json()
    c.post(f"/api/invoices/{inv['id']}/simulate", headers=H)
    week = c.get("/api/sales/week").json()["days"]
    assert len(week) == 7 and week[-1]["total_xof"] == 3000 and week[-1]["count"] == 1
    assert sum(c.get("/api/sales/today").json()["by_hour"]) == 3000
