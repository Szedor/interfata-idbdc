import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 1. CONFIGURARE & INIȚIALIZARE (FUNDAȚIA)
# ==========================================
st.set_page_config(page_title="Sistemul de administrare IDBDC", layout="wide")

# Inițializăm stările de sesiune pentru persistența datelor
if 'autorizat_p1' not in st.session_state:
    st.session_state.autorizat_p1 = False
if 'operator_identificat' not in st.session_state:
    st.session_state.operator_identificat = None

# Stil Vizual Personalizat (Armonizat research.upt.ro)
st.markdown("""
<style>
    .stApp {
        background-color: #003366; /* Albastru UPT */
    }
    h1, h2, h3, h4, p, label, .stMarkdown {
        color: white !important;
    }
    .eroare-idbdc { 
        color: white; 
        background-color: #FF4B4B; 
        padding: 12px; 
        border-radius: 8px; 
        text-align: center; 
        font-weight: bold; 
    }
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #ddd;
    }
    section[data-testid="stSidebar"] .stMarkdown p, 
    section[data-testid="stSidebar"] label {
        color: #31333F !important;
    }
</style>
""", unsafe_allow_html=True)

# Conectare API Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# ==========================================
# 2. POARTA 1: ACCES SISTEM (ECRAN CENTRAL)
# ==========================================
if not st.session_state.autorizat_p1:
    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🛡️</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-top: 0; color: white;'>Sistemul de administrare IDBDC</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #FF4B4B;'>Acces restricționat</h4>", unsafe_allow_html=True)
    
    st.write("") 

    col_stanga, col_centru, col_dreapta = st.columns([1.3, 0.5, 1.3])
    
    with col_centru:
        st.write("Parola de acces:")
        parola_introdusa = st.text_input("Parola", type="password", label_visibility="collapsed", key="p1_pass")
        
        if st.button("Autorizare acces", use_container_width=True):
            if parola_introdusa == "EverDream2SZ":
                st.session_state.autorizat_p1 = True
                st.rerun()
            else:
                st.markdown("<div class='eroare-idbdc'>⚠️ Parolă incorectă.</div>", unsafe_allow_html=True)
    st.stop() 

# ==========================================
# 3. POARTA 2: IDENTIFICARE (SIDEBAR)
# ==========================================
st.sidebar.markdown("<h1 style='text-align: center;'>🛡️👤</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-weight: bold;'>Identificare Operator</p>", unsafe_allow_html=True)

if not st.session_state.operator_identificat:
    cod_introdus = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod")
    if cod_introdus:
        try:
            res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_introdus).execute()
            if res_op.data:
                st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                st.rerun()
            else:
                st.sidebar.error("Cod operator invalid!")
        except Exception as e:
            st.sidebar.error(f"Eroare DB Operator: {e}")
else:
    st.sidebar.success(f"Salut, {st.session_state.operator_identificat}!")
    if st.sidebar.button("Ieșire/Resetare"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 4. PANOU DE LUCRU (ZONA CENTRALĂ)
# ==========================================
if st.session_state.operator_identificat:
    st.markdown(f"## Panou de Lucru IDBDC")
    st.markdown(f"**Operator activ:** {st.session_state.operator_identificat}")
    st.write("---")
    
    col_a, col_b = st.columns([1, 1])
    cat_selectata = "---"

    # CASETA 1: Selectare Categorie Principală
    with col_a:
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
            if res_cat.data:
                liste_categorii = [item
