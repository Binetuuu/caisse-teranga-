"""Données de démonstration : « Boutique Awa » avec une journée de ventes réaliste.

Identifiants de démo (fictifs, documentés dans le README) :
    téléphone 77 123 45 67 — code secret 4826
"""
from __future__ import annotations

import logging
import random
import secrets
import time

from . import db, security
from .rates import xof_to_sat

log = logging.getLogger("caisse.seed")

DEMO_PHONE = "+221771234567"
DEMO_PIN = "4826"

# Prix typiques d'une boutique de quartier (pain, sucre, crédit, savon, riz...).
PRICES = [150, 250, 300, 500, 500, 750, 1000, 1000, 1500, 2000, 2500, 3000, 5000, 7500]


def seed_if_empty(crypto: security.Crypto, settings, wallet) -> None:
    with db.connect() as conn:
        if conn.execute("SELECT COUNT(*) FROM merchants").fetchone()[0]:
            return
        cur = conn.execute(
            "INSERT INTO merchants(name, shop_name, area, phone_hash, phone_enc, pin_hash, created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            ("Awa Diop", "Boutique Awa", "Médina, Dakar", crypto.blind("phone:" + DEMO_PHONE),
             crypto.encrypt(DEMO_PHONE), security.hash_pin(DEMO_PIN), int(time.time()) - 30 * 86_400),
        )
        merchant_id = cur.lastrowid

    rng = random.Random(221)
    now = int(time.time())
    rate = settings.btc_xof_static
    today = now - now % 86_400
    yesterday = today - 86_400

    def add(paid_at: int, sale_no: int, amount: int) -> None:
        confirm = rng.randint(2, 6)
        created = paid_at - confirm
        sats = xof_to_sat(amount, rate)
        with db.connect() as conn:
            conn.execute(
                "INSERT INTO invoices(id, merchant_id, sale_no, amount_xof, amount_sat, rate_xof_btc, payment_hash, "
                "bolt11, status, created_at, expires_at, paid_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (secrets.token_urlsafe(12), merchant_id, sale_no, amount, sats, rate,
                 secrets.token_hex(32), "historique-demo",
                 "paid", created, created + 600, paid_at),
            )

    # Semaine passée : 12 à 24 ventes/jour. Aujourd'hui : 16 ventes réparties sur les heures passées.
    for back in range(6, 1, -1):
        day = today - back * 86_400
        for i, ts in enumerate(sorted(day + rng.randint(8 * 3600, 20 * 3600) for _ in range(rng.randint(12, 24))), 1):
            add(ts, i, rng.choice(PRICES))
    for i, ts in enumerate(sorted(yesterday + rng.randint(8 * 3600, 20 * 3600) for _ in range(19)), 1):
        add(ts, i, rng.choice(PRICES))
    span_start = max(today + 7 * 3600, now - 9 * 3600)
    span_start = min(span_start, now - 1800)
    span_end = max(span_start + 600, now - 300)
    stamps = sorted(rng.randint(span_start, span_end) for _ in range(16))
    for i, ts in enumerate(stamps, 1):
        add(min(ts, now - 60), i, rng.choice(PRICES))
    log.info("données de démo créées (Boutique Awa)")
