import streamlit as st
import psycopg2
import pandas as pd

# 1. Configurare Pagină
st.set_page_config(page_title="Consola Responsabili IDBDC", layout="wide")

# 2. Inițializare Sesiune (Starea de autentificare)
if "autentificat" not in st.session_state:
    st.session_state.autentificat = False

# 3. Funcție Conexiune (Placeholder până la datele reale)
def connect_db():
    try:
        return psycopg2.connect(
            host="localhost", 
            database="nume_db", 
            user="postgres", 
            password="parola"
        )
    except Exception as e:
        return None

# --- LOGICA DE ACCES ---
if not st.session_state.autentificat:
    st.title("🛡️ Consola Responsabili IDBDC")
    st.subheader("Acces Restricționat")
    
    # Folosim o metodă directă, fără formulare complexe care pot da erori
    parola_introdusa = st.text_input("Introduceți parola de acces:", type="password")
    if st.button("Validare"):
        if parola_introdusa == "UPT_CERCETARE_2026":
            st.session_state.autentificat = True
            st.rerun()
        else:
            st.error("Parolă incorectă! Verificați CAPS LOCK sau spațiile goale.")

else:
    # --- INTERFAȚA IDBDC ---
    st.sidebar.header("Meniu Specialist")
    responsabili_autorizati = ["ID001", "ID002", "ID003", "ID004", "ID005", "ID006", "ID007", "ID008", "ID009"]
    
    user_id = st.sidebar.text_input("Cod Identificare Responsabil:")
    
    if user_id in responsabili_autorizati:
        st.title(f"🛡️ Consola Responsabili IDBDC - {user_id}")
        st.sidebar.success(f"Autorizat: {user_id}")
        
        baza_selectata = st.sidebar.selectbox("Sursă Date:", ["base_proiecte_fdi", "base_proiecte_pnrr", "altele"])
        
        st.header(f"📂 Lucrați în: {baza_selectata}")
        
        # Test Conexiune
        conn = connect_db()
        if conn:
            st.success("Baza de date este conectată.")
            conn.close()
        else:
            st.warning("Verificați setările serverului (Host/Port).")
            
    elif user_id != "":
        st.sidebar.error("Cod neautorizat!")

    if st.sidebar.button("Logout"):
        st.session_state.autentificat = False
        st.rerun()
