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

# Stil Vizual UPT
st.markdown("""
<style>
    .stApp { background-color: #003366; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { color: white !important; }
    /* Ajustare font etichete pentru a fi unitare */
    label { font-size: 16px !important; font-weight: 400 !important; }
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
        # Am pus label clar deasupra și placeholder gol pentru a nu apărea scris în casetă
        categorii_sel = st.multiselect("1. Categoria de informații:", list_cat, placeholder="", key="f_cat_multi")

    with c2:
        tipuri_sel = []
        if "Contracte & Proiecte" in categorii_sel:
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
            tipuri_sel = st.multiselect("2. Tipul de contract / proiect:", list_tip, placeholder="", key="f_tip_multi")

    # FILTRE DE RAFINARE (Apar doar dacă s-a ales Tipul)
    if tipuri_sel:
        st.write("---")
        
        # 5. TITLUL PROIECTULUI - Pe tot ecranul, cu cifra 5 și font similar cu restul
        titlu_sel = st.text_input("5. Titlul proiectului / Obiectul contractului", key="f_titlu")
        
        st.write("") # Spațiu între rânduri

        # Cele 3 coloane pentru restul criteriilor
        f1, f2, f3 = st.columns(3)
        
        with f1:
            # 3. ID / Nr. Contract
            id_sel = st.text_input("3. ID proiect / Nr. contract", key="f_id")
            # 4. Acronim
            acro_sel = st.text_input("4. Acronim proiect", key="f_acro")

        with f2:
            # 7. Anul de implementare
            an_sel = st.number_input("7. Anul de implementare", min_value=2010, max_value=2035, value=2024, key="f_an")
            
            # 6. Director de proiect / Responsabil contract - MUTAT SUB AN conform solicitării
            try:
                res_dir = supabase.table("com_echipe_proiecte").select("nume_prenume_membru").eq("reprezinta_idbdc", "DA").execute()
                directori = sorted(list(set([d['nume_prenume_membru'] for d in res_dir.data])))
                dir_sel = st.multiselect("6. Director de proiect / Responsabil contract", directori, placeholder="", key="f_dir")
            except:
                dir_sel = st.multiselect("6. Director de proiect / Responsabil contract", [], placeholder="", key="f_dir_err")

        with f3:
            # 8. Rol UPT - Denumirea criteriului deasupra, fără text în casetă
            rol_sel = st.multiselect("8. Rol UPT", ["Coordonator", "Partener"], placeholder="", key="f_rol")
            
            # 9. Statusul proiectului - Denumirea criteriului deasupra, fără text în casetă
            status_sel = st.multiselect("9. Statusul proiectului", ["În derulare", "Finalizat"], placeholder="", key="f_status")

        st.write("---")
        st.info(f"Interogare pregătită pentru: {', '.join(tipuri_sel)}")

# ==========================================
# CALEA 2: ADMIN (IZOLATĂ)
# ==========================================
elif calea_activa == "admin":
    st.info("Secțiunea Administrare este activă. Urmați pașii de autentificare din Sidebar.")
