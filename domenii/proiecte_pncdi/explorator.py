# =========================================================
# IDBDC/domenii/proiecte_pncdi/explorator.py
# VERSIUNE: 1.0 | DATA: 2026.06.02
# =========================================================

from utils.fisa_completa_orchestrator import render_fisa_completa

def run(supabase, cod, tabela_gasita, eticheta):
    render_fisa_completa(supabase, cod, tabela_gasita, eticheta)
