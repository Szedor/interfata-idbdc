import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 0. CONFIGURARE & STIL (CONTRAST MAXIM CONFORM PROTOCOL)
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide")

query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.markdown("""
<style>
    .stApp { background-color: #003366; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { color: white !important; }
    
    /* SIDEBAR - STILIZARE VIZIBILA */
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 3px solid #ddd; }
    
    /* Titlul casetei (label) - Albastru inchis pe Gri deschis */
    [data-testid="stSidebar"] label p { 
        color: #003366 !important; 
        font-weight: 900 !important; 
        font-size: 16px !important;
    }
    
    /* Caseta input - Alb pur cu text Negru intens */
    [data-testid="stSidebar"] input { 
        color: #000000 !important; 
        background-color: #ffffff !important; 
        border: 2px solid #003366 !important;
    }
    
    /* EROARE - ROSU PUR PE ALB (Fara roz!) */
    .eroare-idbdc-rosu { 
        color: #ffffff !important; 
        background-color: #ff0000 !important; 
        padding: 10px; 
        border-radius: 4px; 
        text-align: center; 
        font-weight: bold;
        border: 2px solid #8b0000;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CALEA 1: EXPLORATOR (ÎNGHEȚAT)
# ==========================================
if calea_activa == "explorator":
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de date</h1>", unsafe_allow_html=True)
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
            list_cat = [i["denumire_categorie"] for i in res_cat.data]
        except: list_cat = ["Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"]
        categorii_sel = st.multiselect("1. Categoria de informații:", list_cat, placeholder="", key="main_cat")
    with c2:
        tipuri_sel = []
        if "Contracte & Proiecte" in categorii_sel:
            try:
                res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
                tipuri_sel = st.multiselect("2. Tipul de contract / proiect:", list_tip, placeholder="", key="f_tip_multi")
            except: tipuri_sel = []

    if "Contracte & Proiecte" in categorii_sel and tipuri_sel:
        st.write("---")
        st.text_input("5. Titlul proiectului / Obiectul contractului", key="f_titlu")
        f1, f2, f3 = st.columns(3)
        with f1:
            st.text_input("3. ID proiect / Nr. contract", key="f_id")
            st.text_input("4. Acronim proiect", key="f_acro")
        with f2:
            st.number_input("7. Anul de implementare", 2010, 2035, 2024, key="f_an")
            st.multiselect("6. Director de proiect / Responsabil contract", [], placeholder="", key="f_dir")
            st.text_input("10. Departamentul implicat", key="f_dept")
        with f3:
            st.multiselect("8. Rol UPT", ["Lider", "Coordonator", "Partener"], placeholder="", key="f_rol")
            st.multiselect("9. Statusul proiectului", ["În derulare", "Finalizat"], placeholder="", key="f_status")

# ==========================================
# CALEA 2: ADMINISTRARE (CONFIRMATA)
# ==========================================
elif calea_activa == "admin":
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    # POARTA 1: MASTER
    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'>🛡️ Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola master:", type="password", key="p1_pass")
            if st.button("Autorizare acces", use_container_width=True):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
