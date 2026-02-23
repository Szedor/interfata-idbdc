import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 1. CONFIGURARE VIZUALĂ (Armonizare cu Poarta 1)
# ==========================================
st.set_page_config(page_title="Poarta 2 - Identificare IDBDC", layout="wide")

st.markdown("""
<style>
    .stApp {
        background-color: #003366; /* Albastru UPT */
    }
    h1, h2, h3, h4, p, label, .stMarkdown {
        color: white !important;
    }
    /* Stil Sidebar pentru contrast */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
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

# Inițializare stare operator
if 'operator_identificat' not in st.session_state:
    st.session_state.operator_identificat = None

# ==========================================
# 2. LOGICĂ POARTA 2: IDENTIFICARE (SIDEBAR)
# ==========================================
st.sidebar.markdown("<h1 style='text-align: center;'>🛡️👤</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-weight: bold;'>Identificare Operator</p>", unsafe_allow_html=True)

if not st.session_state.operator_identificat:
    # Căutare operator în com_operatori folosind cod_operatori
    cod_introdus = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod")
    
    if cod_introdus:
        try:
            # Interogare tabel com_operatori
            res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_introdus).execute()
            
            if res_op.data:
                st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                st.rerun()
            else:
                st.sidebar.error("Cod operator invalid!")
        except Exception as e:
            st.sidebar.error(f"Eroare DB Operator: {e}")
else:
    # Afișare succes și buton de resetare
    st.sidebar.success(f"Salut, {st.session_state.operator_identificat}!")
    if st.sidebar.button("Ieșire/Resetare"):
        st.session_state.operator_identificat = None
        st.rerun()

# ==========================================
# 3. PANOU DE LUCRU (ZONA CENTRALĂ)
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
                liste_categorii = [item["denumire_categorie"] for item in res_cat.data]
                cat_selectata = st.selectbox("Selectați Categoria:", ["---"] + liste_categorii)
        except:
            st.error("Eroare la încărcarea categoriilor.")

    # CASETA 2: Selectare Tip Contract/Proiect
    with col_b:
        if cat_selectata == "Contracte & Proiecte":
            try:
                res_sub = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                if res_sub.data:
                    liste_sub = [item["acronim_contracte_proiecte"] for item in res_sub.data]
                    st.selectbox("Selectați tipul de contract sau proiect:", ["---"] + liste_sub)
            except:
                st.error("Eroare la încărcarea acronimelor.")
        else:
            st.selectbox("Selectați tipul de contract sau proiect:", ["---"], disabled=True)

    if cat_selectata != "---":
        st.info(f"Context activ stabilit pentru: **{cat_selectata}**")
else:
    st.info("Sistemul așteaptă identificarea operatorului în Sidebar pentru a debloca Panoul de Lucru.")
