import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 0. CONFIGURARE & DISPECER (ROUTING)
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide")

# Parametri URL pentru navigare între pagini
query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

# Conexiune Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Stil Vizual UPT - Optimizat pentru Vizibilitate și Contrast
st.markdown("""
<style>
    /* Fundalul principal al aplicației */
    .stApp { background-color: #003366; }
    
    /* Textele generale pe fundal albastru */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { 
        color: white !important; 
    }
    
    /* Stil Sidebar pentru contrast */
    [data-testid="stSidebar"] { 
        background-color: #f8f9fa !important; 
        border-right: 2px solid #ddd; 
    }
    
    /* Textele din Sidebar (Negru pe Gri deschis) */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { 
        color: #003366 !important; 
    }
    
    /* REGLAJ VIZIBILITATE CASETE INPUT SIDEBAR */
    /* Fundal alb, text negru și border vizibil pentru caseta de identificare */
    [data-testid="stSidebar"] input { 
        color: #000000 !important; 
        background-color: #ffffff !important; 
        border: 2px solid #003366 !important;
        font-weight: bold !important;
    }

    label { font-size: 14px !important; font-weight: bold !important; }
    .eroare-idbdc { color: white; background-color: #FF4B4B; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CALEA 1: EXPLORATOR DE DATE (Public)
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
        categorii_sel = st.multiselect("1. Categoria de informații:", list_cat, placeholder="Selectați...", key="main_cat")

    with c2:
        tipuri_sel = []
        if "Contracte & Proiecte" in categorii_sel:
            try:
                res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
                tipuri_sel = st.multiselect("2. Tipul de contract / proiect:", list_tip, placeholder="Selectați...", key="f_tip_multi")
            except: tipuri_sel = []

    # Afișare câmpuri specifice pentru Contracte & Proiecte
    if "Contracte & Proiecte" in categorii_sel and tipuri_sel:
        st.write("---")
        st.markdown("##### 📂 Detalii Căutare Contracte & Proiecte")
        st.text_input("5. Titlul proiectului / Obiectul contractului", key="f_titlu")
        f1, f2, f3 = st.columns(3)
        with f1:
            st.text_input("3. ID proiect / Nr. contract", key="f_id")
            st.text_input("4. Acronim proiect", key="f_acro")
        with f2:
            st.number_input("7. Anul de implementare", 2010, 2035, 2024, key="f_an")
            st.multiselect("6. Director / Responsabil", [], placeholder="Căutați nume...", key="f_dir")
        with f3:
            st.multiselect("8. Rol UPT", ["Lider", "Coordonator", "Partener"], placeholder="Selectați...", key="f_rol")
            st.multiselect("9. Statusul proiectului", ["În derulare", "Finalizat", "Audit"], placeholder="Selectați...", key="f_status")

# ==========================================
# CALEA 2: ADMINISTRARE (Baza: com_operatori)
# ==========================================
elif calea_activa == "admin":
    # State management pentru sesiune
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    # Pasul 1: Parola Generală (Acces poartă)
    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'>🛡️ Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola de sistem:", type="password", key="p1_pass")
            if st.button("Autorizare acces", use_container_width=True):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
                else: 
                    st.markdown("<div class='eroare-idbdc'>⚠️ Parolă incorectă.</div>", unsafe_allow_html=True)
        st.stop()

    # Pasul 2: Identificare Operator (în Sidebar)
    st.sidebar.markdown("### 👤 Identificare Operator")
    if not st.session_state.operator_identificat:
        # CONEXIUNE CORECTĂ: Verificăm codul în tabela com_operatori, coloana cod_operatori
        cod_in = st.sidebar.text_input("Introduceți Cod Identificare", type="password", key="p2_cod_final")
        
        if cod_in:
            try:
                # Verificare în baza de date
                res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_in).execute()
                
                if res_op.data and len(res_op.data) > 0:
                    st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                    st.rerun()
                else: 
                    st.sidebar.error("Cod operator invalid!")
            except Exception as e:
                st.sidebar.error("Eroare tehnică la verificarea codului.")
        st.stop()
    else:
        # Interfața după logare reușită
        st.sidebar.success(f"Salut, {st.session_state.operator_identificat}!")
        if st.sidebar.button("Ieșire (Resetare Sesiune)"):
            st.session_state.clear()
            st.rerun()

    # Panoul de Administrare (După ce operatorul a fost identificat)
    st.markdown(f"### 🛠️ Panou de Administrare: {st.session_state.operator_identificat}")
    st.write("---")
    
    col_a, col_b = st.columns([1, 1])
    cat_sel = "---"
    with col_a:
        try:
            res_c = supabase.table("nom_categorie").select("denumire_categorie").execute()
            l_cat = [i["denumire_categorie"] for i in res_c.data]
            cat_sel = st.selectbox("Selectați Categoria pentru editare:", ["---"] + l_cat)
        except: st.error("Eroare la încărcarea categoriilor.")
    
    with col_b:
        if cat_sel == "Contracte & Proiecte":
            try:
                res_s = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                l_sub = [i["acronim_contracte_proiecte"] for i in res_s.data]
                st.selectbox("Selectați tipul specific:", ["---"] + l_sub)
            except: st.error("Eroare la încărcarea tipurilor de contracte.")
        else:
            st.selectbox("Tip:", ["---"], disabled=True)
