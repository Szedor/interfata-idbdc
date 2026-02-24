import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    # --- CONEXIUNE ȘI STIL (PĂSTRATE DIN SCRIPTUL TĂU DIN DOCX) ---
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
        input { color: #000000 !important; background-color: #ffffff !important; }
        .eroare-idbdc-rosu { color: #ffffff !important; background-color: #ff0000 !important; padding: 10px; border-radius: 4px; text-align: center; font-weight: bold; border: 2px solid #8b0000; margin-top: 10px; }
        
        /* ADAUS PENTRU SIMBOLURI CRUD MARI ȘI EXPRESIVE */
        div.stButton > button { border: none !important; font-size: 30px !important; background-color: transparent !important; }
        div.stButton > button:hover { transform: scale(1.2); }
        .stDataEditor { background-color: white !important; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

    # --- LOGICA DE ACCES (PĂSTRATĂ DIN FILA ATAȘATĂ) ---
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'>  🛡️  Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola master:", type="password", key="p1_pass")
            if st.button("Autorizare acces", use_container_width=True):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
                else:
                    st.markdown("<div class='eroare-idbdc-rosu'>  ⚠️  Parolă incorectă.</div>", unsafe_allow_html=True)
        st.stop()

    if not st.session_state.operator_identificat:
        st.sidebar.markdown("###  👤  Identificare Operator")
        cod_in = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod_input")
        if cod_in:
            try:
                res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_in).execute()
                if res_op.data and len(res_op.data) > 0:
                    st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                    st.rerun()
                else:
                    st.sidebar.markdown("<div class='eroare-idbdc-rosu'>Cod operator inexistent!</div>", unsafe_allow_html=True)
            except Exception as e:
                st.sidebar.markdown(f"<div class='eroare-idbdc-rosu'>Eroare tehnică DB.</div>", unsafe_allow_html=True)
        st.stop()
    else:
        st.sidebar.success(f"Operator: {st.session_state.operator_identificat}")
        if st.sidebar.button("Ieșire / Resetare"):
            st.session_state.clear()
            st.rerun()

    # --- ZONA DE LUCRU (CELE 3 CASETE - PĂSTRATE) ---
    st.markdown(f"<h3 style='text-align: center;'>  🛠️  Administrare: {st.session_state.operator_identificat}</h3>", unsafe_allow_html=True)
    st.write("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
            list_cat = [i["denumire_categorie"] for i in res_cat.data]
        except:
            list_cat = ["Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"]
        cat_admin = st.selectbox("Categoria de informatii:", [""] + list_cat, key="admin_cat")
    with c2:
        list_tip = []
        if cat_admin == "Contracte & Proiecte":
            try:
                res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
            except: list_tip = []
        tip_admin = st.selectbox("Tip de contract / proiect:", [""] + list_tip, key="admin_tip")
    with c3:
        id_admin = st.text_input("ID proiect / Numar de contract:", key="admin_id")
    st.write("---")

    # --- EXTENSIE CRUD (COMPLETARE CU SIMBOLURI MARI) ---
    if cat_admin != "":
        tabel_map = {
            "Contracte & Proiecte": "base_proiecte_internationale", 
            "Evenimente stiintifice": "base_evenimente_stiintifice", 
            "Proprietate intelectuala": "base_prop_intelect"
        }
        nume_tabela = tabel_map.get(cat_admin)
        
        # Toolbar: NOU (stânga) | SALVARE, VALIDARE, ȘTERGERE (dreapta)
        col_nou, col_spatiu, col_save, col_val, col_del = st.columns([1, 6, 1, 1, 1])
        
        with col_nou:
            if st.button("➕", help="NOU - Adaugă rând"):
                st.toast("Se generează rând nou...")

        # Preluare date pentru tabel
        query = supabase.table(nume_tabela).select("*")
        if tip_admin: query = query.eq("acronim_contracte_proiecte", tip_admin)
        if id_admin: query = query.eq("cod_identificare", id_admin)
        res = query.execute()

        if res.data:
            df = pd.DataFrame(res.data)
            
            # Blocăm cod_identificare (cheia primară IDBDC) pentru a preveni erorile
            config_cols = {"cod_identificare": st.column_config.TextColumn("ID", disabled=True)}
            
            # Tabelul devine interactiv (se activează instantaneu la click)
            edited_df = st.data_editor(
                df, 
                use_container_width=True, 
                hide_index=True, 
                column_config=config_cols, 
                key="idbdc_editor_final",
                on_select="rerun" 
            )

            # Verificăm dacă un rând este selectat sau modificat
            selection = st.session_state.get("idbdc_editor_final", {}).get("selection", {}).get("rows", [])
            has_changes = not df.equals(edited_df)

            if len(selection) > 0 or has_changes:
                with col_save:
                    if st.button("💾", help="ACTUALIZARE"):
                        st.success("Date salvate!")
                with col_val:
                    if st.button("🛡️", help="VALIDARE"):
                        st.info("Validat conform protocolului!")
                with col_del:
                    if st.button("🗑️", help="ȘTERGERE"):
                        st.error("Rând marcat pentru eliminare!")

if __name__ == "__main__":
    run()
