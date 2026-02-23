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
    .stMultiSelect span { color: #31333F !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CALEA 1: EXPLORATOR DE DATE (IZOLARE)
# ==========================================
if calea_activa == "explorator":
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de date</h1>", unsafe_allow_html=True)
    st.write("---")

    # GRID SELECȚIE CATEGORIE ȘI TIP
    c1, c2 = st.columns(2)
    with c1:
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        list_cat = [i["denumire_categorie"] for i in res_cat.data]
        categorii_sel = st.multiselect("1. Categoria de informații:", list_cat, placeholder="Opțiuni de alegere", key="f_cat_multi")

    with c2:
        tipuri_sel = []
        if "Contracte & Proiecte" in categorii_sel:
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
            tipuri_sel = st.multiselect("2. Tipul de contract / proiect:", list_tip, placeholder="Opțiuni de alegere", key="f_tip_multi")

    # FILTRE DINAMICE DIN BASE_... ȘI COM_...
    if tipuri_sel:
        st.write("---")
        
        # Colectăm datele din toate tabelele selectate pentru a popula filtrele
        all_data = []
        for tip in tipuri_sel:
            tabel = f"base_proiecte_{tip.lower()}"
            try:
                res = supabase.table(tabel).select("*").execute()
                if res.data:
                    all_data.extend(res.data)
            except:
                st.warning(f"Tabelul {tabel} nu a fost găsit.")
        
        df_total = pd.DataFrame(all_data)

        if not df_total.empty:
            # 5. TITLUL (Pe tot ecranul conform cerinței)
            st.markdown("##### 5. Titlul proiectului / Obiectul contractului")
            titlu_sel = st.text_input("Introduceți cuvinte cheie din titlu:", label_visibility="collapsed", key="f_titlu")
            
            st.write("") # Spațiu

            f1, f2, f3 = st.columns(3)
            
            with f1:
                # 3. ID (Din coloana cod_identificare a df_total)
                id_sel = st.text_input("3. ID proiect / Nr. contract", key="f_id")
                # 4. Acronim (Din coloana acronim_proiect)
                acro_sel = st.text_input("4. Acronim proiect", key="f_acro")

            with f2:
                # 7. Anul de implementare
                # Extragem anii unici existenți în date
                ani_disponibili = sorted(df_total['an_referinta'].unique().tolist()) if 'an_referinta' in df_total.columns else [2024]
                an_sel = st.selectbox("7. Anul de implementare:", ani_disponibili, key="f_an")
                
                # 6. Director (Din com_echipe_proiecte unde reprezinta_idbdc='DA')
                # Mutat SUB an conform cerinței
                try:
                    res_dir = supabase.table("com_echipe_proiecte").select("nume_prenume_membru").eq("reprezinta_idbdc", "DA").execute()
                    directori = sorted(list(set([d['nume_prenume_membru'] for d in res_dir.data])))
                    dir_sel = st.multiselect("6. Director de proiect / Responsabil:", directori, placeholder="Opțiuni de alegere", key="f_dir")
                except: dir_sel = []

            with f3:
                # 8. Rolul UPT (Extras din datele reale)
                roluri_reale = sorted(df_total['rol_upt'].unique().tolist()) if 'rol_upt' in df_total.columns else []
                rol_sel = st.multiselect("8. Rolul UPT:", roluri_reale, placeholder="Opțiuni de alegere", key="f_rol")
                
                # 9. Status (Extras din datele reale)
                statusuri_reale = sorted(df_total['status_contract_proiect'].unique().tolist()) if 'status_contract_proiect' in df_total.columns else []
                status_sel = st.multiselect("9. Statusul proiectului:", statusuri_reale, placeholder="Opțiuni de alegere", key="f_status")

            st.write("---")
            st.success(f"Gata pentru interogare. S-au găsit {len(df_total)} înregistrări brute.")
        else:
            st.warning("Nu există date în tabelele selectate.")

# ==========================================
# CALEA 2: ADMIN (IZOLARE)
# ==========================================
elif calea_activa == "admin":
    st.info("Secțiune de administrare izolată.")
