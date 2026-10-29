import os
import tempfile

# Environnement de test commun (chargé avant tous les modules de test).
os.environ.update(
    DATA_DIR=tempfile.mkdtemp(prefix="ct-"),
    APP_ENV="demo",
    LIGHTNING_BACKEND="fake",
    RATE_SOURCE="static",
    SEED_DEMO="false",
    METRICS_TOKEN="test-metrics-token",
    NWC_ALLOW_PRIVATE="true",
)
os.environ.pop("ANTHROPIC_API_KEY", None)
