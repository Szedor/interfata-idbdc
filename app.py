import streamlit as st

# --- LOGICA DE MAPPING (Cod -> Nickname) ---
# Aici am adăugat și corecția pentru litere mici
mapping_specialisti = {
    "SZEKELY": "szekely", 
    "RESP01": "adina",
    "RESP02": "bogdan",
    "RESP03": "adina", # Exemplul tău
    "RESP09": "cristi"
}

# Funcție pentru a obține nickname-ul corectat (Prima literă mare)
def get_friendly_name(cod):
    name = mapping_specialisti.get(cod.upper(), "Specialist")
    return name.capitalize()

# --- MODIFICARE ÎN SCRIPTUL EXISTENT ---

# ... (după bariera 1 de parolă) ...

st.sidebar.title("Meniu Specialist")
cod_identificare = st.sidebar.text_input("Introduceți Cod Identificare Responsabil")

if not cod_identificare:
    st.sidebar.write("Așteptare cod responsabil...")
else:
    cod_up = cod_identificare.upper()
    if cod_up in mapping_specialisti:
        # Preluăm nickname-ul și îl transformăm din "adina" în "Adina"
        nume_prietenos = get_friendly_name(cod_up)
        
        st.sidebar.success(f"Autorizat: {nume_prietenos}")
        
        # MESAJUL DE BINE VENIT ACTUALIZAT
        st.markdown(f"### 🤝 Bine ai venit, **{nume_prietenos}**!")
        st.write(f"Sistemul IDBDC a încărcat porția de date pentru codul: `{cod_up}`")
        
        # Aici continuă restul funcțiilor CRUD...
    else:
        st.sidebar.error("Cod Neautorizat!")
