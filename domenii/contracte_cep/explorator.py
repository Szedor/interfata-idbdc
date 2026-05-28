# =========================================================
# IDBDC/domenii/contracte_cep/explorator.py
# v.modul.1.0 - Fațadă Explorator pentru Contracte CEP
# =========================================================

from domenii._baza.sectiune_tehnic import render as _baza_render_tehnic


def run(supabase, cod, tabela_gasita, eticheta):
    """
    Afișează fișa completă pentru un contract CEP.
    Pentru contracte, secțiunea Tehnic nu se afișează.
    """
    # Importul orchestratorului trebuie făcut aici pentru a evita import circular
    from utils.fisa_completa_orchestrator import render_fisa_completa
    
    render_fisa_completa(supabase, cod, tabela_gasita, eticheta)
