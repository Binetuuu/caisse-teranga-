# Démo de 3 minutes — script

Format exigé : **problème → solution → impact → prochaines étapes.**
Astuce : enregistrez l'écran du téléphone (ou le navigateur en vue mobile) avec OBS ; voix off en français, une phrase en wolof pour l'ouverture.

## 0:00 – 0:30 · Problème
> « Voici Awa, elle tient une boutique à la Médina. Quand un client la paie autrement qu'en espèces, elle attend **deux à trois jours** son argent, et perd une partie en commissions. Elle n'a ni terminal de paiement, ni ordinateur — juste un téléphone et une 3G qui coupe. »

*(Écran : page de connexion, bouton WO pour montrer le wolof.)*

## 0:30 – 1:45 · Solution (démo en direct)
1. Connexion avec le compte de démo — *« un numéro, un code à 4 chiffres. »*
2. Taper **2 500** — *« elle pense en FCFA ; la caisse affiche l'équivalent en sats, figé pour la vente. »*
3. « Créer la facture » → QR + compte à rebours — *« le client scanne avec n'importe quel portefeuille Lightning. »*
4. **Vrai paiement** : un coéquipier scanne avec Wallet of Satoshi / Phoenix (portefeuille du commerçant relié par **Nostr Wallet Connect**) → **son + vibration + « Fey bi agsi na »**, *« confirmé en 3 secondes, vente n° 17 — et l'argent est sur le portefeuille d'Awa, pas chez nous »*.
5. Onglet **Retrait** → 5 000 FCFA vers Orange Money, code secret → « En cours » puis « Reçu ». *« Awa retrouve ses francs CFA sur son Mobile Money. »*
6. « Mes ventes » → total, graphiques, **résumé en wolof**, puis recherche « 2500 » dans l'historique → le reçu s'ouvre.

## 1:45 – 2:30 · Impact + sécurité
> « Payée en **3 secondes au lieu de 3 jours**. Frais de quelques francs. Un animateur peut équiper **10 commerçants par jour** : sur un seul marché, c'est **50 commerçants et environ 1 400 ventes Lightning par semaine** encaissées instantanément. »

> « Côté sécurité : la caisse ne peut **que recevoir**, jamais dépenser — même si le serveur est volé, l'argent est à l'abri. Les numéros de téléphone sont chiffrés, rien de personnel dans les journaux, et l'IA ne voit que des totaux. Tout est décrit dans notre modèle de menaces. »

*(Écran : README, tableau sécurité ; `docker compose up -d` en une ligne.)*

## 2:30 – 3:00 · Prochaines étapes
> « Prochaine étape : brancher le retrait sur un **partenaire d'échange agréé**, mode hors ligne complet, et un **pilote sur le marché de Sandaga** avec 50 commerçants. Caisse Teranga : la teranga, c'est aussi être payé tout de suite. »

---

## Texte court pour Devpost

**Caisse Teranga** est une caisse Lightning pour les petits commerçants du Sénégal. Le commerçant tape un prix en FCFA, le client scanne un QR, et le paiement est confirmé en quelques secondes — au lieu de plusieurs jours. Interface ultra-légère (≈ 22 Ko) et responsive en français et en wolof, résumé des ventes par IA, assistante intégrée. Sécurité dès la conception : clé LNbits en réception seule (impossible de dépenser), numéros chiffrés, aucune donnée personnelle dans les journaux, conteneur durci, 51 tests automatisés, affiche QR, preuve de paiement, caisse unique (espèces), Nostr Wallet Connect (vrais paiements vers le portefeuille du commerçant), retrait Mobile Money. Installation : `docker compose up -d`.

**Construit avec :** Python, FastAPI, SQLite, LNbits, bolt11, Lightning Network, Claude API, Docker.

## Questions probables du jury

- **« Et la volatilité ? »** — Prix fixé en FCFA, sats figés à la vente ; la prochaine itération convertit automatiquement vers Mobile Money.
- **« Et si le client n'a pas de portefeuille ? »** — Le marché cible commence par les clients déjà équipés (diaspora, jeunes) ; à terme, recharge de portefeuille via Mobile Money.
- **« Custodial ? »** — Par défaut, portefeuille de la coopérative ; chaque commerçant peut relier **son propre portefeuille** (clé chiffrée, réception seule).
- **« Pourquoi pas une appli native ? »** — Rien à installer, fonctionne sur tout téléphone, installable en PWA ; native prévue ensuite.
