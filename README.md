# ⚡ Caisse Teranga

**Encaissez en bitcoin Lightning, simplement.**
Une caisse web légère pour les petits commerçants du Sénégal : le commerçant tape un montant en FCFA, le client scanne un QR code, l'argent arrive **en quelques secondes** — au lieu de plusieurs jours.

> Projet pour le **Hackathon #4 des Dakar Bitcoin Days** (Btrust).

---

## 1. Le problème

Awa tient une boutique à la Médina. Quand un client paie autrement qu'en espèces, elle attend souvent **2 à 3 jours** avant de toucher son argent, et perd une partie en commissions. Elle n'a pas de terminal de paiement, pas d'ordinateur, un téléphone Android d'entrée de gamme et une connexion 3G instable.

**Utilisateur principal :** commerçant·e de quartier (boutique, étal de marché, vendeur ambulant, tailleur), 20 à 80 ventes par jour, montants de 100 à 10 000 FCFA.

## 2. La solution

| Avant | Avec Caisse Teranga |
|---|---|
| Paiement reçu après 2–3 jours | **Reçu en ~3 secondes**, confirmé automatiquement |
| Commissions élevées | Frais Lightning de quelques sats |
| Cahier de ventes à la main | Total du jour, liste des ventes, **résumé en français et en wolof** |
| Il faut un terminal ou un compte bancaire | Un téléphone et un navigateur suffisent |

**Le flux quotidien d'Awa :**
1. Elle tape `2 500` → « Créer la facture ».
2. Le client scanne le QR avec son portefeuille Lightning (Wallet of Satoshi, Phoenix, Blink…).
3. Le téléphone **sonne, vibre et dit « Paiement reçu »** — elle remet la marchandise.
4. Le soir, « Mes ventes » lui donne le total et un résumé en wolof.

### Fonctionnalités du MVP
- Montant saisi **en FCFA**, conversion indicative en sats (taux en direct, **figé dans la vente**).
- Vraie facture **BOLT11** + QR code généré côté serveur (pas de bibliothèque JS à télécharger).
- **Confirmation automatique** : surveillance côté serveur, même si le téléphone perd le réseau.
- Numéro de vente du jour, reçu partageable (WhatsApp / partage natif), **annonce vocale** en français ou en wolof (voir § Voix wolof).
- **Vrais paiements par scan** : le commerçant relie **son propre portefeuille** via **Nostr Wallet Connect** (Alby Hub, Coinos, Primal…). Tout client équipé d'un portefeuille Lightning paie en scannant ; l'argent arrive chez le commerçant, jamais chez l'opérateur.
- **Retrait vers Mobile Money** (Orange Money, Mixx by Yas) : solde disponible (masquable), frais affichés avant validation, **code secret exigé**, argent envoyé **uniquement sur le numéro du compte**, plafond quotidien, suivi « En cours → Reçu ».
- **Client sans bitcoin** : sur la facture, il paie avec Orange Money ou Mixx by Yas ; un partenaire d'échange règle la facture Lightning (simulé en démo).
- **Affiche QR à imprimer** (LNURL-pay, LUD-06/16) : QR fixe + adresse Lightning ; le client scanne, choisit le montant et paie.
- **Preuve de paiement** sur chaque reçu Lightning : la préimage, vérifiée par SHA-256(préimage) = empreinte de la facture.
- **Caisse unique** : ventes en espèces et Mobile Money, note par vente (« 2 pains + sucre »), **export Excel** (CSV protégé contre l'injection de formules).
- **Mode entraînement** : faux bitcoins pour former les commerçants ; exclus du solde et des indicateurs.
- **Écrans d'accueil** à la première ouverture.
- **Historique complet** : toutes les ventes groupées par jour, **recherche** par montant, n° de vente ou date (« 26/10 »), chargement automatique en faisant défiler ; un appui ouvre le reçu.
- Total du jour, **résumé IA en français et en wolof** (avec repli local sans IA).
- **Assistante** intégrée (FR/WO) pour les questions d'usage.
- Interface **bilingue FR / WO**, **mode léger** pour les connexions lentes, installable (PWA).
- **Responsive** : barre d'onglets sur téléphone ; sur ordinateur/tablette, menu latéral, caisse + ventes du jour côte à côte, tableau de bord avec graphiques (heure par heure, 7 jours). Thème clair/sombre automatique.
- Inscription du commerçant en 2 étapes (infos puis code secret à 4 chiffres, saisi deux fois ; codes faibles refusés) et **changement du code** dans Réglages (les autres appareils sont déconnectés).

## 3. Installation (une seule commande)

Prérequis : Docker + Docker Compose v2.

```bash
docker compose up -d
```

Ouvrez **http://localhost:8000** → bouton « Essayer le compte de démo ».

| Compte de démo | |
|---|---|
| Téléphone | `77 123 45 67` |
| Code secret | `4826` |

Sans fichier `.env`, l'application démarre en **mode démo** : portefeuille factice (vraies factures BOLT11 sur le réseau de test `regtest`, donc impossibles à payer par erreur avec de vrais bitcoins), données initiales (16 ventes du jour, journée d'hier) et bouton « Simuler le paiement du client ».

