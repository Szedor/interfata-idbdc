# =========================================================
# IDBDC/domenii/proiecte_internationale/definitie.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.06.01
# =========================================================

TIP_LABEL  = "INTERNATIONALE"
CAT_LABEL  = "Proiecte"

BASE_TABLE   = "base_proiecte_internationale"
FIN_TABLE    = "com_date_financiare"
ECHIPA_TABLE = "com_echipe_proiect"
TEHNIC_TABLE = "com_aspecte_tehnice"

# ── Tab-uri vizibile în Calea2 (Administrare) ──────────────────────────
TAB_LABELS_ADMIN = [
    "📋 Date de bază",
    "💰 Date financiare",
    "👥 Echipă",
    "🧪 Aspecte tehnice",
]

# ── Tab-uri vizibile în Calea1 (Explorator) ───────────────────────────
TAB_LABELS_EXPLORATOR = ["Generale", "Financiar", "Echipa", "Tehnic"]

# ── Tabele implicate în ștergere completă ─────────────────────────────
SECTIUNI_SALVARE = [BASE_TABLE, FIN_TABLE, ECHIPA_TABLE, TEHNIC_TABLE]
