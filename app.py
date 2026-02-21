import streamlit as st
import psycopg2
import urllib.parse

# 1. DESIGN & CONFIGURARE ASPECT (Centrat și Profesional)
st.set_page_config(page_title="IDBDC | Consola Cercetare", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #004a99; color: white; border: none; font-weight: bold; transition: 0.3s; }
    .stButton>button:hover { background-color: #003366; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
    .auth-card { padding: 30px; border-radius: 15px; border: 1px solid #d0d7de; background-color: white; box-shadow: 0 8px 16px rgba(0,0,0,0.1); }
    h1, h2 { color: #004a99; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAȚIE SHARED POOLER (FORȚARE IPv4) ---
# Această configurație folosește adresa de pooler care suportă IPv4 pe portul 6543
project_id = "zkkkirpggtczbdzqqlyc"
user = f"postgres.{project_id}"
password = urllib.parse.quote_plus("23elf18SKY05!")
# Folosim host-ul de pooler regional care este cunoscut pentru stabilitate IPv4
host = "aws-0-eu-central-1.pooler.supabase.com"

DB_URI = f"postgresql://{user}:{password}@{host}:6543/postgres?sslmode=require"

if "autentificat" not in st.session_state:
    st.session_state["autentificat"] = False
if "operator_valid" not in st.session_state:
    st.session_state["operator_valid"] = None

# --- BARIERA 1: POARTA SITE ---
if not st.session_state["autentificat"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.image("https://img.icons8.com/fluency/96/shield-lock.png", width=60)
        st.header("Acces Protocol IDBDC")
        parola_gen = st.text_input("Cheie Acces General:", type="password", placeholder="••••••••")
        if st.button("ACCESEAZĂ CONSOLA"):
            if parola_gen == "EverDream2SZ":
                st.session_state["autentificat"] = True
                st.rerun()
            else:
                st.error("❌ Cod de acces invalid.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- BARIERA 2: IDENTIFICARE OPERATOR ---
elif st.session_state["operator_valid"] is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.image("https://img.icons8.com/fluency/96/security-user-male.png", width=60)
        st.header("Identificare Operator")
        cod_input = st.text_input("Cod Unic Operator (IDBDC):", type="password", placeholder="Introduceți codul...")
        
        if st.button("VERIFICĂ IDENTITATEA"):
            try:
                # Conexiune prin URI Encoded pe port 6543 (Pooler IPv4)
                conn = psycopg2.connect(DB_URI)
                cur = conn.cursor()
                cur.execute("SELECT nume_operator, filtru_categorie, filtru_proiect FROM com_operatori WHERE cod_acces = %s", (cod_input,))
                res = cur.fetchone()
                
                if res:
                    st.session_state["operator_valid"] = {"nume": res[0], "cat": res[1], "prj": res[2]}
                    st.rerun()
                else:
                    st.error("❌ Codul nu a fost recunoscut în baza de date.")
                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"⚠️ Eroare de rețea: {e}")
                st.info("Sistemul întâmpină dificultăți la rutarea IPv4/IPv6.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- INTERFAȚĂ DE LUCRU (LIVE) ---
else:
    op = st.session_state["operator_valid"]
    st.sidebar.success(f"✅ OPERATOR: {op['nume']}")
    st.sidebar.markdown(f"**Proiect curent:**\n{op['prj']}")
    st.sidebar.markdown(f"**Nivel Acces:**\n{op['cat']}")
    
    st.title(f"Salut, {op['nume']}!")
    st.markdown("---")
    st.write("Baza de date IDBDC este conectată. Puteți începe gestionarea datelor.")
    
    # Aici vom pune afișarea celor 9 utilizatori în pasul următor
    
    if st.sidebar.button("DECONECTARE SECURIZATĂ"):
        st.session_state["autentificat"] = False
        st.session_state["operator_valid"] = None
        st.rerun()
