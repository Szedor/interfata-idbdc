import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 1. CONFIGURARE & DISPECER (ROUTING)
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide")

# Citim destinația din link (URL)
query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

# Conectare API Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Stil Vizual (Păstrat din scriptul tău)
st.markdown("""
<style>
    .stApp { background-color: #003366; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { color: white !important; }
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #ddd; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #003366 !important; }
    [data-testid="stSidebar"] input { color: #31333F !important; background-color: white !important; }
    .eroare-idbdc { color: white; background-color: #FF4B4B; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CALEA 1: EXPLORATOR (VIZITATORI)
# ==========================================
if calea_activa == "explorator":
    st.markdown("# 🔍 Explorator de Date IDBDC")
    st.write("Sistem de interogare pentru vizitatori.")
    # Aici vom construi interfața publică cerută anterior (An, ID, Director)

# ==========================================
# CALEA 2: ADMIN (SCRIPTUL TĂU FINISAT)
# ==========================================
elif calea_activa == "admin":
    # Inițializare stări (Logica ta)
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    # POARTA 1: ACCES SISTEM
    if not st.session_state.autorizat_p1:
        st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🛡️</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>Sistemul de administrare IDBDC</h2>", unsafe_allow_html=True)
        
        col_st, col_ce, col_dr = st.columns([1.3, 0.5, 1.3])
        with col_ce:
            st.write("Parola de acces:")
            parola_introdusa = st.text_input("Parola", type="password", label_visibility="collapsed", key="p1_pass")
            if st.button("Autorizare acces", use_container_width=True):
                if parola_introdusa == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
                else:
                    st.markdown("<div class='eroare-idbdc'>⚠️ Parolă incorectă.</div>", unsafe_allow_html=True)
        st.stop() 

    # POARTA 2: IDENTIFICARE (SIDEBAR)
    st.sidebar.markdown("<h1 style='text-align: center;'>🛡️👤</h1>", unsafe_allow_html=True)
    if not st.session_state.operator_identificat:
        cod_introdus = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod")
        if cod_introdus:
            try:
                res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_introdus).execute()
                if res_op.data:
                    st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                    st.rerun()
                else: st.sidebar.error("Cod operator invalid!")
            except Exception as e: st.sidebar.error(f"Eroare DB: {e}")
        st.stop()
    else:
        st.sidebar.success(f"Salut, {st.session_state.operator_identificat}!")
        if st.sidebar.button("Ieșire/Resetare"):
            st.session_state.clear()
            st.rerun()

    # PANOU DE LUCRU (Zona Centrală din scriptul tău)
    st.markdown(f"### Panou de Lucru: {st.session_state.operator_identificat}")
    st.write("---")
    
    col_a, col_b = st.columns([1, 1])
    cat_selectata = "---"

    with col_a:
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
            liste_categorii = [item["denumire_categorie"] for item in res_cat.data]
            cat_selectata = st.selectbox("Selectați Categoria:", ["---"] + liste_categorii)
        except: st.error("Eroare la încărcarea categoriilor.")

    with col_b:
        if cat_selectata == "Contracte & Proiecte":
            try:
                res_sub = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                liste_sub = [item["acronim_contracte_proiecte"] for item in res_sub.data]
                st.selectbox("Selectați tipul de contract sau proiect:", ["---"] + liste_sub)
            except: st.error("Eroare la încărcarea acronimelor.")
        else:
            st.selectbox("Selectați tipul:", ["---"], disabled=True)

# ==========================================
# CALEA 3: AI (PROFESORI)
# ==========================================
elif calea_activa == "ai":
    st.markdown("# 🧠 Brainstorming AI")
    st.write("Modul dedicat profesorilor.")
