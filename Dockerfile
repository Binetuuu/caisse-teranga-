# ---- base commune --------------------------------------------------------------
FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /srv
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app
# Utilisateur sans privilèges, sans shell ; seul /data est accessible en écriture.
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin caisse \
 && mkdir /data && chown caisse /data && chmod 700 /data
ENV DATA_DIR=/data

# ---- tests : docker build --target test . -------------------------------------
FROM base AS test
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY tests ./tests
USER 10001
RUN DATA_DIR=/tmp/ct-test python -m pytest -q tests

# ---- image d'exécution (cible par défaut : Docker Compose, Cloud Run) ------------
FROM base AS app
USER 10001
# PORT est fourni par Cloud Run (8080) ; 8000 en local.
ENV PORT=8000
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/api/health' % os.environ.get('PORT', '8000'), timeout=3)"]
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port \"$PORT\" --no-access-log --no-server-header"]
