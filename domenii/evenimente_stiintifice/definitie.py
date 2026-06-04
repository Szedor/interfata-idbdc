# =========================================================
# IDBDC/domenii/evenimente_stiintifice/definitie.py
# VERSIUNE: 1.0 | DATA: 2026.06.02
# =========================================================

TIP_LABEL    = "STIINTIFICE"
CAT_LABEL    = "Evenimente"

BASE_TABLE   = "base_evenimente_stiintifice"
FIN_TABLE    = None
ECHIPA_TABLE = "com_echipe_proiect"
TEHNIC_TABLE = None

TAB_LABELS_ADMIN = [
    "📋 Date de bază",
    "👥 Echipă",
]

TAB_LABELS_EXPLORATOR = ["Generale", "Echipa"]

SECTIUNI_SALVARE = [BASE_TABLE, ECHIPA_TABLE]
