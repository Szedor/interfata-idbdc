# =========================================================
# explorator/fise/proiecte_pncdi.py
# VERSIUNE: 1.0
# STATUS: STABIL - Fațadă Explorator pentru Proiecte PNCDI
# DATA: 2026.05.05
# =========================================================
# CONȚINUT:
#   Fațadă pentru Calea1 (Explorator) — apelează
#   orchestratorul pentru afișarea fișei complete a unui
#   proiect PNCDI.
#
# MODIFICĂRI VERSIUNEA 1.0:
#   - Creare inițială.
# =========================================================

from utils.fisa_completa_orchestrator import render_fisa_completa


def run(supabase, cod, tabela_gasita, eticheta):
    render_fisa_completa(supabase, cod, tabela_gasita, eticheta)