Variante avec génération de la clé secrète :

```bash
sh scripts/install.sh
```

**Mettre en ligne sur Firebase :** voir [docs/DEPLOIEMENT_FIREBASE.md](docs/DEPLOIEMENT_FIREBASE.md) — une commande, `scripts\deploy-firebase.ps1 -ProjectId <id>` (Firebase Hosting + Cloud Run, clé dans Secret Manager).

**Tester sur un téléphone du même Wi-Fi :** ajoutez `BIND_ADDR=0.0.0.0` dans `.env`, relancez, puis ouvrez `http://<IP-de-l-ordinateur>:8000`.

### Scénario nominal à tester (2 minutes)
1. Connexion avec le compte de démo.
2. Taper `2500` → « Créer la facture » → QR + compte à rebours de 10 min.
3. « Simuler le paiement du client (démo) » → écran « Paiement reçu », **vente n° 17**, confirmée en ~2 s.
4. « Voir mes ventes » → total du jour, résumé FR + wolof.
5. Onglet « Aide » → « Le paiement n'arrive pas ».
6. Bouton **WO** → toute l'interface passe en wolof.

### Vrai paiement par scan (recommandé pour la démo) — Nostr Wallet Connect

Aucun serveur Lightning à installer : le commerçant relie son portefeuille.

1. Créez un portefeuille compatible NWC : **Alby Hub**, **Coinos** ou **Primal** (gratuits).
2. Dans ce portefeuille : *Connexions / Apps → Nostr Wallet Connect* → créez une connexion **« recevoir seulement »** (`make_invoice`, `lookup_invoice`). Copiez le lien `nostr+walletconnect://…`.
3. Dans Caisse Teranga : **Réglages → Mon portefeuille → coller le lien → Relier**. La caisse crée une facture test de 1 sat pour vérifier, puis **avertit si la connexion peut aussi dépenser**.
4. Encaissez 100 FCFA : un client scanne avec n'importe quel portefeuille Lightning (Wallet of Satoshi, Phoenix, Blink, Breez…) → « Paiement reçu » en quelques secondes. Le bouton « Simuler » disparaît : c'est un **vrai paiement**.

Le lien NWC est **chiffré en base** ; les réponses du portefeuille sont **vérifiées** (signature Schnorr, lien avec la requête, montant et empreinte de la facture) ; le relais doit être en `wss://` public (anti-SSRF).

### Retrait Mobile Money

Onglet **Retrait** : solde disponible = ventes encaissées − retraits. Choix Orange Money / Mixx by Yas, montant, frais (`PAYOUT_FEE_BPS`, 1 % par défaut), code secret → la demande passe « En cours » puis « Reçu ».
En démo, le partenaire est **simulé** (aucun argent réel). En production, l'étape « envoyer les FCFA » est confiée à un **partenaire d'échange agréé BCEAO** qui reçoit les sats (facture Lightning) et crédite le numéro Mobile Money du commerçant ; l'interface et les contrôles de sécurité ne changent pas.

### Voix wolof

Aucun téléphone ne possède de voix de synthèse en wolof. La caisse joue donc en priorité un **enregistrement** `app/static/audio/wo/paiement-recu.mp3` (à enregistrer par un locuteur natif, ex. « Fey bi agsi na »), puis lit le montant ; sans fichier, la phrase wolof est lue par la voix française du téléphone.

### Vrai paiement Lightning (LNbits)

