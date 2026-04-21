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
        from tab1_fisa_completa import render_fisa_completa as run_fisa
    run_fisa(supabase, cod)
