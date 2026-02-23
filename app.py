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

# Stil Vizual General UPT
st.markdown("""
<style>
    .stApp { background-color: #003366; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { color: white !important; }
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CALEA 1: EXPLORATOR DE DATE (IZOLARE TOTALĂ)
# ==========================================
if calea_activa == "explorator":
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de date</h1>", unsafe_allow_html=True)
    st.write("---")

    # GRID SELECTII DE BAZĂ (Punctele 1 și 2) cu SELECTIE MULTIPLA
    c1, c2 = st.columns(2)
    
    with c1:
        # 1. Categoria de informatii (Toate cele 3 opțiuni din IDBDC)
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
            list_categorii = [i["denumire_categorie"] for i in res_cat.data]
            categorii_sel = st.multiselect("1. Categoria de informații:", list_categorii, key="f_cat_multi")
        except: 
            st.error("Eroare la citirea categoriilor din IDBDC.")
            categorii_sel = []

    with c2:
        # 2. Tipul de contract / proiect (Cele 8 variante din IDBDC)
        tipuri_sel = []
        if "Contracte & Proiecte" in categorii_sel:
            try:
                res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                list_tipuri = [i["acronim_contracte_proiecte"] for i in res_tip.data]
                tipuri_sel = st.multiselect("2. Tipul de contract / proiect:", list_tipuri, key="f_tip_multi")
            except: 
                st.error("Eroare la citirea tipurilor din IDBDC.")

    # FILTRE DE RAFINARE (Punctele 3 - 9)
    # Apar dacă a fost selectat cel puțin un tip de proiect (FDI, PNRR etc.)
    if tipuri_sel:
        st.write("---")
        st.markdown(f"#### 🛠️ Rafinare interogare pentru: {', '.join(tipuri_sel)}")
        
        f1, f2, f3 = st.columns(3)
        
        with f1:
            # 3, 4, 5 - Căutare text (Conform Mapării tale)
            id_sel = st.text_input("3. ID proiect / Nr. contract", key="f_id")
            acro_sel = st.text_input("4. Acronim proiect", key="f_acro")
            titlu_sel = st.text_input("5. Titlul proiectului / Obiect contract", key="f_titlu")

        with f2:
            # 6. Director (Sursă: com_echipe_proiecte unde reprezinta_idbdc = 'DA')
            try:
                res_dir = supabase.table("com_echipe_proiecte").select("nume_prenume_membru").eq("reprezinta_idbdc", "DA").execute()
                directori = sorted(list(set([d['nume_prenume_membru'] for d in res_dir.data])))
                dir_sel = st.multiselect("6. Director / Responsabil:", directori, key="f_dir")
            except: dir_sel = []
            
            # 7. Anul de implementare (Aici vom aplica logica de intervale la Pasul Următor)
            an_sel = st.number_input("7. Anul de implementare", min_value=2010, max_value=2030, value=2024, key="f_an")

        with f3:
            # 8. Rolul UPT (Din tabelele base_...)
            rol_sel = st.multiselect("8. Rolul UPT:", ["Coordonator", "Partener"], key="f_rol")
            
            # 9. Statusul proiectului
            status_sel = st.multiselect("9. Statusul proiectului:", ["În derulare", "Finalizat", "Inactiv"], key="f_status")

        st.write("---")
        st.info("După ce fixăm detaliile, aici va rula scriptul final pentru extragerea datelor combinate.")

# ==========================================
# CALEA 2: ADMIN (IZOLARE TOTALĂ CU PORȚI)
# ==========================================
elif calea_activa == "admin":
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    
    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'>🛡️ Administrare IDBDC</h2>", unsafe_allow_html=True)
        col_s, col_c, col_d = st.columns([1.3, 0.6, 1.3])
        with col_c:
            p_master = st.text_input("Parola Master", type="password")
            if st.button("Autorizare"):
                if p_master == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
        st.stop()
    
    st.success("Zona de Administrare este activă și izolată.")

# ==========================================
# CALEA 3: AI
# ==========================================
elif calea_activa == "ai":
    st.markdown("<h1 style='text-align: center;'>🧠 Brainstorming AI</h1>", unsafe_allow_html=True)
