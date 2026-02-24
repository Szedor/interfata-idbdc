import streamlit as st
from supabase import create_client, Client
import motor_admin  # IMPORTĂM MOTORUL SEPARAT

def run():
    # --- SECȚIUNE VALIDATĂ / ÎNGHEȚATĂ ---
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
        input { color: #000000 !important; background-color: #ffffff !important; }
        div.stButton > button { border: 1px solid white !important; color: white !important; background-color: rgba(255,255,255,0.1) !important; width: 100%; font-size: 14px !important; font-weight: bold !important; height: 45px !important; }
        div.stButton > button:hover { background-color: white !important; color: #003366 !important; }
    </style>
    """, unsafe_allow_html=True)

    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False

    if not st.session_state.autorizat_p1:
        st.subheader("🔒 Acces Securizat - Consola Admin")
        cod_acces = st.text_input("Introduceți codul de autorizare", type="password")
        if st.button("Validare Acces"):
            if cod_acces == "IDBDC2024":
                st.session_state.autorizat_p1 = True
                st.rerun()
            else: st.error("Cod incorect!")
        return

    # AICI SE FACE LEGĂTURA CU MOTORUL DE FUNCȚIONARE
    motor_admin.executa_logica(supabase)
