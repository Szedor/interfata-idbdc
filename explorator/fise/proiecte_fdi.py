# =========================================================
# explorator/fise/proiecte_fdi.py
# VERSIUNE: 1.0
# STATUS: STABIL - Fațadă Explorator pentru Proiecte FDI
# DATA: 2026.05.04
# =========================================================
# CONȚINUT:
#   Fațadă minimală pentru Calea1 (Explorator) — afișează
#   fișa completă a unui proiect FDI prin orchestratorul
#   comun (fisa_completa_orchestrator), care suportă deja
#   toate cele 4 secțiuni inclusiv "Tehnic" (com_aspecte_tehnice).
#
# MODIFICĂRI VERSIUNEA 1.0:
#   - Creare inițială. Pattern identic cu contracte_cep.py
#     din explorator/fise/.
# =========================================================

from utils.fisa_completa_orchestrator import render_fisa_completa


def run(supabase, cod, tabela_gasita, eticheta):
    """
    Afișează fișa completă pentru un proiect FDI.
    Parametri:
        supabase     : clientul Supabase
        cod          : codul identificator al proiectului
        tabela_gasita: numele tabelei de bază (ex: "base_contracte_cep")
        eticheta     : eticheta vizuală a tipului (ex: "FDI")
    """
    render_fisa_completa(supabase, cod, tabela_gasita, eticheta)