L'application parle à **LNbits** avec une clé **« Invoice/read »** uniquement (créer des factures, lire leur état — **jamais dépenser**).

**Option A — LNbits local (démo de bout en bout, sans vrais fonds) :**
```bash
docker compose --profile lnbits up -d
```
1. Ouvrez http://localhost:5000, créez le compte administrateur, un portefeuille « Boutique » et un portefeuille « Client » ; créditez le portefeuille « Client » depuis l’interface d’administration (fonds fictifs du FakeWallet).
2. Dans `.env` :
   ```
   LIGHTNING_BACKEND=lnbits
   LNBITS_URL=http://lnbits:5000
   LNBITS_ALLOW_HTTP=true
   LNBITS_INVOICE_KEY=<clé Invoice/read du portefeuille Boutique>
   ```
3. `docker compose --profile lnbits up -d` puis encaissez : payez la facture depuis le portefeuille « Client » de LNbits (« Pay invoice » → collez la facture copiée). La caisse passe à « Paiement reçu » via l'API LNbits.

**Option B — vrai réseau :** un LNbits relié à un nœud (signet/Mutinynet pour les tests, puis mainnet avec de petits montants). Mettez `LNBITS_URL=https://…`. Chaque commerçant peut ensuite **relier son propre portefeuille** dans *Réglages* (sa clé est chiffrée en base) : l'argent va directement chez lui (non-custodial vis-à-vis de l'opérateur).

### Tests
```bash
docker build --target test .        # lance les 51 tests dans le conteneur
# ou en local : pip install -r requirements-dev.txt && pytest -q
```
Les tests couvrent le scénario nominal et la sécurité : CSRF, isolement entre commerçants, verrouillage après 5 essais, non-énumération des comptes, codes faibles, validation des entrées, bornes de montant, en-têtes de sécurité, drapeaux du cookie, numéros et jetons **absents en clair de la base**, masquage des journaux, vérification des factures BOLT11, **protocole NWC complet** contre un relais + portefeuille simulés en local (chiffrement NIP-04, signatures, détection du paiement, secret chiffré, alerte « peut dépenser »), liens NWC malveillants (http, IP privées), historique (recherche, pagination, isolement), changement de code, retrait (mauvais code, dépassement de solde, numéro imposé).

## 4. Architecture

```mermaid
flowchart LR
  subgraph Téléphone du commerçant
    UI["Interface web (PWA)<br/>HTML + CSS + JS sans framework ≈ 22 Ko gzip<br/>FR / WO · mode léger"]
  end
  subgraph Conteneur caisse (non-root, lecture seule)
    API["FastAPI<br/>validation stricte · CSRF · limites"]
    POLL["Surveillant des paiements<br/>(toutes les 4 s)"]
    DB[("SQLite<br/>numéros chiffrés · PIN Argon2id<br/>sessions hachées")]
    QR["QR SVG (segno)"]
  end
  LN["LNbits<br/>clé Invoice/read<br/>(ne peut pas dépenser)"]
  NWC["Portefeuille du commerçant<br/>via Nostr Wallet Connect<br/>(recevoir seulement)"]
  MM["Partenaire Mobile Money<br/>(simulé en démo)"]
  RATE["CoinGecko<br/>taux BTC/XOF"]
  AI["API Claude<br/>stats agrégées uniquement"]
  CLIENT["Portefeuille Lightning<br/>du client"]

  UI -- "HTTPS, cookie HttpOnly" --> API
  API --> DB
  API --> QR
  POLL --> LN
  API -- "créer facture / état" --> LN
  API --> RATE
  API -. "optionnel" .-> AI
  CLIENT -- "scanne le QR, paie" --> LN
  API -- "relais Nostr wss:// (NIP-47, chiffré)" --> NWC
  CLIENT -- "scanne le QR, paie" --> NWC
  API -- "retrait (code secret)" --> MM
```

