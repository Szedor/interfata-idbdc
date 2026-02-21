mport streamlit as st
import psycopg2

# 1. DESIGN & CONFIGURARE (Aspect Profesional)
st.set_page_config(page_title="IDBDC | Consola Cercetare", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004a99; color: white; }
    .stTextInput>div>div>input { border-radius: 5px; }
    .auth-card { padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- DATE CONEXIUNE (Verifică dacă parola e exact 23elf18SKY05!) ---
DB_CONFIG = {
    "host": "aws-0-eu-central-1.pooler.supabase.com",
    "database": "postgres",
    "user": "postgres.zkkkirpggtczbdzqqlyc",
    "password": "23elf18SKY05!",
    "port": "5432", # Session Mode (mai stabil pentru ce am făcut data trecută)
    "sslmode": "require"
}

if "autentificat" not in st.session_state:
    st.session_state["autentificat"] = False
if "operator_valid" not in st.session_state:
    st.session_state["operator_valid"] = None

# --- BARIERA 1: ACCES GENERAL ---
if not st.session_state["autentificat"]:
    st.image("https://img.icons8.com/fluency/96/shield-lock.png", width=80)
    st.header("Acces Protocol IDBDC")
    with st.container():
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        parola_gen = st.text_input("Introduceți Cheia de Acces General:", type="password", placeholder="Poarta 1")
        if st.button("Deblochează Sistemul"):
            if parola_gen == "EverDream2SZ":
                st.session_state["autentificat"] = True
                st.rerun()
            else:
                st.error("❌ Cheie incorectă. Acces refuzat.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- BARIERA 2: IDENTIFICARE OPERATOR ---
elif st.session_state["operator_valid"] is None:
    st.image("https://img.icons8.com/fluency/96/security-user-male.png", width=80)
    st.header("Identificare Responsabil")
    st.info("Sistemul așteaptă validarea codului de operator din baza de date centrală.")
    
    with st.container():
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        cod_input = st.text_input("Cod Unic Operator:", type="password", placeholder="Ex: ID-XXXX")
        
        if st.button("Verifică Identitatea"):
            try:
                conn = psycopg2.connect(**DB_CONFIG)
                cur = conn.cursor()
                cur.execute("SELECT nume_operator, filtru_categorie, filtru_proiect FROM com_operatori WHERE cod_acces = %s", (cod_input,))
                res = cur.fetchone()
                
                if res:
                    st.session_state["operator_valid"] = {"nume": res[0], "cat": res[1], "prj": res[2]}
                    st.rerun()
                else:
                    st.error("❌ Operatorul nu figurează în baza de date IDBDC.")
                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"⚠️ Eroare de comunicație server: {e}")
                st.warning("Sugestie: Verificați dacă parola bazei de date a fost resetată corect în Supabase.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- INTERFAȚA FINALĂ ---
else:
    op = st.session_state["operator_valid"]
    st.sidebar.success(f"✅ Conectat: {op['nume']}")
    st.sidebar.markdown(f"**Proiect:** {op['prj']}")
    st.sidebar.markdown(f"**Categorie:** {op['cat']}")
    
    st.title(f"Salut, {op['nume']}!")
    st.write("---")
    st.subheader("Baza de date este acum accesibilă.")
    # Aici vor apărea datele tale (cele 9 înregistrări etc.)

    if st.sidebar.button("Închide Sesiunea"):
        st.session_state["autentificat"] = False
        st.session_state["operator_valid"] = None
        st.rerun()
