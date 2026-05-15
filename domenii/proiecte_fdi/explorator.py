# =========================================================
# IDBDC/domenii/proiecte_fdi/explorator.py
# VERSIUNE: 1.0
# STATUS: NOU - fațadă Explorator pentru Proiecte FDI
# DATA: 2026.05.09
# =========================================================

from utils.fisa_completa_orchestrator import render_fisa_completa


def run(supabase, cod, tabela_gasita, eticheta):
    render_fisa_completa(supabase, cod, tabela_gasita, eticheta)
