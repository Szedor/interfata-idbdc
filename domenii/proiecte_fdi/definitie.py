# =========================================================
# IDBDC/domenii/proiecte_fdi/definitie.py
# VERSIUNE: 1.0
# STATUS: NOU - definiție domeniu Proiecte FDI
# DATA: 2026.05.09
# =========================================================

CATEGORIE    = "Proiecte"
TIP_LABEL    = "FDI"
TIP_SEL      = "FDI"

BASE_TABLE   = "base_proiecte_fdi"
FIN_TABLE    = "com_date_financiare"
ECHIPA_TABLE = "com_echipe_proiect"
TEHNIC_TABLE = "com_aspecte_tehnice"

TAB_LABELS = ["📋 Date de bază", "💰 Date financiare", "👥 Echipă", "🧪 Aspecte tehnice"]

SECTIUNI_SALVARE = [BASE_TABLE, FIN_TABLE, ECHIPA_TABLE, TEHNIC_TABLE]

COL_LABELS = {
    "denumire_categorie":      "CATEGORIE",
    "acronim_tip_proiecte":    "TIPUL DE PROIECT",
    "cod_identificare":        "COD FINAL INREGISTRARE",
    "titlul_proiect":          "TITLUL PROIECTULUI",
    "acronim_proiect":         "ACRONIMUL PROIECTULUI",
    "data_inceput":            "DATA DE INCEPUT",
    "data_sfarsit":            "DATA DE SFARSIT",
    "durata":                  "DURATA (luni)",
    "status_contract_proiect": "STATUS CONTRACT",
    "program":                 "PROGRAM DE FINANTARE",
    "cod_domeniu_fdi":         "DOMENIU",
    "cod_temporar":            "COD DEPUNERE",
    "observatii":              "OBSERVATII",
    "valuta":                  "VALUTA",
    "suma_solicitata_fdi":     "SUMA SOLICITATA",
    "suma_aprobata_mec":       "SUMA APROBATA",
    "cofinantare_upt_fdi":     "COFINANTARE",
    "total_buget_proiect_fdi": "TOTAL VALOARE CONTRACT",
    "nume_prenume":            "NUME SI PRENUME",
    "rol":                     "ROLUL IN CONTRACT",
    "persoana_contact":        "PERSOANA DE CONTACT",
    "departament":             "DEPARTAMENT",
    "email":                   "EMAIL",
    "telefon":                 "TELEFON",
    "obiectiv_general":        "OBIECTIV GENERAL",
    "obiective_specifice":     "OBIECTIVE SPECIFICE",
    "activitati_proiect":      "ACTIVITATI",
    "rezultate_proiect":       "REZULTATE",
}

COLS_HIDDEN = {
    "nr_crt",
    "creat_de", "creat_la", "modificat_de", "modificat_la",
    "acronim_departament", "denumire_departament",
    "telefon_mobil", "telefon_fix",
    "persoana_contact",
}

COLS_COMPUSE = {
    "departament": ["acronim_departament", "denumire_departament"],
    "telefon":     ["telefon_mobil", "telefon_fix"],
}

COL_ORDER_GENERALE = [
    "denumire_categorie",
    "acronim_tip_proiecte",
    "cod_identificare",
    "titlul_proiect",
    "acronim_proiect",
    "data_inceput",
    "data_sfarsit",
    "durata",
    "status_contract_proiect",
    "program",
    "cod_domeniu_fdi",
    "cod_temporar",
]

COL_ORDER_FINANCIAR = [
    "cod_identificare",
    "valuta",
    "suma_solicitata_fdi",
    "suma_aprobata_mec",
    "cofinantare_upt_fdi",
    "total_buget_proiect_fdi",
]

COL_ORDER_ECHIPA = [
    "cod_identificare",
    "nume_prenume",
    "rol",
    "persoana_contact",
    "departament",
    "email",
    "telefon",
]

COL_ORDER_TEHNIC = [
    "cod_identificare",
    "obiectiv_general",
    "obiective_specifice",
    "activitati_proiect",
    "rezultate_proiect",
]
