# =========================================================
# IDBDC/domenii/contracte_cep/definitie.py
# VERSIUNE: 1.1
# STATUS: ACTUALIZAT - mapare completă coloane SQL → etichete vizuale
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Toate constantele specifice domeniului Contracte CEP:
#   tabele SQL, etichete vizuale, ordine câmpuri, câmpuri
#   ascunse, câmpuri compuse. Folosită identic în Calea1
#   (Explorator) și Calea2 (Administrare).
#
# REGULI PERMANENTE:
#   - nr_crt: generat de sistem, niciodată afișat
#   - creat_de, creat_la, modificat_de, modificat_la:
#     niciodată afișate în Calea1; vizibile în Calea2
#     exclusiv pentru operatorii cu rol ADMIN
#   - DEPARTAMENT = acronim_departament + denumire_departament
#   - TELEFON = telefon_mobil + telefon_fix
#   - cod_identificare → NR.CONTRACT în toate cele 4 secțiuni
# =========================================================

CATEGORIE  = "Contracte"
TIP_LABEL  = "CEP"
TIP_SEL    = "CEP"

BASE_TABLE   = "base_contracte_cep"
FIN_TABLE    = "com_date_financiare"
ECHIPA_TABLE = "com_echipe_proiect"

TAB_LABELS = ["📋 Date de bază", "💰 Date financiare", "👥 Echipă"]

SECTIUNI_SALVARE = [BASE_TABLE, FIN_TABLE, ECHIPA_TABLE]

# ── Mapare coloană SQL → etichetă vizuală ─────────────────────────────
COL_LABELS = {
    # GENERALE / DATE DE BAZĂ
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
    "observatii":                          "OBSERVAȚII",
    # FINANCIAR
    "valuta":                              "VALUTĂ",
    "valoare_contract_cep_terti_speciale": "VALOARE CONTRACT",
    # ECHIPĂ
    "nume_prenume":                        "NUME ȘI PRENUME",
    "rol":                                 "ROLUL ÎN CONTRACT",
    "persoana_contact":                    "PERSOANĂ DE CONTACT",
    "departament":                         "DEPARTAMENT",
    "email":                               "EMAIL",
    "telefon":                             "TELEFON",
}

# ── Câmpuri niciodată afișate (Calea1 și Calea2) ──────────────────────
COLS_HIDDEN = {
    "nr_crt",
    "creat_de", "creat_la", "modificat_de", "modificat_la",
    "acronim_departament", "denumire_departament",
    "telefon_mobil", "telefon_fix",
}

# ── Câmpuri compuse (construite din mai multe coloane SQL) ─────────────
# Cheia = numele câmpului virtual; valoarea = lista coloanelor sursă
COLS_COMPUSE = {
    "departament": ["acronim_departament", "denumire_departament"],
    "telefon":     ["telefon_mobil", "telefon_fix"],
}

# ── Ordinea câmpurilor în Calea1 secțiunea Generale ───────────────────
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
]

# ── Ordinea câmpurilor în Calea1 secțiunea Financiar ──────────────────
COL_ORDER_FINANCIAR = [
    "cod_identificare",
    "valuta",
    "valoare_contract_cep_terti_speciale",
]

# ── Ordinea câmpurilor în Calea1 secțiunea Echipă ─────────────────────
COL_ORDER_ECHIPA = [
    "cod_identificare",
    "nume_prenume",
    "rol",
    "persoana_contact",
    "departament",
    "email",
    "telefon",
]
