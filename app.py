import streamlit as st
from supabase import create_client, Client

def run():
    # Conexiune Supabase locală pentru acest modul
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    # Stil Vizual UPT - ÎNGHEȚAT [cite: 13, 14]
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

    st.markdown("<h1 style='text-align: center;'> 🔍  Explorator de date</h1>", unsafe_allow_html=True) [cite: 30]
    st.write("---") [cite: 31]

    # RÂNDUL 1: CATEGORIA ȘI TIPUL [cite: 32]
    c1, c2 = st.columns(2) [cite: 33]
    with c1:
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute() [cite: 36]
            list_cat = [i["denumire_categorie"] for i in res_cat.data] [cite: 37]
        except:
            list_cat = ["Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"] [cite: 39]
        categorii_sel = st.multiselect("1. Categoria de informații:", list_cat, placeholder="", key="main_cat") [cite: 40]

    with c2:
        tipuri_sel = [] [cite: 42]
        if "Contracte & Proiecte" in categorii_sel: [cite: 43]
            try:
                res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute() [cite: 45]
                list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data] [cite: 46]
                tipuri_sel = st.multiselect("2. Tipul de contract / proiect:", list_tip, placeholder="", key="f_tip_multi") [cite: 47]
            except:
                tipuri_sel = [] [cite: 49]

    # SECTIUNEA: CONTRACTE [cite: 51]
    if "Contracte & Proiecte" in categorii_sel and tipuri_sel: [cite: 52]
        st.write("---") [cite: 53]
        st.markdown("#####  📂  Contracte & Proiecte") [cite: 54]
        st.text_input("5. Titlul proiectului / Obiectul contractului", key="f_titlu") [cite: 55]
        f1, f2, f3 = st.columns(3) [cite: 56]
        with f1:
            st.text_input("3. ID proiect / Nr. contract", key="f_id") [cite: 58]
            st.text_input("4. Acronim proiect", key="f_acro") [cite: 59]
        with f2:
            st.number_input("7. Anul de implementare", 2010, 2035, 2024, key="f_an") [cite: 61]
            st.multiselect("6. Director / Responsabil", [], placeholder="", key="f_dir") [cite: 62]
            st.multiselect("10. Departament", [], placeholder="", key="f_dep") [cite: 63]
        with f3:
            st.multiselect("8. Rol UPT", ["Lider", "Coordonator", "Partener"], placeholder="", key="f_rol") [cite: 65]
            st.multiselect("9. Statusul proiectului", [], placeholder="", key="f_status") [cite: 66]

    # SECTIUNEA: EVENIMENTE [cite: 67]
    if "Evenimente stiintifice" in categorii_sel: [cite: 68]
        st.write("---") [cite: 69]
        st.markdown("#####  🎤  Evenimente științifice") [cite: 70]
        e1, e2, e3 = st.columns(3) [cite: 71]
        with e1:
            st.multiselect("Tipul de eveniment", ["Conferinta", "Simpozion", "Workshop"], placeholder="", key="f_ev_tip") [cite: 73]
        with e2:
            st.number_input("Anul desfășurării", 2010, 2035, 2024, key="f_ev_an") [cite: 75]
        with e3:
            st.multiselect("Persoana de contact", [], placeholder="", key="f_ev_pers") [cite: 77]

    # SECTIUNEA: PROPRIETATE INTELECTUALĂ [cite: 78]
    if "Proprietate intelectuala" in categorii_sel: [cite: 79]
        st.write("---") [cite: 80]
        st.markdown("#####  💡  Proprietate intelectuală") [cite: 81]
        p1, p2, p3 = st.columns(3) [cite: 82]
        with p1:
            st.multiselect("Tipul de proprietate", ["Patent", "Cerere inregistrare", "Model utilitate"], placeholder="", key="f_pi_tip") [cite: 84]
        with p2:
            st.text_input("Număr înregistrare cerere", key="f_pi_nr") [cite: 86]
        with p3:
            st.multiselect("Autor", [], placeholder="", key="f_pi_autor") [cite: 88]
