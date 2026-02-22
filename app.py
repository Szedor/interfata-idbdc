import streamlit as st
import psycopg2
import urllib.parse

# 1. DESIGN & CONFIGURARE ASPECT (Interfață Profesională)
st.set_page_config(page_title="IDBDC | Consola Cercetare", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #004a99; color: white; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #003366; }
    .auth-card { padding: 30px; border-radius: 15px; border: 1px solid #dee2e6; background-color: white; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
    .header-text { color: #004a99; text-align: center; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAȚIE SHARED POOLER (CU NOUA PAROLĂ) ---
project_id = "zkkkirpggtczbdzqqlyc"
user = f"postgres.{project_id}"
# Folosim noua parolă fără caractere speciale
password = "EverDream2026IDBDC" 
host = "aws-0-eu-central-1.pooler.supabase.com"

# Construim configurația tip dicționar (cea mai stabilă formă)
DB_CONFIG = {
    "host": host,
    "database": "postgres",
    "user": user,
    "password": password,
    "port": "6543",
    "sslmode": "require"
}

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
        st.markdown('<h2 class="header-text">🛡️ Consola IDBDC</h2>', unsafe_allow_html=True)
        st.write("---")
        parola_gen = st.text_input("Cheie Acces Sistem:", type="password", placeholder="Introduceți parola generală")
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
        st.markdown('<h2 class="header-text">🔑 Validare Operator</h2>', unsafe_allow_html=True)
        cod_input = st.text_input("Cod de Identificare Responsabil:", type="password", placeholder="Introduceți codul unic")
        
        if st.button("VERIFICĂ ACCESUL"):
            try:
                # Conectare prin Shared Pooler cu noua parolă
                conn = psycopg2.connect(**DB_CONFIG)
                cur = conn.cursor()
                
                # Interogăm tabela creată conform Protocolului Working IDBDC
                cur.execute("SELECT nume_operator, filtru_categorie, filtru_proiect FROM com_operatori WHERE cod_acces = %s", (cod_input,))
                res = cur.fetchone()
                
                if res:
                    st.session_state["operator_valid"] = {"nume": res[0], "cat": res[1], "prj": res[2]}
                    st.rerun()
                else:
                    st.error("❌ Codul de operator nu a fost găsit.")
                
                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"⚠️ Eroare de conexiune: {e}")
                st.info("Verifică dacă ai salvat noua parolă în Supabase înainte de a rula.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- CONSOLA OPERATOR (LIVE) ---
else:
    op = st.session_state["operator_valid"]
    st.sidebar.title("📑 Navigare IDBDC")
    st.sidebar.info(f"Operator: {op['nume']}\nProiect: {op['prj']}")
    
    st.title(f"Panou de Control: {op['nume']}")
    st.markdown("---")
    st.success(f"✅ Sistem conectat. Aveți acces la categoria: **{op['cat']}**")
    
    # Aici vom afișa datele din baza de date
    st.write("Sesiunea de lucru este activă.")

    if st.sidebar.button("Ieșire Securizată"):
        st.session_state["autentificat"] = False
        st.session_state["operator_valid"] = None
        st.rerun()
