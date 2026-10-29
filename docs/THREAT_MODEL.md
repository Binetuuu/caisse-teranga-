# Modèle de menaces — Caisse Teranga

Méthode : STRIDE sur les flux du schéma d'architecture (README §4). Version MVP, novembre 2026.

## 1. Ce qu'on protège

| Actif | Pourquoi c'est sensible |
|---|---|
| **Fonds du commerçant** | Perte directe d'argent |
| Clés LNbits (opérateur et commerçants) | Accès au portefeuille |
| Numéro de téléphone, nom, quartier | Données personnelles (loi sénégalaise 2008-12, CDP) |
| Historique des ventes | Données commerciales confidentielles |
| Session / code secret | Prise de contrôle du compte |

## 2. Acteurs et limites de confiance

- **Commerçant** (navigateur) — authentifié par numéro + code secret.
- **Client payeur** — ne touche jamais l'application, seulement la facture Lightning.
- **Attaquant réseau** — Wi-Fi public, opérateur.
- **Attaquant web** — site malveillant ouvert dans le même navigateur.
- **Voleur de téléphone / regard par-dessus l'épaule.**
- **Attaquant ayant une copie de la base** (sauvegarde volée, disque).
- **Services tiers** : LNbits, CoinGecko, API Claude.

Limites de confiance : navigateur ↔ API ; API ↔ LNbits ; API ↔ CoinGecko ; API ↔ Claude ; conteneur ↔ hôte.

## 3. Menaces et contre-mesures (STRIDE)

