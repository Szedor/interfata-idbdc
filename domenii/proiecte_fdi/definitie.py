# =========================================================
# IDBDC/domenii/proiecte_fdi/definitie.py
# v.modul.1.0 - Definiție Proiecte FDI
# =========================================================

TIP_LABEL = "FDI"
BASE_TABLE = "base_proiecte_fdi"
FIN_TABLE = "com_date_financiare"
ECHIPA_TABLE = "com_echipe_proiect"
TEHNIC_TABLE = "com_aspecte_tehnice"

TAB_LABELS_ADMIN = ["📋 Date de bază", "💰 Date financiare", "👥 Echipă", "🧪 Aspecte tehnice"]
TAB_LABELS_EXPLORATOR = ["Generale", "Financiar", "Echipa", "Tehnic"]

SECTIUNI_SALVARE = [BASE_TABLE, FIN_TABLE, ECHIPA_TABLE, TEHNIC_TABLE]

FIELDS_BAZA = {
    "categorie": "CATEGORIE",
    "tip": "TIPUL DE PROIECT",
    "cod": "COD PROIECT",
    "titlu": "TITLUL PROIECTULUI",
    "acronim": "ACRONIMUL PROIECTULUI",
    "data_inceput": "DATA DE INCEPUT",
    "data_sfarsit": "DATA DE SFARSIT",
    "durata": "DURATA",
    "status": "STATUS PROIECT",
    "program": "PROGRAM DE FINANTARE",
    "domeniu": "DOMENIU",
    "cod_depunere": "COD DEPUNERE",
    "observatii": "OBSERVAȚII",
}
