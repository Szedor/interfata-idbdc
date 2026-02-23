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

# Stil Vizual General UPT
st.markdown("""
<style>
    .stApp { background-color: #003366; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { color: white !important; }
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #ddd; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #003366 !important; }
    [data-testid="stSidebar"] input { color: #31333F !important; background-color: white !important; }
    .eroare-idbdc { color: white; background-color: #FF4B4B; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CALEA 1: EXPLORATOR DE DATE (IZOLARE TOTALĂ)
# ==========================================
if calea_activa == "explorator":
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de date</h1>", unsafe_allow_html=True)
    st.write("---")

    # GRID SELECTII DE BAZĂ (Punctele 1 și 2)
    c1, col_sp, c2, c3 = st.columns([1, 0.1, 1, 1])
    
    with c1:
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
            categorii = [i["denumire_categorie"] for i in res_cat.data]
            cat_selectata = st.selectbox("1. Categoria de informații:", ["---"] + categorii, key="f_cat")
        except: cat_selectata = "---"

    with c2:
        tip_ales = "---"
        if cat_selectata == "Contracte & Proiecte":
            try:
                res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                tipuri = [i["acronim_contracte_proiecte"] for i in res_tip.data]
                tip_ales = st.selectbox("2. Tipul de contract / proiect:", ["---"] + tipuri, key="f_tip")
            except: pass

    # FILTRE DE RAFINARE (Punctele 3 - 9)
    if tip_ales != "---":
        st.write("---")
        st.markdown("#### Rafinare interogare:")
        
        f1, f2, f3 = st.columns(3)
        tabel_tinta = f"base_proiecte_{tip_ales.lower()}"
        
        try:
            res_data = supabase.table(tabel_tinta).select("*").execute()
            df = pd.DataFrame(res_data.data)

            if not df.empty:
                with f1:
                    id_sel = st.text_input("3. ID Proiect / Nr. Contract:", key="f_id")
                    acro_sel = st.text_input("4. Acronim proiect:", key="f_acro")
                    titlu_sel = st.text_input("5. Titlu / Obiect contract:", key="f_titlu")

                with f2:
                    try:
                        res_dir = supabase.table("com_echipe_proiecte").select("nume_prenume_membru").eq("reprezinta_idbdc", "DA").execute()
                        directori = sorted(list(set([d['nume_prenume_membru'] for d in res_dir.data])))
                        dir_sel = st.multiselect("6. Director / Responsabil:", directori, key="f_dir")
                    except: dir_sel = []
                    
                    ani = sorted(df['an_implementare'].unique().tolist()) if 'an_implementare' in df.columns else []
                    an_sel = st.multiselect("7. Anul de implementare:", ani, key="f_an")

                with f3:
                    roluri = sorted(df['rol_upt'].unique().tolist()) if 'rol_upt' in df.columns else ["Coordonator", "Partener"]
                    rol_sel = st.multiselect("8. Rolul UPT:", roluri, key="f_rol")
                    
                    statusuri = sorted(df['status'].unique().tolist()) if 'status' in df.columns else ["În derulare", "Finalizat"]
                    status_sel = st.multiselect("9. Status proiect:", statusuri, key="f_status")

                # LOGICA FILTRARE
                if id_sel: df = df[df['cod_identificare'].astype(str).str.contains(id_sel, case=False, na=False)]
                if acro_sel: df = df[df['acronim'].str.contains(acro_sel, case=False, na=False)]
                if titlu_sel: df = df[df['titlu'].str.contains(titlu_sel, case=False, na=False)]
                if dir_sel and 'director_proiect' in df.columns: df = df[df['director_proiect'].isin(dir_sel)]
                if an_sel: df = df[df['an_implementare'].isin(an_sel)]
                if rol_sel: df = df[df['rol_upt'].isin(rol_sel)]
                if status_sel: df = df[df['status'].isin(status_sel)]

                st.write("---")
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button("📥 Descarcă Selecția", df.to_csv(index=False), f"export_{tip_ales.lower()}.csv")
            else:
                st.warning("Nu există date în acest tabel.")
        except Exception as e:
            st.error(f"Eroare: Tabelul {tabel_tinta} nu a fost găsit sau structura diferă.")

# ==========================================
# CALEA 2: ADMIN (IZOLARE TOTALĂ CU PORȚI)
# ==========================================
elif calea_activa == "admin":
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'>🛡️ Administrare IDBDC</h2>", unsafe_allow_html=True)
        col_s, col_c, col_d = st.columns([1.3, 0.6, 1.3])
        with col_c:
            p_master = st.text_input("Parola Master", type="password", key="p1_pass")
            if st.button("Autorizare", use_container_width=True):
                if p_master == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
                else: st.markdown("<div class='eroare-idbdc'>⚠️ Parolă incorectă.</div>", unsafe_allow_html=True)
        st.stop()

    if not st.session_state.operator_identificat:
        st.sidebar.markdown("### 👤 Identificare")
        cod_op = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod")
        if cod_op:
            res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_op).execute()
            if res_op.data:
                st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                st.rerun()
            else: st.sidebar.error("Cod invalid!")
        st.stop()
    else:
        st.sidebar.success(f"Salut, {st.session_state.operator_identificat}!")
        if st.sidebar.button("Ieșire/Reset"):
            st.session_state.clear()
            st.rerun()

    st.markdown(f"### Panou Admin: {st.session_state.operator_identificat}")
    st.info("Sistemul este gata pentru gestionare date.")

# ==========================================
# CALEA 3: AI
# ==========================================
elif calea_activa == "ai":
    st.markdown("<h1 style='text-align: center;'>🧠 Brainstorming AI</h1>", unsafe_allow_html=True)
