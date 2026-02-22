import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 1. CONFIGURARE & INIȚIALIZARE
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide")

if 'autorizat_p1' not in st.session_state:
    st.session_state.autorizat_p1 = False
if 'operator_identificat' not in st.session_state:
    st.session_state.operator_identificat = None

# Conectare API Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# ==========================================
# 2. POARTA 1: ACCES SISTEM (ECRAN CENTRAL)
# ==========================================
if not st.session_state.autorizat_p1:
    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🛡️</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-top: 0;'>Sistemul de Gestiune IDBDC</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #555;'>Universitatea Politehnica Timișoara</h3>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #CC0000;'>Acces restricționat</h4>", unsafe_allow_html=True)
    
    col_st, col_ce, col_dr = st.columns([1.3, 0.5, 1.3])
    with col_ce:
        st.write("Parola de acces:")
        parola_introdusa = st.text_input("Parola", type="password", label_visibility="collapsed", key="p1_pass")
        if st.button("Autorizare acces", use_container_width=True):
            if parola_introdusa == "EverDream2SZ":
                st.session_state.autorizat_p1 = True
                st.rerun()
            else:
                st.error("⚠️ Parolă incorectă.")
    st.stop() 

# ==========================================
# 3. POARTA 2: IDENTIFICARE (SIDEBAR 1/8)
# ==========================================
# SIMBOL CONCATENAT CERUT
st.sidebar.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🛡️👤</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-weight: bold; margin-top: 0;'>Identificare Operator</p>", unsafe_allow_html=True)

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
            st.sidebar.error(f"Eroare DB: {e}")
else:
    st.sidebar.success(f"Salut, {st.session_state.operator_identificat}!")
    if st.sidebar.button("Ieșire/Resetare"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 4. ZONA CENTRALĂ: LOGICĂ SELECTII (7/8)
# ==========================================
if st.session_state.operator_identificat:
    st.markdown(f"### Panou de Lucru: {st.session_state.operator_identificat}")
    st.write("---")
    
    col_a, col_b = st.columns([1, 1])
    
    # 1. Obținem datele pentru Categorie
    try:
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        optiuni_cat = ["---"] + [r["denumire_categorie"] for r in res_cat.data]
    except:
        optiuni_cat = ["---", "Eroare încărcare"]

    with col_a:
        cat_aleasa = st.selectbox("Selectați Categoria:", optiuni_cat)

    # 2. Obținem datele pentru Sub-categorie (Contracte & Proiecte)
    with col_b:
        if cat_aleasa == "Contracte & Proiecte":
            try:
                res_sub = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                optiuni_sub = ["---"] + [r["acronim_contracte_proiecte"] for r in res_sub.data]
                st.selectbox("Selectati tipul de contract sau proiect", optiuni_sub)
            except:
                st.error("Eroare la acronime")
        else:
            st.selectbox("Selectati tipul de contract sau proiect", ["---"], disabled=True)

    if cat_aleasa != "---":
        st.info(f"Sunteți în secțiunea: **{cat_aleasa}**")
