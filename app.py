import streamlit as st

# --- LISTA DEFINITIVĂ (Extrasă din tabel_responsabili.csv) ---
mapping_specialisti = {
    "RESP01": "ioana",
    "RESP02": "anamaria",
    "RESP03": "adina",
    "RESP04": "andreia",
    "RESP05": "vio",
    "RESP06": "anca",
    "RESP07": "claudia",
    "RESP08": "agi",
    "RESP09": "eugen"
}

# Funcția care transformă nickname-ul: prima literă Mare (ex: agi -> Agi)
def get_friendly_name(cod):
    nume_raw = mapping_specialisti.get(cod.upper(), "Specialist")
    return nume_raw.capitalize()

# --- BARIERA 1: PAROLA DE SITE ---
if "autentificat_site" not in st.session_state:
    st.session_state["autentificat_site"] = False

if not st.session_state["autentificat_site"]:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.subheader("Acces Restricționat")
        parola_introdusa = st.text_input("Introduceți parola de acces:", type="password")
        if st.button("Verifică Parola", use_container_width=True):
            if parola_introdusa == "EverDream2SZ":
                st.session_state["autentificat_site"] = True
                st.rerun()
            elif parola_introdusa != "":
                st.error("Parolă incorectă!")
    st.stop()

# --- BARIERA 2: MENIU SPECIALIST (Sidebar) ---
st.sidebar.title("Meniu Specialist")
st.sidebar.write("---")
# Input pentru Cod Identificare
cod_input = st.sidebar.text_input("Introduceți Cod Identificare Responsabil").upper()

if not cod_input:
    st.sidebar.write("Așteptare cod responsabil...")
else:
    if cod_input in mapping_specialisti:
        # Preluăm nickname-ul formatat cu Majusculă
        nume_afisat = get_friendly_name(cod_input)
        
        st.sidebar.success(f"Autorizat: {nume_afisat}")
        
        # MESAJUL DE BINE VENIT SOLICITAT
        st.markdown(f"### 🤝 Bine ai venit, **{nume_afisat}**!")
        st.info(f"Profil activat pentru: {cod_input}")
        
        # De aici se activează secțiunea CRUD
    else:
        st.sidebar.error("Codul introdus nu este autorizat!")
