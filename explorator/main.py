# în explorator/main.py, în funcția care gestionează Tab1 (fișa completă)
if cod_found:
    if tabela_gasita == "base_contracte_cep":
        from explorator.fise.contracte_cep import run as run_fisa
    elif tabela_gasita == "base_contracte_terti":
        from explorator.fise.contracte_terti import run as run_fisa
    elif tabela_gasita == "base_contracte_speciale":
        from explorator.fise.contracte_speciale import run as run_fisa
    else:
        # fallback la vechea funcție (sau eroare)
        from utils.fisa_completa_orchestrator import render_fisa_completa as run_fisa

# Determinăm tabela_gasita (dacă nu există deja, trebuie calculată)
# De obicei, în calea1_explorator.py există deja o variabilă `tabela_gasita`
# setată după căutarea codului în ALL_BASE_TABLES. Dacă nu, o calculați similar.

# Determinăm titlul etichetei vizuale (ex: "CEP", "TERȚI", "SPECIALE")
# Se poate extrage din TABLE_LABELS (importat din utils.display_config)
from utils.display_config import TABLE_LABELS
eticheta = TABLE_LABELS.get(tabela_gasita, "").split(" ", 1)[-1]  # elimină emoji-ul

run_fisa(supabase, cod, tabela_gasita, eticheta)
