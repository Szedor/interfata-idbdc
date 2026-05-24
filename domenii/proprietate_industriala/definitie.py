# =========================================================
# IDBDC/domenii/proprietate_industriala/definitie.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.05.23
# =========================================================
# STRUCTURA SPECIALA:
#   - Fara sectiune financiara si fara aspecte tehnice
#   - Date de baza impartite in doua subsectiuni (acelasi tabel):
#       * GENERALE   — vizibile in Calea1 si Calea2
#       * SUPLIMENTARE — vizibile NUMAI in Calea2 (admin)
#   - 3 taburi in Calea2: Date de baza | Date suplimentare | Echipa
#   - 2 taburi in Calea1: Date de baza | Echipa
# =========================================================

CATEGORIE    = "Proprietate Industrială"
TIP_LABEL    = "PROPRIETATE INDUSTRIALĂ"
BASE_TABLE   = "base_prop_industr"
ECHIPA_TABLE = "com_echipe_proiect"

# Taburi Calea2 (Admin)
TAB_LABELS_ADMIN     = ["📋 Date de bază", "🔒 Date suplimentare", "👥 Echipă"]
# Taburi Calea1 (Explorator)
TAB_LABELS_EXPLORATOR = ["📋 Date de bază", "👥 Echipă"]

SECTIUNI_SALVARE = [BASE_TABLE, ECHIPA_TABLE]

COL_LABELS = {
    "denumire_categorie":      "CATEGORIE",
    "acronim_prop_industr":    "ACRONIM TIP PROPRIETATE",
    "denumire_prop_industr":   "DENUMIRE PROPRIETATE INDUSTRIALA",
    "titlul_proprietatii":     "TITLUL PROPRIETATII",
    "cod_identificare":        "NR.INREGISTRARE CERERE",
    "data_depozit_cerere":     "DATA DEPOZIT CERERE",
    "numar_publicare_cerere":  "NR.PUBLICARE CERERE",
    "numar_oficial_acordare":  "NR.OFICIAL DE ACORDARE",
    "data_oficiala_de_acordare": "DATA OFICIALA DE ACORDARE",
    "data_inceput_valabilitate": "DATA DE INCEPUT VALABILITATE",
    "ani_de_valabilitate":     "DURATA DE VALABILITATE (ani)",
    "data_sfarsit_valabilitate": "DATA DE SFARSIT VALABILITATE",
    "id_proiect_contract_sursa": "ID PROIECT SURSA/CONTRACT",
    "denumire_solicitant":     "DENUMIRE SOLICITANT",
    "denumire_titular":        "DENUMIRE TITULAR",
    "link_espacenet":          "LINK ESPACENET",
    "titlu_engleza_diploma":   "TITLU ENGLEZA DIPLOMA",
    # Suplimentare
    "numar_data_notificare_intern":       "NR.SI DATA DE NOTIFICARE INTERNA",
    "document_oficial_original":          "DOCUMENT OFICIAL ORIGINAL",
    "status_document":                    "STATUS DOCUMENT",
    "spin_off":                           "SPIN OFF",
    "comentarii_document":                "COMENTARII DOCUMENT",
    "comentarii_diverse":                 "COMENTARII DIVERSE",
    "numar_autori_total":                 "NUMAR AUTORI TOTAL",
    "numar_autori_upt":                   "NUMAR AUTORI UPT",
    "domeniu_aplicare":                   "DOMENIU APLICARE",
    "contract_cesiune_inventatori_externi": "CONTRACT CESIUNE INVENTATORI EXTERNI",
    "titlu_engleza_epo":                  "TITLU ENGLEZA EPO",
    "titlu_engleza_fisa_inventiei":       "TITLU ENGLEZA FISA INVENTIEI",
    # Echipa
    "nume_prenume":     "NUME SI PRENUME",
    "rol":              "ROLUL IN CONTRACT",
    "persoana_contact": "PERSOANA DE CONTACT",
    "departament":      "DEPARTAMENT",
    "email":            "EMAIL",
    "telefon":          "TELEFON",
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
    "denumire_categorie", "acronim_prop_industr", "denumire_prop_industr",
    "titlul_proprietatii", "cod_identificare", "data_depozit_cerere",
    "numar_publicare_cerere", "numar_oficial_acordare", "data_oficiala_de_acordare",
    "data_inceput_valabilitate", "ani_de_valabilitate", "data_sfarsit_valabilitate",
    "id_proiect_contract_sursa", "denumire_solicitant", "denumire_titular",
    "link_espacenet", "titlu_engleza_diploma",
]
COL_ORDER_SUPLIMENTARE = [
    "cod_identificare",
    "numar_data_notificare_intern", "document_oficial_original", "status_document",
    "spin_off", "comentarii_document", "comentarii_diverse",
    "numar_autori_total", "numar_autori_upt", "domeniu_aplicare",
    "contract_cesiune_inventatori_externi", "titlu_engleza_epo",
    "titlu_engleza_fisa_inventiei",
]
COL_ORDER_ECHIPA = [
    "cod_identificare", "nume_prenume", "rol",
    "persoana_contact", "departament", "email", "telefon",
]
