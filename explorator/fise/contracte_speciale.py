# =========================================================
# explorator/fise/contracte_speciale.py
# v.modul.1.0 - Fațadă pentru afișarea fișei complete SPECIALE
# =========================================================

from utils.fisa_completa_orchestrator import render_fisa_completa

def run(supabase, cod, tabela_gasita, eticheta):
    render_fisa_completa(supabase, cod, tabela_gasita, eticheta)
