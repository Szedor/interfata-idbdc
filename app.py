import streamlit as st
import psycopg2
import pandas as pd

# --- CONFIGURARE BAZĂ DE DATE (IDBDC) ---
def connect_db():
    try:
        return psycopg2.connect(
            host="localhost",      # Schimbă cu host-ul identificat de tine
            database="nume_db",    # Numele bazei de date
            user="postgres",       # Utilizatorul
            password="parola"      # Parola
        )
    except Exception as e:
        st.error(f"Eroare de conexiune: {e}")
        return None

# 1. Identitatea Vizuală
st.set_page_config(page_title="Consola Responsabili IDBDC", layout="wide")
st.title("🛡️ Consola Responsabili IDBDC")

# Inițializarea stării sesiunii
if "autentificat" not in st.session_state:
    st.session_state["autentificat"] = False

# --- PASUL 1: BARIERA DE PAROLĂ ---
if not st.session_state["autentificat"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Acces Restricționat")
        # Folosim un formular pentru a asigura procesarea corectă la Enter sau Click
        with st.form("form_autentificare"):
            parola_introdusa = st.text_input("Introduceți parola de acces:", type="password")
            buton_validare = st.form_submit_button("Validare")
            
            if buton_validare:
                if parola_introdusa == "UPT_CERCETARE_2026":
                    st.session_state["autentificat"] = True
                    st.rerun()
                else:
                    st.error("Parolă incorectă!")
else:
    # --- PASUL 2: INTERFAȚA DUPĂ AUTENTIFICARE ---
    st.sidebar.image("https://www.research.upt.ro/img/logo.png", width=150)
    st.sidebar.header("Meniu Specialist")
    
    responsabili_autorizati = ["ID001", "ID002", "ID003", "ID004", "ID005", "ID006", "ID007", "ID008", "ID009"]
    user_id = st.sidebar.text_input("Introduceți Cod Identificare Responsabil:")
    
    if user_id in responsabili_autorizati:
        st.sidebar.success(f"Autorizat: Responsabil {user_id}")
        
        st.markdown("---")
        categorie = st.sidebar.selectbox("1. Categorie:", ["Contracte & Proiecte", "Proprietate Intelectuală", "Evenimente"])
        
        if categorie == "Contracte & Proiecte":
            baza_selectata = st.sidebar.selectbox("2. Sursă Date (Cele 8 baze):", [
                "base_proiecte_internationale", 
                "base_proiecte_fdi", 
                "base_proiecte_pnrr",
                "base_proiecte_pncdi",
                "base_contracte_terti",
                "base_proiecte_interreg",
                "base_proiecte_noneu",
                "base_contracte_cep"
            ])
            
            st.header(f"📂 Lucrați în: {baza_selectata}")
            
            conn = connect_db()
            if conn:
                try:
                    query = f'SELECT * FROM "{baza_selectata}"' # Am pus ghilimele pentru siguranța numelui tabelului
                    df = pd.read_sql(query, conn)
                    st.dataframe(df)
                    st.success(f"Date încărcate: {len(df)} rânduri găsite.")
                    conn.close()
                except Exception as e:
                    st.error(f"Eroare la citirea datelor: {e}")
            else:
                st.info("Conexiunea la baza de date nu este configurată.")

    elif user_id == "":
        st.sidebar.warning("Așteptare cod responsabil...")
    else:
        st.sidebar.error("Cod neautorizat!")

    # Buton de Logout
    if st.sidebar.button("Ieșire (Logout)"):
        st.session_state["autentificat"] = False
        st.rerun()
