"""Historique + recherche, changement de code, retrait Mobile Money, Nostr Wallet Connect."""
import json
import secrets
import threading
import time

import pytest
from fastapi.testclient import TestClient
from websockets.sync.server import serve

from app import nwc, security
from app.lightning import FakeWallet
from app.main import app, process_payouts

H = {"X-Requested-With": "caisse"}
_seq = iter(range(5000000, 5999999))


@pytest.fixture(autouse=True)
def reset_limits():
    security.limiter._hits.clear()


@pytest.fixture(scope="module", autouse=True)
def started():
    with TestClient(app):
        yield


def merchant(pin="4826"):
    c = TestClient(app)
    phone = f"78{next(_seq)}"
    r = c.post("/api/auth/signup", headers=H, json={
        "name": "Moussa Ndiaye", "shop_name": "Quincaillerie Moussa", "area": "Thiès",
        "phone": phone, "pin": pin, "accept_terms": True,
    })
    assert r.status_code == 201, r.text
    return c, phone


def sell(c, amount):
    inv = c.post("/api/invoices", headers=H, json={"amount_xof": amount}).json()
    return c.post(f"/api/invoices/{inv['id']}/simulate", headers=H).json()


# ------------------------------------------------------------------ historique

def test_history_search_and_pagination():
    c, _ = merchant()
    for amount in (500, 1000, 2500, 1000, 750):
        sell(c, amount)
    page1 = c.get("/api/sales/history?limit=3").json()
    assert len(page1["sales"]) == 3 and page1["next_before"]
    page2 = c.get(f"/api/sales/history?limit=3&before={page1['next_before']}").json()
    ids = {s["id"] for s in page1["sales"]} | {s["id"] for s in page2["sales"]}
    assert len(ids) == 5  # aucune vente perdue ni en double, même dans la même seconde

    assert {s["amount_xof"] for s in c.get("/api/sales/history?q=1000").json()["sales"]} == {1000}
    by_no = c.get("/api/sales/history?q=n°3").json()["sales"]
    assert [s["sale_no"] for s in by_no] == [3]
    today = time.strftime("%d/%m", time.gmtime())
    assert len(c.get(f"/api/sales/history?q={today}").json()["sales"]) == 5
    assert c.get("/api/sales/history?q=<script>").json()["sales"] == []


def test_history_is_private():
    a, _ = merchant()
    sell(a, 4321)
    b, _ = merchant()
    assert b.get("/api/sales/history?q=4321").json()["sales"] == []


# ------------------------------------------------------------------ code secret

def test_change_pin():
    c, phone = merchant()
    other = TestClient(app)
    assert other.post("/api/auth/login", headers=H, json={"phone": phone, "pin": "4826"}).status_code == 200

    assert c.post("/api/me/pin", headers=H, json={"current_pin": "9999", "new_pin": "5937"}).status_code == 403
    assert c.post("/api/me/pin", headers=H, json={"current_pin": "4826", "new_pin": "1111"}).status_code == 422
    assert c.post("/api/me/pin", headers=H, json={"current_pin": "4826", "new_pin": "5937"}).status_code == 200

    assert other.get("/api/me").status_code == 401          # autre appareil déconnecté
    assert c.get("/api/me").status_code == 200              # appareil courant conservé
    fresh = TestClient(app)
    assert fresh.post("/api/auth/login", headers=H, json={"phone": phone, "pin": "5937"}).status_code == 200


# ------------------------------------------------------------------ retrait Mobile Money

def test_payout_flow_and_guards():
    c, _ = merchant()
    sell(c, 5000)
    info = c.get("/api/payouts").json()
    assert info["available_xof"] == 5000 and "***" in info["destination"]

    bad_pin = c.post("/api/payouts", headers=H, json={"operator": "wave", "amount_xof": 2000, "pin": "0000"})
    assert bad_pin.status_code == 403
    too_much = c.post("/api/payouts", headers=H, json={"operator": "wave", "amount_xof": 9000, "pin": "4826"})
    assert too_much.status_code == 422 and too_much.json()["max"] == 5000
    # Impossible de choisir un autre numéro de destination : champ refusé.
    other = c.post("/api/payouts", headers=H, json={"operator": "wave", "amount_xof": 2000, "pin": "4826", "phone": "770000000"})
    assert other.status_code == 422

    ok = c.post("/api/payouts", headers=H, json={"operator": "orange", "amount_xof": 2000, "pin": "4826"}).json()
    assert ok["status"] == "pending" and ok["fee_xof"] == 20 and ok["net_xof"] == 1980
    assert c.get("/api/payouts").json()["available_xof"] == 3000

    from app import db
    with db.connect() as conn:
        conn.execute("UPDATE payouts SET created_at=created_at-10 WHERE id=?", (ok["id"],))
    process_payouts()
    assert c.get("/api/payouts").json()["items"][0]["status"] == "completed"


# ------------------------------------------------------------------ Nostr Wallet Connect

def test_nip04_and_event_signature_roundtrip():
    a, b = secrets.token_hex(32), secrets.token_hex(32)
    msg = nwc.nip04_encrypt(a, nwc.xonly(b), "Jërëjëf ⚡")
    assert nwc.nip04_decrypt(b, nwc.xonly(a), msg) == "Jërëjëf ⚡"
    ev = nwc.sign_event(a, 23194, "x", [["p", nwc.xonly(b)]])
    assert nwc.verify_event(ev)
    ev["content"] = "y"
    assert not nwc.verify_event(ev)


