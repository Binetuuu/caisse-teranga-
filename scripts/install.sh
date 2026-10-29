#!/usr/bin/env sh
# Installation en une commande :  sh scripts/install.sh
set -eu
cd "$(dirname "$0")/.."

command -v docker >/dev/null 2>&1 || { echo "Docker est requis : https://docs.docker.com/get-docker/"; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "Docker Compose v2 est requis."; exit 1; }

if [ ! -f .env ]; then
  cp .env.example .env
  # Clé maîtresse aléatoire, jamais versionnée.
  KEY=$(docker run --rm python:3.13-slim python -c "import secrets,base64;print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())")
  sed -i.bak "s|^SECRET_KEY=.*|SECRET_KEY=${KEY}|" .env && rm -f .env.bak
  chmod 600 .env
  echo "Fichier .env créé (mode démo)."
fi

docker compose up -d --build
echo ""
echo "Caisse Teranga est prête : http://localhost:${PORT:-8000}"
echo "Compte de démo : 77 123 45 67 — code secret 4826"
