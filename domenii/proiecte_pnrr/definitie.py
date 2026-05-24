# =========================================================
# IDBDC/domenii/proiecte_pnrr/definitie.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.05.23
# =========================================================

CATEGORIE    = "Proiecte"
TIP_LABEL    = "PNRR"
TIP_SEL      = "PNRR"
BASE_TABLE   = "base_proiecte_pnrr"
FIN_TABLE    = "com_date_financiare"
ECHIPA_TABLE = "com_echipe_proiect"
TEHNIC_TABLE = "com_aspecte_tehnice"
TAB_LABELS       = ["📋 Date de bază", "💰 Date financiare", "👥 Echipă", "🧪 Aspecte tehnice"]
SECTIUNI_SALVARE = [BASE_TABLE, FIN_TABLE, ECHIPA_TABLE, TEHNIC_TABLE]

COL_LABELS = {
    "denumire_categorie":      "CATEGORIE",
    "acronim_tip_proiecte":    "TIPUL DE PROIECT",
    "cod_identificare":        "COD PROIECT",
    "data_contract":           "DATA CONTRACT",
    "titlul_proiect":          "TITLUL PROIECTULUI",
    "acronim_proiect":         "ACRONIMUL PROIECTULUI",
    "domeniu_cercetare":       "DOMENIUL",
    "data_inceput":            "DATA DE INCEPUT",
    "data_sfarsit":            "DATA DE SFARSIT",
    "durata":                  "DURATA (luni)",
    "status_contract_proiect": "STATUS PROIECT",
    "numar_participanti":      "NR.PARTICIPANTI",
    "denumire_participanti":   "DENUMIRE PARTICIPANTI",
    "rol_upt":                 "ROL UPT",
    "identificare_apel":       "APELUL",
    "data_inchidere_apel":     "DATA LIMITA DEPUNERE",
    "pilonul":                 "PILONUL",
    "componenta":              "COMPONENTA",
    "investitia":              "INVESTITIA",
    "subinvestitia":           "SUBINVESTITIA",
    "website":                 "WEBSITE",
    "observatii":              "OBSERVATII",
    "valuta":                  "VALUTA",
    "an_referinta":            "ANUL DE REFERINTA",
    "valoare_contract_an_referinta":     "VALOARE AN REFERINTA",
    "cofinantare_contract_an_referinta": "COFINANTARE AN REFERINTA",
    "valoare_totala_contract":           "VALOARE TOTALA",
    "cofinantare_totala_contract":       "COFINANTARE TOTALA",
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
    "nr_crt", "creat_de", "creat_la", "modificat_de", "modificat_la",
    "acronim_departament", "denumire_departament",
    "telefon_mobil", "telefon_fix", "persoana_contact",
}
COLS_COMPUSE = {
    "departament": ["acronim_departament", "denumire_departament"],
    "telefon":     ["telefon_mobil", "telefon_fix"],
}
COL_ORDER_GENERALE = [
    "denumire_categorie", "acronim_tip_proiecte", "cod_identificare",
    "data_contract", "titlul_proiect", "acronim_proiect",
    "domeniu_cercetare", "data_inceput", "data_sfarsit", "durata",
    "status_contract_proiect", "numar_participanti", "denumire_participanti",
    "rol_upt", "identificare_apel", "data_inchidere_apel",
    "pilonul", "componenta", "investitia", "subinvestitia", "website",
]
COL_ORDER_FINANCIAR = [
    "cod_identificare", "valuta", "an_referinta",
    "valoare_contract_an_referinta", "cofinantare_contract_an_referinta",
    "valoare_totala_contract", "cofinantare_totala_contract",
]
COL_ORDER_ECHIPA = ["cod_identificare", "nume_prenume", "rol", "persoana_contact", "departament", "email", "telefon"]
COL_ORDER_TEHNIC = ["cod_identificare", "obiectiv_general", "obiective_specifice", "activitati_proiect", "rezultate_proiect"]
