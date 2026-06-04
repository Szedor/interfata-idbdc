# =========================================================
# IDBDC/domenii/contracte_terti/definitie.py
# VERSIUNE: 2.0 | DATA: 2026.06.02
# =========================================================

TIP_LABEL    = "TERTI"
CAT_LABEL    = "Contracte"

BASE_TABLE   = "base_contracte_terti"
FIN_TABLE    = "com_date_financiare"
ECHIPA_TABLE = "com_echipe_proiect"
TEHNIC_TABLE = None

TAB_LABELS_ADMIN = [
    "📋 Date de bază",
    "💰 Date financiare",
    "👥 Echipă",
]

TAB_LABELS_EXPLORATOR = ["Generale", "Financiar", "Echipa"]

SECTIUNI_SALVARE = [BASE_TABLE, FIN_TABLE, ECHIPA_TABLE]
