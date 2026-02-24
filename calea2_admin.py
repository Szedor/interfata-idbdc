import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    # --- CONEXIUNE ȘI STIL (CONFORM PROTOCOLULUI) ---
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
        input { color: #000000 !important; background-color: #ffffff !important; }
        .eroare-idbdc-rosu { color: #ffffff !important; background-color: #ff0000 !important; padding: 10px; border-radius: 4px; text-align: center; font-weight: bold; border: 2px solid #8b0000; margin-top: 10px; }
        
        /* Stil butoane text CRUD */
        div.stButton > button { 
            border: 1px solid white !important; 
            color: white !important; 
            font-size: 14px !important; 
            background-color: rgba(255, 255, 255, 0.1) !important;
            width: 100%;
        }
        div.stButton > button:hover { 
            background-color: white !important; 
            color: #003366 !important; 
        }
    </style>
    """, unsafe_allow_html=True)

    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    # --- PAS 1: POARTA MASTER ---
    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'> 🛡️ Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola master:", type="password", key="p1_pass")
            if st.button("Autorizare acces", use_container_width=True):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
                else:
                    st.markdown("<div class='eroare-idbdc-rosu'> ⚠️ Parolă incorectă.</div>", unsafe_allow_html=True)
        st.stop()

    # --- PAS 2: IDENTIFICARE OPERATOR ---
    st.sidebar.markdown("### 👤 Identificare Operator")
    if not st.session_state.operator_identificat:
        cod_in = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod_input")
        if cod_in:
            try:
                res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_in).execute()
                if res_op.data and len(res_op.data) > 0:
                    st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                    st.rerun()
                else:
                    st.sidebar.markdown("<div class='eroare-idbdc-rosu'>Cod operator inexistent!</div>", unsafe_allow_html=True)
            except Exception:
                st.sidebar.markdown("<div class='eroare-idbdc-rosu'>Eroare tehnică DB.</div>", unsafe_allow_html=True)
        st.stop()
    else:
        st.sidebar.success(f"Operator: {st.session_state.operator_identificat}")
        if st.sidebar.button("Ieșire / Resetare"):
            st.session_state.clear()
            st.rerun()

    # --- ZONA DE LUCRU (CELE 3 CASETE) ---
    st.markdown(f"<h3 style='text-align: center;'> 🛠️ Administrare: {st.session_state.operator
