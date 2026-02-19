import streamlit as st

# Configurare pagină
st.set_page_config(page_title="Consola Responsabili IDBDC", layout="wide")

st.title("🛡️ Consola Responsabili IDBDC")

# --- BARIERA 1: PAROLA DE SITE (Centrată și Scurtă) ---
if "autentificat_site" not in st.session_state:
    st.session_state["autentificat_site"] = False

if not st.session_state["autentificat_site"]:
    # Creăm 3 coloane: una mică în stânga, una medie la mijloc, una mică în dreapta
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2: # Lucrăm doar în coloana din mijloc
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

# Câmpul de intrare
cod_identificare = st.sidebar.text_input("Introduceți Cod Identificare Responsabil")

# LISTA ACTUALIZATĂ A CELOR 9 (Am adăugat RESP09)
lista_specialisti = ["SZEKELY", "RESP01", "RESP02", "RESP03", "RESP04", "RESP05", "RESP06", "RESP07", "RESP08", "RESP09"]

if not cod_identificare:
    st.sidebar.write("Așteptare cod responsabil...")
    st.info("Vă rugăm să introduceți codul de identificare în sidebar pentru a activa funcțiile CRUD.")
    st.stop()
else:
    # Verificare cod (Case sensitive sau transformat în Upper)
    if cod_identificare.upper() in lista_specialisti:
        st.sidebar.success(f"Autorizat: Responsabil {cod_identificare.upper()}")
        # AICI ÎNCEPE LOGICA CRUD
        st.write(f"### Bine ați venit, Specialist {cod_identificare.upper()}!")
    else:
        st.sidebar.error(f"Codul {cod_identificare} nu este autorizat!")
        st.stop()

# --- De aici în colo urmează Filtrarea în Cascadă și Tabelul ---
st.divider()
st.write("Aici vor apărea opțiunile de filtrare pentru tabelele base_ și fișa de proiect.")
