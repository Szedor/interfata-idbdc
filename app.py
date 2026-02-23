import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 0. DISPECERUL (MOTORUL DE NAVIGARE)
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide")

# Aceasta este linia care previne NameError:
query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

# Conectare API Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Stil Vizual General UPT
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
# CALEA 1: EXPLORATOR DE DATE (Public)
# ==========================================
if calea_activa == "explorator":
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de date</h1>", unsafe_allow_html=True)
    st.write("---")

    # GRID SELECTII DE BAZĂ (Punctele 1 și 2)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # 1. Categoria de informatii
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
            categorii = [i["denumire_categorie"] for i in res_cat.data]
            cat_selectata = st.selectbox("Alege categoria de informații:", ["---"] + categorii, key="f_cat")
        except: cat_selectata = "---"

    with c2:
        # 2. Tipul de contract / proiect
        tip_ales = "---"
        if cat_selectata == "Contracte & Proiecte":
            try:
                res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                tipuri = [i["acronim_contracte_proiecte"] for i in res_tip.data]
                tip_ales = st.selectbox("Tipul de contract / proiect:", ["---"] + tipuri, key="f_tip")
            except: pass

    # FILTRE DE RAFINARE (Punctele 3 - 9)
    if tip_ales != "---":
        st.write("---")
        st.markdown("#### Rafinare interogare:")
        
        f1, f2, f3 = st.columns(3)
        tabel_tinta = f"base_proiecte_{tip_ales.lower()}"
        
        try:
            res_data = supabase.table(tabel_tinta).select("*").execute()
            df = pd.DataFrame(res_data.data)

            if not df.empty:
                with f1:
                    # 3, 4, 5 - Căutare text
                    id_sel = st.text_input("3. ID Proiect / Nr. Contract:", key="f_id")
                    acro_sel = st.text_input("4. Acronim proiect:", key="f_acro")
                    titlu_sel = st.text_input("5. Titlu / Obiect contract:", key="f_titlu")

                with f2:
                    # 6. Director (Doar IDBDC)
                    try:
                        res_dir = supabase.table("com_echipe_proiecte").select("nume_prenume_membru").eq("reprezinta_idbdc", "DA").execute()
                        directori = sorted(list(set([d['nume_prenume_membru'] for d in res_dir.data])))
                        dir_sel = st.multiselect("6. Director / Responsabil:", directori, key="f_dir")
                    except: dir_sel = []
                    
                    # 7. Anul
                    ani = sorted(df['an_implementare'].unique().tolist()) if 'an_implementare' in df.columns else []
                    an_sel = st.multiselect("7. Anul de implementare:", ani, key="f_an")

                with f3:
                    # 8. Rolul UPT
                    roluri = sorted(df['rol_upt'].unique().tolist()) if 'rol_upt' in df.columns else ["Coordonator", "Partener"]
                    rol_sel = st.multiselect("8. Rolul UPT:", roluri, key="f_rol")
