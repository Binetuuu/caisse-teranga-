# Déployer Caisse Teranga sur Firebase

## Comment ça marche

Firebase Hosting sert une adresse publique en HTTPS (`https://<projet>.web.app`) et transmet chaque requête au serveur Python, qui tourne sur **Cloud Run** (le service de conteneurs de Google relié à Firebase). C'est la même image Docker qu'en local.

```
Navigateur ──HTTPS──▶ Firebase Hosting (<projet>.web.app) ──▶ Cloud Run (conteneur caisse-teranga)
                                                                   └── clé secrète : Secret Manager
```

## Ce que vous devez faire vous-même (une seule fois)

1. **Créer le projet** sur https://console.firebase.google.com → « Ajouter un projet ». Notez son **ID** (ex. `caisse-teranga-2026`).
2. **Passer en formule Blaze** (paiement à l'usage) : Cloud Run l'exige. Ajoutez une **alerte de budget** (ex. 5 $) dans la console Google Cloud → Facturation → Budgets.
3. **Se connecter** dans un terminal :
   ```
   gcloud auth login
   firebase login
   ```

## Déployer (une commande)

Dans le dossier `caisse-teranga` :

```
powershell -ExecutionPolicy Bypass -File scripts\deploy-firebase.ps1 -ProjectId <id-du-projet>
```

Le script :
1. active Cloud Run, Cloud Build et Secret Manager ;
2. crée la **clé secrète** de l'application dans Secret Manager (jamais dans le code), lisible seulement par Cloud Run ;
3. construit l'image et la déploie sur Cloud Run (région `europe-west1`, 1 instance) ;
4. publie Firebase Hosting. L'appli est alors en ligne sur `https://<id-du-projet>.web.app`.

Pour une mise à jour : relancez la même commande.

## Réglages appliqués en ligne

| Variable | Valeur | Pourquoi |
|---|---|---|
| `COOKIE_SECURE` | `true` | Cookie envoyé uniquement en HTTPS |
| `SESSION_COOKIE_NAME` | `__session` | Firebase Hosting ne transmet que ce cookie à Cloud Run |
| `TRUST_PROXY` | `true` | Vraie adresse IP du client (limites anti-abus) |
| `ALLOWED_HOSTS` | `<id>.web.app,<id>.firebaseapp.com` | Protection anti-CSRF derrière Firebase |
| `SECRET_KEY` | Secret Manager | Clé maîtresse hors du code |
| `APP_ENV` | `demo` | Garde le compte de démo et la simulation pour le jury |

Pour activer l'IA : créez un secret `anthropic-api-key` et ajoutez `--set-secrets ANTHROPIC_API_KEY=anthropic-api-key:latest` au déploiement.

## Limites à connaître

- **Les données sont temporaires.** La base SQLite vit dans le conteneur : un redéploiement ou un redémarrage efface les comptes créés, les ventes réelles et les portefeuilles reliés (les données de démo se recréent toutes seules). Parfait pour une démo ; pour un pilote réel, passer à une base gérée (Cloud SQL ou Firestore).
- **Une seule instance** (`--max-instances 1`) : obligatoire avec SQLite, et suffisant pour une démo.
- **Coût :** l'instance minimale reste allumée pour garder les données. Vérifiez le prix sur la page de tarifs Cloud Run et supprimez le service après le hackathon : `gcloud run services delete caisse-teranga --region europe-west1`.
