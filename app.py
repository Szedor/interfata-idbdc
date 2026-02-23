import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 1. MOTORUL DE NAVIGARE (DISPECERUL)
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
    st.markdown("<p style='text-align: center;'>Sistem de interogare rapidă a informațiilor de cercetare</p>", unsafe_allow_html=True)
    st.write("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
            cat_selectata = st.selectbox("Alege categoria de informații:", ["---"] + [item["denumire_categorie"] for item in res_cat.data], key="exp_cat")
        except: cat_selectata = "---"

    with col2:
        tip_ales = "---"
        if cat_selectata == "Contracte & Proiecte":
            try:
                res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                tip_ales = st.selectbox("Alege tipul de proiect:", ["---"] + [item["acronim_contracte_proiecte"] for item in res_tip.data], key="exp_tip")
            except: pass

    if tip_ales != "---":
        st.write("---")
        st.markdown("#### Rafinare interogare:")
        f1, f2, f3 = st.columns(3)
        tabel_tinta = f"base_proiecte_{tip_ales.lower()}"
        try:
            res_date = supabase.table(tabel_tinta).select("*").execute()
            df = pd.DataFrame(res_date.data)
            if not df.empty:
                with f1:
                    ani = sorted(df['an_referinta'].unique().tolist()) if 'an_referinta' in df.columns else []
                    an_sel = st.multiselect("An referință:", ani)
                    id_sel = st.text_input("Cod / Nr. Contract:")
                with f2:
                    res_dir = supabase.table("com_echipe_proiecte").select("nume_prenume_membru").eq("reprezinta_idbdc", "DA").execute()
                    directori = sorted(list(set([d['nume_prenume_membru'] for d in res_dir.data])))
                    dir_sel = st.multiselect("Director Proiect:", directori)
                with f3:
                    depts = sorted(df['departament'].unique().tolist()) if 'departament' in df.columns else []
                    dept_sel = st.multiselect("Departament:", depts)

                if an_sel: df = df[df['an_referinta'].isin(an_sel)]
                if id_sel: df = df[df['cod_identificare'].astype(str).str.contains(id_sel, case=False, na=False)]
                if dir_sel and 'director_proiect' in df.columns: df = df[df['director_proiect'].isin(dir_sel)]
                if dept_sel: df = df[df['departament'].isin(dept_sel)]

                st.write("---")
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button("📥 Descarcă rezultatele", df.to_csv(index=False), f"export_{tip_ales.lower()}.csv")
        except: st.error("Eroare la accesarea datelor.")

# ==========================================
# CALEA 2: ADMIN (REPARAT - PORȚI DE ACCES)
# ==========================================
elif calea_activa == "admin":
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    # POARTA 1: ACCES MASTER
    if not st.session_state.autorizat_p1:
        st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🛡️</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>Sistemul de administrare IDBDC</h2>", unsafe_allow_html=True)
        col_s, col_c, col_d = st.columns([1.3, 0.6, 1.3])
        with col_c:
            st.write("Parola Master:")
            p_introdusa = st.text_input("Parola", type="password", label_visibility="collapsed", key="p1_pass")
            if st.button("Autorizare", use_container_width=True):
                if p_introdusa == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
                else: st.markdown("<div class='eroare-idbdc'>⚠️ Parolă incorectă.</div>", unsafe_allow_html=True)
        st.stop()

    # POARTA 2: IDENTIFICARE OPERATOR
    st.sidebar.markdown("<h1 style='text-align: center;'>🛡️👤</h1>", unsafe_allow_html=True)
    if not st.session_state.operator_identificat:
        cod_introdus = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod")
        if cod_introdus:
            res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_introdus).execute()
            if res_op.data:
                st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                st.rerun()
            else: st.sidebar.error("Cod invalid!")
        st.stop()
    else:
        st.sidebar.success(f"Operator: {st.session_state.operator_identificat}")
        if st.sidebar.button("Ieșire/Reset"):
            st.session_state.clear()
            st.rerun()

    # ZONA DE LUCRU ADMIN
    st.markdown(f"### Panou de Lucru: {st.session_state.operator_identificat}")
    st.write("---")
    # Logica ta de selecție Categorii/Subcategorii pentru Admin
    col_a, col_b = st.columns(2)
    with col_a:
        res_c = supabase.table("nom_categorie").select("denumire_categorie").execute()
        cat_adm = st.selectbox("Selectați Categoria (Admin):", ["---"] + [i["denumire_categorie"] for i in res_c.data])
    with col_b:
        if cat_adm == "Contracte & Proiecte":
            res_s = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            st.selectbox("Tip proiect (Admin):", ["---"] + [i["acronim_contracte_proiecte"] for i in res_s.data])

# ==========================================
# CALEA 3: AI
# ==========================================
elif calea_activa == "ai":
    st.markdown("<h1 style='text-align: center;'>🧠 Brainstorming AI</h1>", unsafe_allow_html=True)
