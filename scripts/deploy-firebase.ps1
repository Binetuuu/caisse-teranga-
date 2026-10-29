# Déploiement de Caisse Teranga sur Firebase (Hosting + Cloud Run).
# Usage, depuis le dossier caisse-teranga :
#   powershell -ExecutionPolicy Bypass -File scripts\deploy-firebase.ps1 -ProjectId mon-projet-firebase
#
# Prérequis (une seule fois, à faire vous-même) :
#   gcloud auth login        puis   firebase login
#   Projet Firebase en formule Blaze (paiement à l'usage), obligatoire pour Cloud Run.
param(
  [Parameter(Mandatory = $true)][string]$ProjectId,
  [string]$Region = "europe-west1",
  [string]$Service = "caisse-teranga"
)
$ErrorActionPreference = "Stop"
function Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Yellow }
function Check($what) { if ($LASTEXITCODE -ne 0) { throw "Échec : $what (voir le message ci-dessus)" } }

Step "Projet $ProjectId"
gcloud config set project $ProjectId | Out-Null
$ProjectNumber = gcloud projects describe $ProjectId --format="value(projectNumber)"; Check "projet introuvable ou accès refusé"

Step "Activation des services Google Cloud (Cloud Run, Cloud Build, Secret Manager)"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com; Check "activation des services (formule Blaze ?)"

Step "Clé secrète de l'application (Secret Manager, jamais dans le code)"
$ErrorActionPreference = "Continue"
gcloud secrets describe caisse-secret-key --format="value(name)" *> $null
$exists = ($LASTEXITCODE -eq 0)
$ErrorActionPreference = "Stop"
if (-not $exists) {
  $key = python -c "import secrets,base64;print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
  $key | gcloud secrets create caisse-secret-key --replication-policy=automatic --data-file=-
  Write-Host "Clé créée."
} else { Write-Host "Clé déjà présente, conservée." }
# Le compte de service de Cloud Run doit pouvoir LIRE ce secret (et rien d'autre).
gcloud secrets add-iam-policy-binding caisse-secret-key `
  --member="serviceAccount:$ProjectNumber-compute@developer.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor" | Out-Null

Step "Construction et déploiement du serveur sur Cloud Run ($Region)"
$envVars = @(
  "APP_ENV=demo", "SEED_DEMO=true", "COOKIE_SECURE=true", "SESSION_COOKIE_NAME=__session",
  "TRUST_PROXY=true", "ALLOWED_HOSTS=$ProjectId.web.app,$ProjectId.firebaseapp.com", "RATE_SOURCE=coingecko"
) -join ";"
# « ^;^ » : séparateur « ; » car ALLOWED_HOSTS contient déjà des virgules.
$envVars = "^;^" + $envVars
gcloud run deploy $Service --source . --region $Region --allow-unauthenticated `
  --min-instances 1 --max-instances 1 --memory 512Mi --cpu 1 `
  --set-env-vars $envVars --set-secrets "SECRET_KEY=caisse-secret-key:latest"; Check "déploiement Cloud Run"

Step "Publication de Firebase Hosting (https://$ProjectId.web.app)"
firebase deploy --only hosting --project $ProjectId; Check "déploiement Firebase Hosting"

Write-Host "`nTerminé : https://$ProjectId.web.app" -ForegroundColor Green
Write-Host "Compte de démo : 77 123 45 67 — code 4826"
