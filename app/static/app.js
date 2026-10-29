/* Caisse Teranga — interface responsive sans framework.
   Téléphone : barre d'onglets en bas. Ordinateur : menu latéral + tableau de bord. */
"use strict";

// ================================================================== textes FR / WO
// Le wolof est en bêta : à faire relire par un locuteur natif avant le pilote.
const T = {
  fr: {
    hero_title: "Payé en <em>3 secondes</em>,<br>pas en 3 jours.",
    hero_sub: "La caisse bitcoin Lightning des commerçants du Sénégal. Un téléphone suffit.",
    perk1_t: "Argent reçu tout de suite", perk1_d: "Le client scanne, vous êtes payé en quelques secondes.",
    perk2_t: "Prix en FCFA", perk2_d: "Vous pensez en francs, la caisse calcule les sats.",
    perk3_t: "Sécurisé", perk3_d: "La caisse peut recevoir, jamais dépenser. Vos données sont chiffrées.",
    login_title: "Connexion", login_sub: "Entrez votre numéro et votre code secret.",
    phone: "Numéro de téléphone", pin: "Code secret", forgot: "Code oublié ?", login: "Se connecter",
    no_account: "Pas encore de compte ?", create_account: "Créer un compte",
    demo_title: "Compte de démonstration", demo_hint: "77 123 45 67 · code 4826", demo_fill: "Remplir",
    forgot_info: "Pour votre sécurité, le code n'est jamais envoyé par message. Appelez le support : il vérifiera votre identité avant de le changer.",
    signup_title: "Créer mon compte", step1: "Étape 1 sur 2 · Vos informations", step2: "Étape 2 sur 2 · Sécurité",
    your_name: "Votre nom", shop_name: "Nom de la boutique", area: "Quartier / ville",
    terms: "J'accepte les conditions d'utilisation. Mes données restent privées et ne sont jamais revendues.",
    continue: "Continuer", already: "Déjà un compte ?",
    pin_create: "Créez votre code secret", pin_confirm: "Confirmez votre code",
    pin_help: "4 chiffres que vous seul connaissez. Évitez 1234 ou votre année de naissance.",
    pin_again: "Tapez le même code une deuxième fois.", pin_validate: "Valider mon code",
    pin_mismatch: "Les deux codes sont différents. Recommencez.",
    nav_collect: "Encaisser", nav_sales: "Ventes", nav_help: "Assistante", nav_settings: "Réglages",
    hello: "Bonjour", to_collect: "Montant à encaisser", indicative: "indicatif",
    create_invoice: "Créer la facture", min_amount: "Minimum {min} FCFA", max_amount: "Maximum {max} FCFA",
    rate: "1 BTC ≈ {r} FCFA", today_total: "Encaissé aujourd'hui", sales_count: "Ventes", avg_time: "Délai moyen",
    vs_yesterday: "vs hier", recent: "Dernières ventes", see_all: "Tout voir",
    invoice: "Facture Lightning", waiting: "En attente du paiement", left: "{t} restantes",
    how_title: "Comment le client paie", how1: "Il ouvre son portefeuille Lightning (Wallet of Satoshi, Phoenix, Blink…).",
    how2: "Il scanne ce QR code ou colle la facture copiée.", how3: "L'écran affiche « Paiement reçu » tout seul.",
    give_after: "Ne remettez la marchandise qu'après « Paiement reçu ».",
    copy: "Copier", copied: "Facture copiée.", open_wallet: "Ouvrir", cancel: "Annuler la facture",
    simulate: "Simuler le paiement (démo)", expired: "Facture expirée", cancelled: "Facture annulée",
    expired_help: "Le client n'a pas payé à temps. Créez une nouvelle facture du même montant.",
    retry_same: "Nouvelle facture, même montant", back_pos: "Retour à la caisse",
    paid: "Paiement reçu", auto_confirmed: "Confirmé en {s} s", sale: "Vente", sale_no: "N° de vente",
    in_sats: "Montant en sats", time: "Heure", new_sale: "Nouvelle vente", see_sales: "Mes ventes",
    share: "Partager", receipt_text: "{shop} — Paiement reçu : {xof} FCFA ({sat} sats) — Vente n° {n} — {time}",
    my_sales: "Mes ventes", by_hour: "Aujourd'hui, heure par heure", last7: "7 derniers jours",
    day_summary: "Résumé du jour", french: "Français", wolof: "Wolof (bêta)", ai: "IA", local: "Automatique",
    load_summary: "Afficher le résumé", no_sales: "Pas encore de vente aujourd'hui. La première arrive !",
    all_sales: "Ventes du jour", paid_label: "Payé", total_sats: "Total en sats",
    assistant: "Assistante Teranga", online: "Répond en français et en wolof",
    chat_hello: "Bonjour {name} ! Je peux vous aider à encaisser, comprendre un paiement ou lire vos ventes. Que voulez-vous savoir ?",
    q1: "Comment mon client paie ?", q2: "Le paiement n'arrive pas", q3: "C'est quoi les sats ?", q4: "Parler à un conseiller",
    ask: "Écrivez votre question…", send: "Envoyer",
    settings: "Réglages", prefs: "Préférences", language: "Langue", theme: "Apparence",
    th_auto: "Auto", th_light: "Clair", th_dark: "Sombre",
    lite: "Mode léger", lite_help: "Moins de données et d'animations, pour les connexions lentes.",
    voice: "Annonce vocale", voice_help: "Le téléphone dit « Paiement reçu » à voix haute.",
    wallet: "Portefeuille Lightning", wallet_linked: "Relié : l'argent arrive directement sur votre portefeuille.",
    wallet_default: "Le portefeuille de la coopérative est utilisé.", wallet_key: "Clé « Invoice / read » LNbits",
    wallet_key_help: "Jamais la clé « Admin » : la caisse peut seulement recevoir, jamais dépenser.",
    wallet_save: "Relier mon portefeuille", wallet_unlink: "Délier",
    demo_wallet: "Mode démo : les paiements sont simulés, aucun vrai bitcoin ne circule.",
    security: "Sécurité", sec1: "Votre numéro est chiffré dans la base.", sec2: "La caisse ne peut jamais dépenser votre argent.",
    sec3: "Après 5 codes faux, le compte se bloque.", support: "Support", logout: "Se déconnecter",
    offline: "Pas de connexion. Les ventes déjà payées sont enregistrées.",
    err_network: "Pas de réseau. Vérifiez votre connexion puis réessayez.",
    err_bad_credentials: "Numéro ou code secret incorrect.", err_locked: "Trop d'essais. Réessayez dans {minutes} min.",
    err_too_many: "Trop de demandes. Attendez une minute.", err_phone_invalid: "Numéro invalide. Exemple : 77 123 45 67.",
    err_phone_taken: "Ce numéro a déjà un compte. Connectez-vous.", err_pin_format: "Le code doit avoir 4 chiffres.",
    err_pin_weak: "Code trop facile à deviner. Choisissez-en un autre.", err_terms: "Merci d'accepter les conditions.",
    err_invalid: "Vérifiez les champs en rouge (lettres et chiffres simples).",
    err_amount_range: "Montant entre {min} et {max} FCFA.",
    err_lightning_down: "Le service de paiement ne répond pas. Réessayez dans un instant.",
    err_wallet_key_format: "La clé doit faire 32 caractères (chiffres et lettres a à f).",
    err_wallet_key_rejected: "Cette clé n'est pas acceptée par LNbits.",
    err_auth: "Session expirée. Reconnectez-vous.", err_default: "Une erreur est survenue. Réessayez.",
    back: "Retour",
    create_merchant: "Nouveau commerçant ? Créer mon compte", by_day: "Jour par jour",
    add_note: "Ajouter une note", note_ph: "Ex. : 2 pains + sucre", note: "Note",
    pay_other: "Le client paie en espèces ou Mobile Money", other_title: "Comment le client paie-t-il ?",
    cash: "Espèces", mobile: "Mobile Money", lightning: "Lightning", record_sale: "Enregistrer la vente",
    method: "Moyen de paiement", sale_recorded: "Vente enregistrée",
    proof: "Preuve de paiement", proof_ok: "Vérifiée : ce paiement a bien eu lieu",
    proof_help: "Ce code secret n’est connu que si le client a réellement payé (SHA-256). Il règle tout litige.",
    copy_proof: "Copier la preuve", from_poster: "Payé via l’affiche QR",
    training_bar: "Mode entraînement : faux bitcoins, rien n’est réel.", training_off: "Quitter",
    training: "Mode entraînement", training_help: "Apprendre à encaisser avec de faux bitcoins, sans risque.",
    training_clear: "Effacer les ventes d’entraînement", training_cleared: "{n} vente(s) d’entraînement effacée(s).",
    training_tag: "Entraînement",
    poster: "Mon affiche QR", poster_help: "Un QR fixe à coller sur l’étal : le client scanne, choisit le montant et paie.",
    poster_scan: "Scannez pour payer", poster_free: "Montant libre : vous le tapez dans votre portefeuille Lightning.",
    poster_wallets: "Wallet of Satoshi · Phoenix · Blink · Breez…", print: "Imprimer l’affiche",
    poster_sim: "Simuler un client (démo)", poster_amount: "Montant payé par le client (FCFA)",
    poster_offline: "Pour que de vrais portefeuilles puissent utiliser l’affiche, la caisse doit être en ligne (adresse https).",
    export: "Exporter (Excel)", lnaddr: "Adresse Lightning",
    onramp_q: "Le client n’a pas de bitcoin ?", onramp_help: "Il paie avec son Mobile Money ; un partenaire convertit et la caisse reçoit des sats.",
    onramp_demo: "Démo : partenaire de conversion simulé.", via: "via {op}",
    ob1_t: "Encaissez en bitcoin, simplement", ob1_d: "Tapez le prix en FCFA, le client scanne le QR : payé en 3 secondes.",
    ob2_t: "Toutes vos ventes au même endroit", ob2_d: "Lightning, espèces ou Mobile Money : un seul cahier de ventes, des graphiques et un résumé en wolof.",
    ob3_t: "Votre argent, en sécurité", ob3_d: "La caisse peut recevoir, jamais dépenser. Retirez vers Orange Money ou Mixx by Yas quand vous voulez.",
    ob_skip: "Passer", ob_next: "Suivant", ob_start: "Commencer",
    nav_payout: "Retrait",
    history: "Historique des ventes", search_ph: "Montant, n° de vente ou date (26/10)",
    today_lbl: "Aujourd'hui", yesterday_lbl: "Hier", more: "Voir plus", no_result: "Aucune vente trouvée.",
    sales_day: "{n} ventes · {xof} FCFA", back_history: "Retour à l'historique", view_receipt: "Reçu de vente",
    real_payment: "Paiement Lightning réel", demo_payment: "Démo — reliez votre portefeuille dans Réglages pour encaisser de vrais bitcoins.",
    payout_title: "Retirer vers Mobile Money", available: "Disponible au retrait", daily_left: "Encore {x} FCFA retirables aujourd'hui",
    choose_op: "Vers quel service ?", amount_fcfa: "Montant (FCFA)", all: "Tout",
    fee: "Frais ({p} %)", you_receive: "Vous recevez", to_number: "Sur votre numéro {n}",
    only_own: "Par sécurité, l'argent ne peut aller que sur le numéro du compte.",
    confirm_pin: "Code secret pour confirmer", withdraw: "Retirer {x} FCFA", payouts_hist: "Mes retraits",
    no_payouts: "Aucun retrait pour l'instant.", st_pending: "En cours", st_completed: "Reçu", st_failed: "Échec",
    payout_ok: "Demande envoyée. Vous recevrez un message de {op}.",
    payout_demo: "Démo : le transfert est simulé, aucun argent réel n'est envoyé.",
    hide_bal: "Masquer le solde", show_bal: "Afficher le solde",
    nwc_title: "Mon portefeuille (Nostr Wallet Connect)",
    nwc_on: "Relié : vos clients paient directement sur VOTRE portefeuille. Les vrais scans fonctionnent.",
    nwc_off: "Reliez votre portefeuille Lightning pour que vos clients puissent vraiment payer en scannant.",
    nwc_step1: "Ouvrez Alby Hub, Coinos ou Primal → Connexions → Nostr Wallet Connect.",
    nwc_step2: "Créez une connexion « Recevoir seulement » (créer et consulter des factures).",
    nwc_step3: "Copiez le lien nostr+walletconnect://… et collez-le ici.",
    nwc_link: "Relier mon portefeuille", nwc_unlink: "Délier", nwc_ok: "Portefeuille relié et testé.",
    nwc_spend_warn: "Attention : cette connexion peut aussi DÉPENSER votre argent. Créez plutôt une connexion « Recevoir seulement ».",
    nwc_testing: "Test de la connexion…",
    pin_section: "Code secret", pin_current: "Code actuel", pin_new: "Nouveau code", pin_new2: "Confirmer le nouveau code",
    pin_change: "Changer mon code", pin_changed: "Code modifié. Vos autres appareils ont été déconnectés.",
    err_bad_pin: "Code secret incorrect.", err_payout_range: "Montant entre {min} et {max} FCFA.",
    err_nwc_format: "Lien invalide. Il doit commencer par nostr+walletconnect://",
    err_nwc_relay: "Relais non autorisé (wss:// public uniquement).",
    err_nwc_unreachable: "Le portefeuille ne répond pas. Vérifiez le lien et réessayez.",
  },
  wo: {
    hero_title: "Fey ci <em>3 saa</em>,<br>du 3 fan.",
    hero_sub: "Caisse bitcoin Lightning bu jaaykat yi ci Senegaal. Benn telefon doy na.",
    perk1_t: "Xaalis bi agsi na ci saa si", perk1_d: "Kiliyaan bi scanner, nga jot sa xaalis.",
    perk2_t: "Njëg ci FCFA", perk2_d: "Yaa xalaat ci dërëm, caisse bi xayma sats yi.",
    perk3_t: "Kaarange", perk3_d: "Caisse bi mën na jot rekk, du mën a génne.",
    login_title: "Duggu", login_sub: "Bindal sa nimero ak sa code secret.",
    phone: "Nimero telefon", pin: "Code secret", forgot: "Fàtte nga code bi ?", login: "Duggu",
    no_account: "Amaguloo compte ?", create_account: "Ubbi compte",
    demo_title: "Compte démo", demo_hint: "77 123 45 67 · code 4826", demo_fill: "Fees ko",
    forgot_info: "Ngir sa kaarange, code bi du ñu ko yónne ci message. Woowal support bi.",
    signup_title: "Ubbi sama compte", step1: "Tappaan 1 ci 2 · Say xibaar", step2: "Tappaan 2 ci 2 · Kaarange",
    your_name: "Sa tur", shop_name: "Turu bitik bi", area: "Gox / dëkk",
    terms: "Nangu naa sàrti jëfandikoo. Sama xibaar yi dañuy des ci man.",
    continue: "Kontine", already: "Am nga compte ?",
    pin_create: "Sos sa code secret", pin_confirm: "Dëggalal sa code",
    pin_help: "4 siffar yoo xam yow rekk. Bul jël 1234 walla sa atum juddu.",
    pin_again: "Bindaatal code bi.", pin_validate: "Dëggal sama code", pin_mismatch: "Ñaari code yi wuute nañu. Tambaliwaat.",
    nav_collect: "Jot", nav_sales: "Jaay", nav_help: "Ndimbal", nav_settings: "Réglages",
    hello: "Asalaa maalekum", to_collect: "Xaalis bi ngay jot", indicative: "lu jege",
    create_invoice: "Sos facture bi", min_amount: "Lu gëna tuuti : {min} FCFA", max_amount: "Lu gëna bari : {max} FCFA",
    rate: "1 BTC ≈ {r} FCFA", today_total: "Li nga jot tey", sales_count: "Jaay", avg_time: "Diir",
    vs_yesterday: "ak démb", recent: "Jaay yu mujj", see_all: "Seet yépp",
    invoice: "Facture Lightning", waiting: "Nu ngi xaar fey bi", left: "{t} des na",
    how_title: "Naka la kiliyaan bi di fey", how1: "Mu ubbi portefeuille Lightning bi (Wallet of Satoshi, Phoenix, Blink…).",
    how2: "Mu scanner QR code bii.", how3: "Ekraan bi dina wone « Paiement reçu ».",
    give_after: "Bul jox njaay ji balaa « Paiement reçu ».",
    copy: "Kopi", copied: "Facture bi kopi nañu ko.", open_wallet: "Ubbi", cancel: "Neenal facture bi",
    simulate: "Def ni dañu fey (démo)", expired: "Facture bi jeex na", cancelled: "Facture bi neenal nañu ko",
    expired_help: "Kiliyaan bi feyul ci waxtu. Sosal beneen facture.",
    retry_same: "Beneen facture, njëg gi rekk", back_pos: "Dellu ci caisse bi",
    paid: "Fey bi agsi na", auto_confirmed: "Dëggal nañu ko ci {s} s", sale: "Jaay", sale_no: "Nimero jaay",
    in_sats: "Ci sats", time: "Waxtu", new_sale: "Beneen jaay", see_sales: "Sama jaay yi",
    share: "Yónnee", receipt_text: "{shop} — Fey bi agsi na : {xof} FCFA ({sat} sats) — Jaay n° {n} — {time}",
    my_sales: "Sama jaay yi", by_hour: "Tey, waxtu ak waxtu", last7: "7 fan yu mujj",
    day_summary: "Tënk bu tey", french: "Français", wolof: "Wolof (bêta)", ai: "IA", local: "Auto",
    load_summary: "Wone tënk bi", no_sales: "Jaayoo dara tey.", all_sales: "Jaay yu tey",
    paid_label: "Fey na", total_sats: "Yépp ci sats",
    assistant: "Assistante Teranga", online: "Day tontu ci français ak wolof",
    chat_hello: "Asalaa maalekum {name} ! Maa ngi fi ngir dimbali la ci caisse bi. Lan nga bëgg xam ?",
    q1: "Naka la sama kiliyaan di fey ?", q2: "Fey bi agsiwul", q3: "Lan mooy sats ?", q4: "Wax ak ab conseiller",
    ask: "Bindal sa laaj…", send: "Yónnee",
    settings: "Réglages", prefs: "Li ma bëgg", language: "Làkk", theme: "Melo",
    th_auto: "Auto", th_light: "Leer", th_dark: "Lëndëm",
    lite: "Mode léger", lite_help: "Data bu néew, ngir réseau bu yéex.",
    voice: "Baat", voice_help: "Telefon bi dina wax « Paiement reçu ».",
    wallet: "Portefeuille Lightning", wallet_linked: "Lëkkaloo na : xaalis bi ci sa portefeuille lay dem.",
    wallet_default: "Portefeuille coopérative bi lañuy jëfandikoo.", wallet_key: "Clé « Invoice / read » LNbits",
    wallet_key_help: "Du clé « Admin » : caisse bi mën na jot rekk.", wallet_save: "Lëkkale sama portefeuille", wallet_unlink: "Tënqi",
    demo_wallet: "Démo : fey yi du dëgg, amul bitcoin bu dëgg.",
    security: "Kaarange", sec1: "Sa nimero dañu ko nëbb.", sec2: "Caisse bi du mën a génne sa xaalis.",
    sec3: "Su code bi juumee 5 yoon, compte bi dina tëj.", support: "Support", logout: "Génn",
    offline: "Amul réseau. Jaay yi feyoon nañu ko, des nañu.",
    err_network: "Amul réseau. Seetal sa connexion te jéemaat.", err_bad_credentials: "Nimero bi walla code bi baaxul.",
    err_locked: "Jéem nga lu bari. Jéemaatal ci {minutes} simili.", err_too_many: "Laaj yi bari nañu. Xaaral benn simili.",
    err_phone_invalid: "Nimero bi baaxul. Misaal : 77 123 45 67.", err_phone_taken: "Nimero bii am na compte ba noppi.",
    err_pin_format: "Code bi war na am 4 siffar.", err_pin_weak: "Code bi dafa yomb a xam. Tànnal beneen.",
    err_terms: "Nangul sàrt yi.", err_invalid: "Seetal li ñu bind ci xonq.",
    err_amount_range: "Njëg gi war na nekk diggante {min} ak {max} FCFA.",
    err_lightning_down: "Service fey bi tontuwul. Jéemaatal.", err_wallet_key_format: "Clé bi war na am 32 araf.",
    err_wallet_key_rejected: "LNbits nanguwul clé bii.", err_auth: "Sa session jeex na. Duggaatal.",
    err_default: "Am na lu baaxul. Jéemaatal.", back: "Dellu",
    create_merchant: "Jaaykat bu bees ? Ubbi sama compte", by_day: "Bés ak bés",
    cash: "Xaalis loxo", training: "Mode entraînement", ob_skip: "Bàyyi", ob_next: "Ci kanam", ob_start: "Tàmbali", poster: "Sama affiche QR", poster_scan: "Scanner ngir fey",
    training_bar: "Mode entraînement : bitcoin yu dul dëgg.", print: "Imprimer affiche bi", nav_payout: "Génne",
    history: "Jaay yu weesu", search_ph: "Njëg, nimero jaay walla bés (26/10)",
    today_lbl: "Tey", yesterday_lbl: "Démb", more: "Wone yeneen", no_result: "Gisuñu benn jaay.",
    sales_day: "{n} jaay · {xof} FCFA", back_history: "Dellu ci jaay yi", view_receipt: "Reçu jaay",
    real_payment: "Fey Lightning bu dëgg", demo_payment: "Démo — lëkkale sa portefeuille ci Réglages ngir jot bitcoin bu dëgg.",
    payout_title: "Génne ci Mobile Money", available: "Li nga mën a génne", daily_left: "Mën nga génne {x} FCFA tey",
    choose_op: "Fan lay dem ?", amount_fcfa: "Njëg (FCFA)", all: "Yépp",
    fee: "Frais ({p} %)", you_receive: "Dinga jot", to_number: "Ci sa nimero {n}",
    only_own: "Ngir kaarange, xaalis bi mën na dem ci nimero compte bi rekk.",
    confirm_pin: "Code secret ngir dëggal", withdraw: "Génne {x} FCFA", payouts_hist: "Sama génne yi",
    no_payouts: "Génneegoo dara.", st_pending: "Mi ngi dem", st_completed: "Agsi na", st_failed: "Antuwul",
    payout_ok: "Yónnee nañu ko. {op} dina la yónnee message.",
    payout_demo: "Démo : du xaalis bu dëgg.",
    hide_bal: "Nëbb", show_bal: "Wone",
    nwc_title: "Sama portefeuille (Nostr Wallet Connect)",
    nwc_on: "Lëkkaloo na : say kiliyaan ci SA portefeuille lañuy fey.",
    nwc_off: "Lëkkale sa portefeuille Lightning ngir say kiliyaan mën a fey ci dëgg.",
    nwc_step1: "Ubbil Alby Hub, Coinos walla Primal → Connexions → Nostr Wallet Connect.",
    nwc_step2: "Sosal connexion « Recevoir seulement ».",
    nwc_step3: "Kopil lien nostr+walletconnect://… te taxawal ko fii.",
    nwc_link: "Lëkkale sama portefeuille", nwc_unlink: "Tënqi", nwc_ok: "Lëkkaloo na.",
    nwc_spend_warn: "Moytul : connexion bii mën na génne sa xaalis. Sosal connexion « Recevoir seulement ».",
    nwc_testing: "Nu ngi seet…",
    pin_section: "Code secret", pin_current: "Code bi nga am", pin_new: "Code bu bees", pin_new2: "Dëggal code bu bees bi",
    pin_change: "Soppi sama code", pin_changed: "Soppi nañu code bi.",
    err_bad_pin: "Code secret bi baaxul.", err_payout_range: "Njëg gi war na nekk diggante {min} ak {max} FCFA.",
    err_nwc_format: "Lien bi baaxul.", err_nwc_relay: "Relais bii nanguñu ko.",
    err_nwc_unreachable: "Portefeuille bi tontuwul.",
  },
};

