import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 0. MOTORUL DE NAVIGARE (DISPECER)
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
    .stSelectbox label, .stMultiSelect label, .stTextInput label { color: #FFD700 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CALEA 1: EXPLORATOR DE DATE
# ==========================================
if calea_activa == "explorator":
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de date</h1>", unsafe_allow_html=True)
    st.write("---")

    # RÂNDUL 1: SELECȚII PRINCIPALE (Punctele 1 și 2)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # 1. Categoria de informatii
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        categorii = [i["denumire_categorie"] for i in res_cat.data]
        cat_selectata = st.selectbox("1. Categoria de informații:", ["---"] + categorii)

    with c2:
        # 2. Tipul de contract / proiect
        tip_ales = "---"
        if cat_selectata == "Contracte & Proiecte":
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            tipuri = [i["acronim_contracte_proiecte"] for i in res_tip.data]
            tip_ales = st.selectbox("2. Tipul de contract / proiect:", ["---"] + tipuri)

    # RÂNDUL 2: FILTRE SPECIFICE (Doar pentru Contracte & Proiecte)
    if cat_selectata == "Contracte & Proiecte" and tip_ales != "---":
        st.write("---")
        st.markdown(f"#### 🛠️ Rafinare Interogare: {tip_ales}")
        
        # Organizăm punctele 3-9 în 3 coloane
        f1, f2, f3 = st.columns(3)
        
        with f1:
            # 3. ID-ul proiect / Numar contract
            id_sel = st.text_input("3. ID Proiect / Nr. Contract")
            # 4. Acronim proiect / contract
            acro_sel = st.text_input("4. Acronim proiect")
            # 5. Titlul proiect / Obiectul contractului
            titlu_sel = st.text_input("5. Titlu / Obiect contract")

        with f2:
            # 6. Director de proiect / Responsabil contract
            # (Vom popula lista după ce îmi spui sursa exactă, momentan e text)
            dir_sel = st.text_input("6. Director / Responsabil")
            # 7. Anul de implementare
            an_sel = st.multiselect("7. Anul de implementare", [2023, 2024, 2025, 2026])

        with f3:
            # 8. Rolul UPT
            rol_sel = st.multiselect("8. Rolul UPT", ["Coordonator", "Partener", "Subcontractant"])
            # 9. Statusul proiectului / contractului
            status_sel = st.multiselect("9. Status proiect", ["În derulare", "Finalizat", "Inactiv"])

        st.write("---")
        st.info("Aici vor fi afișate datele imediat ce stabilim sursele pentru fiecare casetă.")

# ==========================================
# CALEA 2: ADMIN (IZOLATĂ)
# ==========================================
elif calea_activa == "admin":
    st.markdown("<h2 style='text-align: center;'>🛡️ Administrare IDBDC</h2>", unsafe_allow_html=True)
    st.warning("Secțiune în așteptare pentru a nu interfera cu Exploratorul.")

# ==========================================
# CALEA 3: AI (IZOLATĂ)
# ==========================================
elif calea_activa == "ai":
    st.markdown("<h1 style='text-align: center;'>🧠 Brainstorming AI</h1>", unsafe_allow_html=True)
