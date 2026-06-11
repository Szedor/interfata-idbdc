# =========================================================
# IDBDC/domenii/resurse_umane/definitie.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.06.11
# =========================================================

TIP_LABEL    = "RESURSE UMANE"
CAT_LABEL    = "Resurse umane"

BASE_TABLE   = "det_resurse_umane"
FIN_TABLE    = None
ECHIPA_TABLE = None
TEHNIC_TABLE = None

# ── Tab-uri vizibile în Calea2 (Administrare) ──────────────────────────
TAB_LABELS_ADMIN = [
    "📋 Date persoană",
]

# ── Calea1 (Explorator) — exclus total ────────────────────────────────
TAB_LABELS_EXPLORATOR = []

# ── Tabele implicate în ștergere completă ─────────────────────────────
SECTIUNI_SALVARE = [BASE_TABLE]
