# =========================================================
# explorator/fise/proiecte_interreg.py
# VERSIUNE: 1.0
# STATUS: STABIL - Fațadă Explorator pentru Proiecte INTERREG
# DATA: 2026.05.05
# =========================================================
# CONȚINUT:
#   Fațadă pentru Calea1 (Explorator) — apelează
#   orchestratorul pentru afișarea fișei complete a unui
#   proiect INTERREG.
#
# MODIFICĂRI VERSIUNEA 1.0:
#   - Creare inițială.
# =========================================================

from utils.fisa_completa_orchestrator import render_fisa_completa


def run(supabase, cod, tabela_gasita, eticheta):
    render_fisa_completa(supabase, cod, tabela_gasita, eticheta)
