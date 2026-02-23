import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 1. DISPECERUL DE PAGINI (ROUTING)
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide")

# Citim destinația din link (URL)
query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

# Stil Vizual UPT
st.markdown("""
<style>
    .stApp { background-color: #003366; }
    h1, h2, h3, h4, p, label { color: white !important; }
    .stSelectbox label, .stMultiSelect label, .stTextInput label { font-weight: bold; color: #FFD700 !important; }
</style>
""", unsafe_allow_html=True)

# Conectare Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# ==========================================
# CALEA 1: EXPLORATOR DE DATE (PENTRU VIZITATORI)
# ==========================================
if calea_activa == "explorator":
    st.markdown("# 🔍 Explorator de Date IDBDC")
    st.write("Interogare informații publice de cercetare")
    st.write("---")

    # i) Titlul: Alege categoria de informatii
    st.markdown("### i) Alege categoria de informații")
    try:
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        categorii = [item["denumire_categorie"] for item in res_cat.data]
        cat_selectata = st.selectbox("Selectați categoria:", ["---"] + categorii, label_visibility="collapsed")
    except:
        st.error("Eroare la încărcarea nomenclatorului de categorii.")
        cat_selectata = "---"

    # i1) Daca alege Contracte & Proiecte
    if cat_selectata == "Contracte & Proiecte":
        st.write("")
        st.markdown("### i1.1) Alege tipul de contract sau proiect")
        
        try:
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            tipuri = [item["acronim_contracte_proiecte"] for item in res_tip.data]
            tip_ales = st.selectbox("Selectați tipul (FDI, PNRR etc.):", ["---"] + tipuri, label_visibility="collapsed")
            
            if tip_ales != "---":
                # Determinăm tabelul bază
                tabel_tinta = f"base_proiecte_{tip_ales.lower()}"
                
                # Preluăm datele
                res_date = supabase.table(tabel_tinta).select("*").execute()
                df = pd.DataFrame(res_date.data)

                if not df.empty:
                    st.write("---")
                    st.markdown("#### Casete de interogare specifice:")
                    
                    c1, c2, c3 = st.columns(3)
                    
                    with c1:
                        # Filtru An Referință
                        ani = sorted(df['an_referinta'].unique().tolist()) if 'an_referinta' in df.columns else []
                        an_filtru = st.multiselect("Anul referință:", ani)
                        
                        # Filtru ID/Nr Contract (din cod_identificare)
                        id_filtru = st.text_input("Cod identitificare / Nr. Contract:")

                    with c2:
                        # Filtru Director de Proiect (cu bifa reprezinta_idbdc = DA)
                        try:
                            res_dir = supabase.table("com_echipe_proiecte").select("nume_prenume_membru").eq("reprezinta_idbdc", "DA").execute()
                            directori = sorted(list(set([d['nume_prenume_membru'] for d in res_dir.data])))
                            dir_filtru = st.multiselect("Director de proiect (IDBDC):", directori)
                        except:
                            dir_filtru = []
                            st.warning("Nu am putut încărca lista de directori.")

                    with c3:
                        # Filtru Departament & Acronim
                        acronime = sorted(df['acronim'].unique().tolist()) if 'acronim' in df.columns else []
                        acro_filtru = st.multiselect("Acronim proiect:", acronime)
                        
                        depts = sorted(df['departament'].unique().tolist()) if 'departament' in df.columns else []
                        dept_filtru = st.multiselect("Departament:", depts)

                    # --- APLICAREA FILTRELOR PE TABEL ---
                    if an_filtru: df = df[df['an_referinta'].isin(an_filtru)]
                    if id_filtru: df = df[df['cod_identificare'].str.contains(id_filtru, case=False, na=False)]
                    if dir_filtru: 
                        if 'director_proiect' in df.columns:
                            df = df[df['director_proiect'].isin(dir_filtru)]
                    if acro_filtru: df = df[df['acronim'].isin(acro_filtru)]
                    if dept_filtru: df = df[df['departament'].isin(dept_filtru)]

                    # --- AFIȘARE REZULTAT ---
                    st.write("---")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Opțiuni export
                    st.download_button("📥 Descarcă lista (CSV)", df.to_csv(index=False), f"interogare_{tip_ales}.csv", "text/csv")
                else:
                    st.warning(f"Nu există date înregistrate pentru {tip_ales}.")
        except:
            st.error(f"Eroare: Tabelul '{tabel_tinta}' nu a fost găsit.")

# ==========================================
# CALEA 2: CONSOLA DE ADMINISTRARE (CRUD)
# ==========================================
elif calea_activa == "admin":
    # Aici rămâne logica cu barierele de securitate și identificare operator
    st.markdown("# 🛡️ Consola de Administrare")
    st.write("Identificați-vă pentru a gestiona datele.")
    # (Păstrezi aici logica de parola și operator)

# ==========================================
# CALEA 3: BRAINSTORMING AI (PROFESORI)
# ==========================================
elif calea_activa == "ai":
    st.markdown("# 🧠 Brainstorming AI")
    st.write("Modul de analiză inteligentă pentru cadre didactice.")
