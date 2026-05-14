# =========================================================
# IDBDC/domenii/contracte_terti/explorator.py
# VERSIUNE: 1.0
# STATUS: NOU - fațadă Explorator pentru Contracte TERȚI
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Fațadă pentru Calea1 (Explorator) — apelează
#   orchestratorul pentru afișarea fișei complete a unui
#   contract TERȚI.
# =========================================================

from utils.fisa_completa_orchestrator import render_fisa_completa


def run(supabase, cod, tabela_gasita, eticheta):
    render_fisa_completa(supabase, cod, tabela_gasita, eticheta)
