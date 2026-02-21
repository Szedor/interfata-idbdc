import streamlit as st
import psycopg2
import urllib.parse

# Configurare vizuală IDBDC
st.set_page_config(page_title="Consola Responsabili IDBDC", layout="wide")
st.title("🛡️ Consola Responsabili IDBDC")

# --- DATE INTEGRATE (SOLUȚIA CARE A FUNCȚIONAT DATA TRECUTĂ) ---
# Am revenit la dbname='postgres' dar am securizat user-ul
project_id = "zkkkirpggtczbdzqqlyc"
user = f"postgres.{project_id}"
password = "23elf18SKY05!" # Fără encoding aici pentru a testa transmiterea directă
host = "aws-0-eu-central-1.pooler.supabase.com"

# Construim conexiunea prin parametri separați, care e mai stabilă decât URI-ul lung
DB_CONFIG = {
    "host": host,
    "database": "postgres",
    "user": user,
    "password": password,
    "port": "6543",
    "sslmode": "require"
}

# Gestionare Sesiune
if "autentificat" not in st.session_state:
    st.session_state["autentificat"] = False
if "operator_valid" not in st.session_state:
    st.session_state["operator_valid"] = None

# BARIERA 1: POARTA SITE
if not st.session_state["autentificat"]:
    st.subheader("Bariera 1: Acces General")
    parola_gen = st.text_input("Parola secretă IDBDC:", type="password")
    if st.button("Verifică"):
        if parola_gen == "EverDream2SZ":
            st.session_state["autentificat"] = True
            st.rerun()
        else:
            st.error("Parolă incorectă!")

# BARIERA 2: CONEXIUNE OPERATOR
elif st.session_state["operator_valid"] is None:
    st.subheader("🔑 Bariera 2: Identificare Operator")
    cod_input = st.text_input("Introduceți Codul de Acces Unic:", type="password")
    
    if st.button("Validare Operator"):
        try:
            # Conectare folosind dicționarul de parametri
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            # Verificăm în tabela de operatori
            cur.execute("SELECT nume_operator, filtru_categorie, filtru_proiect FROM com_operatori WHERE cod_acces = %s", (cod_input,))
            res = cur.fetchone()
            
            if res:
                st.session_state["operator_valid"] = {"nume": res[0], "cat": res[1], "prj": res[2]}
                st.success("Conexiune reușită! Cei 9 utilizatori sunt gata.")
                st.rerun()
            else:
                st.error("❌ Codul nu a fost găsit în baza de date!")
            
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Eroare de identificare: {e}")

# INTERFAȚA DE LUCRU
else:
    op = st.session_state["operator_valid"]
    st.sidebar.success(f"Logat: {op['nume']}")
    st.header(f"Salut, {op['nume']}!")
    st.write("Accesul la baza de date IDBDC este acum complet.")

    if st.sidebar.button("Log Out"):
        st.session_state["autentificat"] = False
        st.session_state["operator_valid"] = None
        st.rerun()