| # | Menace | Catégorie | Contre-mesure | Reste à faire |
|---|---|---|---|---|
| 1 | Vol du serveur ⇒ vol des fonds | Élévation | **Clé Invoice/read uniquement** : le serveur ne peut pas dépenser. Aucune clé Admin, aucune graine. | — |
| 2 | Facture falsifiée par un LNbits compromis ou un intermédiaire (mauvais montant, autre destinataire) | Falsification | Chaque facture est **décodée et vérifiée** (`bolt11`) : montant et empreinte doivent correspondre. HTTPS obligatoire, pas de redirection suivie. | Vérifier aussi le nœud destinataire attendu (`payee`) |
| 3 | Faux « Paiement reçu » (capture d'écran, fausse notification montrée par le client) | Usurpation | L'état « payé » ne vient **que du serveur**, qui interroge LNbits. L'écran de confirmation recharge la facture et exige `status=paid`. Formation : « ne remettez la marchandise qu'après l'écran vert + le son ». | — |
| 4 | Force brute du code à 4 chiffres | Usurpation | Argon2id ; **verrouillage progressif** par numéro après 5 échecs (15 min → 24 h) ; limite par IP (30/15 min) ; codes faibles refusés. | 2ᵉ facteur (SMS/WebAuthn) |
| 5 | Blocage volontaire d'un compte par un tiers (essais ratés exprès) | Déni de service | Durée limitée ; journal d'alerte. **Accepté** pour le MVP. | Déblocage par SMS |
| 6 | Énumération des numéros inscrits | Divulgation | Même réponse et même durée (hash factice) pour compte inconnu ou code faux. L'inscription indique « numéro déjà utilisé » (compromis ergonomique, limité à 10/h/IP). | — |
| 7 | CSRF : un site tiers crée/annule des factures | Falsification | Cookie `SameSite=Strict` + en-tête `X-Requested-With` obligatoire (impossible sans CORS) + contrôle d'`Origin`. Aucun CORS activé. | — |
| 8 | XSS (nom de boutique piégé…) | Falsification | Liste blanche de caractères côté serveur ; **échappement systématique** côté client ; **CSP sans `unsafe-inline`** (ni script ni style en ligne). | — |
| 9 | Clickjacking | Falsification | `X-Frame-Options: DENY`, `frame-ancestors 'none'`. | — |
| 10 | Vol de session (réseau, XSS) | Usurpation | Cookie `HttpOnly`, `Secure` + HSTS en production ; jeton 256 bits ; **stocké haché** ; expiration 12 h ; déconnexion côté serveur. | Liste des appareils connectés |
| 11 | Accès aux factures d'un autre commerçant (IDOR) | Divulgation | Toutes les requêtes filtrent par `merchant_id` de session ; ID aléatoires 96 bits ; 404 identique. **Testé.** | — |
| 12 | Fuite de la base | Divulgation | Numéros **chiffrés** (Fernet) + recherche par **HMAC** ; PIN Argon2id ; sessions hachées ; clés LNbits chiffrées ; clé maîtresse hors base (`.env`). **Testé** (le numéro n'apparaît pas dans le fichier). | Chiffrement du volume |
| 13 | Données personnelles dans les journaux | Divulgation | Pas de journal d'accès ; journal = méthode + gabarit de route + statut + durée ; **filtre de masquage** (numéros, factures, clés). **Testé.** | — |
| 14 | Données envoyées à l'IA | Divulgation | Uniquement des **statistiques agrégées** ; l'assistante ne reçoit que la question. | — |
| 15 | Injection de consignes dans l'assistante | Élévation | L'assistante n'a **aucun outil ni donnée** ; consignes système défensives ; sortie affichée en texte échappé. Pire cas : une réponse inexacte. | — |
| 16 | Taux de change manipulé (API tierce compromise) | Falsification | Bornes de cohérence (1 M – 1 Md FCFA/BTC) ; repli sur taux fixe ; taux **figé et enregistré** dans chaque vente. | Médiane de plusieurs sources |
| 17 | Requêtes massives (coût IA, création de factures) | Déni de service | Limites par commerçant (30 factures/min, 15 questions/10 min, 20 résumés/h) ; cache des résumés ; corps ≤ 16 Ko. | Limiteur partagé (Redis) |
| 18 | Évasion du conteneur / mouvement latéral | Élévation | Utilisateur non-root sans shell, FS **lecture seule**, `cap_drop: ALL`, `no-new-privileges`, mémoire et PID bornés, port lié à `127.0.0.1` par défaut. | Image signée, digest épinglé |
| 19 | Dépendance compromise | Falsification | Versions **figées** ; bibliothèques reconnues (LNbits `bolt11`, `cryptography`, `argon2-cffi`). | `pip --require-hashes`, Dependabot, SBOM |
| 20 | Démo déployée en production par erreur | Élévation | `APP_ENV=production` **refuse de démarrer** sans `SECRET_KEY` ou avec le portefeuille factice ; la simulation n'existe qu'avec le portefeuille factice ; factures de démo sur `regtest` (impayables). | — |
| 21 | Paiement arrivé après annulation | Intégrité | La facture annulée reste surveillée jusqu'à expiration ; si elle est payée, la vente est **enregistrée** (l'argent est arrivé). **Testé.** | — |
| 23 | Session volée ⇒ retrait vers le numéro de l'attaquant | Élévation | Code secret **redemandé** à chaque retrait (avec verrouillage) ; destination **imposée** = numéro du compte ; plafond quotidien ; 5 demandes/10 min. **Testé.** | Notification SMS à chaque retrait |
| 24 | Lien NWC volé (fuite de base) | Divulgation | Lien **chiffré** (Fernet) ; connexion « recevoir seulement » recommandée et **vérifiée** (alerte si elle peut dépenser). **Testé.** | Budget NWC obligatoire |
| 25 | Faux portefeuille / relais malveillant (faux « payé », facture vers un autre destinataire) | Usurpation | Réponse acceptée seulement si **signée** (Schnorr BIP-340) par la clé du portefeuille et liée à l'`id` de la requête ; facture **décodée et vérifiée** (montant, empreinte). **Testé.** | NIP-44 |
| 26 | SSRF via l'URL de relais fournie par le commerçant | Divulgation | `wss://` uniquement ; résolution DNS et refus des IP privées, de bouclage, locales, réservées. **Testé.** | Proxy de sortie dédié |
| 22 | Téléphone volé déverrouillé | Usurpation | Session limitée à 12 h ; aucune fonction de retrait des fonds dans l'application. | Verrouillage par code à l'ouverture |

## 4. Hypothèses

- L'hôte Docker et le fichier `.env` sont sous le contrôle de l'opérateur.
- En production, un proxy HTTPS termine TLS devant le conteneur.
- LNbits est maintenu à jour par l'opérateur ou le commerçant.

## 5. Revue

À refaire à chaque nouvelle fonctionnalité touchant l'argent (retrait Mobile Money, NWC) ou les données personnelles (SMS).
