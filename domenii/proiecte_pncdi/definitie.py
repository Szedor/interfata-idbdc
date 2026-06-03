# =========================================================
# IDBDC/domenii/proiecte_pncdi/definitie.py
# VERSIUNE: 1.0 | DATA: 2026.06.02
# =========================================================

TIP_LABEL    = "PNCDI"
CAT_LABEL    = "Proiecte"

BASE_TABLE   = "base_proiecte_pncdi"
FIN_TABLE    = "com_date_financiare_pn"   # tabelă dedicată PNCDI
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

# Flag special — indică motorului că FIN_TABLE folosește cheia compusă
# (cod_identificare + an_referinta) și NU trebuie șters an_referinta la salvare
FIN_TABLE_MULTI_ROW = True