**Choix techniques**
- **Python / FastAPI + SQLite** : un seul conteneur, rien à administrer, sauvegarde = un fichier.
- **Pas de framework front** : interface complète ≈ 22 Ko compressée, polices système, QR rendu côté serveur, cache hors-ligne de l'interface par *service worker*.
- **Bibliothèques éprouvées** : `bolt11` (celle de LNbits) pour encoder/décoder et **vérifier chaque facture** reçue (montant + empreinte), `argon2-cffi`, `cryptography` (Fernet/HKDF), `segno` pour les QR, SDK officiel `anthropic`.
- **Lightning interchangeable** : `FakeWallet` (démo), `LNbitsWallet` ou `NWCWallet` (Nostr Wallet Connect, par commerçant) derrière la même interface.
- **Nostr** : NIP-47 implémenté avec `coincurve` (libsecp256k1, la bibliothèque de Bitcoin Core) pour les signatures Schnorr/ECDH et `cryptography` pour AES — aucune primitive maison.

## 5. Sécurité dès la conception

Résumé ci-dessous ; détail complet dans **[docs/THREAT_MODEL.md](docs/THREAT_MODEL.md)**.

| Principe | Mise en œuvre |
|---|---|
| **Moindre privilège** | Clé LNbits *Invoice/read* seulement : un vol du serveur ne permet **pas** de dépenser les fonds. Conteneur non-root, système de fichiers en lecture seule, `cap_drop: ALL`, `no-new-privileges`, mémoire/processus bornés. |
| **Secrets** | Aucun secret dans le code ni l'image. `.env` hors Git ; `SECRET_KEY` obligatoire en production ; sous-clés dérivées par HKDF (chiffrement ≠ empreintes). Clés LNbits des commerçants **chiffrées** (Fernet). Clé IA lue par le SDK depuis l'environnement. |
| **Données personnelles** | Numéro de téléphone stocké **chiffré** + recherche par **HMAC** (une fuite de la base ne révèle pas les numéros). Jetons de session stockés **hachés**. Numéro masqué à l'affichage. |
| **Journaux sans PII** | Pas de journal d'accès Uvicorn ; journal maison = méthode + *gabarit* de route + statut + durée (pas d'IP, pas d'ID). Filtre de masquage (numéros, factures, clés) en filet de sécurité. |
| **Authentification** | PIN Argon2id, codes faibles refusés (1234, 0000, années…), **verrouillage progressif** après 5 échecs (15 min → 24 h), limite par IP, réponse identique compte existant/inexistant, durée constante. Cookie `HttpOnly`, `SameSite=Strict`, `Secure` en production. |
| **Entrées validées** | Schémas Pydantic stricts (`extra=forbid`, longueurs), liste blanche de caractères, numéros sénégalais uniquement, bornes de montant, identifiants de facture aléatoires (96 bits), données externes (taux, réponses LNbits) contrôlées. |
| **Web** | CSP stricte (`script-src 'self'`, aucun script ni style en ligne), anti-CSRF (en-tête personnalisé + contrôle d'`Origin`), `X-Frame-Options: DENY`, `no-referrer`, HSTS, corps limité à 16 Ko, échappement systématique côté interface. |
| **Argent sortant** | Retrait : **code secret redemandé**, destination **imposée** (numéro du compte, aucun champ « autre numéro »), plafond quotidien, limite de fréquence, solde vérifié dans une transaction. Une session volée ne peut pas vider la caisse. |
| **NWC** | Connexion « recevoir seulement » recommandée et **vérifiée** (alerte si `pay_invoice` est autorisé) ; lien chiffré en base ; réponses acceptées seulement si signées par le portefeuille et liées à la requête ; relais `wss://` public uniquement (anti-SSRF). |
| **Isolement** | Toute requête filtre par `merchant_id` de la session ; une facture d'un autre commerçant répond 404 (comme une facture inexistante). |
| **IA** | Claude ne reçoit **que des statistiques agrégées** (aucun nom, numéro, facture). L'assistante n'a accès à aucune donnée ni outil. Repli local si l'IA est indisponible ou refuse. |
| **Démo ≠ production** | `APP_ENV=production` refuse de démarrer sans `SECRET_KEY` ou avec le portefeuille factice ; la simulation de paiement n'existe pas hors démo. |

## 6. Contraintes et limites connues

- **Volatilité** : le montant en sats est figé au moment de la vente ; le commerçant porte le risque de change jusqu'à la conversion (→ retrait Mobile Money prévu).
- **Portefeuille du client** : il doit déjà avoir un portefeuille Lightning approvisionné.
- **Custodie** : avec le portefeuille par défaut, l'opérateur (coopérative) détient les fonds ; recommandé : chaque commerçant relie son propre portefeuille.
- **Code à 4 chiffres** : choix d'ergonomie, compensé par Argon2id + verrouillage ; un attaquant peut volontairement bloquer un compte 15 min (déni de service ciblé accepté et documenté).
- **Fuseau** : Dakar est à GMT toute l'année, les journées sont calculées en UTC.
- **Wolof** : traductions en **bêta**, à faire relire par des locuteurs natifs avant le pilote.
- **Limiteur de débit en mémoire** : suffisant pour une instance ; à déplacer dans Redis pour plusieurs instances.

## 7. Indicateurs à suivre

Endpoint protégé `GET /api/metrics` (en-tête `Authorization: Bearer $METRICS_TOKEN`), données **agrégées et anonymes** :

| Indicateur | Pourquoi | Objectif pilote (3 mois) |
|---|---|---|
| `merchants_active_7d` | Adoption réelle | 50 commerçants actifs/semaine |
| `sales_7d`, `volume_xof_7d` | Usage | 1 400 ventes Lightning/semaine |
| `median_confirm_s_7d` | La promesse « payé tout de suite » | < 10 s |
| `expired_rate_7d` | Friction côté client (pas de portefeuille, QR mal scanné) | < 15 % |
| Rétention à 4 semaines (à ajouter) | Valeur durable | > 60 % |

**Estimation de portée :** un animateur terrain peut équiper ~10 commerçants/jour sur un marché (Sandaga, HLM, Tilène). Pilote : 1 marché, 50 commerçants × 40 ventes/jour = 2 000 ventes/jour ; avec 10 % payées en Lightning au départ, ≈ **1 400 ventes/semaine** encaissées instantanément.

## 8. Prochaine itération

- Brancher le **retrait Mobile Money** sur un partenaire d'échange agréé (l'interface et les contrôles existent déjà).
- **Multi-boutiques** et comptes vendeurs (employé sans accès aux réglages).
- **Mode hors ligne complet** (file d'attente, factures pré-générées), **appli native** légère.
- Chiffrement NIP-44 pour NWC (en plus de NIP-04) ; Phoenixd/LND.
- Confirmation du numéro par **SMS**, récupération de compte, **empreinte digitale** (WebAuthn).
- Wolof relu par des natifs, **enregistrements audio wolof** pour tous les montants, pulaar.
- Option « garder une part en FCFA stable » pour limiter la volatilité.

## 9. Configuration

Toutes les variables sont documentées dans [`.env.example`](.env.example). Principales :

| Variable | Défaut | Rôle |
|---|---|---|
| `APP_ENV` | `demo` | `production` active les contrôles stricts |
| `SECRET_KEY` | générée en démo | Clé maîtresse (base64, ≥ 32 octets) |
| `LIGHTNING_BACKEND` | `fake` | `fake` ou `lnbits` |
| `LNBITS_URL` / `LNBITS_INVOICE_KEY` | – | Service Lightning (clé Invoice/read) |
| `RATE_SOURCE` | `coingecko` | ou `static` (`BTC_XOF_STATIC`) |
| `ANTHROPIC_API_KEY` | vide | Active le résumé et l'assistante IA |
| `AI_MODEL` | `claude-opus-5-5` | Modèle Claude |
| `METRICS_TOKEN` | vide | Active `/api/metrics` |

**Production :** derrière un proxy HTTPS (Caddy/Traefik), `APP_ENV=production`, `COOKIE_SECURE=true`, sauvegarde quotidienne du volume `caisse-data`.

## 10. Structure

```
app/
  main.py        API, middleware de sécurité, surveillant des paiements
  security.py    chiffrement, PIN, sessions, verrouillage, masquage des journaux
  lightning.py   FakeWallet / LNbitsWallet + vérification BOLT11
  nwc.py         Nostr Wallet Connect (NIP-47, NIP-04, signatures Schnorr)
  rates.py       taux FCFA ↔ BTC (figé par vente)
  ai.py          résumé + assistante (Claude) avec repli local
  seed.py        données de démo
  static/        interface (index.html, app.js, app.css, sw.js)
tests/           51 tests (scénario nominal, sécurité, NWC, historique, retrait, affiche QR, preuve, espèces, entraînement, export)
docs/            modèle de menaces, script de démo
```

Licence : MIT.