// ================================================================== outils
const app = document.getElementById("app");
const store = {
  get(k, d) { try { const v = localStorage.getItem("ct_" + k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem("ct_" + k, JSON.stringify(v)); } catch { /* stockage indisponible */ } },
};
const state = {
  me: null, pub: null, signup: null, chat: [], amount: "", rate: null, timers: [],
  lang: store.get("lang", "fr"), lite: store.get("lite", false), voice: store.get("voice", true), theme: store.get("theme", "auto"),
};
const desktop = () => matchMedia("(min-width: 960px)").matches;
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (n) => Number(n || 0).toLocaleString("fr-FR").replace(/[  ]/g, " ");
const $ = (sel) => app.querySelector(sel);
const on = (sel, ev, fn) => app.querySelectorAll(sel).forEach((el) => el.addEventListener(ev, fn));
function t(key, vars = {}) {
  const s = T[state.lang]?.[key] ?? T.fr[key] ?? key;
  return s.replace(/\{(\w+)\}/g, (_, k) => (k in vars ? vars[k] : ""));
}
function errText(d) {
  const code = d?.error || "default";
  return T.fr["err_" + code] ? t("err_" + code, { minutes: d?.minutes, min: fmt(d?.min), max: fmt(d?.max) }) : t("err_default");
}
function showMsg(msg, el = $("[role=alert]"), info = false) {
  if (!el) return;
  el.className = info ? "alert info" : "alert";
  el.textContent = msg || "";
}
const todayLabel = () => new Date().toLocaleDateString(state.lang === "wo" ? "fr-SN" : "fr-FR", { weekday: "long", day: "numeric", month: "long" });

const P = {
  pos: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><path d="M14 14h3v3M21 14v.01M14 21h7v-4"/>',
  chart: '<path d="M3 3v18h18"/><path d="M7 15v2M11 11v6M15 7v10M19 12v5"/>',
  chat: '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>',
  gear: '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/>',
  check: '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
  back: '<path d="m15 18-6-6 6-6"/>',
  copy: '<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1"/>',
  open: '<path d="M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
  send: '<path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/>',
  logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  spark: '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 17v4M17 19h4"/>',
  shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
  coins: '<circle cx="8" cy="8" r="6"/><path d="M18.1 10.4A6 6 0 1 1 10.3 18"/><path d="M7 6h1v4"/>',
  share: '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  del: '<path d="M21 4H8l-7 8 7 8h13a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2z"/><path d="m18 9-6 6M12 9l6 6"/>',
  wallet: '<path d="M19 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0 0 4h14a2 2 0 0 1 2 2v3h-4a2 2 0 0 0 0 4h4v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5"/>',
  phone: '<rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M11 18h2"/>',
  cash: '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/><path d="M6 12h.01M18 12h.01"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
  eye: '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
  chevron: '<path d="m9 18 6-6-6-6"/>',
  receipt: '<path d="M5 2v20l3-2 2 2 2-2 2 2 2-2 3 2V2l-3 2-2-2-2 2-2-2-2 2z"/><path d="M9 9h6M9 13h6"/>',
};
const ic = (n) => `<svg class="i" viewBox="0 0 24 24" aria-hidden="true">${P[n]}</svg>`;
const BOLT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>';

// ================================================================== réseau
async function api(method, path, body) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 15000);
  try {
    const res = await fetch(path, {
      method, signal: ctrl.signal, credentials: "same-origin",
      headers: { "Content-Type": "application/json", "X-Requested-With": "caisse" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (res.status === 401 && state.me && !path.startsWith("/api/auth/")) { state.me = null; go("/login"); }
    return { ok: res.ok, status: res.status, data };
  } catch {
    return { ok: false, status: 0, data: { error: "network" } };
  } finally {
    clearTimeout(timer);
  }
}

// ================================================================== rendu et minuteries
function go(path) { if (location.hash !== "#" + path) location.hash = path; else route(); }
function clearTimers() { state.timers.forEach((id) => { clearTimeout(id); clearInterval(id); }); state.timers = []; }
const later = (fn, ms) => state.timers.push(setTimeout(fn, ms));
const every = (fn, ms) => state.timers.push(setInterval(fn, ms));
function render(html) {
  clearTimers(); padKey = null;
  app.innerHTML = html;
  const h = $("h1, h2"); if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
  window.scrollTo(0, 0);
}

function langToggle() {
  return `<div class="langs" role="group" aria-label="Langue">${["fr", "wo"].map((l) =>
    `<button type="button" data-lang="${l}" aria-pressed="${state.lang === l}">${l.toUpperCase()}</button>`).join("")}</div>`;
}
function bindCommon() {
  on("[data-lang]", "click", (e) => {
    state.lang = e.currentTarget.dataset.lang; store.set("lang", state.lang);
    document.documentElement.lang = state.lang === "wo" ? "wo" : "fr";
    if (state.me) api("PATCH", "/api/me", { lang: state.lang });
    route();
  });
  on("[data-go]", "click", (e) => go(e.currentTarget.dataset.go));
  on("[data-logout]", "click", logout);
  on("[data-training-off]", "click", async () => { await api("PATCH", "/api/me", { training: false }); await loadMe(); route(); });
}

// ---------------------------------------------------------------- mise en page « connexion »
function authLayout(inner) {
  const perk = (icon, k) => `<li><span class="ic">${ic(icon)}</span><div><b>${t(k + "_t")}</b><span>${t(k + "_d")}</span></div></li>`;
  return `<div class="auth">
    <section class="auth-hero">
      <div class="row between"><div class="brand"><span class="logo">${BOLT}</span>Caisse Teranga</div>${langToggle()}</div>
      <h1>${t("hero_title")}</h1><p>${t("hero_sub")}</p>
      <ul class="perks">${perk("clock", "perk1")}${perk("coins", "perk2")}${perk("shield", "perk3")}</ul>
    </section>
    <main class="auth-main"><div class="auth-card">${inner}</div></main>
  </div>`;
}

// ---------------------------------------------------------------- mise en page « application »
const NAV = [["caisse", "pos", "nav_collect"], ["ventes", "chart", "nav_sales"], ["retrait", "cash", "nav_payout"], ["aide", "chat", "nav_help"], ["reglages", "gear", "nav_settings"]];
function appLayout(active, inner) {
  const me = state.me;
  const initial = esc(me.shop_name.trim()[0]?.toUpperCase() || "T");
  const links = NAV.map(([href, icon, label]) =>
    `<a href="#/${href}" ${active === href ? 'aria-current="page"' : ""}>${ic(icon)}<span>${t(label)}</span></a>`).join("");
  return `<div class="shell">
    <aside class="sidebar">
      <div class="brand"><span class="logo">${BOLT}</span>Caisse Teranga</div>
      <nav aria-label="Menu">${links}</nav>
      ${langToggle()}
      <div class="shop"><span class="avatar">${initial}</span><div class="grow"><b>${esc(me.shop_name)}</b><span>${esc(me.name)}</span></div>
        <button class="icon-btn" data-logout aria-label="${t("logout")}" title="${t("logout")}">${ic("logout")}</button></div>
    </aside>
    <div>
      <header class="topbar-m"><span class="avatar">${initial}</span>
        <div class="title"><span class="muted small">${t("hello")}, ${esc(me.name.split(" ")[0])}</span><b>${esc(me.shop_name)}</b></div>
        ${langToggle()}</header>
      ${me.training ? `<div class="training-bar no-print">${ic("spark")}<span>${t("training_bar")}</span><button class="link" data-training-off>${t("training_off")}</button></div>` : ""}
      <main class="content">${inner}</main>
    </div>
    <nav class="tabbar" aria-label="Menu">${links}</nav>
  </div>`;
}

// ---------------------------------------------------------------- pavé numérique
let padKey = null;
function padHTML() {
  return `<div class="pad">${[1, 2, 3, 4, 5, 6, 7, 8, 9].map((d) => `<button type="button" data-k="${d}">${d}</button>`).join("")}
    <button type="button" class="fn" data-k="C" aria-label="Tout effacer">C</button><button type="button" data-k="0">0</button>
    <button type="button" class="fn" data-k="<" aria-label="Effacer un chiffre">${ic("del")}</button></div>`;
}
function bindPad(onKey) {
  padKey = onKey;
  on(".pad [data-k]", "click", (e) => { navigator.vibrate?.(8); onKey(e.currentTarget.dataset.k); });
}
document.addEventListener("keydown", (e) => {
  if (!padKey || !$(".pad") || e.target.matches("input, textarea")) return;
  if (/^\d$/.test(e.key)) padKey(e.key);
  else if (e.key === "Backspace") padKey("<");
  else if (e.key === "Escape") padKey("C");
  else if (e.key === "Enter") $("#create:not(:disabled)")?.click();
});

// ================================================================== écrans d'accueil (première visite)
function screenOnboarding() {
  const slides = [["pos", "ob1"], ["chart", "ob2"], ["shield", "ob3"]];
  let i = 0;
  const done = () => { store.set("onboarded", true); go("/login"); };
  const draw = () => {
    const [icon, k] = slides[i];
    render(`<div class="onboard">
      <div class="row between"><div class="brand"><span class="logo">${BOLT}</span>Caisse Teranga</div>
        <button class="link" id="skip">${t("ob_skip")}</button></div>
      <div class="onboard-body"><div class="onboard-ic">${ic(icon)}</div>
        <h1>${t(k + "_t")}</h1><p class="muted">${t(k + "_d")}</p></div>
      <div class="row between"><div class="dots-ob">${slides.map((_, j) => `<span class="${j === i ? "on" : ""}"></span>`).join("")}</div>
        <button class="btn" id="next">${i === slides.length - 1 ? t("ob_start") : t("ob_next")}</button></div>
    </div>`);
    on("#skip", "click", done);
    on("#next", "click", () => { if (i < slides.length - 1) { i++; draw(); } else done(); });
  };
  draw();
}

// ================================================================== connexion / inscription
function screenLogin() {
  const demo = state.pub?.demo;
  render(authLayout(`
    <div><h2>${t("login_title")}</h2><p class="muted">${t("login_sub")}</p></div>
    ${demo ? `<div class="demo-box"><span class="avatar">${ic("spark")}</span><div class="grow"><b>${t("demo_title")}</b><div class="muted small">${t("demo_hint")}</div></div>
      <button type="button" class="btn sm ghost" id="demo">${t("demo_fill")}</button></div>` : ""}
    <form id="f" class="stack" novalidate>
      <label class="field">${t("phone")}
        <span class="input-group"><span class="addon">+221</span>
        <input class="input" id="phone" inputmode="tel" autocomplete="tel-national" placeholder="77 123 45 67" maxlength="14" required></span></label>
      <label class="field"><span class="row between">${t("pin")}<button type="button" class="link small" id="forgot">${t("forgot")}</button></span>
        <input class="input" id="pin" type="password" inputmode="numeric" pattern="[0-9]*" maxlength="4" autocomplete="current-password" placeholder="••••" required></label>
      <p class="alert" role="alert"></p>
      <button class="btn lg block" id="go">${t("login")}</button>
    </form>
    <div class="or"><span>ou</span></div>
    <a class="btn ghost lg block" href="#/inscription">${ic("plus")}${t("create_merchant")}</a>`));
  bindCommon();
  on("#forgot", "click", () => showMsg(t("forgot_info") + (state.pub?.support_phone ? " " + state.pub.support_phone : ""), undefined, true));
  on("#demo", "click", () => { $("#phone").value = "77 123 45 67"; $("#pin").value = "4826"; $("#go").focus(); });
  on("#f", "submit", async (e) => {
    e.preventDefault();
    const btn = $("#go"); btn.disabled = true;
    const r = await api("POST", "/api/auth/login", { phone: $("#phone").value, pin: $("#pin").value });
    btn.disabled = false;
    if (!r.ok) { showMsg(r.status === 422 ? t("err_bad_credentials") : errText(r.data)); $("#pin").value = ""; return; }
    await loadMe(); go("/caisse");
  });
}

function screenSignup() {
  const s = state.signup || {};
  render(authLayout(`
    <div><h2>${t("signup_title")}</h2><p class="muted small">${t("step1")}</p></div>
    <div class="steps" aria-hidden="true"><span class="on"></span><span></span></div>
    <form id="f" class="stack" novalidate>
      <label class="field">${t("your_name")}<input class="input" name="name" autocomplete="name" maxlength="60" value="${esc(s.name)}" placeholder="Awa Diop"></label>
      <label class="field">${t("shop_name")}<input class="input" name="shop_name" autocomplete="organization" maxlength="60" value="${esc(s.shop_name)}" placeholder="Boutique Awa"></label>
      <label class="field">${t("area")}<input class="input" name="area" autocomplete="address-level2" maxlength="60" value="${esc(s.area)}" placeholder="Médina, Dakar"></label>
      <label class="field">${t("phone")}<span class="input-group"><span class="addon">+221</span>
        <input class="input" name="phone" inputmode="tel" autocomplete="tel-national" maxlength="14" value="${esc(s.phone)}" placeholder="77 123 45 67"></span></label>
      <label class="check"><input type="checkbox" name="accept_terms" ${s.accept_terms ? "checked" : ""}><span>${t("terms")}</span></label>
      <p class="alert" role="alert">${esc(s._err)}</p>
      <button class="btn lg block">${t("continue")}</button>
    </form>
    <p class="center muted">${t("already")} <a href="#/login">${t("login")}</a></p>`));
  bindCommon();
  on("#f", "submit", (e) => {
    e.preventDefault();
    const f = e.currentTarget;
    const data = { name: f.name.value.trim(), shop_name: f.shop_name.value.trim(), area: f.area.value.trim(), phone: f.phone.value.trim(), accept_terms: f.accept_terms.checked };
    let bad = false;
    for (const k of ["name", "shop_name", "area"]) { const ok = data[k].length >= 2; f[k].setAttribute("aria-invalid", String(!ok)); bad ||= !ok; }
    const digits = data.phone.replace(/\D/g, "").replace(/^221/, "");
    const phoneOk = /^(7[05678]|3[03])\d{7}$/.test(digits);
    f.phone.closest(".input-group").querySelector("input").setAttribute("aria-invalid", String(!phoneOk));
    if (bad) return showMsg(t("err_invalid"));
    if (!phoneOk) return showMsg(t("err_phone_invalid"));
    if (!data.accept_terms) return showMsg(t("err_terms"));
    state.signup = data; go("/code");
  });
}

function screenPin() {
  if (!state.signup) return go("/inscription");
  let first = null, code = "";
  const draw = (msg = "") => {
    render(authLayout(`
      <div class="row"><button class="icon-btn" data-go="/inscription" aria-label="${t("back")}">${ic("back")}</button>
        <div><h2>${first ? t("pin_confirm") : t("pin_create")}</h2><p class="muted small">${t("step2")}</p></div></div>
      <div class="steps" aria-hidden="true"><span class="on"></span><span class="on"></span></div>
      <p class="muted">${first ? t("pin_again") : t("pin_help")}</p>
      <div class="pin-dots" aria-label="${code.length} / 4">${[0, 1, 2, 3].map((i) => `<span class="${i < code.length ? "on" : ""}"></span>`).join("")}</div>
      <p class="alert" role="alert">${esc(msg)}</p>
      <div class="card terminal">${padHTML()}</div>
      <button class="btn lg block" id="ok" ${code.length === 4 ? "" : "disabled"}>${t("pin_validate")}</button>`));
    bindCommon();
    bindPad((k) => {
      if (k === "C") code = ""; else if (k === "<") code = code.slice(0, -1); else if (code.length < 4) code += k;
      draw();
    });
    on("#ok", "click", submit);
  };
  const submit = async () => {
    if (!first) {
      if (/^(\d)\1{3}$/.test(code) || "0123456789".includes(code) || "9876543210".includes(code)) { code = ""; return draw(t("err_pin_weak")); }
      first = code; code = ""; return draw();
    }
    if (code !== first) { first = null; code = ""; return draw(t("pin_mismatch")); }
    $("#ok").disabled = true;
    const r = await api("POST", "/api/auth/signup", { ...state.signup, pin: code });
    if (!r.ok) {
      if (["pin_weak", "pin_format"].includes(r.data.error)) { first = null; code = ""; return draw(errText(r.data)); }
      state.signup = { ...state.signup, _err: errText(r.data) };
      return go("/inscription");
    }
    state.signup = null;
    await loadMe(); go("/caisse");
  };
  draw();
}

// ================================================================== caisse
async function getRate() {
  if (state.rate && Date.now() - state.rate.at < 300000) return state.rate.v;
  const r = await api("GET", "/api/rate");
  if (r.ok) state.rate = { at: Date.now(), v: r.data.xof_per_btc };
  return state.rate?.v;
}

function salesList(sales, limit) {
  if (!sales.length) return `<p class="empty">${t("no_sales")}</p>`;
  return `<ul class="sales">${sales.slice(0, limit).map(saleItem).join("")}</ul>`;
}

function saleItem(s) {
  const m = s.method || "lightning";
  const sub = m === "lightning" ? `${fmt(s.amount_sat)} sats` : t(m);
  const extra = [s.note ? esc(s.note) : "", s.training ? t("training_tag") : "", s.source === "affiche" ? "QR" : ""].filter(Boolean).join(" · ");
  return `<li><a class="sale-link" href="#/vente/${encodeURIComponent(s.id)}"><span class="ic ${m !== "lightning" ? "ic-cash" : ""}">${ic(m === "lightning" ? "check" : "cash")}</span>
    <div class="meta"><b>${t("sale")} ${s.sale_no}</b><span>${esc(s.time)} · ${t("paid_label")}${extra ? " · " + extra : ""}</span></div>
    <div class="amt num">${fmt(s.amount_xof)} F<small>${sub}</small></div>${ic("chevron")}</a></li>`;
}

function deltaHTML(today, yesterday) {
  if (!yesterday) return "";
  const pct = Math.round(((today - yesterday) / yesterday) * 100);
  return `<div class="d ${pct >= 0 ? "up" : "down"}">${pct >= 0 ? "▲" : "▼"} ${Math.abs(pct)} % ${t("vs_yesterday")}</div>`;
}

function screenCaisse() {
  const cfg = state.me.config;
  render(appLayout("caisse", `
    <div class="page-head hide-mobile"><div><h1>${t("nav_collect")}</h1><p class="muted">${esc(todayLabel())}</p></div>
      <div class="row wrap"><span class="pill neutral" id="rate"></span><a class="btn ghost sm" href="#/affiche">${ic("pos")}${t("poster")}</a></div></div>
    <div class="pos">
      <section class="card terminal" aria-label="${t("to_collect")}">
        <div class="screen-amount"><div class="lbl">${t("to_collect")}</div>
          <div class="amt num" id="amt" aria-live="polite"></div><span class="conv" id="conv"></span></div>
        <div class="quick-amounts">${[500, 1000, 2000, 5000, 10000].map((v) => `<button type="button" data-q="${v}">${fmt(v)}</button>`).join("")}</div>
        ${padHTML()}
        <div class="actions stack">
          <details class="note-box"${state.note ? " open" : ""}><summary>${ic("plus")}${t("add_note")}</summary>
            <input class="input" id="note" maxlength="60" placeholder="${t("note_ph")}" value="${esc(state.note || "")}" autocomplete="off"></details>
          <p class="alert" role="alert"></p>
          <button class="btn lg block" id="create">${BOLT.replace("<svg", '<svg class="i" fill="currentColor"')}${t("create_invoice")}</button>
          <button class="link center" id="other">${t("pay_other")}</button>
          <div class="other-pay" id="otherbox" hidden>
            <p class="small muted">${t("other_title")}</p>
            <div class="btn-row"><button class="btn ghost" data-method="cash">${ic("cash")}${t("cash")}</button>
              <button class="btn ghost" data-method="mobile">${ic("phone")}${t("mobile")}</button></div>
          </div>
          <a class="btn ghost block hide-desktop" href="#/affiche">${ic("pos")}${t("poster")}</a></div>
      </section>
      <aside class="side" id="side"></aside>
    </div>
    <section class="card hide-desktop mt" id="recentm" hidden></section>`));
  bindCommon();

  const update = async () => {
    const n = Number(state.amount || 0);
    $("#amt").innerHTML = `${fmt(n)}<small>FCFA</small>`;
    const rate = await getRate();
    if (!$("#conv")) return;
    const warn = n && n < cfg.min_xof ? t("min_amount", { min: fmt(cfg.min_xof) }) : n > cfg.max_xof ? t("max_amount", { max: fmt(cfg.max_xof) }) : "";
    const conv = $("#conv");
    conv.className = warn ? "conv warn" : "conv";
    conv.textContent = warn || `≈ ${fmt(rate && n ? Math.max(1, Math.round((n * 1e8) / rate)) : 0)} sats · ${t("indicative")}`;
    $("#create").disabled = !(n >= cfg.min_xof && n <= cfg.max_xof);
    app.querySelectorAll("[data-method]").forEach((b) => { b.disabled = !(n > 0 && n <= cfg.max_xof); });
    if (rate && $("#rate")) $("#rate").textContent = t("rate", { r: fmt(rate) });
  };
  bindPad((k) => {
    if (k === "C") state.amount = "";
    else if (k === "<") state.amount = state.amount.slice(0, -1);
    else if (state.amount.length < 7 && !(state.amount === "" && k === "0")) state.amount += k;
    update();
  });
  on("[data-q]", "click", (e) => { state.amount = e.currentTarget.dataset.q; update(); });
  on("#note", "input", (e) => { state.note = e.target.value; });
  const noteVal = () => (state.note || "").trim() || undefined;
  on("#create", "click", async (e) => {
    e.currentTarget.disabled = true;
    const r = await api("POST", "/api/invoices", { amount_xof: Number(state.amount), note: noteVal() });
    if (!r.ok) { e.currentTarget.disabled = false; return showMsg(errText(r.data)); }
    state.note = "";
    go("/facture/" + r.data.id);
  });
  on("#other", "click", () => { const b = $("#otherbox"); b.hidden = !b.hidden; });
  on("[data-method]", "click", async (e) => {
    e.currentTarget.disabled = true;
    const r = await api("POST", "/api/sales/cash", { amount_xof: Number(state.amount), method: e.currentTarget.dataset.method, note: noteVal() });
    if (!r.ok) { e.currentTarget.disabled = false; return showMsg(errText(r.data)); }
    state.amount = ""; state.note = "";
    go("/recu/" + r.data.id);
  });
  update();

  // Ventes du jour : panneau latéral sur ordinateur, liste sous la caisse sur téléphone (sauf mode léger).
  if (desktop() || !state.lite) {
    api("GET", "/api/sales/today").then((r) => {
      const side = $("#side"); if (!r.ok || !side) return;
      const d = r.data;
      const recent = `<div class="row between"><h3>${t("recent")}</h3><a href="#/ventes" class="small">${t("see_all")}</a></div>${salesList(d.sales, 5)}`;
      if (!desktop()) { const m = $("#recentm"); m.innerHTML = recent; m.hidden = false; return; }
      side.innerHTML = `
        <div class="tiles two">
          <div class="tile hero"><div class="k">${t("today_total")}</div><div class="v num">${fmt(d.total_xof)} <small>FCFA</small></div></div>
          <div class="tile"><div class="k">${ic("receipt")}${t("sales_count")}</div><div class="v num">${d.count}</div>${deltaHTML(d.total_xof, d.yesterday_xof)}</div>
          <div class="tile"><div class="k">${ic("clock")}${t("avg_time")}</div><div class="v num">${d.median_confirm_s ?? "–"} <small>s</small></div></div>
        </div>
        <div class="card"><div class="row between"><h3>${t("recent")}</h3><a href="#/ventes" class="small">${t("see_all")}</a></div>${salesList(d.sales, 6)}</div>`;
    });
  }
}

// ================================================================== facture
function screenInvoice(id) {
  let inv = null, polls = 0;
  const left = () => Math.max(0, inv.expires_at - Math.floor(Date.now() / 1000));
  const mmss = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
  const total = () => Math.max(1, inv.expires_at - inv.created_at);
  const ring = () => {
    const c = 2 * Math.PI * 9, frac = left() / total();
    return `<svg class="ring" viewBox="0 0 22 22" aria-hidden="true"><circle class="bg" cx="11" cy="11" r="9"/><circle class="fg" cx="11" cy="11" r="9" stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${(c * (1 - frac)).toFixed(1)}"/></svg>`;
  };

  const draw = () => {
    const st = inv.status, pending = st === "pending";
    render(appLayout("caisse", `
      <div class="page-head"><div class="row"><button class="icon-btn" data-go="/caisse" aria-label="${t("back")}">${ic("back")}</button><h1>${t("invoice")}</h1></div></div>
      <div class="invoice">
        <section class="card qr-card">
          <div><div class="inv-amount num">${fmt(inv.amount_xof)}<small>FCFA</small></div><div class="muted num">${fmt(inv.amount_sat)} sats</div></div>
          ${pending ? `<div class="qr-frame"><img src="/api/invoices/${encodeURIComponent(id)}/qr.svg" alt="QR code de la facture de ${fmt(inv.amount_xof)} FCFA"><span class="logo badge-bolt">${BOLT}</span></div>
            <div class="row wrap center"><span class="pill"><span class="dot"></span>${t("waiting")}</span><span class="timer" id="timer">${ring()}<span>${t("left", { t: mmss(left()) })}</span></span></div>
            <div class="btn-row"><button class="btn ghost sm" id="copy">${ic("copy")}${t("copy")}</button><a class="btn ghost sm" href="lightning:${esc(inv.bolt11)}">${ic("open")}${t("open_wallet")}</a></div>`
          : `<span class="pill err">${st === "expired" ? t("expired") : t("cancelled")}</span><p class="muted">${t("expired_help")}</p>`}
        </section>
        <section class="card stack">
          <h3>${t("how_title")}</h3>
          <ol class="howto"><li>${t("how1")}</li><li>${t("how2")}</li><li>${t("how3")}</li></ol>
          <p class="alert info">${t("give_after")}</p>
          <p class="alert" role="alert"></p>
          ${inv.real ? `<span class="pill ok">${ic("check")}${t("real_payment")}</span>` : `<p class="muted small">${t("demo_payment")}</p>`}
          ${pending && inv.simulate ? `<button class="btn dark block" id="sim">${ic("spark")}${t("simulate")}</button>` : ""}
          ${pending && inv.simulate ? `<details class="onramp"><summary>${ic("phone")}${t("onramp_q")}</summary>
            <p class="small muted">${t("onramp_help")}</p>
            <div class="btn-row"><button class="btn ghost sm" data-onramp="orange">Orange Money</button><button class="btn ghost sm" data-onramp="free">Mixx by Yas</button></div>
            <p class="small muted">${t("onramp_demo")}</p></details>` : ""}
          ${pending ? `<button class="btn ghost block" id="cancel">${t("cancel")}</button>`
            : `<button class="btn block" id="again">${t("retry_same")}</button><button class="btn ghost block" data-go="/caisse">${t("back_pos")}</button>`}
        </section>
      </div>`));
    bindCommon();
    on("#copy", "click", async () => {
      try { await navigator.clipboard.writeText(inv.bolt11); showMsg(t("copied"), undefined, true); } catch { /* presse-papier refusé */ }
    });
    on("#cancel", "click", async () => { await api("POST", `/api/invoices/${encodeURIComponent(id)}/cancel`); state.amount = ""; go("/caisse"); });
    on("#again", "click", async (e) => {
      e.currentTarget.disabled = true;
      const r = await api("POST", "/api/invoices", { amount_xof: inv.amount_xof });
      if (r.ok) go("/facture/" + r.data.id); else { e.currentTarget.disabled = false; showMsg(errText(r.data)); }
    });
    on("[data-onramp]", "click", async (e) => {
      e.currentTarget.disabled = true;
      const r = await api("POST", `/api/invoices/${encodeURIComponent(id)}/onramp`, { operator: e.currentTarget.dataset.onramp });
      if (r.ok) { inv = r.data; settle(); } else { e.currentTarget.disabled = false; showMsg(errText(r.data)); }
    });
    on("#sim", "click", async (e) => {
      e.currentTarget.disabled = true;
      const r = await api("POST", `/api/invoices/${encodeURIComponent(id)}/simulate`);
      if (r.ok) { inv = r.data; settle(); } else e.currentTarget.disabled = false;
    });
    if (pending) {
      every(() => { const el = $("#timer"); if (el) el.innerHTML = `${ring()}<span>${t("left", { t: mmss(left()) })}</span>`; }, 1000);
      poll();
    }
  };

  const settle = () => { if (inv.status === "paid") { state.amount = ""; go("/recu/" + id); return true; } return false; };

  // Vérification rapide au début, plus espacée ensuite ou en mode léger. Pause si l'onglet est caché.
  const poll = () => {
    const delay = state.lite ? 5000 : polls < 15 ? 2000 : 4000;
    later(async () => {
      if (document.hidden) return poll();
      polls++;
      const r = await api("GET", `/api/invoices/${encodeURIComponent(id)}`);
      if (r.ok) {
        const before = inv.status; inv = r.data;
        if (settle()) return;
        if (inv.status !== before) return draw();
      }
      poll();
    }, delay);
  };

  (async () => {
    const r = await api("GET", `/api/invoices/${encodeURIComponent(id)}`);
    if (!r.ok) return go("/caisse");
    inv = r.data;
    if (!settle()) draw();
  })();
}

// ================================================================== reçu
function celebrate(inv) {
  navigator.vibrate?.([120, 60, 120]);
  if (state.lite) return;
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    [880, 1320].forEach((f, i) => {
      const o = ctx.createOscillator(), g = ctx.createGain(), at = ctx.currentTime + i * 0.16;
      o.frequency.value = f; o.connect(g); g.connect(ctx.destination);
      g.gain.setValueAtTime(0.18, at); g.gain.exponentialRampToValueAtTime(0.001, at + 0.15);
      o.start(at); o.stop(at + 0.16);
    });
  } catch { /* son indisponible */ }
  if (state.voice) announce(inv.amount_xof);
}

// Aucun téléphone n'a de voix de synthèse en wolof. On joue donc en priorité un enregistrement
// fait par un locuteur natif (/audio/wo/paiement-recu.mp3), sinon la phrase wolof lue par la voix française.
function speak(text) {
  if (!("speechSynthesis" in window)) return;
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "fr-FR"; u.rate = 0.95; speechSynthesis.cancel(); speechSynthesis.speak(u);
}
function announce(amount) {
  if (state.lang !== "wo") return speak(`Paiement reçu. ${amount} francs.`);
  const clip = new Audio("/audio/wo/paiement-recu.mp3");
  clip.addEventListener("ended", () => speak(`${amount} francs.`), { once: true });
  clip.play().catch(() => speak(`Fey bi agsi na. ${amount} francs. Jërëjëf.`));
}

async function screenReceipt(id, fromHistory = false) {
  const r = await api("GET", `/api/invoices/${encodeURIComponent(id)}`);
  if (!r.ok || r.data.status !== "paid") return go(fromHistory ? "/ventes" : "/caisse");
  const inv = r.data;
  const lightning = (inv.method || "lightning") === "lightning";
  const proof = inv.proof;
  render(appLayout(fromHistory ? "ventes" : "caisse", `
    ${fromHistory ? `<div class="page-head"><div class="row"><button class="icon-btn" data-go="/ventes" aria-label="${t("back_history")}">${ic("back")}</button><h1>${t("view_receipt")}</h1></div></div>` : ""}
    <div class="receipt">
      <section class="card ticket">
        <div class="top"><div class="success">${ic("check")}</div><h1>${t("paid")}</h1>
          <div class="big num">${fmt(inv.amount_xof)} <small>FCFA</small></div>
          ${lightning ? `<span class="pill ok">${ic("clock")}${t("auto_confirmed", { s: inv.confirm_s ?? "–" })}</span>` : `<span class="pill neutral">${t("sale_recorded")}</span>`}
          ${inv.training ? `<span class="pill">${t("training_tag")}</span>` : ""}</div>
        <div class="tear"></div>
        <div class="lines">
          <div><span>${t("sale_no")}</span><b>${inv.sale_no}</b></div>
          <div><span>${t("method")}</span><b>${t(inv.method || "lightning")}${inv.source === "affiche" ? " · QR" : ""}${(inv.source || "").startsWith("onramp-") ? " · " + t("via", { op: { orange: "Orange Money", free: "Mixx by Yas", wave: "Wave" }[inv.source.slice(7)] || "Mobile Money" }) : ""}</b></div>
          ${lightning ? `<div><span>${t("in_sats")}</span><b class="num">${fmt(inv.amount_sat)}</b></div>` : ""}
          ${inv.note ? `<div><span>${t("note")}</span><b>${esc(inv.note)}</b></div>` : ""}
          <div><span>${t("time")}</span><b>${esc(new Date(inv.date + "T12:00:00Z").toLocaleDateString("fr-FR"))} · ${esc(inv.time)}</b></div>
          <div><span>${t("shop_name")}</span><b>${esc(state.me.shop_name)}</b></div>
        </div>
        ${proof ? `<div class="proof"><div class="row">${ic("shield")}<b>${t("proof")}</b>
          <span class="pill ${proof.valid ? "ok" : "err"}">${proof.valid ? t("proof_ok") : "✗"}</span></div>
          <code>${esc(proof.preimage.slice(0, 16))}…${esc(proof.preimage.slice(-16))}</code>
          <p class="small muted">${t("proof_help")}</p>
          <button class="link small" id="cproof">${ic("copy")}${t("copy_proof")}</button></div>` : ""}
      </section>
      <div class="stack mt">
        <button class="btn lg block" id="new">${ic("plus")}${t("new_sale")}</button>
        <div class="btn-row"><button class="btn ghost" data-go="/ventes">${ic("chart")}${t("see_sales")}</button>
          <button class="btn ghost" id="share">${ic("share")}${t("share")}</button></div>
      </div>
    </div>`));
  bindCommon();
  if (!fromHistory) celebrate(inv);
  on("#new", "click", () => go("/caisse"));
  on("#cproof", "click", async () => { try { await navigator.clipboard.writeText(proof.preimage); } catch { /* refusé */ } });
  on("#share", "click", async () => {
    const text = t("receipt_text", { shop: state.me.shop_name, xof: fmt(inv.amount_xof), sat: fmt(inv.amount_sat), n: inv.sale_no, time: inv.time });
    if (navigator.share) { try { await navigator.share({ text }); } catch { /* partage annulé */ } }
    else window.open("https://wa.me/?text=" + encodeURIComponent(text), "_blank", "noopener");
  });
}

// ================================================================== ventes
function barChart(values, labels, { highlightLast = false, every: step = 1 } = {}) {
  const W = 340, H = 180, top = 12, bottom = 24, left = 4;
  const max = Math.max(1, ...values);
  const slot = (W - left) / values.length, bw = Math.max(4, slot * 0.62);
  const bars = values.map((v, i) => {
    const h = Math.max(v ? 3 : 2, ((H - top - bottom) * v) / max);
    const x = left + i * slot + (slot - bw) / 2, y = H - bottom - h;
    const cls = !v ? "bar dim" : highlightLast && i === values.length - 1 ? "bar today" : "bar";
    return `<rect class="${cls}" x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" rx="3"><title>${esc(labels[i])} : ${fmt(v)} FCFA</title></rect>` +
      (i % step === 0 ? `<text x="${(x + bw / 2).toFixed(1)}" y="${H - 6}" text-anchor="middle">${esc(labels[i])}</text>` : "");
  }).join("");
  const mid = H - bottom - (H - top - bottom) / 2;
  return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="Graphique"><line class="grid" x1="0" x2="${W}" y1="${mid}" y2="${mid}"/><line class="grid" x1="0" x2="${W}" y1="${top}" y2="${top}"/>${bars}</svg>`;
}

async function screenSales() {
  render(appLayout("ventes", `<div class="page-head"><div><h1>${t("my_sales")}</h1><p class="muted">${esc(todayLabel())}</p></div></div><p class="muted">…</p>`));
  bindCommon();
  const [r, w] = await Promise.all([api("GET", "/api/sales/today"), api("GET", "/api/sales/week")]);
  if (!r.ok) { showMsg(errText(r.data)); return; }
  const d = r.data;
  const hours = d.by_hour.slice(6, 23), hourLabels = hours.map((_, i) => `${i + 6}h`);
  const days = w.ok ? w.data.days : [];
  const dayLabels = days.map((x) => new Date(x.day + "T12:00:00Z").toLocaleDateString("fr-FR", { weekday: "short" }).replace(".", ""));
  render(appLayout("ventes", `
    <div class="page-head"><div><h1>${t("my_sales")}</h1><p class="muted">${esc(todayLabel())}</p></div>
      <div class="row wrap"><a class="btn ghost sm" href="/api/sales/export.csv" download>${ic("receipt")}${t("export")}</a>
      <button class="btn sm" data-go="/caisse">${ic("plus")}${t("new_sale")}</button></div></div>
    <div class="tiles">
      <div class="tile hero"><div class="k">${t("today_total")}</div><div class="v num">${fmt(d.total_xof)} <small>FCFA</small></div></div>
      <div class="tile"><div class="k">${ic("receipt")}${t("sales_count")}</div><div class="v num">${d.count}</div>${deltaHTML(d.total_xof, d.yesterday_xof)}</div>
      <div class="tile"><div class="k">${ic("coins")}${t("total_sats")}</div><div class="v num">${fmt(d.total_sat)}</div></div>
      <div class="tile"><div class="k">${ic("clock")}${t("avg_time")}</div><div class="v num">${d.median_confirm_s ?? "–"} <small>s</small></div></div>
    </div>
    <div class="grid-2 mt">
      <section class="card"><h3>${t("by_hour")}</h3>${barChart(hours, hourLabels, { every: 3 })}</section>
      <section class="card"><h3>${t("last7")}</h3>${days.length ? barChart(days.map((x) => x.total_xof), dayLabels, { highlightLast: true }) : ""}</section>
    </div>
    <div class="grid-2 mt">
      <section class="card ai-card" aria-live="polite">
        <div class="row between"><h3>${t("day_summary")}</h3><span class="tag" id="src">${ic("spark")}…</span></div>
        <div id="sum">${state.lite ? `<button class="btn sm ghost mt" id="loadsum">${t("load_summary")}</button>` : `<p class="muted mt">…</p>`}</div>
      </section>
      <section class="card"><h3>${t("by_day")}</h3><ul class="sales">${days.slice().reverse().filter((x) => x.count).map((x) =>
        `<li><div class="meta"><b>${esc(dayTitle(x.day))}</b><span>${t("sales_day", { n: x.count, xof: fmt(x.total_xof) })}</span></div>
        <button class="btn ghost sm" data-day="${x.day}">${ic("search")}</button></li>`).join("")}</ul></section>
    </div>
    <section class="card mt history" id="history">
      <h3>${t("history")}</h3>
      <label class="search"><span class="sr">${t("search_ph")}</span>${ic("search")}
        <input id="hq" type="search" inputmode="search" maxlength="20" placeholder="${t("search_ph")}" autocomplete="off"></label>
      <div id="hlist"></div>
      <button class="btn ghost block" id="hmore" hidden>${t("more")}</button>
      <div id="hsentinel"></div>
    </section>`));
  bindCommon();
  const loadSummary = async () => {
    const box = $("#sum"); if (!box) return;
    box.innerHTML = `<p class="muted mt">…</p>`;
    const s = await api("GET", "/api/sales/summary");
    if (!$("#sum")) return;
    if (!s.ok) { box.innerHTML = `<p class="muted">${esc(errText(s.data))}</p>`; return; }
    $("#src").innerHTML = `${ic("spark")}${s.data.source === "ia" ? t("ai") : t("local")}`;
    const fr = `<h4>${t("french")}</h4><p lang="fr">${esc(s.data.fr)}</p>`;
    const wo = `<h4>${t("wolof")}</h4><p lang="wo">${esc(s.data.wo)}</p>`;
    box.innerHTML = state.lang === "wo" ? wo + fr : fr + wo;
  };
  if (state.lite) on("#loadsum", "click", loadSummary); else loadSummary();
  initHistory();
}

function dayTitle(day) {
  const d = new Date(day + "T12:00:00Z");
  const today = new Date().toISOString().slice(0, 10);
  const yest = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
  if (day === today) return t("today_lbl");
  if (day === yest) return t("yesterday_lbl");
  return d.toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long" });
}

// Historique « comme Wave » : groupé par jour, recherche, chargement au défilement.
function initHistory() {
  let cursor = "", query = "", loading = false, lastDay = "", seq = 0;
  const list = $("#hlist"), more = $("#hmore");
  const load = async (reset) => {
    if (loading && !reset) return;
    loading = true;
    const mine = ++seq;
    if (reset) { cursor = ""; lastDay = ""; list.innerHTML = `<p class="muted">…</p>`; }
    const params = new URLSearchParams({ limit: "25" });
    if (query) params.set("q", query);
    if (cursor) params.set("before", cursor);
    const r = await api("GET", "/api/sales/history?" + params);
    if (mine !== seq || !$("#hlist")) return;
    loading = false;
    if (reset) list.innerHTML = "";
    if (!r.ok) { list.insertAdjacentHTML("beforeend", `<p class="alert">${esc(errText(r.data))}</p>`); return; }
    let html = "";
    for (const s of r.data.sales) {
      if (s.date !== lastDay) {
        if (lastDay) html += "</ul>";
        html += `<div class="day-head">${esc(dayTitle(s.date))}</div><ul class="sales">`;
        lastDay = s.date;
      } else if (!html) html += `<ul class="sales">`;
      html += saleItem(s);
    }
    if (html) html += "</ul>";
    list.insertAdjacentHTML("beforeend", html);
    if (reset && !r.data.sales.length) list.innerHTML = `<p class="empty">${t("no_result")}</p>`;
    cursor = r.data.next_before || "";
    more.hidden = !cursor;
  };
  let timer = null;
  on("#hq", "input", (e) => {
    clearTimeout(timer);
    timer = setTimeout(() => { query = e.target.value.trim(); load(true); }, 300);
  });
  on("[data-day]", "click", (e) => {
    const [y, m, d] = e.currentTarget.dataset.day.split("-");
    const input = $("#hq"); input.value = `${d}/${m}`; query = input.value; load(true);
    $("#history").scrollIntoView({ behavior: state.lite ? "auto" : "smooth" });
  });
  on("#hmore", "click", () => load(false));
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => { if (entries[0].isIntersecting && cursor && !loading) load(false); }, { rootMargin: "200px" });
    io.observe($("#hsentinel"));
  }
  load(true);
}

// ================================================================== retrait Mobile Money
const OPS = [["wave", "Wave"], ["orange", "Orange Money"], ["free", "Mixx by Yas"]];
async function screenPayout() {
  render(appLayout("retrait", `<div class="page-head"><h1>${t("payout_title")}</h1></div><p class="muted">…</p>`));
  bindCommon();
  const r = await api("GET", "/api/payouts");
  if (!r.ok) return showMsg(errText(r.data));
  const d = r.data;
  let op = store.get("op", "wave"), hidden = store.get("hidebal", false);
  const max = Math.min(d.available_xof, d.daily_left_xof);
  const statusPill = (st) => `<span class="pill ${st === "completed" ? "ok" : st === "failed" ? "err" : ""}">${st === "pending" ? '<span class="dot"></span>' : ""}${t("st_" + st)}</span>`;
  render(appLayout("retrait", `
    <div class="page-head"><h1>${t("payout_title")}</h1></div>
    <div class="settings">
      <div class="stack">
        <section class="balance">
          <div class="row between"><span>${t("available")}</span>
            <button class="icon-btn on-dark" id="eye" aria-label="${hidden ? t("show_bal") : t("hide_bal")}">${ic("eye")}</button></div>
          <div class="amount num" id="bal">${hidden ? "•••••" : fmt(d.available_xof)} <small>FCFA</small></div>
          <div class="small">${t("daily_left", { x: fmt(d.daily_left_xof) })}</div>
        </section>
        <form class="card stack" id="pf" novalidate>
          <div class="field">${t("choose_op")}
            <div class="ops" role="radiogroup">${OPS.map(([v, name]) =>
              `<button type="button" class="op op-${v}" role="radio" data-op="${v}" aria-checked="${op === v}"><span class="dot-op"></span>${name}</button>`).join("")}</div></div>
          <label class="field">${t("amount_fcfa")}
            <input class="input num" id="pamt" inputmode="numeric" pattern="[0-9]*" maxlength="9" placeholder="${fmt(Math.min(5000, max))}"></label>
          <div class="chips">${[[0.25, "25 %"], [0.5, "50 %"], [1, t("all")]].map(([f, l]) => `<button type="button" data-frac="${f}">${l}</button>`).join("")}</div>
          <div class="recap" id="recap"></div>
          <p class="muted small">${ic("shield")} ${t("only_own")}</p>
          <label class="field">${t("confirm_pin")}
            <input class="input" id="ppin" type="password" inputmode="numeric" pattern="[0-9]*" maxlength="4" autocomplete="off" placeholder="••••"></label>
          <p class="alert" role="alert"></p>
          <button class="btn lg block" id="pgo" disabled>${ic("cash")}<span id="pgol">${t("withdraw", { x: "0" })}</span></button>
          ${d.simulated ? `<p class="muted small center">${t("payout_demo")}</p>` : ""}
        </form>
      </div>
      <section class="card"><h3>${t("payouts_hist")}</h3>
        ${d.items.length ? `<ul class="sales">${d.items.map((p) => `<li><span class="ic op-ic op-${p.operator}">${ic("cash")}</span>
          <div class="meta"><b>${esc(p.operator_name)}</b><span>${esc(dayTitle(p.date))} · ${esc(p.time)}</span></div>
          <div class="amt num">−${fmt(p.amount_xof)} F<small>${statusPill(p.status)}</small></div></li>`).join("")}</ul>`
          : `<p class="empty">${t("no_payouts")}</p>`}
      </section>
    </div>`));
  bindCommon();
  const amountOf = () => Number(($("#pamt").value || "").replace(/\D/g, "")) || 0;
  const update = () => {
    const a = amountOf(), fee = Math.round((a * d.fee_pct) / 100);
    $("#recap").innerHTML = a ? `<div><span>${t("fee", { p: d.fee_pct })}</span><b class="num">${fmt(fee)} F</b></div>
      <div><span>${t("you_receive")}</span><b class="num">${fmt(a - fee)} FCFA</b></div>
      <div class="muted small">${t("to_number", { n: esc(d.destination) })}</div>` : "";
    $("#pgol").textContent = t("withdraw", { x: fmt(a) });
    $("#pgo").disabled = !(a >= d.min_xof && a <= max && /^\d{4}$/.test($("#ppin").value));
  };
  on("[data-op]", "click", (e) => {
    op = e.currentTarget.dataset.op; store.set("op", op);
    app.querySelectorAll("[data-op]").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.op === op)));
  });
  on("[data-frac]", "click", (e) => { $("#pamt").value = String(Math.floor(max * Number(e.currentTarget.dataset.frac))); update(); });
  on("#pamt", "input", update);
  on("#ppin", "input", update);
  on("#eye", "click", () => { hidden = !hidden; store.set("hidebal", hidden); $("#bal").innerHTML = `${hidden ? "•••••" : fmt(d.available_xof)} <small>FCFA</small>`; });
  on("#pf", "submit", async (e) => {
    e.preventDefault();
    $("#pgo").disabled = true;
    const res = await api("POST", "/api/payouts", { operator: op, amount_xof: amountOf(), pin: $("#ppin").value });
    $("#ppin").value = "";
    if (!res.ok) { update(); return showMsg(errText(res.data)); }
    navigator.vibrate?.(60);
    screenPayout().then(() => showMsg(t("payout_ok", { op: res.data.operator_name }), undefined, true));
  });
  update();
  // Rafraîchit l'état des retraits en cours.
  if (d.items.some((p) => p.status === "pending")) later(() => { if (location.hash === "#/retrait") screenPayout(); }, 4000);
}

// ================================================================== assistante
function screenHelp() {
  if (!state.chat.length) state.chat.push({ role: "assistant", content: t("chat_hello", { name: state.me.name.split(" ")[0] }) });
  const draw = (busy = false) => {
    render(appLayout("aide", `
      <div class="chat-wrap">
        <div class="page-head"><div class="row"><span class="avatar">${ic("chat")}</span><div><h1>${t("assistant")}</h1><p class="muted small">${t("online")}</p></div></div></div>
        <div class="chat" id="chat">${state.chat.map((m) => `<div class="bubble ${m.role === "user" ? "me" : ""}">${esc(m.content)}</div>`).join("")}
          ${busy ? `<div class="bubble" aria-label="…"><span class="typing"><i></i><i></i><i></i></span></div>` : ""}</div>
        <div class="chips">${["q1", "q2", "q3", "q4"].map((q) => `<button type="button" data-ask="${q}">${t(q)}</button>`).join("")}</div>
        <form class="composer" id="f"><label class="sr" for="q">${t("ask")}</label>
          <input class="input" id="q" maxlength="500" placeholder="${t("ask")}" autocomplete="off">
          <button class="send" aria-label="${t("send")}">${ic("send")}</button></form>
      </div>`));
    bindCommon();
    app.querySelector("#chat .bubble:last-child")?.scrollIntoView({ block: "end" });
    on("[data-ask]", "click", (e) => ask(t(e.currentTarget.dataset.ask)));
    on("#f", "submit", (e) => { e.preventDefault(); const v = $("#q").value.trim(); if (v) ask(v); });
    if (!busy && desktop()) $("#q")?.focus();
  };
  const ask = async (q) => {
    const history = state.chat.slice(-6).map((m) => ({ role: m.role, content: m.content.slice(0, 1200) }));
    state.chat.push({ role: "user", content: q }); draw(true);
    const r = await api("POST", "/api/assistant", { message: q, history, lang: state.lang });
    let reply = r.ok ? r.data.reply : errText(r.data);
    if (r.ok && /conseiller|support/i.test(q) && state.me.config.support_phone) reply += "\n☎ " + state.me.config.support_phone;
    state.chat.push({ role: "assistant", content: reply }); draw();
  };
  draw();
}

// ================================================================== réglages
function screenSettings() {
  const me = state.me, cfg = me.config;
  const sw = (id, val) => `<button class="switch" id="${id}" role="switch" aria-checked="${val}" aria-label="${t(id)}"></button>`;
  const seg = (name, opts, cur) => `<div class="seg" role="group">${opts.map(([v, label]) =>
    `<button type="button" data-${name}="${v}" aria-pressed="${cur === v}">${label}</button>`).join("")}</div>`;
  render(appLayout("reglages", `
    <div class="page-head"><h1>${t("settings")}</h1></div>
    <div class="settings">
      <div class="stack">
        <section class="card"><div class="profile"><span class="avatar">${esc(me.shop_name.trim()[0]?.toUpperCase())}</span>
          <div><b>${esc(me.shop_name)}</b><div class="muted small">${esc(me.name)} · ${esc(me.area)}</div><div class="muted small num">${esc(me.phone)}</div></div></div></section>
        <section class="card"><h3>${t("prefs")}</h3>
          <div class="setting"><div class="txt">${t("language")}</div>${seg("lang", [["fr", "Français"], ["wo", "Wolof"]], state.lang)}</div>
          <div class="setting"><div class="txt">${t("theme")}</div>${seg("theme", [["auto", t("th_auto")], ["light", t("th_light")], ["dark", t("th_dark")]], state.theme)}</div>
          <div class="setting"><div class="txt">${t("lite")}<small>${t("lite_help")}</small></div>${sw("lite", state.lite)}</div>
          <div class="setting"><div class="txt">${t("voice")}<small>${t("voice_help")}</small></div>${sw("voice", state.voice)}</div>
          <div class="setting"><div class="txt">${t("training")}<small>${t("training_help")}</small></div>${sw("training", !!me.training)}</div>
          ${me.training ? `<button class="link small" id="tclear">${t("training_clear")}</button><p class="alert info" role="status" id="tmsg"></p>` : ""}
        </section>
        <section class="card stack"><div class="row">${ic("pos")}<h3>${t("poster")}</h3></div>
          <p class="muted">${t("poster_help")}</p><a class="btn ghost sm" href="#/affiche">${t("poster")}</a></section>
      </div>
      <div class="stack">
        <section class="card stack"><div class="row">${ic("wallet")}<h3>${t("nwc_title")}</h3></div>
          ${me.nwc_linked ? `<p class="alert info">${t("nwc_on")}</p><p class="alert" role="alert" id="nwarn"></p><button type="button" class="btn ghost sm" id="nunlink">${t("nwc_unlink")}</button>`
            : `<p class="muted">${t("nwc_off")}</p>
            <ol class="howto"><li>${t("nwc_step1")}</li><li>${t("nwc_step2")}</li><li>${t("nwc_step3")}</li></ol>
            <form id="nf" class="stack">
              <label class="field"><span class="sr">Nostr Wallet Connect</span><input class="input" id="nuri" autocomplete="off" spellcheck="false" maxlength="1000" placeholder="nostr+walletconnect://…"></label>
              <p class="alert" role="alert" id="nerr"></p>
              <button class="btn sm">${ic("wallet")}${t("nwc_link")}</button>
            </form>`}
        </section>
        <section class="card stack"><div class="row">${ic("shield")}<h3>${t("pin_section")}</h3></div>
          <form id="pinf" class="stack">
            <label class="field">${t("pin_current")}<input class="input" id="pc" type="password" inputmode="numeric" maxlength="4" autocomplete="current-password"></label>
            <label class="field">${t("pin_new")}<input class="input" id="pn" type="password" inputmode="numeric" maxlength="4" autocomplete="new-password"></label>
            <label class="field">${t("pin_new2")}<input class="input" id="pn2" type="password" inputmode="numeric" maxlength="4" autocomplete="new-password"></label>
            <p class="alert" role="alert" id="pinerr"></p>
            <button class="btn ghost sm">${t("pin_change")}</button>
          </form>
        </section>
        ${cfg.backend !== "lnbits" ? "" : `<section class="card stack"><div class="row">${ic("wallet")}<h3>${t("wallet")}</h3></div>
          ${`
            <p class="muted">${me.wallet_linked ? t("wallet_linked") : t("wallet_default")}</p>
            <form id="wf" class="stack">
              <label class="field">${t("wallet_key")}<input class="input" id="wkey" autocomplete="off" spellcheck="false" maxlength="64" placeholder="32 caractères"></label>
              <p class="muted small">${t("wallet_key_help")}</p>
              <p class="alert" role="alert" id="werr"></p>
              <button class="btn sm">${t("wallet_save")}</button>
              ${me.wallet_linked ? `<button type="button" class="btn ghost sm" id="wun">${t("wallet_unlink")}</button>` : ""}
            </form>`}
        </section>`}
        <section class="card"><div class="row">${ic("shield")}<h3>${t("security")}</h3></div>
          <ul class="sales">${["sec1", "sec2", "sec3"].map((k) => `<li><span class="ic">${ic("check")}</span><div class="meta">${t(k)}</div></li>`).join("")}</ul>
          ${cfg.support_phone ? `<div class="setting"><div class="txt">${t("support")}</div><a href="tel:${esc(cfg.support_phone.replace(/[^\d+]/g, ""))}">${esc(cfg.support_phone)}</a></div>` : ""}
        </section>
        <button class="btn ghost block" data-logout>${ic("logout")}${t("logout")}</button>
      </div>
    </div>`));
  bindCommon();
  on("[data-theme]", "click", (e) => { state.theme = e.currentTarget.dataset.theme; store.set("theme", state.theme); applyPrefs(); screenSettings(); });
  on("#lite", "click", () => { state.lite = !state.lite; store.set("lite", state.lite); applyPrefs(); screenSettings(); });
  on("#voice", "click", () => { state.voice = !state.voice; store.set("voice", state.voice); screenSettings(); });
  on("#training", "click", async () => { await api("PATCH", "/api/me", { training: !me.training }); await loadMe(); screenSettings(); });
  on("#tclear", "click", async () => {
    const r = await api("DELETE", "/api/me/training-sales");
    if (r.ok) showMsg(t("training_cleared", { n: r.data.deleted }), $("#tmsg"), true);
  });
  on("#wf", "submit", async (e) => {
    e.preventDefault();
    const r = await api("PUT", "/api/me/wallet", { invoice_key: $("#wkey").value.trim() });
    if (!r.ok) return showMsg(errText(r.data), $("#werr"));
    await loadMe(); screenSettings();
  });
  on("#wun", "click", async () => { await api("DELETE", "/api/me/wallet"); await loadMe(); screenSettings(); });
  on("#nf", "submit", async (e) => {
    e.preventDefault();
    const btn = e.currentTarget.querySelector("button"); btn.disabled = true;
    showMsg(t("nwc_testing"), $("#nerr"), true);
    const r = await api("PUT", "/api/me/nwc", { uri: $("#nuri").value.trim() });
    btn.disabled = false;
    if (!r.ok) return showMsg(errText(r.data), $("#nerr"));
    await loadMe(); screenSettings();
    if (r.data.can_spend) showMsg(t("nwc_spend_warn"), $("#nwarn"));
  });
  on("#nunlink", "click", async () => { await api("DELETE", "/api/me/nwc"); await loadMe(); screenSettings(); });
  on("#pinf", "submit", async (e) => {
    e.preventDefault();
    const err = $("#pinerr");
    if ($("#pn").value !== $("#pn2").value) return showMsg(t("pin_mismatch"), err);
    const r = await api("POST", "/api/me/pin", { current_pin: $("#pc").value, new_pin: $("#pn").value });
    e.currentTarget.reset();
    showMsg(r.ok ? t("pin_changed") : errText(r.data), err, r.ok);
  });
}

// ================================================================== affiche QR à imprimer
async function screenPoster() {
  const r = await api("GET", "/api/me/poster");
  if (!r.ok) return go("/caisse");
  const d = r.data;
  render(appLayout("caisse", `
    <div class="page-head no-print"><div class="row"><button class="icon-btn" data-go="/caisse" aria-label="${t("back")}">${ic("back")}</button>
      <div><h1>${t("poster")}</h1><p class="muted">${t("poster_help")}</p></div></div>
      <div class="row wrap"><button class="btn sm" id="print">${t("print")}</button></div></div>
    ${d.reachable ? "" : `<p class="alert info no-print">${t("poster_offline")}</p>`}
    <div class="poster-wrap">
      <article class="poster" aria-label="${t("poster")}">
        <div class="poster-top"><span class="logo">${BOLT}</span><span>Caisse Teranga</span></div>
        <h2>${esc(d.shop_name)}</h2>
        <p class="poster-area">${esc(d.area)}</p>
        <div class="poster-qr"><img src="/api/me/poster-qr.svg" alt="QR code de paiement Lightning de ${esc(d.shop_name)}"></div>
        <p class="poster-scan">${t("poster_scan")} ⚡</p>
        <p class="poster-free">${t("poster_free")}</p>
        <p class="poster-wallets">${t("poster_wallets")}</p>
        <p class="poster-addr">${t("lnaddr")} : <b>${esc(d.lightning_address)}</b></p>
      </article>
    </div>
    ${state.me.config.simulate || state.me.training ? `<form class="card stack no-print mt" id="psim">
      <h3>${t("poster_sim")}</h3>
      <label class="field">${t("poster_amount")}<input class="input" id="pamt" inputmode="numeric" maxlength="7" value="2500"></label>
      <p class="alert" role="alert"></p>
      <button class="btn dark">${ic("spark")}${t("poster_sim")}</button></form>` : ""}`));
  bindCommon();
  on("#print", "click", () => window.print());
  on("#psim", "submit", async (e) => {
    e.preventDefault();
    const res = await api("POST", "/api/me/poster/simulate", { amount_xof: Number($("#pamt").value.replace(/\D/g, "")) || 0 });
    if (!res.ok) return showMsg(errText(res.data));
    go("/recu/" + res.data.id);
  });
}

// ================================================================== routeur
async function loadMe() {
  const r = await api("GET", "/api/me");
  state.me = r.ok ? r.data : null;
  return state.me;
}
async function logout() {
  await api("POST", "/api/auth/logout");
  state.me = null; state.chat = []; state.amount = "";
  go("/login");
}
function applyPrefs() {
  const root = document.documentElement;
  root.classList.toggle("lite", state.lite);
  if (state.theme === "auto") delete root.dataset.theme; else root.dataset.theme = state.theme;
  root.lang = state.lang === "wo" ? "wo" : "fr";
}

async function route() {
  const [, page = "", arg] = (location.hash.slice(1) || "/caisse").split("/");
  const open = { login: screenLogin, inscription: screenSignup, code: screenPin, bienvenue: screenOnboarding };
  if (page === "login" && !store.get("onboarded", false)) return screenOnboarding();
  if (open[page]) {
    if (!state.pub) { const p = await api("GET", "/api/public-config"); state.pub = p.ok ? p.data : {}; }
    return open[page]();
  }
  if (!state.me && !(await loadMe())) return go("/login");
  const pages = {
    caisse: screenCaisse, ventes: screenSales, retrait: screenPayout, affiche: screenPoster, aide: screenHelp, reglages: screenSettings,
    facture: () => screenInvoice(arg), recu: () => screenReceipt(arg), vente: () => screenReceipt(arg, true),
  };
  (pages[page] || screenCaisse)();
}

function updateOnline() {
  const bar = document.getElementById("offline");
  bar.hidden = navigator.onLine;
  bar.textContent = t("offline");
}

window.addEventListener("hashchange", route);
window.addEventListener("online", updateOnline);
window.addEventListener("offline", updateOnline);
applyPrefs();
updateOnline();
route();
if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
