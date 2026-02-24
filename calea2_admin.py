import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    # --- CONEXIUNE ȘI STIL (PĂSTRATE EXACT DIN SCRIPTUL TĂU BUN) ---
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
        input { color: #000000 !important; background-color: #ffffff !important; }
        .eroare-idbdc-rosu { color: #ffffff !important; background-color: #ff0000 !important; padding: 10px; border-radius: 4px; text-align: center; font-weight: bold; border: 2px solid #8b0000; margin-top: 10px; }
        
        /* STIL PENTRU SIMBOLURI CRUD MARI */
        div.stButton > button { border: none !important; font-size: 35px !important; background-color: transparent !important; }
        div.stButton > button:hover { transform: scale(1.2); }
        .stDataEditor { background-color: white !important; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

    # --- LOGICA DE ACCES (RESTABILITĂ CONFORM DOCX) ---
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'> \u26E8 Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola master:", type="password", key="p1_pass")
            if st.button("Autorizare acces", use_container_width=True):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
        st.stop()

    if not st.session_state.operator_identificat:
        st.sidebar.markdown("### \U0001F464 Identificare Operator")
        cod_in = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod_input")
        if cod_in:
            try:
                # Verificăm în tabela com_operatori folosind coloana cod_operatori
                res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_in).execute()
                if res_op.data and len(res_op.data) > 0:
                    st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                    st.rerun()
                else:
                    st.sidebar.markdown("<div class='eroare-idbdc-rosu'>Cod inexistent!</div>", unsafe_allow_html=True)
            except Exception as e:
                st.sidebar.error("Eroare DB: Verificați conexiunea sau numele coloanei.")
        st.stop()
    else:
        st.sidebar.success(f"Operator: {st.session_state.operator_identificat}")
        if st.sidebar.button("Ieșire / Resetare"):
            st.session_state.clear()
            st.rerun()

    # --- ZONA DE FILTRARE (IDENTICĂ DOCX) ---
    st.markdown(f"<h3 style='text-align: center;'> \u2692 Administrare: {st.session_state.operator_identificat}</h3>", unsafe_allow_html=True)
    st.write("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        list_cat = [i["denumire_categorie"] for i in res_cat.data]
        cat_admin = st.selectbox("Categoria de informatii:", [""] + list_cat, key="admin_cat")
    with c2:
        list_tip = []
        if cat_admin == "Contracte & Proiecte":
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
        tip_admin = st.selectbox("Tip de contract / proiect:", [""] + list_tip, key="admin_tip")
    with c3:
        id_admin = st.text_input("ID proiect / Numar de contract:", key="admin_id")
    st.write("---")

    # --- LOGICA CRUD: RÂND NOU LA ÎNCEPUT ---
    if cat_admin != "":
        tabel_map = {"Contracte & Proiecte": "base_proiecte_internationale", "Evenimente stiintifice": "base_evenimente_stiintifice", "Proprietate intelectuala": "base_prop_intelect"}
        nume_tabela = tabel_map.get(cat_admin)

        if f'data_{nume_tabela}' not in st.session_state:
            query = supabase.table(nume_tabela).select("*")
            if tip_admin: query = query.eq("acronim_contracte_proiecte", tip_admin)
            if id_admin: query = query.eq("cod_identificare", id_admin)
            res = query.execute()
            st.session_state[f'data_{nume_tabela}'] = pd.DataFrame(res.data)

        df_curent = st.session_state[f'data_{nume_tabela}']

        # Butoane aliniate: NOU (stânga) | ACTUALIZARE, VALIDARE, ȘTERGERE (dreapta)
        col_nou, col_sp, col_save, col_val, col_del = st.columns([1, 6, 1, 1, 1])
        
        with col_nou:
            if st.button("\u2795", help="ADAUGĂ RÂND NOU SUS"):
                empty_row = pd.DataFrame([{col: None for col in df_curent.columns}])
                st.session_state[f'data_{nume_tabela}'] = pd.concat([empty_row, df_curent], ignore_index=True)
                st.rerun()

        edited_df = st.data_editor(
            st.session_state[f'data_{nume_tabela}'],
            use_container_width=True,
            hide_index=True,
            key="editor_idbdc_v8"
        )

        # Apar butoanele în dreapta doar dacă s-a modificat ceva
        if not st.session_state[f'data_{nume_tabela}'].equals(edited_df):
            with col_save:
                if st.button("\U0001F4BE", help="ACTUALIZARE"):
                    st.session_state[f'data_{nume_tabela}'] = edited_df
                    st.success("Modificări gata de salvare!")
            with col_val:
                if st.button("\U0001F6E1", help="VALIDARE"):
                    st.info("Protocol respectat!")
            with col_del:
                if st.button("\U0001F5D1", help="ȘTERGERE"):
                    st.error("Rând marcat!")

if __name__ == "__main__":
    run()
