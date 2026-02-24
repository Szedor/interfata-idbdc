import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    # --- CONEXIUNE ȘI STIL (PĂSTRATE DIN SCRIPTUL TĂU BUN) ---
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
        input { color: #000000 !important; background-color: #ffffff !important; }
        .eroare-idbdc-rosu { color: #ffffff !important; background-color: #ff0000 !important; padding: 10px; border-radius: 4px; text-align: center; font-weight: bold; border: 2px solid #8b0000; margin-top: 10px; }
        
        /* SIMBOLURI CRUD MARI */
        div.stButton > button { border: none !important; font-size: 35px !important; background-color: transparent !important; }
        div.stButton > button:hover { transform: scale(1.2); }
        .stDataEditor { background-color: white !important; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True) [cite: 8-32]

    # --- LOGICA DE ACCES (PĂSTRATĂ DIN SCRIPTUL TĂU BUN) ---
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'> Scut Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola master:", type="password", key="p1_pass")
            if st.button("Autorizare acces", use_container_width=True):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
        st.stop() [cite: 33-47]

    if not st.session_state.operator_identificat:
        st.sidebar.markdown("### Identificare Operator")
        cod_in = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod_input")
        if cod_in:
            try:
                res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_in).execute()
                if res_op.data:
                    st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                    st.rerun()
            except: st.sidebar.error("Eroare DB")
        st.stop() [cite: 48-71]

    # --- ZONA DE LUCRU (CONFORM SCRIPTULUI TAU BUN) ---
    st.markdown(f"<h3 style='text-align: center;'> Administrare: {st.session_state.operator_identificat}</h3>", unsafe_allow_html=True)
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
    st.write("---") [cite: 72-94]

    # --- EXTENSIE CRUD: RAND NOU SUS ȘI SIMBOLURI ---
    if cat_admin != "":
        tabel_map = {"Contracte & Proiecte": "base_proiecte_internationale", "Evenimente stiintifice": "base_evenimente_stiintifice", "Proprietate intelectuala": "base_prop_intelect"}
        nume_tabela = tabel_map.get(cat_admin)

        # Încărcăm datele inițiale în session_state dacă nu există
        if f'df_{nume_tabela}' not in st.session_state:
            query = supabase.table(nume_tabela).select("*")
            if tip_admin: query = query.eq("acronim_contracte_proiecte", tip_admin)
            if id_admin: query = query.eq("cod_identificare", id_admin)
            res = query.execute()
            st.session_state[f'df_{nume_tabela}'] = pd.DataFrame(res.data)

        df_lucru = st.session_state[f'df_{nume_tabela}']

        # TOOLBAR
        col_nou, col_spatiu, col_save, col_val, col_del = st.columns([1, 6, 1, 1, 1])
        
        with col_nou:
            if st.button("\u2795", help="ADAUGĂ RÂND NOU SUS"):
                # Creăm un rând gol cu structura tabelului
                new_row = pd.DataFrame([[None] * len(df_lucru.columns)], columns=df_lucru.columns)
                # Îl punem la începutul tabelului (Index 0)
                st.session_state[f'df_{nume_tabela}'] = pd.concat([new_row, df_lucru], ignore_index=True)
                st.rerun()

        # TABELUL EDITABIL
        config_cols = {"cod_identificare": st.column_config.TextColumn("ID", disabled=False)}
        
        edited_df = st.data_editor(
            st.session_state[f'df_{nume_tabela}'],
            use_container_width=True,
            hide_index=True,
            column_config=config_cols,
            key="idbdc_editor_v6",
            num_rows="dynamic" # Permite adăugarea manuală dacă e nevoie
        )

        # Detectăm modificări pentru simbolurile din dreapta
        if not st.session_state[f'df_{nume_tabela}'].equals(edited_df):
            with col_save:
                if st.button("\U0001F4BE", help="ACTUALIZARE"):
                    st.session_state[f'df_{nume_tabela}'] = edited_df
                    st.success("Date pregătite pentru DB!")
            with col_val:
                if st.button("\U0001F6E1", help="VALIDARE"):
                    st.info("Validat!")
            with col_del:
                if st.button("\U0001F5D1", help="ȘTERGERE"):
                    st.warning("Marcat!")

if __name__ == "__main__":
    run()
