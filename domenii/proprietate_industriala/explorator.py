# =========================================================
# IDBDC/domenii/proprietate_industriala/explorator.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.05.23
# =========================================================
# ATENTIE:
#   Calea1 afiseaza NUMAI datele generale si echipa.
#   Datele suplimentare (base_prop_industr - sectiunea a doua)
#   NU sunt afisate in Calea1.
# =========================================================

from utils.fisa_completa_orchestrator import render_fisa_completa

def run(supabase, cod, tabela_gasita, eticheta):
    render_fisa_completa(supabase, cod, tabela_gasita, eticheta)
