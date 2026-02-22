import streamlit as st
import pandas as pd
from supabase import create_client, Client

# 1. CONFIGURARE PAGINĂ & DESIGN (CARTA PROIECTULUI IDBDC)
st.set_page_config(page_title="Sistem IDBDC", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #004a99;
        color: white;
    }
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-style {
        color: #004a99;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGICA DE ACCES (ECRANUL DE START)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    st.markdown("<h1 class='header-style'>Sistem IDBDC</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Interogare și Dezvoltare Baze Date Cercetare</p>", unsafe_allow_html=True)
    
    parola_introdusa = st.text_input("Cheie de Acces Sistem:", type="password")
    
    if st.button("AUTENTIFICARE"):
        if parola_introdusa == "EverDream2SZ":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Cheie de acces invalidă. Vă rugăm să reîncercați.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 3. INTERFAȚA DUPĂ AUTENTIFICARE
st.markdown(f"<h2 style='color: #004a99;'>Protocol de Lucru IDBDC: Panou Control</h2>", unsafe_allow_html=True)
st.sidebar.success("Conexiune API Activă (Port 443)")

# Conectare la Supabase prin API
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]

try:
    supabase: Client = create_client(url, key)
    
    # Afișare tabel FDI (Conform cerinței curente)
    response = supabase.table("base_proiecte_fdi").select("*").execute()
    
    if response.data:
        df = pd.DataFrame(response.data)
        st.write("### 📂 Vizualizare Date: base_proiecte_fdi")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Sistemul este conectat, dar tabelul solicitat este gol.")

except Exception as e:
    st.error(f"Eroare de comunicare cu serverul: {e}")

st.divider()
st.caption("IDBDC v1.0 | Securizat prin Protocolul de Lucru stabilit.")
