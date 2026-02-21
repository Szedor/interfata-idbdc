import streamlit as st
import psycopg2
import urllib.parse

# Configurare vizuală IDBDC
st.set_page_config(page_title="Consola Responsabili IDBDC", layout="wide")
st.title("🛡️ Consola Responsabili IDBDC")

# --- CONFIGURAȚIE SHARED POOLER (REVIZUITĂ TOTAL) ---
project_id = "zkkkirpggtczbdzqqlyc"
user = f"postgres.{project_id}"
password = urllib.parse.quote_plus("23elf18SKY05!")
host = "aws-0-eu-central-1.pooler.supabase.com"
# SCHIMBAREA CHEIE: Numele bazei de date devine ID-ul proiectului
dbname = project_id 

DB_URI = f"postgresql://{user}:{password}@{host}:6543/{dbname}?sslmode=require"

# Gestionare Sesiune
if "autentificat" not in st.session_state:
    st.session_state["autentificat"] = False
if "operator_valid" not in st.session_state:
    st.session_state["operator_valid"] = None

# BARIERA 1
if not st.session_state["autentificat"]:
    st.subheader("Bariera 1: Acces General")
    parola_gen = st.text_input("Parola secretă IDBDC:", type="password")
    if st.button("Verifică"):
        if parola_gen == "EverDream2SZ":
            st.session_state["autentificat"] = True
            st.rerun()
        else:
            st.error("Parolă incorectă!")

# BARIERA 2
elif st.session_state["operator_valid"] is None:
    st.subheader("🔑 Bariera 2: Identificare Operator")
    cod_input = st.text_input("Introduceți Codul de Acces Unic:", type="password")
    
    if st.button("Validare Operator"):
        try:
            # Încercăm conexiunea cu noua structură de Tenant
            conn = psycopg2.connect(DB_URI)
            cur = conn.cursor()
            
            cur.execute("SELECT nume_operator, filtru_categorie, filtru_proiect FROM com_operatori WHERE cod_acces = %s", (cod_input,))
            res = cur.fetchone()
            
            if res:
                st.session_state["operator_valid"] = {"nume": res[0], "cat": res[1], "prj": res[2]}
                st.success("Barieră străpunsă! Bine ați venit.")
                st.rerun()
            else:
                st.error("❌ Codul nu a fost găsit în baza de date IDBDC!")
            
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Eroare Identificare: {e}")
            st.info("Dacă eroarea persistă, înseamnă că parola bazei de date trebuie resetată în Supabase fără simboluri speciale.")

# INTERFAȚA DE LUCRU
else:
    op = st.session_state["operator_valid"]
    st.sidebar.success(f"Logat: {op['nume']}")
    st.header(f"Salut, {op['nume']}!")
    st.write(f"Conexiunea IDBDC este acum LIVE prin Shared Pooler (IPv4 compatible).")

    if st.sidebar.button("Log Out"):
        st.session_state["autentificat"] = False
        st.session_state["operator_valid"] = None
        st.rerun()
