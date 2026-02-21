import streamlit as st
import psycopg2

# 1. DESIGN & CONFIGURARE (Aspect IDBDC)
st.set_page_config(page_title="IDBDC | Consola Cercetare", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004a99; color: white; border: none; }
    .stTextInput>div>div>input { border-radius: 5px; }
    .auth-card { padding: 25px; border-radius: 12px; border: 1px solid #e0e0e0; background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    h1, h2 { color: #004a99; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAȚIE BAZĂ DE DATE ---
# Am revenit la setările de bază pe portul 5432 (Direct/Session)
DB_CONFIG = {
    "host": "db.zkkkirpggtczbdzqqlyc.supabase.co",
    "database": "postgres",
    "user": "postgres",
    "password": "23elf18SKY05!",
    "port": "5432",
    "sslmode": "require"
}

if "autentificat" not in st.session_state:
    st.session_state["autentificat"] = False
if "operator_valid" not in st.session_state:
    st.session_state["operator_valid"] = None

# --- BARIERA 1: ACCES GENERAL (POARTA 1) ---
if not st.session_state["autentificat"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://img.icons8.com/fluency/96/shield-lock.png", width=80)
        st.header("Acces Protocol IDBDC")
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        parola_gen = st.text_input("Cheie Acces General:", type="password", placeholder="Introduceți parola...")
        if st.button("Deblochează Sistemul"):
            if parola_gen == "EverDream2SZ":
                st.session_state["autentificat"] = True
                st.rerun()
            else:
                st.error("❌ Parolă incorectă.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- BARIERA 2: IDENTIFICARE OPERATOR (POARTA 2) ---
elif st.session_state["operator_valid"] is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://img.icons8.com/fluency/96/security-user-male.png", width=80)
        st.header("Identificare Operator")
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        cod_input = st.text_input("Cod Acces Unic (IDBDC):", type="password", placeholder="Cod Operator...")
        
        if st.button("Verifică Identitatea"):
            try:
                # Încercăm conexiunea directă
                conn = psycopg2.connect(**DB_CONFIG)
                cur = conn.cursor()
                cur.execute("SELECT nume_operator, filtru_categorie, filtru_proiect FROM com_operatori WHERE cod_acces = %s", (cod_input,))
                res = cur.fetchone()
                
                if res:
                    st.session_state["operator_valid"] = {"nume": res[0], "cat": res[1], "prj": res[2]}
                    st.rerun()
                else:
                    st.error("❌ Operatorul nu a fost găsit.")
                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"Eroare de conexiune: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# --- INTERFAȚĂ DE LUCRU ---
else:
    op = st.session_state["operator_valid"]
    st.sidebar.success(f"✅ Logat: {op['nume']}")
    st.sidebar.markdown(f"**Proiect:** {op['prj']}")
    st.sidebar.markdown(f"**Categorie:** {op['cat']}")
    
    st.title(f"Salut, {op['nume']}!")
    st.write("---")
    st.info(f"Sunteți autorizat pentru gestionarea bazei de date în cadrul proiectului {op['prj']}.")
    
    # Buton de logout în sidebar
    if st.sidebar.button("Ieșire Securizată"):
        st.session_state["autentificat"] = False
        st.session_state["operator_valid"] = None
        st.rerun()
