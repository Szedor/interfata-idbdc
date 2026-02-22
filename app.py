import streamlit as st
import pandas as pd
from supabase import create_client, Client

# 1. CONFIGURARE & STIL
st.set_page_config(page_title="IDBDC UPT", layout="wide")

st.markdown("""
<style>
    .eroare-idbdc { color: white; background-color: #FF4B4B; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
    .stSidebar { background-color: #f8f9fa; border-right: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

# Inițializare stări sesiune
if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

# Conectare API Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# ==========================================
# POARTA 1: ACCES SISTEM
# ==========================================
if not st.session_state.autorizat_p1:
    st.markdown("<h1 style='text-align: center;'>🛡️</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Sistemul de Gestiune IDBDC</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("Parola pentru autorizare acces")
        parola_introdusa = st.text_input("Parola", type="password", label_visibility="collapsed", key="p1_pass")
        if st.button("Autorizare acces", use_container_width=True):
            if parola_introdusa == "EverDream2SZ":
                st.session_state.autorizat_p1 = True
                st.rerun()
            else:
                st.markdown("<div class='eroare-idbdc'>⚠️ Parolă incorectă.</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# POARTA 2: IDENTIFICARE OPERATOR (SIDEBAR)
# ==========================================
# Simbol Scut cu Efigie în Sidebar
st.sidebar.markdown("<h1 style='text-align: center;'>🛡️👤</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-weight: bold;'>Identificare Operator</p>", unsafe_allow_html=True)

cod_identificare = st.sidebar.text_input("Cod Identificare", type="password")

if cod_identificare:
    # Verificăm operatorul în tabela com_operatori
    res_op = supabase.table("com_operatori").select("nume_operator").eq("cod_identificare", cod_identificare).execute()
    if res_op.data:
        st.session_state.operator_identificat = res_op.data[0]['nume_operator']
        st.sidebar.success(f"Salut, {st.session_state.operator_identificat}!")
    else:
        st.sidebar.error("Cod invalid!")
        st.session_state.operator_identificat = None

# ==========================================
# ZONA CENTRALĂ: OPTIUNI CRUD (7/8)
# ==========================================
if st.session_state.operator_identificat:
    st.markdown(f"### Panou de Lucru: {st.session_state.operator_identificat}")
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        # Preluare categorii din nom_categorii
        res_cat = supabase.table("nom_categorii").select("nume_categorie").execute()
        liste_categorii = [item['nume_categorie'] for item in res_cat.data] if res_cat.data else []
        categorie_selectata = st.selectbox("Selectați Categoria:", ["---"] + liste_categorii)

    with col_b:
        # Logica condiționată pentru a doua casetă
        if categorie_selectata == "Contracte & Proiecte":
            res_sub = supabase.table("nom_contracte_proiecte").select("nume_optiune").execute()
            liste_sub = [item['nume_optiune'] for item in res_sub.data] if res_sub.data else []
            optiune_selectata = st.selectbox("Selectați Tipul:", liste_sub)
        else:
            st.selectbox("Selectați Tipul:", ["---"], disabled=True)

    st.write("---")
    if categorie_selectata != "---":
        st.info(f"Ați selectat secțiunea: {categorie_selectata}. Aici vor apărea atributele CRUD.")
else:
    st.info("Vă rugăm să introduceți codul de identificare în partea stângă pentru a continua.")

# Resetare
if st.sidebar.button("Ieșire Sistem"):
    st.session_state.clear()
    st.rerun()
