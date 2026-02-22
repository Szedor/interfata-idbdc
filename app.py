import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

# 1. CONFIGURARE PAGINĂ
st.set_page_config(page_title="Consola Centrală IDBDC", layout="centered")

# --- DATE CONEXIUNE ---
# Aici pui adresa ta lungă de la Neon între ghilimele
DB_URI = "postgresql://neondb_owner:npg_oRwnHk82CFUj@ep-silent-hill-ag8n1884-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    return psycopg2.connect(DB_URI, cursor_factory=RealDictCursor)

# Inițializare variabile de sesiune
if "etapa" not in st.session_state:
    st.session_state.etapa = "bariera_1"
if "date_operator" not in st.session_state:
    st.session_state.date_operator = None

# --- BARIERA 1: ACCES SISTEM ---
if st.session_state.etapa == "bariera_1":
    st.title("🛡️ Sistem IDBDC")
    parola_sistem = st.text_input("Introdu Cheia de Acces Sistem:", type="password")
    if st.button("VERIFICĂ SISTEM"):
        if parola_sistem == "EverDream2SZ":
            st.session_state.etapa = "bariera_2"
            st.rerun()
        else:
            st.error("Cheie incorectă.")

# --- BARIERA 2: LOGIN OPERATOR ---
elif st.session_state.etapa == "bariera_2":
    st.title("🔑 Identificare Responsabil")
    cod_acces = st.text_input("Introdu Codul tău de Operator (ex: IDBDC-001):", type="password")
    
    if st.button("AUTENTIFICARE"):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT nume_operator, filtru_categorie, filtru_proiect FROM com_operatori WHERE cod_acces = %s", (cod_acces,))
            user = cur.fetchone()
            
            if user:
                st.session_state.date_operator = user
                st.session_state.etapa = "consola_activa"
                st.rerun()
            else:
                st.error("Cod de operator invalid.")
            
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Eroare tehnică: {e}")

# --- CONSOLA ACTIVĂ ---
elif st.session_state.etapa == "consola_activa":
    op = st.session_state.date_operator
    st.balloons()
    st.success(f"Acces Confirmat: {op['nume_operator']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Categorie:** {op['filtru_categorie']}")
    with col2:
        st.info(f"**Proiect:** {op['filtru_proiect']}")
    
    st.write("---")
    st.write("Sistemul este acum conectat la Neon.tech și gata de procesare.")
    
    if st.button("Ieșire Securizată"):
        st.session_state.clear()
        st.rerun()
