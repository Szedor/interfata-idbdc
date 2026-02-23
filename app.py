import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 0. CONFIGURARE & DISPECER (ROUTING)
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide") [cite: 8]

query_params = st.query_params [cite: 10]
calea_activa = query_params.get("pagina", "explorator") [cite: 11]

# Conectare API Supabase
url: str = st.secrets["SUPABASE_URL"] [cite: 13]
key: str = st.secrets["SUPABASE_KEY"] [cite: 14]
supabase: Client = create_client(url, key) [cite: 15]

# Stil Vizual UPT (Conform 2.administrare.docx)
st.markdown("""
<style>
    .stApp { background-color: #003366; } [cite: 19]
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { color: white !important; } [cite: 20]
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #ddd; } [cite: 21]
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #003366 !important; } [cite: 22]
    [data-testid="stSidebar"] input { color: #31333F !important; background-color: white !important; } [cite: 23]
    .eroare-idbdc { color: white; background-color: #FF4B4B; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; } [cite: 24]
    /* Elimină "choose options" */
    .stMultiSelect [data-baseweb="select"] div[aria-live="polite"] { display: none; }
</style>
""", unsafe_allow_html=True) [cite: 17, 26]

# ==========================================
# CALEA 1: EXPLORATOR DE DATE (VALIDATĂ)
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

    # Concatenare secțiuni
    if "Contracte & Proiecte" in categorii_sel and tipuri_sel:
        st.write("---")
        st.markdown("##### 📂 Contracte & Proiecte")
        st.text_input("5. Titlul proiectului / Obiectul contractului", key="f_titlu")
        f1, f2, f3 = st.columns(3)
        with f1:
            st.text_input("3. ID proiect / Nr. contract", key="f_id")
            st.text_input("4. Acronim proiect", key="f_acro")
        with f2:
            st.number_input("7. Anul de implementare", 2010, 2035, 2024, key="f_an")
            st.multiselect("6. Director / Responsabil", [], placeholder="", key="f_dir")
        with f3:
            st.multiselect("8. Rol UPT", ["Lider", "Coordonator", "Partener"], placeholder="", key="f_rol")
            st.multiselect("9. Statusul proiectului", [], placeholder="", key="f_status")

    if "Evenimente stiintifice" in categorii_sel:
        st.write("---")
        st.markdown("##### 🎤 Evenimente științifice")
        e1, e2, e3 = st.columns(3)
        with e1: st.multiselect("Tipul de eveniment", ["Conferinta", "Simpozion"], placeholder="", key="f_ev_tip")
        with e2: st.number_input("Anul desfășurării", 2010, 2035, 2024, key="f_ev_an")
        with e3: st.multiselect("Persoana de contact", [], placeholder="", key="f_ev_pers")

    if "Proprietate intelectuala" in categorii_sel:
        st.write("---")
        st.markdown("##### 💡 Proprietate intelectuală")
        p1, p2, p3 = st.columns(3)
        with p1: st.multiselect("Tipul de proprietate", ["Patent", "Cerere"], placeholder="", key="f_pi_tip")
        with p2: st.text_input("Număr înregistrare cerere", key="f_pi_nr")
        with p3: st.multiselect("Autor", [], placeholder="", key="f_pi_autor")

# ==========================================
# CALEA 2: ADMIN (RESTAURATĂ DIN DOCX)
# ==========================================
elif calea_activa == "admin": [cite: 37]
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False [cite: 39]
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None [cite: 40]

    # POARTA 1: ACCES SISTEM [cite: 41]
    if not st.session_state.autorizat_p1: [cite: 42]
        st.markdown("<h1 style='text-align: center; margin-bottom: 0;'> 🛡️ </h1>", unsafe_allow_html=True) [cite: 43]
        st.markdown("<h2 style='text-align: center;'>Sistemul de administrare IDBDC</h2>", unsafe_allow_html=True) [cite: 44]
        col_st, col_ce, col_dr = st.columns([1.3, 0.5, 1.3]) [cite: 45]
        with col_ce:
            st.write("Parola de acces:") [cite: 47]
            parola_introdusa = st.text_input("Parola", type="password", label_visibility="collapsed", key="p1_pass") [cite: 48]
            if st.button("Autorizare acces", use_container_width=True): [cite: 49]
                if parola_introdusa == "EverDream2SZ": [cite: 50]
                    st.session_state.autorizat_p1 = True [cite: 51]
                    st.rerun() [cite: 52]
                else:
                    st.markdown("<div class='eroare-idbdc'> ⚠️ Parolă incorectă.</div>", unsafe_allow_html=True) [cite: 54]
        st.stop() [cite: 55]

    # POARTA 2: IDENTIFICARE (SIDEBAR) [cite: 56]
    st.sidebar.markdown("<h1 style='text-align: center;'> 🛡️👤 </h1>", unsafe_allow_html=True) [cite: 57]
    if not st.session_state.operator_identificat: [cite: 58]
        cod_introdus = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod") [cite: 59]
        if cod_introdus:
            try:
                res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_introdus).execute() [cite: 62]
                if res_op.data:
                    st.session_state.operator_identificat = res_op.data[0]['nume_prenume'] [cite: 64]
                    st.rerun() [cite: 65]
                else: st.sidebar.error("Cod operator invalid!") [cite: 66]
            except Exception as e: st.sidebar.error(f"Eroare DB: {e}") [cite: 67]
        st.stop() [cite: 68]
    else:
        st.sidebar.success(f"Salut, {st.session_state.operator_identificat}!") [cite: 70]
        if st.sidebar.button("Ieșire/Resetare"): [cite: 71]
            st.session_state.clear() [cite: 72]
            st.rerun() [cite: 73]

    # PANOU DE LUCRU [cite: 74]
    st.markdown(f"### Panou de Lucru: {st.session_state.operator_identificat}") [cite: 75]
    st.write("---") [cite: 76]
    col_a, col_b = st.columns([1, 1]) [cite: 77]
    cat_selectata = "---" [cite: 78]
    with col_a:
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute() [cite: 81]
            liste_categorii = [item["denumire_categorie"] for item in res_cat.data] [cite: 82]
            cat_selectata = st.selectbox("Selectați Categoria:", ["---"] + liste_categorii) [cite: 83]
        except: st.error("Eroare la încărcarea categoriilor.") [cite: 84]
    with col_b:
        if cat_selectata == "Contracte & Proiecte": [cite: 86]
            try:
                res_sub = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute() [cite: 88]
                liste_sub = [item["acronim_contracte_proiecte"] for item in res_sub.data] [cite: 89]
                st.selectbox("Selectați tipul de contract sau proiect:", ["---"] + liste_sub) [cite: 90]
            except: st.error("Eroare la încărcarea acronimelor.") [cite: 91]
        else:
            st.selectbox("Selectați tipul:", ["---"], disabled=True) [cite: 93]
