import streamlit as st

# --- DATE REALE EXTRASE DIN TABELUL TĂU ---
# Am mapat exact coloana cod_identificare cu coloana nickname
mapping_specialisti = {
    "RESP01": "ioana",
    "RESP02": "anamaria",
    "RESP03": "adina",
    "RESP04": "andreia",
    "RESP05": "vio",
    "RESP06": "anca",
    "RESP07": "mihaela",
    "RESP08": "terezia",
    "RESP09": "cristina",
    "SZEKELY": "szekely" # Adăugat pentru testarea ta
}

# Funcție care transformă nickname-ul: prima literă Mare (ex: adina -> Adina)
def format_nickname(cod):
    nume_mic = mapping_specialisti.get(cod.upper(), "Specialist")
    return nume_mic.capitalize()

# --- BARIERA 1: PAROLA DE SITE ---
if "autentificat_site" not in st.session_state:
    st.session_state["autentificat_site"] = False

if not st.session_state["autentificat_site"]:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.subheader("Acces Restricționat")
        # Parola nouă stabilită de tine
        parola_introdusa = st.text_input("Introduceți parola de acces:", type="password")
        if st.button("Verifică Parola", use_container_width=True):
            if parola_introdusa == "EverDream2SZ":
                st.session_state["autentificat_site"] = True
                st.rerun()
            elif parola_introdusa != "":
                st.error("Parolă incorectă!")
    st.stop()

# --- BARIERA 2: MENIU SPECIALIST ---
st.sidebar.title("Meniu Specialist")
cod_identificare = st.sidebar.text_input("Introduceți Cod Identificare Responsabil")

if not cod_identificare:
    st.sidebar.write("Așteptare cod responsabil...")
else:
    cod_up = cod_identificare.upper()
    if cod_up in mapping_specialisti:
        # Aici se produce transformarea în majusculă cerută de tine
        nume_formatat = format_nickname(cod_up)
        
        st.sidebar.success(f"Autorizat: {nume_formatat}")
        
        # MESAJUL DE BINE VENIT PERSONALIZAT
        st.markdown(f"### 🤝 Bine ai venit, **{nume_formatat}**!")
        st.write(f"Ai fost logat cu succes ca Responsabil: `{cod_up}`")
    else:
        st.sidebar.error(f"Codul {cod_up} nu a fost găsit în baza de date!")
