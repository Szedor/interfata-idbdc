# =========================================================
# IDBDC/domenii/evenimente_stiintifice/definitie.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.05.23
# =========================================================
# STRUCTURA:
#   - 2 taburi: Date de baza | Echipa
#   - Fara sectiune financiara si fara aspecte tehnice
#   - Dropdown NATURA EVENIMENTULUI → nom_evenimente_stiintifice.natura_eveniment
#     cu completare automata CLASIFICAREA EVENIMENTULUI → clasificare_eveniment
#   - Dropdown FORMATUL EVENIMENTULUI → nom_format_evenimente.format_eveniment
# =========================================================

CATEGORIE    = "Evenimente Științifice"
TIP_LABEL    = "EVENIMENTE ȘTIINȚIFICE"
BASE_TABLE   = "base_evenimente_stiintifice"
ECHIPA_TABLE = "com_echipe_proiect"

TAB_LABELS       = ["📋 Date de bază", "👥 Echipă"]
SECTIUNI_SALVARE = [BASE_TABLE, ECHIPA_TABLE]

COL_LABELS = {
    "denumire_categorie":      "CATEGORIE",
    "natura_eveniment":        "NATURA EVENIMENTULUI STIINTIFIC",
    "cod_identificare":        "COD EVENIMENT",
    "titlul_eveniment":        "TITLUL EVENIMENTULUI",
    "data_inceput":            "DATA DE INCEPUT",
    "data_sfarsit":            "DATA DE SFARSIT",
    "format_eveniment":        "FORMATUL EVENIMENTULUI",
    "loc_desfasurare":         "LOCUL DE DESFASURARE",
    "institutii_organizatoare":"INSTITUTIILE ORGANIZATOARE",
    "clasificare_eveniment":   "CLASIFICAREA EVENIMENTULUI",
    "website":                 "WEBSITEA WEBSITEULUI",
    "observatii":              "OBSERVATII",
    "nume_prenume":            "NUME SI PRENUME",
    "rol":                     "ROLUL IN CONTRACT",
    "persoana_contact":        "PERSOANA DE CONTACT",
    "departament":             "DEPARTAMENT",
    "email":                   "EMAIL",
    "telefon":                 "TELEFON",
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
    "denumire_categorie", "natura_eveniment", "cod_identificare",
    "titlul_eveniment", "data_inceput", "data_sfarsit",
    "format_eveniment", "loc_desfasurare", "institutii_organizatoare",
    "clasificare_eveniment", "website", "observatii",
]
COL_ORDER_ECHIPA = [
    "cod_identificare", "nume_prenume", "rol",
    "persoana_contact", "departament", "email", "telefon",
]
