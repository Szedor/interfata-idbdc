import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 0. CONFIGURARE & DISPECER (ROUTING)
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide")

query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Stil Vizual UPT - ÎNGHEȚAT
st.markdown("""
<style>
    .stApp { background-color: #003366; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { color: white !important; }
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #ddd; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #003366 !important; }
    [data-testid="stSidebar"] input { color: #31333F !important; background-color: white !important; }
    label { font-size: 14px !important; font-weight: 400 !important; }
    /* Elimină textul ajutător de sub multiselect */
    .stMultiSelect [data-baseweb="select"] div[aria-live="polite"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CALEA 1: EXPLORATOR DE DATE
# ==========================================
if calea_activa == "explorator":
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de date</h1>", unsafe_allow_html=True)
    st.write("---")

    # RÂNDUL 1: CATEGORIA ȘI TIPUL
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

    # --- CONCATENARE SECȚIUNI (Rând sub rând) ---
    
    # CONTRACTE
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
            st.multiselect("10. Departament", [], placeholder="", key="f_dep")
        with f3:
            st.multiselect("8. Rol UPT", ["Lider", "Coordonator", "Partener"], placeholder="", key="f_rol")
            st.multiselect("9. Statusul proiectului", [], placeholder="", key="f_status")

    # EVENIMENTE
    if "Evenimente stiintifice" in categorii_sel:
        st.write("---")
        st.markdown("##### 🎤 Evenimente științifice")
        e1, e2, e3 = st.columns(3)
        with e1:
            st.multiselect("Tipul de eveniment", ["Conferinta", "Simpozion"], placeholder="", key="f_ev_tip")
        with e2:
            st.number_input("Anul desfășurării", 2010, 2035, 2024, key="f_ev_an")
        with e3:
            st.multiselect("Persoana de contact", [], placeholder="", key="f_ev_pers")

    # PROPRIETATE INTELECTUALĂ (REPARAT)
    if "Proprietate intelectuala" in categorii_sel:
        st.write("---")
        st.markdown("##### 💡 Proprietate intelectuală")
        p1, p2, p3 = st.columns(3)
        with p1:
            st.multiselect("Tipul de proprietate", ["Patent", "Cerere"], placeholder="", key="f_pi_tip")
        with p2:
            st.text_input("Număr înregistrare cerere", key="f_pi_nr")
        with p3:
            st.multiselect("Autor", [], placeholder="", key="f_pi_autor")

# ==========================================
# CALEA 2: ADMINISTRARE (CONFORM DOCX)
# ==========================================
elif calea_activa == "admin":
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_nume' not in st.session_state: st.session_state.operator_nume = None

    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'>🛡️ Acces Securizat</h2>", unsafe_allow_html=True)
        _, col_c, _ = st.columns([1, 0.5, 1])
        with col_c:
            parola = st.text_input("Parola master:", type="password")
            if st.button("Autorizare"):
                if parola == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
        st.stop()

    st.sidebar.markdown("### 👤 Identificare")
    if not st.session_state.operator_nume:
        cod = st.sidebar.text_input("Cod Identificare", type="password")
        if cod:
            res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod).execute()
            if res_op.data:
                st.session_state.operator_nume = res_op.data[0]['nume_prenume']
                st.rerun()
            else: st.sidebar.error("Cod invalid!")
        st.stop()
    else:
        st.sidebar.write(f"Salut, {st.session_state.operator_nume}!")
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()
    
    st.markdown(f"### Panou de Lucru: {st.session_state.operator_nume}")
