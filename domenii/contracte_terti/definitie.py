# =========================================================
# IDBDC/domenii/contracte_terti/definitie.py
# v.modul.1.1 - Versiune completă (cu toate câmpurile)
# =========================================================

TIP_LABEL = "TERTI"
BASE_TABLE = "base_contracte_terti"
FIN_TABLE = "com_date_financiare"
ECHIPA_TABLE = "com_echipe_proiect"
TEHNIC_TABLE = None

TAB_LABELS_ADMIN = ["📋 Date de bază", "💰 Date financiare", "👥 Echipă"]
TAB_LABELS_EXPLORATOR = ["Generale", "Financiar", "Echipa"]

SECTIUNI_SALVARE = [BASE_TABLE, FIN_TABLE, ECHIPA_TABLE]

FIELDS_BAZA = {
    "categorie": "CATEGORIE",
    "tip": "TIPUL DE CONTRACT",
    "cod": "NR.CONTRACT",
    "data_contract": "DATA CONTRACTULUI",
    "obiect": "OBIECTUL CONTRACTULUI",
    "beneficiar": "BENEFICIAR",
    "data_inceput": "DATA DE INCEPUT",
    "data_sfarsit": "DATA DE SFARSIT",
    "durata": "DURATA",
    "status": "STATUS CONTRACT",
    "derulat_prin": "DERULAT PRIN",
    "observatii": "OBSERVAȚII",
}

# Pentru consistență (deși nu sunt folosite direct de baza.py)
COL_LABELS = {
    "denumire_categorie": "CATEGORIE",
    "acronim_tip_contract": "TIPUL DE CONTRACT",
    "cod_identificare": "NR.CONTRACT",
    "data_contract": "DATA CONTRACTULUI",
    "obiectul_contractului": "OBIECTUL CONTRACTULUI",
    "denumire_beneficiar": "BENEFICIAR",
    "data_inceput": "DATA DE INCEPUT",
    "data_sfarsit": "DATA DE SFARSIT",
    "durata": "DURATA",
    "status_contract_proiect": "STATUS CONTRACT",
    "derulat_prin": "DERULAT PRIN",
    "observatii": "OBSERVAȚII",
    "valuta": "VALUTA",
    "valoare_contract": "VALOARE CONTRACT",
    "nume_prenume": "NUME SI PRENUME",
    "rol": "ROLUL IN CONTRACT",
    "persoana_contact": "PERSOANA DE CONTACT",
}

COLS_HIDDEN = {
    "nr_crt", "creat_de", "creat_la", "modificat_de", "modificat_la",
    "acronim_departament", "denumire_departament", "telefon_mobil", "telefon_fix",
}

COLS_COMPUSE = {
    "departament": ["acronim_departament", "denumire_departament"],
    "telefon": ["telefon_mobil", "telefon_fix"],
}
