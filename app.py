import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 1. CONFIGURARE & CONEXIUNE (Neschimbate)
# ==========================================
st.set_page_config(page_title="IDBDC UPT - Interogare", layout="wide")

# Stil Vizual (Păstrăm Albastru UPT conform imaginii tale)
st.markdown("""
<style>
    .stApp { background-color: #003366; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { color: white !important; }
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #003366 !important; }
</style>
""", unsafe_allow_html=True)

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- Logica de Acces (Barierele rămân active) ---
if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

# (Codul pentru Poarta 1 și Poarta 2 rămâne activ aici pentru securitate)
# ... (presupunem că operatorul este deja logat conform pașilor anteriori)

# ==========================================
# 4. MODULUL DE INTEROGARE & FILTRARE
# ==========================================
if st.session_state.operator_identificat:
    st.markdown(f"## 🔍 Explorator & Interogare: {st.session_state.operator_identificat}")
    st.write("---")

    # Randul 1: Selecție Sursă Date
    col1, col2 = st.columns([1, 1])
    with col1:
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        cat_selectata = st.selectbox("Alege Categoria:", ["---"] + [item["denumire_categorie"] for item in res_cat.data])

    with col2:
        tip_ales = "---"
        if cat_selectata == "Contracte & Proiecte":
            res_sub = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            tip_ales = st.selectbox("Alege Tip Proiect (FDI, PNRR etc):", ["---"] + [item["acronim_contracte_proiecte"] for item in res_sub.data])

    # --- ZONA DE FILTRARE DINAMICĂ ---
    if tip_ales != "---":
        nume_tabel_db = f"base_proiecte_{tip_ales.lower()}"
        
        try:
            # 1. Citim toate datele pentru acest tip
            date_res = supabase.table(nume_tabel_db).select("*").execute()
            df = pd.DataFrame(date_res.data)

            st.markdown(f"### 📊 Filtrare Rapidă: {tip_ales}")
            
            # Creăm filtre dinamice pe baza coloanelor din tabel
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                # Exemplu: Filtru după Director de Proiect (dacă există coloana)
                if 'director_proiect' in df.columns:
                    director = st.multiselect("Director Proiect:", options=df['director_proiect'].unique())
                    if director:
                        df = df[df['director_proiect'].isin(director)]
                else:
                    st.write("Filtru Director: N/A")

            with col_f2:
                # Exemplu: Filtru după Status sau Cod
                if 'cod_inregistrare' in df.columns:
                    cautare_cod = st.text_input("Caută Cod Înregistrare:")
                    if cautare_cod:
                        df = df[df['cod_inregistrare'].str.contains(cautare_cod, case=False)]

            with col_f3:
                # Filtru financiar (Suma mai mare de...)
                if 'valoare_totala' in df.columns:
                    min_val = st.number_input("Valoare minimă:", value=0)
                    df = df[df['valoare_totala'] >= min_val]

            st.write("---")

            # --- AFIȘARE REZULTAT ---
            st.markdown(f"**Rezultate găsite: {len(df)}**")
            st.dataframe(df, use_container_width=True, hide_index=True)

            # --- EXPORT (Funcționalitate cheie pentru management) ---
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descarcă Situația (CSV)",
                data=csv,
                file_name=f"situatie_{tip_ales.lower()}_idbdc.csv",
                mime='text/csv',
            )

        except Exception as e:
            st.error(f"Eroare la interogare: Tabelul '{nume_tabel_db}' nu a fost găsit sau structura diferă.")

else:
    st.info("Sistemul așteaptă identificarea operatorului.")
