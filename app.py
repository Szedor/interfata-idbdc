import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 1. INITIALIZARE & DISPECER (ROUTING)
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide")

# Citim destinația din link
query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

# Stil Vizual UPT
st.markdown("""
<style>
    .stApp { background-color: #003366; }
    h1, h2, h3, h4, p, label, .stMarkdown { color: white !important; }
    .stSelectbox label { color: #FFD700 !important; }
</style>
""", unsafe_allow_html=True)

# Conectare Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# ==========================================
# CALEA 1: EXPLORATOR DE DATE (Public)
# ==========================================
if calea_activa == "explorator":
    st.markdown("# 🔍 Explorator de Date IDBDC")
    st.write("Interogare informații de cercetare")
    
    # i) Alege categoria
    try:
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        cat_selectata = st.selectbox("i) Alege categoria de informații:", ["---"] + [item["denumire_categorie"] for item in res_cat.data])

        if cat_selectata == "Contracte & Proiecte":
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            tip_ales = st.selectbox("i1.1) Alege tipul de contract sau proiect:", ["---"] + [item["acronim_contracte_proiecte"] for item in res_tip.data])
            
            if tip_ales != "---":
                st.info(f"Filtre active pentru: {tip_ales}")
                # Aici vom finisa casetele de interogare (An, ID, Director)
    except Exception as e:
        st.error("Eroare la încărcarea datelor.")

# ==========================================
# CALEA 2: CONSOLA DE ADMINISTRARE (Privat)
# ==========================================
elif calea_activa == "admin":
    # Initializare stari securitate
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    # Poarta 1: Parola Master
    if not st.session_state.autorizat_p1:
        st.markdown("## 🛡️ Acces Restricționat")
        p_master = st.text_input("Parola Master:", type="password")
        if st.button("Autorizare"):
            if p_master == "EverDream2SZ":
                st.session_state.autorizat_p1 = True
                st.rerun()
            else: st.error("Parolă incorectă!")
        st.stop()

    # Poarta 2: Identificare Operator
    if not st.session_state.operator_identificat:
        st.sidebar.markdown("### 👤 Identificare")
        cod_op = st.sidebar.text_input("Cod Operator:", type="password")
        if cod_op:
            res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_op).execute()
            if res_op.data:
                st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                st.rerun()
            else: st.sidebar.error("Cod invalid!")
        st.stop()
    else:
        st.sidebar.success(f"Operator: {st.session_state.operator_identificat}")
        if st.sidebar.button("Ieșire"):
            st.session_state.clear()
            st.rerun()

    # Panoul de lucru Admin
    st.markdown(f"## 🛠️ Consola Admin: {st.session_state.operator_identificat}")
    st.write("Sistemul este gata pentru gestionare date.")

# ==========================================
# CALEA 3: BRAINSTORMING AI
# ==========================================
elif calea_activa == "ai":
    st.markdown("# 🧠 Brainstorming AI")
    st.write("Modul dedicat analizei profesorilor.")
