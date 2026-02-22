import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 1. CONFIGURARE & STIL (PĂSTRĂM ASPECTUL IDBDC)
# ==========================================
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
# POARTA 1: ACCES SISTEM (ECRAN CENTRAL)
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
# POARTA 2: IDENTIFICARE OPERATOR (SIDEBAR 1/8)
# ==========================================
st.sidebar.markdown("<h1 style='text-align: center;'>🛡️👤</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-weight: bold;'>Identificare Operator</p>", unsafe_allow_html=True)

# Caseta pentru cod_acces
cod_introdus = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod")

if cod_introdus:
    try:
        # Verificare în tabela com_operatori pe coloana cod_acces
        res_op = supabase.table("com_operatori").select("nume_operator").eq("cod_acces", cod_introdus).execute()
        
        if res_op.data:
            st.session_state.operator_identificat = res_op.data[0]['nume_operator']
            st.sidebar.success(f"Salut, {st.session_state.operator_identificat}!")
        else:
            st.sidebar.error("Cod acces invalid!")
            st.session_state.operator_identificat = None
    except Exception as e:
        st.sidebar.error(f"Eroare DB: {e}")

# ==========================================
# ZONA CENTRALĂ: LOGICĂ CATEGORII (7/8)
# ==========================================
if st.session_state.operator_identificat:
    st.markdown(f"### Panou de Lucru: {st.session_state.operator_identificat}")
    st.write("---")
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        # Preluare categorii din nom_categorii
        res_cat = supabase.table("nom_categorii").select("nume_categorie").execute()
        liste_categorii = [item['nume_categorie'] for item in res_cat.data] if res_cat.data else []
        categorie_selectata = st.selectbox("Alegeți Categoria:", ["---"] + liste_categorii)

    with col_b:
        # Logica condiționată pentru Contracte & Proiecte
        if categorie_selectata == "Contracte & Proiecte":
            res_sub = supabase.table("nom_contracte_proiecte").select("nume_optiune").execute()
            liste_sub = [item['nume_optiune'] for item in res_sub.data] if res_sub.data else []
            optiune_selectata = st.selectbox("Alegeți Tipul:", ["---"] + liste_sub)
        else:
            # Rămâne albă/inaccesibilă pentru celelalte categorii
            st.selectbox("Alegeți Tipul:", ["Nespecificat"], disabled=True)

    if categorie_selectata != "---":
        st.write(f"Sunteți în secțiunea: **{categorie_selectata}**")
        if categorie_selectata == "Contracte & Proiecte" and 'optiune_selectata' in locals() and optiune_selectata != "---":
             st.info(f"Identificat ca {st.session_state.operator_identificat}. Acces CRUD activ pentru {optiune_selectata}.")

else:
    st.info("Sistemul așteaptă identificarea operatorului în partea stângă.")

# Buton Resetare/Ieșire
if st.sidebar.button("Ieșire Sistem"):
    st.session_state.clear()
    st.rerun()
