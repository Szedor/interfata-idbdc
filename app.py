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

# Stil Vizual UPT
st.markdown("""
<style>
    .stApp { background-color: #003366; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { color: white !important; }
    label { font-size: 16px !important; font-weight: 400 !important; color: white !important; }
    .stMultiSelect [data-baseweb="select"] div[aria-live="polite"] { color: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CALEA 1: EXPLORATOR DE DATE
# ==========================================
if calea_activa == "explorator":
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de date</h1>", unsafe_allow_html=True)
    st.write("---")

    # 1. CATEGORIA DE INFORMAȚII (Sursa: nom_categorie)
    res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
    list_cat = [i["denumire_categorie"] for i in res_cat.data]
    categorii_sel = st.multiselect("1. Categoria de informații:", list_cat, placeholder="", key="f_cat_multi")

    # --- SECTIUNEA A: CONTRACTE & PROIECTE ---
    if "Contracte & Proiecte" in categorii_sel:
        st.markdown("### 📂 Filtre: Contracte & Proiecte")
        c2_cp = st.columns(1)
        with c2_cp[0]:
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
            tipuri_sel = st.multiselect("2. Tipul de contract / proiect:", list_tip, placeholder="", key="f_tip_multi")

        if tipuri_sel:
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

    # --- SECTIUNEA B: EVENIMENTE STIINTIFICE ---
    if "Evenimente stiintifice" in categorii_sel:
        st.write("---")
        st.markdown("### 🎤 Filtre: Evenimente științifice")
        e1, e2, e3 = st.columns(3)
        with e1:
            # Tip eveniment (Sursa: base_evenimente_stiintifice -> natura_eveniment)
            res_ev = supabase.table("base_evenimente_stiintifice").select("natura_eveniment").execute()
            tipuri_ev = sorted(list(set([d['natura_eveniment'] for d in res_ev.data if d['natura_eveniment']])))
            st.multiselect("Tipul de eveniment", tipuri_ev, placeholder="", key="f_ev_tip")
        with e2:
            # Anul desfasurarii (Interpretare data_inceput / data_sfarsit)
            st.number_input("Anul desfășurării", min_value=2010, max_value=2035, value=2024, key="f_ev_an")
        with e3:
            # Persoana de contact (Sursa: det_resurse_umane -> nume_prenume)
            res_pers = supabase.table("det_resurse_umane").select("nume_prenume").execute()
            persoane = sorted(list(set([d['nume_prenume'] for d in res_pers.data])))
            st.multiselect("Persoana de contact", persoane, placeholder="", key="f_ev_pers")

    # --- SECTIUNEA C: PROPRIETATE INTELECTUALA ---
    if "Proprietate intelectuala" in categorii_sel:
        st.write("---")
        st.markdown("### 💡 Filtre: Proprietate intelectuală")
        p1, p2, p3 = st.columns(3)
        with p1:
            # Tipul de proprietate (Sursa: base_prop_intelect -> tip_proprietate - presupunem coloana conform logicii)
            res_prop = supabase.table("base_prop_intelect").select("tip_proprietate").execute()
            tipuri_prop = sorted(list(set([d['tip_proprietate'] for d in res_prop.data if d['tip_proprietate']])))
            st.multiselect("Tipul de proprietate", tipuri_prop, placeholder="", key="f_pi_tip")
        with p2:
            # Numar inregistrare cerere (Sursa: base_prop_intelect -> cod_identificare)
            st.text_input("Număr înregistrare cerere", key="f_pi_nr")
        with p3:
            # Autor (Sursa: det_resurse_umane -> nume_prenume)
            res_aut = supabase.table("det_resurse_umane").select("nume_prenume").execute()
            autori = sorted(list(set([d['nume_prenume'] for d in res_aut.data])))
            st.multiselect("Autor", autori, placeholder="", key="f_pi_autor")

    st.write("---")
