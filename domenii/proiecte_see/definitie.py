# =========================================================
# IDBDC/domenii/proiecte_see/definitie.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.06.02
# =========================================================

TIP_LABEL  = "SEE"
CAT_LABEL  = "Proiecte"

BASE_TABLE   = "base_proiecte_see"
FIN_TABLE    = "com_date_financiare"
ECHIPA_TABLE = "com_echipe_proiect"
TEHNIC_TABLE = "com_aspecte_tehnice"

TAB_LABELS_ADMIN = [
    "📋 Date de bază",
    "💰 Date financiare",
    "👥 Echipă",
    "🧪 Aspecte tehnice",
]

TAB_LABELS_EXPLORATOR = ["Generale", "Financiar", "Echipa", "Tehnic"]

SECTIUNI_SALVARE = [BASE_TABLE, FIN_TABLE, ECHIPA_TABLE, TEHNIC_TABLE]
