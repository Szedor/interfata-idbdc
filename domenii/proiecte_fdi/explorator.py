# =========================================================
# IDBDC/domenii/proiecte_fdi/explorator.py
# VERSIUNE: 1.0
# STATUS: NOU — Fațadă Explorator Proiecte FDI
# DATA: 2026.05.31
# =========================================================
# CONȚINUT:
#   Fațadă pentru Calea1 (Explorator).
#   Apelează orchestratorul generic care afișează toate
#   secțiunile bifate (Generale, Financiar, Echipa, Tehnic).
# =========================================================

from utils.fisa_completa_orchestrator import render_fisa_completa


def run(supabase, cod, tabela_gasita, eticheta):
    render_fisa_completa(supabase, cod, tabela_gasita, eticheta)
