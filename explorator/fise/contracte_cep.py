# =========================================================
# explorator/fise/contracte_cep.py
# v.modul.1.0 - Fațadă pentru afișarea fișei complete CEP
# =========================================================

from utils.fisa_completa_orchestrator import render_fisa_completa

def run(supabase, cod, tabela_gasita, eticheta):
    """
    Afișează fișa completă pentru un contract CEP.
    Parametri:
        supabase: clientul Supabase
        cod: codul identificator
        tabela_gasita: numele tabelei (ex: "base_contracte_cep")
        eticheta: eticheta vizuală (ex: "CEP")
    """
    render_fisa_completa(supabase, cod, tabela_gasita, eticheta)
