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

# Stil Vizual UPT - Forțăm culorile și fonturile să fie unitare
st.markdown("""
<style>
    .stApp { background-color: #003366; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { color: white !important; }
    /* Eliminăm gri-ul textului ajutător din multiselect pentru a lăsa doar eticheta deasupra */
    .stMultiSelect [data-baseweb="select"] div[aria-live="polite"] { color: transparent !important; }
    .stMultiSelect span { color: #31333F !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CALEA 1: EXPLORATOR DE DATE (IZOLARE)
# ==========================================
if calea_activa == "explorator":
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de date</h1>", unsafe_allow_html=True)
    st.write("---")

    # GRID SELECȚIE CATEGORIE ȘI TIP (Rândul 1)
    c1, c2 = st.columns(2)
    with c1:
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        list_cat = [i["denumire_categorie"] for i in res_cat.data]
        categorii_sel = st.multiselect("1. Categoria de informații:", list_cat, placeholder="Opțiuni de alegere", key="f_cat_multi")

    with c2:
        tipuri_sel = []
        if "Contracte & Proiecte" in categorii_sel:
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
            tipuri_sel = st.multiselect("2. Tipul de contract / proiect:", list_tip, placeholder="Opțiuni de alegere", key="f_tip_multi")

    # FILTRE DE RAFINARE
    if tipuri_sel:
        st.write("---")
        
        # 5. TITLUL (Pe tot ecranul, font unitar cu label-urile Streamlit)
        st.markdown("<label style='font-size: 16px; font-weight: 400;'>5. Titlul proiectului / Obiectul contractului</label>", unsafe_allow_html=True)
        titlu_sel = st.text_input("Introduceți titlu", label_visibility="collapsed", key="f_titlu")
        
        st.write("") # Spațiu

        # Cele 3 coloane pentru restul filtrelor
        f1, f2, f3 = st.columns(3)
        
        with f1:
            # 3. ID
            id_sel = st.text_input("3. ID proiect / Nr. contract", key="f_id")
            # 4. Acronim
            acro_sel = st.text_input("4. Acronim proiect", key="f_acro")

        with f2:
            # 7. Anul de implementare
            # Aici vom integra ulterior logica de calcul din Word
            an_sel = st.number_input("7. Anul de implementare", min_value=2010, max_value=2030, value=2024, key="f_an")
            
            # 6. Director (POZIȚIONAT SUB AN conform solicitării)
            try:
                res_dir = supabase.table("com_echipe_proiecte").select("nume_prenume_membru").eq("reprezinta_idbdc", "DA").execute()
                directori = sorted(list(set([d['nume_prenume_membru'] for d in res_dir.data])))
                dir_sel = st.multiselect("6. Director de proiect / Responsabil contract:", directori, placeholder="Opțiuni de alegere", key="f_dir")
            except: dir_sel = []

        with f3:
            # 8. Rol UPT (Eticheta deasupra, fără text în interior)
            rol_sel = st.multiselect("8. Rol UPT", ["Coordonator", "Partener"], placeholder="Opțiuni de alegere", key="f_rol")
            
            # 9. Statusul proiectului (Eticheta deasupra, fără text în interior)
            status_sel = st.multiselect("9. Statusul proiectului", ["În derulare", "Finalizat"], placeholder="Opțiuni de alegere", key="f_status")

        st.write("---")
        st.info(f"Interogare activă pentru: {', '.join(tipuri_sel)}")

# ==========================================
# CALEA 2: ADMIN (Rămâne izolată)
# ==========================================
elif calea_activa == "admin":
    st.info("Secțiune de administrare izolată. Identificarea se face în Sidebar.")
