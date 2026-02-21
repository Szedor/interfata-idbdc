import streamlit as st
import psycopg2

# Configurare vizuală IDBDC
st.set_page_config(page_title="Consola Responsabili IDBDC", layout="wide")
st.title("🛡️ Consola Responsabili IDBDC")

# --- DATE INTEGRATE (SOLUȚIA DEFINITIVĂ PENTRU TENANT) ---
# Am modificat User-ul: am adăugat ID-ul proiectului tău după punct (metoda recomandată de Supabase pentru Pooler)
DB_URI = "postgresql://postgres.zkkkirpggtczbdzqqlyc:23elf18SKY05!@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=require"

# Gestionare Sesiune
if "autentificat" not in st.session_state:
    st.session_state["autentificat"] = False
if "operator_valid" not in st.session_state:
    st.session_state["operator_valid"] = None

# BARIERA 1: ACCES GENERAL
if not st.session_state["autentificat"]:
    st.subheader("Bariera 1: Acces General")
    parola_gen = st.text_input("Parola secretă IDBDC:", type="password")
    if st.button("Verifică"):
        if parola_gen == "EverDream2SZ":
            st.session_state["autentificat"] = True
            st.rerun()
        else:
            st.error("Parolă incorectă!")

# BARIERA 2: IDENTIFICARE OPERATOR (CONEXIUNE SQL)
elif st.session_state["operator_valid"] is None:
    st.subheader("🔑 Bariera 2: Identificare Operator")
    cod_input = st.text_input("Introduceți Codul de Acces Unic:", type="password")
    
    if st.button("Validare Operator"):
        try:
            # Conectare folosind URI-ul cu Tenant ID inclus în User
            conn = psycopg2.connect(DB_URI)
            cur = conn.cursor()
            
            cur.execute("SELECT nume_operator, filtru_categorie, filtru_proiect FROM com_operatori WHERE cod_acces = %s", (cod_input,))
            res = cur.fetchone()
            
            if res:
                st.session_state["operator_valid"] = {
                    "nume": res[0], 
                    "cat": res[1], 
                    "prj": res[2]
                }
                st.success("Conexiune stabilită cu succes!")
                st.rerun()
            else:
                st.error("❌ Codul nu a fost găsit în baza de date!")
            
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Eroare de identificare (Tenant/User): {e}")

# INTERFAȚA DE LUCRU
else:
    op = st.session_state["operator_valid"]
    st.sidebar.success(f"Logat: {op['nume']}")
    st.sidebar.info(f"Proiect: {op['prj']}\nCategorie: {op['cat']}")
    
    st.header(f"Salut, {op['nume']}!")
    st.write(f"Sunteți conectat la Consola de Gestionare Cercetare.")
    st.info(f"Filtru activat pe categoria: **{op['cat']}**.")

    if st.sidebar.button("Log Out"):
        st.session_state["autentificat"] = False
        st.session_state["operator_valid"] = None
        st.rerun()
