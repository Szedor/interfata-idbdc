# =========================================================
# IDBDC/domenii/proiecte_see/explorator.py
# VERSIUNE: 1.1
# STATUS: ACTUALIZAT
# DATA: 2026.05.23
# =========================================================

from utils.fisa_completa_orchestrator import render_fisa_completa

def run(supabase, cod, tabela_gasita, eticheta):
    render_fisa_completa(supabase, cod, tabela_gasita, eticheta)
