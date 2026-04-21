# =========================================================
# explorator/fise/contracte_cep.py
# v.modul.1.0 - Fațadă pentru afișarea fișei complete CEP
# =========================================================

from utils.contracte_display_common import render_fisa_completa

def run(supabase, cod):
    render_fisa_completa(supabase, cod, "base_contracte_cep", "CEP")
