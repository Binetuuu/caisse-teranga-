"""Taux indicatif FCFA ↔ bitcoin.

Le taux est figé dans chaque facture au moment de la vente : le commerçant sait
exactement combien de sats correspondent à son prix en FCFA.
"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass

import httpx

log = logging.getLogger("caisse.rates")

XOF_PER_EUR = 655.957  # parité fixe du franc CFA
_SANE_MIN, _SANE_MAX = 1_000_000, 1_000_000_000  # garde-fou sur les données externes
_TTL = 300


@dataclass(frozen=True)
class Rate:
    xof_per_btc: int
    source: str
    fetched_at: int


class RateProvider:
    def __init__(self, source: str, static_rate: int) -> None:
        self._source = source
        self._static = Rate(static_rate, "fixe", int(time.time()))
        self._cached: Rate | None = None
        self._lock = threading.Lock()

    def current(self) -> Rate:
        if self._source == "static":
            return self._static
        with self._lock:
            if self._cached and time.time() - self._cached.fetched_at < _TTL:
                return self._cached
            fresh = self._fetch()
            if fresh:
                self._cached = fresh
            # En cas d'échec : dernier taux connu, sinon taux fixe de secours.
            return self._cached or self._static

    def _fetch(self) -> Rate | None:
        try:
            r = httpx.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "bitcoin", "vs_currencies": "xof,eur"},
                timeout=4.0,
            )
            r.raise_for_status()
            data = r.json().get("bitcoin", {})
            value = data.get("xof") or (data.get("eur", 0) * XOF_PER_EUR)
            value = int(float(value))
        except (httpx.HTTPError, ValueError, TypeError, AttributeError):
            log.warning("taux indisponible, utilisation du taux de secours")
            return None
        if not _SANE_MIN <= value <= _SANE_MAX:
            log.warning("taux hors limites ignoré")
            return None
        return Rate(value, "coingecko", int(time.time()))


def xof_to_sat(amount_xof: int, xof_per_btc: int) -> int:
    return max(1, round(amount_xof * 100_000_000 / xof_per_btc))
