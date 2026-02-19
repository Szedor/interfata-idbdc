import streamlit as st

# Aceasta este singura structură pe care o vom folosi
# O vom popula DOAR cu datele pe care mi le confirmi tu
mapping_real = {
    "SZEKELY": "szekely",
    "RESP03": "adina", # Doar dacă așa este în tabelul tău
    # Restul vor fi citite direct din baza de date
}

def get_clean_name(cod):
    # Luăm nickname-ul de la tine din tabel (cel cu litere mici)
    # și îl corectăm doar vizual (prima literă mare)
    nume_raw = mapping_real.get(cod.upper(), "Specialist")
    return nume_raw.capitalize()

# ... (Bariera 1 cu parola EverDream2SZ) ...

st.sidebar.title("Meniu Specialist")
cod_identificare = st.sidebar.text_input("Introduceți Cod Identificare Responsabil")

if cod_identificare:
    cod_up = cod_identificare.upper()
    
    # Verificăm dacă codul există în baza noastră
    if cod_up in mapping_real:
        nume_fain = get_clean_name(cod_up)
        
        st.sidebar.success(f"Autorizat: {nume_fain}")
        
        # MESAJUL CORECT
        st.markdown(f"### 🤝 Bine ai venit, **{nume_fain}**!")
    else:
        st.sidebar.error("Codul nu a fost găsit în baza de date IDBDC!")
