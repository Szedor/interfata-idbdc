# =========================================================
# explorator/fise/contracte_speciale.py
# v.modul.1.0 - Fațadă pentru afișarea fișei complete SPECIALE
# =========================================================

from utils.contracte_display_common import render_fisa_completa

def run(supabase, cod):
    render_fisa_completa(supabase, cod, "base_contracte_speciale", "SPECIALE")
