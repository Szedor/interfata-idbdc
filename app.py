import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 0. CONFIGURARE & STIL (PROTOCOL IDBDC)
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
    
    /* Sidebar styling */
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 2px solid #ddd; }
    [data-testid="stSidebar"] label { color: #003366 !important; font-weight: bold !important; }
    
    /* REGLAJ VIZIBILITATE CASETA COD (Alb pe Negru) */
    [data-testid="stSidebar"] input { 
        color: #000000 !important; 
        background-color: #ffffff !important; 
        border: 2px solid #003366 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    
    label { font-size: 14px !important; font-weight: bold !important; }
    .eroare-idbdc { color: white; background-color: #FF4B4B; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 10px; }
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

# ==========================================
# CALEA 2: ADMINISTRARE (CORECTATĂ)
# ==========================================
elif calea_activa == "admin":
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    # PAS 1: PAROLA MASTER (POARTA 1)
    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'>🛡️ Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola master:", type="password", key="p1_pass")
            if st.button("Autorizare acces", use_container_width=True):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
                else: 
                    st.markdown("<div class='eroare-idbdc'>⚠️ Parolă incorectă.</div>", unsafe_allow_html=True)
        st.stop()

    # PAS 2: IDENTIFICARE ECONOMIST (SIDEBAR) - TABELA nom_operatori
    st.sidebar.markdown("### 👤 Identificare Operator")
    if not st.session_state.operator_identificat:
        # Caseta de cod cu stilul CSS de mai sus (Alb cu text Negru)
        cod_in = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod_input")
        
        if cod_in:
            try:
                # Verificăm în tabela nom_operatori, coloana cod_identificare
                res_op = supabase.table("nom_operatori").select("nume_prenume").eq("cod_identificare", cod_in).execute()
                
                if res_op.data and len(res_op.data) > 0:
                    st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                    st.rerun()
                else:
                    st.sidebar.error("Cod operator invalid!")
            except Exception as e:
                st.sidebar.error("Eroare legătură tabelă operatori.")
        st.stop()
    else:
        st.sidebar.success(f"Salut, {st.session_state.operator_identificat}!")
        if st.sidebar.button("Ieșire / Resetare"):
            st.session_state.clear()
            st.rerun()

    # PANOU DE LUCRU (Dupa identificare)
    st.markdown(f"### 🛠️ Panou de Administrare: {st.session_state.operator_identificat}")
    st.write("---")
    col_a, col_b = st.columns(2)
    with col_a:
        try:
            res_c = supabase.table("nom_categorie").select("denumire_categorie").execute()
            l_cat = [i["denumire_categorie"] for i in res_c.data]
            cat_admin = st.selectbox("Selectați Categoria:", ["---"] + l_cat)
        except: st.error("Eroare DB Categorii.")
    
    with col_b:
        if cat_admin == "Contracte & Proiecte":
            try:
                res_s = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                l_sub = [i["acronim_contracte_proiecte"] for i in res_s.data]
                st.selectbox("Tip contract/proiect:", ["---"] + l_sub)
            except: st.error("Eroare DB Subcategorii.")
        else:
            st.selectbox("Tip:", ["---"], disabled=True)