@pytest.mark.parametrize("uri", [
    "https://exemple.com",
    "nostr+walletconnect://abc?relay=wss://relay.example&secret=00",
    "nostr+walletconnect://" + "a" * 64 + "?relay=http://relay.example&secret=" + "b" * 64,
    "nostr+walletconnect://" + "a" * 64 + "?relay=wss://127.0.0.1&secret=" + "b" * 64,
    "nostr+walletconnect://" + "a" * 64 + "?relay=wss://192.168.1.10&secret=" + "b" * 64,
])
def test_nwc_uri_rejected(uri):
    with pytest.raises(ValueError):
        nwc.parse_uri(uri, allow_private=False)


class FakeWalletService:
    """Relais Nostr + service de portefeuille NIP-47 minimal, en local, pour les tests."""

    def __init__(self, methods="make_invoice lookup_invoice"):
        self.priv = secrets.token_hex(32)
        self.pub = nwc.xonly(self.priv)
        self.client_priv = secrets.token_hex(32)
        self.methods = methods
        self.ln = FakeWallet()
        self.paid: set[str] = set()
        self.server = serve(self.handle, "127.0.0.1", 0)
        self.port = self.server.socket.getsockname()[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    @property
    def uri(self):
        return f"nostr+walletconnect://{self.pub}?relay=ws://127.0.0.1:{self.port}&secret={self.client_priv}"

    def handle(self, ws):
        subs = {}
        for raw in ws:
            msg = json.loads(raw)
            if msg[0] == "REQ":
                subs[msg[1]] = msg[2]
                if 13194 in msg[2].get("kinds", []):
                    info = nwc.sign_event(self.priv, 13194, self.methods, [])
                    ws.send(json.dumps(["EVENT", msg[1], info]))
                    ws.send(json.dumps(["EOSE", msg[1]]))
            elif msg[0] == "EVENT":
                ev = msg[1]
                assert nwc.verify_event(ev)
                req = json.loads(nwc.nip04_decrypt(self.priv, ev["pubkey"], ev["content"]))
                if req["method"] == "make_invoice":
                    inv = self.ln.create_invoice(req["params"]["amount"] // 1000, req["params"]["description"], 600)
                    result = {"type": "incoming", "invoice": inv.bolt11, "payment_hash": inv.payment_hash}
                else:
                    h = req["params"]["payment_hash"]
                    result = {"payment_hash": h, "settled_at": int(time.time()) if h in self.paid else None}
                content = nwc.nip04_encrypt(self.priv, ev["pubkey"], json.dumps({"result_type": req["method"], "result": result}))
                resp = nwc.sign_event(self.priv, 23195, content, [["p", ev["pubkey"]], ["e", ev["id"]]])
                for sub in subs:
                    ws.send(json.dumps(["EVENT", sub, resp]))


def test_nwc_real_wallet_flow():
    svc = FakeWalletService()
    c, _ = merchant()
    r = c.put("/api/me/nwc", headers=H, json={"uri": svc.uri})
    assert r.status_code == 200, r.text
    assert r.json()["can_spend"] is False
    assert c.get("/api/me").json()["nwc_linked"] is True

    inv = c.post("/api/invoices", headers=H, json={"amount_xof": 2500}).json()
    assert inv["real"] is True and inv["simulate"] is False
    # Impossible de « simuler » un paiement sur un vrai portefeuille.
    assert c.post(f"/api/invoices/{inv['id']}/simulate", headers=H).status_code == 404
    assert c.get(f"/api/invoices/{inv['id']}").json()["status"] == "pending"

    from app import db
    with db.connect() as conn:
        h = conn.execute("SELECT payment_hash FROM invoices WHERE id=?", (inv["id"],)).fetchone()[0]
    svc.paid.add(h)  # le client paie depuis son portefeuille
    assert c.get(f"/api/invoices/{inv['id']}").json()["status"] == "paid"

    raw = open(db._db_path, "rb").read()
    assert svc.client_priv.encode() not in raw  # secret NWC chiffré en base


def test_nwc_warns_if_connection_can_spend():
    svc = FakeWalletService(methods="make_invoice lookup_invoice pay_invoice")
    c, _ = merchant()
    assert c.put("/api/me/nwc", headers=H, json={"uri": svc.uri}).json()["can_spend"] is True


# ------------------------------------------------------------------ derrière Firebase Hosting

def test_firebase_proxy_origin_and_cookie(monkeypatch):
    from dataclasses import replace
    from app.main import S
    monkeypatch.setattr(S, "settings", replace(S.settings, allowed_hosts=frozenset({"caisse.web.app"})))
    c, _ = merchant()
    ok = c.post("/api/invoices", headers={**H, "Origin": "https://caisse.web.app"}, json={"amount_xof": 1000})
    assert ok.status_code == 201
    bad = c.post("/api/invoices", headers={**H, "Origin": "https://pirate.web.app"}, json={"amount_xof": 1000})
    assert bad.status_code == 403
