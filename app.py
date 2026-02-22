import streamlit as st
import psycopg2

# 1. DESIGN & CONFIGURARE VIZUALĂ
st.set_page_config(page_title="IDBDC | Consola Centrală", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #004a99; color: white; border: none; font-weight: bold; }
    .auth-card { padding: 30px; border-radius: 15px; border: 1px solid #dee2e6; background-color: white; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
    .header-text { color: #004a99; text-align: center; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAȚIE DE FORȚĂ (TENANT AS DATABASE NAME) ---
project_id = "zkkkirpggtczbdzqqlyc"

DB_CONFIG = {
    "host": "aws-0-eu-central-1.pooler.supabase.com",
    "database": project_id,           # SCHIMBARE: Folosim ID-ul proiectului ca nume de DB
    "user": f"postgres.{project_id}", # Păstrăm și aici pentru siguranță
    "password": "EverDream2026IDBDC",
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
        parola_gen = st.text_input("Cheie Acces Sistem:", type="password")
        if st.button("AUTENTIFICARE"):
            if parola_gen == "EverDream2SZ":
                st.session_state["autentificat"] = True
                st.rerun()
            else:
                st.error("❌ Parolă incorectă.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- BARIERA 2: IDENTIFICARE OPERATOR ---
elif st.session_state["operator_valid"] is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,4,1])
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="header-text">🔑 Validare Operator</h2>', unsafe_allow_html=True)
        cod_input = st.text_input("Cod de Identificare Responsabil:", type="password")
        
        if st.button("VERIFICĂ ACCESUL"):
            try:
                # Încercăm conexiunea cu noua structură de Tenant
                conn = psycopg2.connect(**DB_CONFIG)
                cur = conn.cursor()
                
                cur.execute("SELECT nume_operator, filtru_categorie, filtru_proiect FROM com_operatori WHERE cod_acces = %s", (cod_input,))
                res = cur.fetchone()
                
                if res:
                    st.session_state["operator_valid"] = {"nume": res[0], "cat": res[1], "prj": res[2]}
                    st.rerun()
                else:
                    st.error("❌ Codul nu a fost găsit în baza centrală.")
                
                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"⚠️ Eroare de rețea: {e}")
                st.info("Dacă eroarea persistă, înseamnă că sistemul refuză identificarea prin Pooler și va trebui să folosim un proxy IPv4 extern.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- INTERFAȚĂ LIVE ---
else:
    op = st.session_state["operator_valid"]
    st.title(f"Salut, {op['nume']}!")
    st.success("✅ Protocol IDBDC activat!")
    st.write(f"Sunteți logat pe proiectul: **{op['prj']}**")
    
    if st.sidebar.button("Ieșire Securizată"):
        st.session_state.clear()
        st.rerun()
