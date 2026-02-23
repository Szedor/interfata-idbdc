import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 0. CONFIGURARE & STIL (Protocol IDBDC)
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
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 2px solid #ddd; }
    [data-testid="stSidebar"] label { color: #003366 !important; }
    [data-testid="stSidebar"] input { color: #000000 !important; background-color: #ffffff !important; border: 2px solid #003366 !important; }
    label { font-size: 14px !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CALEA 1: EXPLORATOR DE DATE
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

    # CASCADA: Detaliile apar doar dacă Tipul este selectat
    if "Contracte & Proiecte" in categorii_sel and tipuri_sel:
        st.write("---")
        # Fără titlu redundant ("Contracte & Proiecte")
        st.text_input("5. Titlul proiectului / Obiectul contractului", key="f_titlu")
        
        f1, f2, f3 = st.columns(3)
        with f1:
            st.text_input("3. ID proiect / Nr. contract", key="f_id")
            st.text_input("4. Acronim proiect", key="f_acro")
        with f2:
            st.number_input("7. Anul de implementare", 2010, 2035, 2024, key="f_an")
            # Redenumire conform punctului 3
            st.multiselect("6. Director de proiect / Responsabil contract", [], placeholder="", key="f_dir")
            # Plasare sub Director/Responsabil conform punctului 4
            st.text_input("10. Departamentul implicat", key="f_dept")
        with f3:
            st.multiselect("8. Rol UPT", ["Lider", "Coordonator", "Partener"], placeholder="", key="f_rol")
            st.multiselect("9. Statusul proiectului", ["În derulare", "Finalizat"], placeholder="", key="f_status")

    # Logica pentru restul categoriilor (fără titluri redundante)
    if "Evenimente stiintifice" in categorii_sel:
        st.write("---")
        e1, e2, e3 = st.columns(3)
        with e1: st.multiselect("Tipul de eveniment", ["Conferinta", "Simpozion"], key="f_ev_tip")
        with e2: st.number_input("Anul desfășurării", 2010, 2035, 2024, key="f_ev_an")
        with e3: st.multiselect("Persoana de contact", [], key="f_ev_pers")

    if "Proprietate intelectuala" in categorii_sel:
        st.write("---")
        p1, p2, p3 = st.columns(3)
        with p1: st.multiselect("Tipul de proprietate", ["Patent", "Cerere"], key="f_pi_tip")
        with p2: st.text_input("Număr înregistrare", key="f_pi_nr")
        with p3: st.multiselect("Autor", [], key="f_pi_autor")

# CALEA 2 rămâne conform acordului anterior pentru a nu altera logica de identificare.
