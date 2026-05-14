# =========================================================
# IDBDC/domenii/contracte_terti/definitie.py
# VERSIUNE: 1.0
# STATUS: NOU - definiție domeniu Contracte TERȚI
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Toate constantele specifice domeniului Contracte TERȚI.
#   Identic cu contracte_cep cu excepția câmpului în plus:
#   DERULAT PRIN → derulat_prin (poziționat după STATUS CONTRACT).
# =========================================================

CATEGORIE    = "Contracte"
TIP_LABEL    = "TERȚI"
TIP_SEL      = "TERȚI"

BASE_TABLE   = "base_contracte_terti"
FIN_TABLE    = "com_date_financiare"
ECHIPA_TABLE = "com_echipe_proiect"

TAB_LABELS = ["📋 Date de bază", "💰 Date financiare", "👥 Echipă"]

SECTIUNI_SALVARE = [BASE_TABLE, FIN_TABLE, ECHIPA_TABLE]

COL_LABELS = {
    "denumire_categorie":                  "CATEGORIE",
    "acronim_tip_contract":                "TIPUL DE CONTRACT",
    "cod_identificare":                    "NR.CONTRACT",
    "data_contract":                       "DATA CONTRACTULUI",
    "obiectul_contractului":               "OBIECTUL CONTRACTULUI",
    "denumire_beneficiar":                 "BENEFICIAR",
    "data_inceput":                        "DATA DE ÎNCEPUT",
    "data_sfarsit":                        "DATA DE SFÂRȘIT",
    "durata":                              "DURATA (luni)",
    "status_contract_proiect":             "STATUS CONTRACT",
    "derulat_prin":                        "DERULAT PRIN",
    "observatii":                          "OBSERVAȚII",
    "valuta":                              "VALUTĂ",
    "valoare_contract_cep_terti_speciale": "VALOARE CONTRACT",
    "nume_prenume":                        "NUME ȘI PRENUME",
    "rol":                                 "ROLUL ÎN CONTRACT",
    "persoana_contact":                    "PERSOANĂ DE CONTACT",
    "departament":                         "DEPARTAMENT",
    "email":                               "EMAIL",
    "telefon":                             "TELEFON",
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
    "acronim_tip_contract",
    "cod_identificare",
    "data_contract",
    "obiectul_contractului",
    "denumire_beneficiar",
    "data_inceput",
    "data_sfarsit",
    "durata",
    "status_contract_proiect",
    "derulat_prin",
]

COL_ORDER_FINANCIAR = [
    "cod_identificare",
    "valuta",
    "valoare_contract_cep_terti_speciale",
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
