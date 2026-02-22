import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 1. CONFIGURARE & INIȚIALIZARE (FUNDAȚIA)
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide")

# Inițializare variabile de sesiune dacă nu există
if 'autorizat_p1' not in st.session_state:
    st.session_state.autorizat_p1 = False
if 'operator_identificat' not in st.session_state:
    st.session_state.operator_identificat = None

# Stil Vizual
st.markdown("""
<style>
    .eroare-idbdc { color: white; background-color: #FF4B4B; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
    .stSidebar { background-color: #f8f9fa; border-right: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

# Conectare la Supabase prin API (Port 443)
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# ==========================================
# 2. POARTA 1: ACCES SISTEM (CENTRAL)
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
# 3. POARTA 2: IDENTIFICARE (SIDEBAR 1/8)
# ==========================================
st.sidebar.markdown("<h1 style='text-align: center;'>🛡️👤</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-weight: bold;'>Identificare Operator</p>", unsafe_allow_html=True)

cod_introdus = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod")

if cod_introdus and not st.session_state.operator_identificat:
    try:
        # Folosim denumirile din DB: cod_operatori și nume_prenume
        res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_introdus).execute()
        
        if res_op.data and len(res_op.data) > 0:
            st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
            st.rerun()
        else:
            st.sidebar.error("Cod operator invalid!")
    except Exception as e:
        st.sidebar.error(f"Eroare DB: {e}")

# ==========================================
# 4. ZONA CENTRALĂ: LOGICĂ CATEGORII (7/8)
# ==========================================
if st.session_state.operator_identificat:
    st.sidebar.success(f"Salut, {st.session_state.operator_identificat}!")
    
    st.markdown(f"### Panou de Lucru: {st.session_state.operator_identificat}")
    st.write("---")
    
    col_a, col_b = st.columns([1, 1])
    
    cat_selectata = "---"

    with col_a:
        try:
            # Încercăm să citim categoriile. Dacă "nume_categorie" e greșit, prindem eroarea.
            res_cat = supabase.table("nom_categorii").select("*").execute()
            if res_cat.data:
                # Detectăm automat numele coloanei din nom_categorii
                cols = list(res_cat.data[0].keys())
                nume_col_cat = "nume_categorie" if "nume_categorie" in cols else cols[0]
                liste_categorii = [item[nume_col_cat] for item in res_cat.data]
                cat_selectata = st.selectbox("Selectați Categoria:", ["---"] + liste_categorii)
        except:
            st.error("Eroare la accesarea tabelului 'nom_categorii'.")

    with col_b:
        if cat_selectata == "Contracte & Proiecte":
            try:
                res_sub = supabase.table("nom_contracte_proiecte").select("*").execute()
                if res_sub.data:
                    # Detectăm automat numele coloanei din nom_contracte_proiecte
                    cols_s = list(res_sub.data[0].keys())
                    nume_col_sub = "nume_optiune" if "nume_optiune" in cols_s else cols_s[0]
                    liste_sub = [item[nume_col_sub] for item in res_sub.data]
                    opt_selectata = st.selectbox("Selectați Tipul:", ["---"] + liste_sub)
            except:
                st.error("Eroare la accesarea tabelului 'nom_contracte_proiecte'.")
        else:
            st.selectbox("Selectați Tipul:", ["---"], disabled=True)

    if cat_selectata != "---":
        st.write(f"Secțiunea curentă: **{cat_selectata}**")
else:
    st.info("Vă rugăm să introduceți codul de identificare în sidebar (stânga).")

# Ieșire
if st.sidebar.button("Ieșire Sistem"):
    st.session_state.clear()
    st.rerun()
