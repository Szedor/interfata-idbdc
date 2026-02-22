import streamlit as st
import psycopg2
import urllib.parse

# 1. DESIGN & CONFIGURARE ASPECT
st.set_page_config(page_title="IDBDC | Consola Cercetare", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #1a73e8; color: white; border: none; font-weight: bold; }
    .auth-card { padding: 30px; border-radius: 15px; border: 1px solid #dee2e6; background-color: white; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
    .header-text { color: #1a73e8; text-align: center; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAȚIE SUPABASE (METODA OPTIONS PENTRU TENANT) ---
project_id = "zkkkirpggtczbdzqqlyc"
user = "postgres" # Revenim la user simplu, dar trimitem proiectul prin options
password = urllib.parse.quote_plus("23elf18SKY05!")
host = "aws-0-eu-central-1.pooler.supabase.com"

# Adăugăm ?options=-c%20project%3D[PROJECT_ID] - aceasta e "cheia magică"
DB_URI = f"postgresql://{user}:{password}@{host}:6543/postgres?sslmode=require&options=-c%20project%3D{project_id}"

if "autentificat" not in st.session_state:
    st.session_state["autentificat"] = False
if "operator_valid" not in st.session_state:
    st.session_state["operator_valid"] = None

# --- BARIERA 1: ACCES GENERAL ---
if not st.session_state["autentificat"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,4,1])
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="header-text">Consola IDBDC</h2>', unsafe_allow_html=True)
        st.write("---")
        parola_gen = st.text_input("Cheie Acces Sistem:", type="password", placeholder="Introdu parola generală")
        if st.button("AUTENTIFICARE"):
            if parola_gen == "EverDream2SZ":
                st.session_state["autentificat"] = True
                st.rerun()
            else:
                st.error("❌ Acces neautorizat.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- BARIERA 2: IDENTIFICARE OPERATOR ---
elif st.session_state["operator_valid"] is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,4,1])
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="header-text">Validare Operator</h2>', unsafe_allow_html=True)
        cod_input = st.text_input("Cod de Identificare Responsabil:", type="password", placeholder="Cod IDBDC-XXXX")
        
        if st.button("VERIFICĂ ACCESUL"):
            try:
                # Conexiune folosind URI-ul cu parametrul OPTIONS
                conn = psycopg2.connect(DB_URI)
                cur = conn.cursor()
                cur.execute("SELECT nume_operator, filtru_categorie, filtru_proiect FROM com_operatori WHERE cod_acces = %s", (cod_input,))
                res = cur.fetchone()
                
                if res:
                    st.session_state["operator_valid"] = {"nume": res[0], "cat": res[1], "prj": res[2]}
                    st.rerun()
                else:
                    st.error("❌ Cod invalid în baza centrală.")
                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"⚠️ Eroare Server: {e}")
                st.info("Sfat: Dacă eroarea 'Tenant not found' persistă, trebuie să resetăm parola bazei de date în Supabase fără simbolul '!'")
        st.markdown('</div>', unsafe_allow_html=True)

# --- CONSOLA OPERATOR ---
else:
    op = st.session_state["operator_valid"]
    st.sidebar.title("🛡️ IDBDC Navigare")
    st.sidebar.info(f"Operator: {op['nume']}\nProiect: {op['prj']}")
    
    st.title(f"Panou Control: {op['nume']}")
    st.markdown("---")
    st.success("✅ Conexiune activă. Baza de date este pregătită pentru interogare.")

    if st.sidebar.button("Log Out"):
        st.session_state["autentificat"] = False
        st.session_state["operator_valid"] = None
        st.rerun()
