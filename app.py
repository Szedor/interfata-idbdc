import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 0. CONFIGURARE & CONECTARE
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide")

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

# Stil Vizual UPT - FIXAT
st.markdown("""
<style>
    .stApp { background-color: #003366; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { color: white !important; }
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #ddd; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #003366 !important; }
    [data-testid="stSidebar"] input { color: #31333F !important; background-color: white !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CALEA 1: EXPLORATOR (CONCATENARE LOGICĂ)
# ==========================================
if calea_activa == "explorator":
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de date</h1>", unsafe_allow_html=True)
    st.write("---")

    # RÂNDUL 1
    c1, c2 = st.columns(2)
    with c1:
        # Încărcare categorii cu protecție
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
            list_cat = [i["denumire_categorie"] for i in res_cat.data]
        except:
            list_cat = ["Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"]
        categorii_sel = st.multiselect("1. Categoria de informații:", list_cat, key="main_cat")

    with c2:
        tipuri_sel = []
        if "Contracte & Proiecte" in categorii_sel:
            try:
                res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
                tipuri_sel = st.multiselect("2. Tipul de contract / proiect:", list_tip, key="f_tip_multi")
            except:
                st.error("Eroare la tabelele de contracte.")

    # --- AFIȘARE DINAMICĂ (CONCATENARE) ---
    
    # 1. CONTRACTE
    if "Contracte & Proiecte" in categorii_sel and tipuri_sel:
        st.write("---")
        st.markdown("##### 📂 Secțiune: Contracte & Proiecte")
        st.text_input("5. Titlul proiectului / Obiectul contractului", key="f_titlu")
        f1, f2, f3 = st.columns(3)
        with f1:
            st.text_input("3. ID proiect / Nr. contract", key="f_id")
            st.text_input("4. Acronim proiect", key="f_acro")
        with f2:
            st.number_input("7. Anul de implementare", 2010, 2035, 2024, key="f_an")
            st.multiselect("6. Director / Responsabil", [], key="f_dir")
            st.multiselect("10. Departament", [], key="f_dep")
        with f3:
            st.multiselect("8. Rol UPT", ["Lider", "Coordonator", "Partener"], key="f_rol")
            st.multiselect("9. Statusul proiectului", [], key="f_status")

    # 2. EVENIMENTE
    if "Evenimente stiintifice" in categorii_sel:
        st.write("---")
        st.markdown("##### 🎤 Secțiune: Evenimente științifice")
        e1, e2, e3 = st.columns(3)
        with e1:
            st.multiselect("Tipul de eveniment", [], key="f_ev_tip")
        with e2:
            st.number_input("Anul desfășurării", 2010, 2035, 2024, key="f_ev_an")
        with e3:
            st.multiselect("Persoana de contact", [], key="f_ev_pers")

    # 3. PROPRIETATE (Aici am reparat eroarea rectorului!)
    if "Proprietate intelectuala" in categorii_sel:
        st.write("---")
        st.markdown("##### 💡 Secțiune: Proprietate intelectuală")
        p1, p2, p3 = st.columns(3)
        with p1:
            # Protecție maximă: dacă baza de date dă eroare, afișăm listă goală, nu oprim scriptul!
            try:
                res_pi = supabase.table("base_prop_intelect").select("tip_proprietate").execute()
                tipuri_pi = sorted(list(set([d['tip_proprietate'] for d in res_pi.data if d.get('tip_proprietate')])))
            except:
                tipuri_pi = []
            st.multiselect("Tipul de proprietate", tipuri_pi, key="f_pi_tip")
        with p2:
            st.text_input("Număr înregistrare cerere", key="f_pi_nr")
        with p3:
            st.multiselect("Autor", [], key="f_pi_autor")

# ==========================================
# CALEA 2: ADMINISTRARE (CONFORM DOCX)
# ==========================================
elif calea_activa == "admin":
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_nume' not in st.session_state: st.session_state.operator_nume = None

    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'>🛡️ Administrare IDBDC</h2>", unsafe_allow_html=True)
        _, col_c, _ = st.columns([1, 0.5, 1])
        with col_c:
            parola = st.text_input("Parola master:", type="password")
            if st.button("Acces"):
                if parola == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
        st.stop()

    # Sidebar pentru identificare operator
    st.sidebar.markdown("### 👤 Operator")
    if not st.session_state.operator_nume:
        cod = st.sidebar.text_input("Cod Identificare", type="password")
        if cod:
            try:
                res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod).execute()
                if res_op.data:
                    st.session_state.operator_nume = res_op.data[0]['nume_prenume']
                    st.rerun()
                else: st.sidebar.error("Cod invalid!")
            except: st.sidebar.error("Eroare Baza de Date!")
        st.stop()
    else:
        st.sidebar.write(f"Salut, {st.session_state.operator_nume}")
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()
