# =========================================================
# IDBDC/domenii/proiecte_fdi/definitie.py
# VERSIUNE: 1.0
# STATUS: NOU — definiție completă Proiecte FDI
# DATA: 2026.05.31
# =========================================================
# CONȚINUT:
#   Toate constantele specifice domeniului Proiecte FDI:
#   tabele, etichete tab-uri, mapare câmpuri pentru Date
#   de bază, configurare Date financiare, Aspecte tehnice.
#
#   Structura respectă principiul de betonare:
#   odată validat, acest fișier nu se modifică fără o
#   versiune nouă explicită.
# =========================================================

TIP_LABEL  = "FDI"
CAT_LABEL  = "Proiecte"

BASE_TABLE   = "base_proiecte_fdi"
FIN_TABLE    = "com_date_financiare"
ECHIPA_TABLE = "com_echipe_proiect"
TEHNIC_TABLE = "com_aspecte_tehnice"

# ── Tab-uri vizibile în Calea2 (Administrare) ──────────────────────────
TAB_LABELS_ADMIN = [
    "📋 Date de bază",
    "💰 Date financiare",
    "👥 Echipă",
    "🧪 Aspecte tehnice",
]

# ── Tab-uri vizibile în Calea1 (Explorator) ───────────────────────────
TAB_LABELS_EXPLORATOR = ["Generale", "Financiar", "Echipa", "Tehnic"]

# ── Tabele implicate în ștergere completă (buton ȘTERGE FIȘA) ─────────
SECTIUNI_SALVARE = [BASE_TABLE, FIN_TABLE, ECHIPA_TABLE, TEHNIC_TABLE]

# ── Mapare câmpuri tehnice → etichete vizuale (Date de bază) ──────────
# Chei: nume câmp logic intern (folosit în baza.py generic)
# Valori: eticheta afișată în data_editor
#
# EMOJI-URI PENTRU CÂMPURI CU SELECȚIE (calendar / dropdown):
#   📅  — câmpuri DateColumn  (calendar picker)
#   🔖  — câmpuri SelectboxColumn (dropdown)
#   🆔  — cod identificare (readonly)
#   🏷️  — câmpuri text simple
FIELDS_BAZA = {
    "categorie":         "CATEGORIE",
    "tip":               "TIPUL DE PROIECT",
    "cod":               "🆔 COD FINAL ÎNREGISTRARE",
    "cod_temporar":      "🏷️ COD DEPUNERE",
    "titlu":             "🏷️ TITLUL PROIECTULUI",
    "acronim":           "🏷️ ACRONIMUL PROIECTULUI",
    "data_inceput":      "📅 DATA DE INCEPUT",
    "data_sfarsit":      "📅 DATA DE SFARSIT",
    "durata":            "DURATA (nr. luni)",
    "status":            "🔖 STATUS PROIECT",
    "program":           "🏷️ PROGRAM DE FINANȚARE",
    "cod_domeniu_fdi":   "🔖 DOMENIU FDI",
    "observatii":        "🏷️ OBSERVAȚII",
}

# ── Configurare coloane Date financiare FDI ───────────────────────────
# Definim explicit câmpurile, ordinea și opțiunile de calcul automat.
# Coloana TOTAL VALOARE PROIECT = SUMA APROBATA + COFINANTARE (automat).
FIN_FIELDS = {
    "valuta":                  "💱 VALUTA",
    "suma_solicitata_fdi":     "💰 SUMA SOLICITATĂ",
    "suma_aprobata_mec":       "✅ SUMA APROBATĂ MEC",
    "cofinantare_upt_fdi":     "🏛️ COFINANȚARE UPT",
    "total_buget_proiect_fdi": "📊 TOTAL VALOARE PROIECT",   # calculat automat
}
FIN_AUTO_TOTAL_FIELD = "total_buget_proiect_fdi"   # câmpul calculat = sum(aprobat + cofin)
FIN_COMPONENTS       = ("suma_aprobata_mec", "cofinantare_upt_fdi")  # componentele sumei
FIN_VALUTE           = ["LEI", "EUR", "USD"]

# ── Câmpuri Aspecte tehnice ────────────────────────────────────────────
TEHNIC_FIELDS = {
    "obiectiv_general":    "🎯 OBIECTIV GENERAL",
    "obiective_specifice": "📌 OBIECTIVE SPECIFICE",
    "activitati_proiect":  "⚙️ ACTIVITATI",
    "rezultate_proiect":   "📈 REZULTATE",
}
