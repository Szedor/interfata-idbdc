import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# ==========================================
# 1. CONFIGURARE & STIL (ÎNGHEȚAT)
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide")

st.markdown(""" <style> .eroare-idbdc {
color: white; background-color: #FF4B4B; padding: 12px; border-radius: 8px;
text-align: center; font-weight: bold; width: 100%; display: block; margin-top:
10px; } </style> """, unsafe_allow_html=True)

if 'autorizat_p1' not in st.session_state:
    st.session_state.autorizat_p1 = False

# ==========================================
# 2. ANTET (PROTOCOL IDBDC)
# ==========================================
st.markdown("<h1 style='text-align: center;'>🛡️</h1>", unsafe_allow_html=True) 
st.markdown("<h2 style='text-align: center;'>Sistemul de Gestiune IDBDC</h2>", unsafe_allow_html=True) 
st.markdown("<h4 style='text-align: center;'>Universitatea Politehnica Timișoara</h4>", unsafe_allow_html=True) 
st.write("---")

# ==========================================
# 3. LOGICA DE AUTORIZARE
# ==========================================
if not st.session_state.autorizat_p1: 
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("Parola pentru autorizare acces")
        parola_introdusa = st.text_input(
            "Parola", 
            type="password", 
            label_visibility="collapsed",
            autocomplete="new-password",
            key="p1_pass"
        )
        
        if st.button("Autorizare acces", use_container_width=True):
            if parola_introdusa == "EverDream2SZ":
                st.session_state.autorizat_p1 = True
                st.rerun()
            else:
                st.markdown(
                    "<div class='eroare-idbdc'>"
                    "⚠️ Acces Neautorizat: Parola nu corespunde sistemului IDBDC."
                    "</div>", 
                    unsafe_allow_html=True
                )
else: 
    # ==========================================
    # 4. AFISARE DATE (SUPABASE)
    # ==========================================
    st.success("✅ Acces Autorizat. Bun venit în sistemul IDBDC.")
    
    try:
        engine = create_engine(st.secrets["DB_URL"])
        query = "SELECT * FROM base_proiecte_internationale"
        df = pd.read_sql(query, engine)

        st.subheader(f"📋 Baza de Date: Operatori ({len(df)} înregistrări)")
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Eroare tehnică la conectare: {e}")

    if st.button("Ieșire (Logout)"): 
        st.session_state.autorizat_p1 = False 
        st.rerun()
