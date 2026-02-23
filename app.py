import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 1. CONFIGURARE & DISPECER (ROUTING) - ESENȚIAL!
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide")

# Liniile de mai jos citesc "biletul" din URL (rezolvă NameError)
query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

# Conectare API Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Stil Vizual (Păstrat din IDBDC Protocol)
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
# CALEA 1: EXPLORATOR DE DATE (Public)
# ==========================================
if calea_activa == "explorator":
    # i) Titlul centrat (Cerința ta)
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de Date IDBDC</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Sistem de interogare rapidă a informațiilor de cercetare</p>", unsafe_allow_html=True)
    st.write("---")

    # i) Alege categoria de informații
    st.markdown("### i) Alege categoria de informații")
    try:
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        categorii = [item["denumire_categorie"] for item in res_cat.data]
        cat_selectata = st.selectbox("Selectați categoria:", ["---"] + categorii, label_visibility="collapsed", key="exp_cat")

        # i1) Dacă alege Contracte & Proiecte
        if cat_selectata == "Contracte & Proiecte":
            st.write("")
            st.markdown("### i1.1) Alege tipul de contract sau proiect")
            
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            tipuri = [item["acronim_contracte_proiecte"] for item in res_tip.data]
            tip_ales = st.selectbox("Selectați tipul (FDI, PNRR etc.):", ["---"] + tipuri, label_visibility="collapsed", key="exp_tip")

            if tip_ales != "---":
                tabel_tinta = f"base_proiecte_{tip_ales.lower()}"
                res_date = supabase.table(tabel_tinta).select("*").execute()
                df = pd.DataFrame(res_date.data)

                if not df.empty:
                    st.write("---")
                    st.markdown("#### Filtre de rafinare situație:")
                    
                    # Integram cele 3 casete (An, ID, Director, Dept)
                    f1, f2, f3 = st.columns(3)
                    
                    with f1:
                        ani = sorted(df['an_referinta'].unique().tolist()) if 'an_referinta' in df.columns else []
                        an_selectat = st.multiselect("An referință:", ani)
                        id_cautat = st.text_input("Cod Identificare / Nr. Contract:")

                    with f2:
                        try:
                            res_dir = supabase.table("com_echipe_proiecte").select("nume_prenume_membru").eq("reprezinta_idbdc", "DA").execute()
                            directori = sorted(list(set([d['nume_prenume_membru'] for d in res_dir.data])))
                            director_ales = st.multiselect("Director Proiect (IDBDC):", directori)
                        except:
                            director_ales = []

                    with f3:
                        depts = sorted(df['departament'].unique().tolist()) if 'departament' in df.columns else []
                        dept_ales = st.multiselect("Departament:", depts)

                    # LOGICA FILTRARE
                    if an_selectat: df = df[df['an_referinta'].isin(an_selectat)]
                    if id_cautat: df = df[df['cod_identificare'].astype(str).str.contains(id_cautat, case=False, na=False)]
                    if director_ales:
                        if 'director_proiect' in df.columns:
                            df = df[df['director_proiect'].isin(director_ales)]
                    if dept_ales: df = df[df['departament'].isin(dept_ales)]

                    st.write("---")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.download_button("📥 Descarcă Raportul", df.to_csv(index=False), f"raport_{tip_ales.lower()}.csv")
    except Exception as e:
        st.error(f"Eroare sistem: {e}")

# ==========================================
# CALEA 2: ADMIN (Consola ta de dimineață)
# ==========================================
elif calea_activa == "admin":
    # Logica ta de parole rămâne aici...
    st.markdown("<h1 style='text-align: center;'>🛡️ Administrare IDBDC</h1>", unsafe_allow_html=True)
    st.info("Utilizați Sidebar-ul pentru identificare.")

# ==========================================
# CALEA 3: AI (Brainstorming)
# ==========================================
elif calea_activa == "ai":
    st.markdown("<h1 style='text-align: center;'>🧠 Brainstorming AI</h1>", unsafe_allow_html=True)
