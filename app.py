import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 0. DISPECERUL (MOTORUL DE NAVIGARE)
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide")

query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

# Conectare API Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Stil Vizual UPT - Control strict etichete și fonturi
st.markdown("""
<style>
    .stApp { background-color: #003366; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { color: white !important; }
    label { font-size: 16px !important; font-weight: 400 !important; color: white !important; }
    .stMultiSelect [data-baseweb="select"] div[aria-live="polite"] { color: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CALEA 1: EXPLORATOR DE DATE
# ==========================================
if calea_activa == "explorator":
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de date</h1>", unsafe_allow_html=True)
    st.write("---")

    # 1 & 2: SELECȚII PRINCIPALE
    c1, c2 = st.columns(2)
    with c1:
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        list_cat = [i["denumire_categorie"] for i in res_cat.data]
        categorii_sel = st.multiselect("1. Categoria de informații:", list_cat, placeholder="", key="f_cat_multi")

    with c2:
        tipuri_sel = []
        if "Contracte & Proiecte" in categorii_sel:
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
            tipuri_sel = st.multiselect("2. Tipul de contract / proiect:", list_tip, placeholder="", key="f_tip_multi")

    # FILTRE DE RAFINARE
    if tipuri_sel:
        st.write("---")
        
        # 5. TITLUL PROIECTULUI - Lățime totală, cifra 5 prezentă
        titlu_sel = st.text_input("5. Titlul proiectului / Obiectul contractului", key="f_titlu")
        
        st.write("") # Spațiu

        f1, f2, f3 = st.columns(3)
        
        with f1:
            # 3. ID / Nr. Contract
            id_sel = st.text_input("3. ID proiect / Nr. contract", key="f_id")
            # 4. Acronim
            acro_sel = st.text_input("4. Acronim proiect", key="f_acro")

        with f2:
            # 7. Anul de implementare
            an_sel = st.number_input("7. Anul de implementare", min_value=2010, max_value=2035, value=2024, key="f_an")
            
            # 6. Director de proiect / Responsabil contract (Sursa: det_resurse_umane)
            try:
                res_dir = supabase.table("det_resurse_umane").select("nume_prenume").execute()
                directori = sorted(list(set([d['nume_prenume'] for d in res_dir.data])))
                dir_sel = st.multiselect("6. Director de proiect / Responsabil contract", directori, placeholder="", key="f_dir")
            except: dir_sel = []

            # 10. Departament (Sub Director, Sursa: nom_departament)
            try:
                res_dep = supabase.table("nom_departament").select("acronim_departament").execute()
                departamente = sorted([d['acronim_departament'] for d in res_dep.data])
                dep_sel = st.multiselect("10. Departament", departamente, placeholder="", key="f_dep")
            except: dep_sel = []

        with f3:
            # 8. Rol UPT - Cele 3 variante solicitate
            rol_sel = st.multiselect("8. Rol UPT", ["Lider", "Coordonator", "Partener"], placeholder="", key="f_rol")
            
            # 9. Statusul proiectului (Sursa: nom_status_proiect)
            try:
                res_st = supabase.table("nom_status_proiect").select("status_contract_proiect").execute()
                statusuri = [s['status_contract_proiect'] for s in res_st.data]
                status_sel = st.multiselect("9. Statusul proiectului", statusuri, placeholder="", key="f_status")
            except: status_sel = []

        st.write("---")
        st.info(f"Interogare pregătită pentru: {', '.join(tipuri_sel)}")

# ==========================================
# CALEA 2: ADMIN (IZOLATĂ)
# ==========================================
elif calea_activa == "admin":
    st.info("Secțiune Administrare activă.")
