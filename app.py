import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 1. CONFIGURARE & DISPECER (ROUTING) - REZOLVĂ NAMEERROR
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide")

# Citim destinația din link (URL)
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
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #003366 !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CALEA 1: EXPLORATOR DE DATE (Public)
# ==========================================
if calea_activa == "explorator":
    # i) Titlu centrat și scurtat
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de date</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Sistem de interogare rapidă a informațiilor de cercetare</p>", unsafe_allow_html=True)
    st.write("---")

    # ii) Organizare pe coloane pentru Selecția Principală (Fără i)
    col1, col2, col3 = st.columns(3)

    with col1:
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
            categorii = [item["denumire_categorie"] for item in res_cat.data]
            cat_selectata = st.selectbox("Alege categoria de informații:", ["---"] + categorii, key="exp_cat")
        except:
            st.error("Eroare la încărcarea nomenclatorului.")
            cat_selectata = "---"

    with col2:
        tip_ales = "---"
        if cat_selectata == "Contracte & Proiecte":
            try:
                res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                tipuri = [item["acronim_contracte_proiecte"] for item in res_tip.data]
                tip_ales = st.selectbox("Alege tipul de proiect:", ["---"] + tipuri, key="exp_tip")
            except:
                st.error("Eroare la încărcarea tipurilor.")

    with col3:
        # Rezervat pentru alte filtre viitoare (ex: Sursă finanțare)
        if tip_ales != "---":
            st.write("") # Spațiu estetic

    # iii) Rafinare interogare pe coloane
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
                    # Filtru An și ID
                    ani = sorted(df['an_referinta'].unique().tolist()) if 'an_referinta' in df.columns else []
                    an_sel = st.multiselect("An referință:", ani)
                    id_sel = st.text_input("Cod / Nr. Contract:")

                with f2:
                    # Filtru Director (doar cei cu bifa DA în com_echipe_proiecte)
                    try:
                        res_dir = supabase.table("com_echipe_proiecte").select("nume_prenume_membru").eq("reprezinta_idbdc", "DA").execute()
                        directori = sorted(list(set([d['nume_prenume_membru'] for d in res_dir.data])))
                        dir_sel = st.multiselect("Director Proiect:", directori)
                    except:
                        dir_sel = []

                with f3:
                    # Filtru Departament
                    depts = sorted(df['departament'].unique().tolist()) if 'departament' in df.columns else []
                    dept_sel = st.multiselect("Departament:", depts)

                # --- LOGICA FILTRARE ---
                if an_sel: df = df[df['an_referinta'].isin(an_sel)]
                if id_sel: df = df[df['cod_identificare'].astype(str).str.contains(id_sel, case=False, na=False)]
                if dir_sel:
                    if 'director_proiect' in df.columns:
                        df = df[df['director_proiect'].isin(dir_sel)]
                if dept_sel: df = df[df['departament'].isin(dept_sel)]

                # Tabel rezultate
                st.write("---")
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button("📥 Descarcă rezultatele", df.to_csv(index=False), f"interogare_{tip_ales.lower()}.csv")
            else:
                st.warning("Nu există date pentru selecția făcută.")
        except:
            st.error(f"Tabelul {tabel_tinta} nu a fost găsit.")

# ==========================================
# CALEA 2: ADMIN (Consola de Administrare)
# ==========================================
elif calea_activa == "admin":
    st.markdown("<h1 style='text-align: center;'>🛡️ Consola de Administrare</h1>", unsafe_allow_html=True)
    # Aici rămâne logica ta cu parolele și operatorul (reducem spațiul aici pentru focus pe Explorator)
    st.info("Acces restricționat. Identificați-vă în Sidebar.")

# ==========================================
# CALEA 3: AI (Brainstorming)
# ==========================================
elif calea_activa == "ai":
    st.markdown("<h1 style='text-align: center;'>🧠 Brainstorming AI</h1>", unsafe_allow_html=True)
