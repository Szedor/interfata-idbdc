import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 0. CONFIGURARE & DISPECER (ROUTING)
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
    label { font-size: 14px !important; font-weight: 400 !important; }
    .stMultiSelect [data-baseweb="select"] div[aria-live="polite"] { color: transparent !important; }
    .eroare-idbdc { color: white; background-color: #FF4B4B; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CALEA 1: EXPLORATOR DE DATE
# ==========================================
if calea_activa == "explorator":
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de date</h1>", unsafe_allow_html=True)
    st.write("---")

    c1, c2 = st.columns(2)
    with c1:
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        list_cat = [i["denumire_categorie"] for i in res_cat.data]
        categorii_sel = st.multiselect("1. Categoria de informații:", list_cat, placeholder="", key="f_cat_multi")
    with c2:
        tipuri_sel = []
        if "Contracte & Proiecte" in categorii_sel:
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
            tipuri_sel = st.multiselect("2. Tipul de contract / proiect:", list_tip, placeholder="", key="f_tip_multi")

    if "Contracte & Proiecte" in categorii_sel and tipuri_sel:
        st.write("---")
        st.text_input("5. Titlul proiectului / Obiectul contractului", key="f_titlu")
        f1, f2, f3 = st.columns(3)
        with f1:
            st.text_input("3. ID proiect / Nr. contract", key="f_id")
            st.text_input("4. Acronim proiect", key="f_acro")
        with f2:
            st.number_input("7. Anul de implementare", min_value=2010, max_value=2035, value=2024, key="f_an")
            res_dir = supabase.table("det_resurse_umane").select("nume_prenume").execute()
            directori = sorted(list(set([d['nume_prenume'] for d in res_dir.data])))
            st.multiselect("6. Director de proiect / Responsabil contract", directori, placeholder="", key="f_dir")
            res_dep = supabase.table("nom_departament").select("acronim_departament").execute()
            departamente = sorted([d['acronim_departament'] for d in res_dep.data])
            st.multiselect("10. Departament", departamente, placeholder="", key="f_dep")
        with f3:
            st.multiselect("8. Rol UPT", ["Lider", "Coordonator", "Partener"], placeholder="", key="f_rol")
            res_st = supabase.table("nom_status_proiect").select("status_contract_proiect").execute()
            statusuri = [s['status_contract_proiect'] for s in res_st.data]
            st.multiselect("9. Statusul proiectului", statusuri, placeholder="", key="f_status")

    if "Evenimente stiintifice" in categorii_sel:
        st.write("---")
        st.markdown("##### 🎤 Evenimente științifice")
        ev_cols = st.columns(3)
        with ev_cols[0]:
            res_ev = supabase.table("base_evenimente_stiintifice").select("natura_eveniment").execute()
            tip_ev = sorted(list(set([d['natura_eveniment'] for d in res_ev.data if d['natura_eveniment']])))
            st.multiselect("Tipul de eveniment", tip_ev, placeholder="", key="f_ev_tip")
        with ev_cols[1]:
            st.number_input("Anul desfășurării", min_value=2010, max_value=2035, value=2024, key="f_ev_an")
        with ev_cols[2]:
            res_p = supabase.table("det_resurse_umane").select("nume_prenume").execute()
            pers = sorted(list(set([d['nume_prenume'] for d in res_p.data])))
            st.multiselect("Persoana de contact", pers, placeholder="", key="f_ev_pers")

    if "Proprietate intelectuala" in categorii_sel:
        st.write("---")
        st.markdown("##### 💡 Proprietate intelectuală")
        pi_cols = st.columns(3)
        with pi_cols[0]:
            res_pr = supabase.table("base_prop_intelect").select("tip_proprietate").execute()
            tip_pi = sorted(list(set([d['tip_proprietate'] for d in res_pr.data if d.get('tip_proprietate')])))
            st.multiselect("Tipul de proprietate", tip_pi, placeholder="", key="f_pi_tip")
        with pi_cols[1]:
            st.text_input("Număr înregistrare cerere", key="f_pi_nr")
        with pi_cols[2]:
            res_au = supabase.table("det_resurse_umane").select("nume_prenume").execute()
            aut = sorted(list(set([d['nume_prenume'] for d in res_au.data])))
            st.multiselect("Autor", aut, placeholder="", key="f_pi_autor")

# ==========================================
# CALEA 2: ADMINISTRARE
# ==========================================
elif calea_activa == "admin":
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'>🛡️ Administrare IDBDC</h2>", unsafe_allow_html=True)
        c_st, c_ce, c_dr = st.columns([1, 0.6, 1])
        with c_ce:
            p_in = st.text_input("Parola master:", type="password")
            if st.button("Acces", use_container_width=True):
                if p_in == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
                else: st.markdown("<div class='eroare-idbdc'>Parolă invalidă!</div>", unsafe_allow_html=True)
        st.stop()

    st.sidebar.markdown("### 👤 Operator")
    if not st.session_state.operator_identificat:
        cod_op = st.sidebar.text_input("Cod ID", type="password")
        if cod_op:
            res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_op).execute()
            if res_op.data:
                st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                st.rerun()
            else: st.sidebar.error("Cod invalid!")
        st.stop()
    else:
        st.sidebar.write(f"Salut, {st.session_state.operator_identificat}")
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()

    st.markdown(f"### Panou: {st.session_state.operator_identificat}")
    st.write("---")
