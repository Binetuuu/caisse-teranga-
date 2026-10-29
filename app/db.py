"""Stockage SQLite. Requêtes toujours paramétrées (pas d'injection SQL)."""
from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS merchants (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    shop_name     TEXT NOT NULL,
    area          TEXT NOT NULL,
    phone_hash    TEXT NOT NULL UNIQUE,   -- HMAC du numéro : recherche sans stocker le numéro en clair
    phone_enc     BLOB NOT NULL,          -- numéro chiffré (Fernet)
    pin_hash      TEXT NOT NULL,          -- Argon2id
    lang          TEXT NOT NULL DEFAULT 'fr',
    ln_key_enc    BLOB,                   -- clé « facture » LNbits du commerçant, chiffrée
    created_at    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token_hash    TEXT PRIMARY KEY,       -- SHA-256 du jeton : un vol de la base ne donne pas de session
    merchant_id   INTEGER NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    created_at    INTEGER NOT NULL,
    expires_at    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS login_attempts (
    key           TEXT PRIMARY KEY,       -- HMAC du numéro ou de l'IP, jamais la valeur brute
    failures      INTEGER NOT NULL,
    locked_until  INTEGER NOT NULL DEFAULT 0,
    updated_at    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS invoices (
    id            TEXT PRIMARY KEY,       -- identifiant aléatoire non devinable
    merchant_id   INTEGER NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    sale_no       INTEGER,                -- numéro de vente du jour, attribué au paiement
    amount_xof    INTEGER NOT NULL,
    amount_sat    INTEGER NOT NULL,
    rate_xof_btc  INTEGER NOT NULL,       -- taux figé au moment de la vente
    payment_hash  TEXT NOT NULL,
    bolt11        TEXT NOT NULL,
    status        TEXT NOT NULL CHECK (status IN ('pending','paid','expired','cancelled')),
    created_at    INTEGER NOT NULL,
    expires_at    INTEGER NOT NULL,
    paid_at       INTEGER
);
CREATE INDEX IF NOT EXISTS idx_invoices_merchant ON invoices(merchant_id, created_at);
CREATE INDEX IF NOT EXISTS idx_invoices_pending ON invoices(status, expires_at);

CREATE TABLE IF NOT EXISTS payouts (
    id            TEXT PRIMARY KEY,
    merchant_id   INTEGER NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    operator      TEXT NOT NULL CHECK (operator IN ('wave','orange','free')),
    amount_xof    INTEGER NOT NULL,
    fee_xof       INTEGER NOT NULL,
    status        TEXT NOT NULL CHECK (status IN ('pending','completed','failed')),
    created_at    INTEGER NOT NULL,
    completed_at  INTEGER
);
CREATE INDEX IF NOT EXISTS idx_payouts_merchant ON payouts(merchant_id, created_at);

CREATE TABLE IF NOT EXISTS ai_cache (
    merchant_id   INTEGER NOT NULL,
    day           TEXT NOT NULL,
    fingerprint   TEXT NOT NULL,
    payload       TEXT NOT NULL,
    PRIMARY KEY (merchant_id, day)
);
"""

_lock = threading.Lock()
_db_path: Path | None = None


def init_db(path: Path) -> None:
    global _db_path
    _db_path = path
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(SCHEMA)
        # Migrations additives (bases créées par une version précédente).
        for sql in (
            "ALTER TABLE merchants ADD COLUMN nwc_enc BLOB",  # connexion NWC chiffrée
            "ALTER TABLE invoices ADD COLUMN backend TEXT NOT NULL DEFAULT 'default'",
            "ALTER TABLE invoices ADD COLUMN note TEXT",               # « 2 pains + sucre »
            "ALTER TABLE invoices ADD COLUMN preimage TEXT",           # preuve de paiement
            "ALTER TABLE invoices ADD COLUMN method TEXT NOT NULL DEFAULT 'lightning'",  # lightning|cash|mobile
            "ALTER TABLE invoices ADD COLUMN source TEXT NOT NULL DEFAULT 'caisse'",     # caisse|affiche
            "ALTER TABLE merchants ADD COLUMN public_id TEXT",         # identifiant public de l'affiche QR
            "ALTER TABLE merchants ADD COLUMN training INTEGER NOT NULL DEFAULT 0",  # mode entraînement
        ):
            try:
                conn.execute(sql)
            except sqlite3.OperationalError:
                pass  # colonne déjà présente
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_merchants_public ON merchants(public_id)")


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    if _db_path is None:
        raise RuntimeError("Base non initialisée")
    conn = sqlite3.connect(_db_path, timeout=10, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def transaction() -> Iterator[sqlite3.Connection]:
    """Transaction exclusive : sert à attribuer les numéros de vente sans doublon."""
    with _lock, connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            yield conn
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise
