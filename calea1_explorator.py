import streamlit as st
from supabase import create_client, Client

def run():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown("""
    <style>
    .stApp { background-color: #003366; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { color: white !important; }
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #ddd; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #003366 !important; }
    [data-testid="stSidebar"] input { color: #31333F !important; background-color: white !important; }
    label { font-size: 14px !important; font-weight: 400 !important; }
    .stMultiSelect [data-baseweb="select"] div[aria-live="polite"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'> 🔍  Explorator de date</h1>", unsafe_allow_html=True)
    st.write("---")

    c1, c2 = st.columns(2)
    with c1:
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
            list_cat = [i["denumire_categorie"] for i in res_cat.data]
        except:
            list_cat = ["Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"]
        categorii_sel = st.multiselect("1. Categoria de informații:", list_cat, placeholder="", key="main_cat")

    with c2:
        tipuri_sel = []
        if "Contracte & Proiecte" in categorii_sel:
            try:
                res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
                tipuri_sel = st.multiselect("2. Tipul de contract / proiect:", list_tip, placeholder="", key="f_tip_multi")
            except:
                tipuri_sel = []

    if "Contracte & Proiecte" in categorii_sel and tipuri_sel:
        st.write("---")
        st.markdown("#####  📂  Contracte & Proiecte")
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

    if "Evenimente stiintifice" in categorii_sel:
        st.write("---")
        st.markdown("#####  🎤  Evenimente științifice")
        e1, e2, e3 = st.columns(3)
        with e1:
            st.multiselect("Tipul de eveniment", ["Conferinta", "Simpozion", "Workshop"], placeholder="", key="f_ev_tip")
        with e2:
            st.number_input("Anul desfășurării", 2010, 2035, 2024, key="f_ev_an")
        with e3:
            st.multiselect("Persoana de contact", [], placeholder="", key="f_ev_pers")

    if "Proprietate intelectuala" in categorii_sel:
        st.write("---")
        st.markdown("#####  💡  Proprietate intelectuală")
        p1, p2, p3 = st.columns(3)
        with p1:
            st.multiselect("Tipul de proprietate", ["Patent", "Cerere inregistrare", "Model utilitate"], placeholder="", key="f_pi_tip")
        with p2:
            st.text_input("Număr înregistrare cerere", key="f_pi_nr")
        with p3:
            st.multiselect("Autor", [], placeholder="", key="f_pi_autor")
