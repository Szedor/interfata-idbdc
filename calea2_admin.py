import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    # 1. CONEXIUNE ȘI STIL (ÎNGHEȚAT)
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown("""
    <style>
        .stApp { background-color: #003366 !important; }
        .stApp h1, h2, h3, h4, p, label { color: white !important; }
        div.stButton > button { border: 1px solid white !important; color: white !important; background-color: rgba(255,255,255,0.1) !important; height: 45px !important; }
        div.stButton > button:hover { background-color: white !important; color: #003366 !important; }
    </style>
    """, unsafe_allow_html=True)

    # 2. MOTORUL DE NOMENCLATOARE (DROPDOWN UNIVERSAL)
    def fetch_options(table, column):
        try:
            res = supabase.table(table).select(column).execute()
            return sorted(list(set([item[column] for item in res.data if item[column]])))
        except: return []

    list_categorii = fetch_options("nom_categorie", "denumire_categorie")
    list_acronime = fetch_options("nom_contracte_proiecte", "acronim_contracte_proiecte")
    list_status = fetch_options("nom_status_proiect", "status_contract_proiect")
    list_operatori = fetch_options("com_operatori", "cod_operatori")
    list_personal = fetch_options("det_resurse_umane", "nume_prenume")

    # 3. INTERFAȚĂ CONTROL
    st.title("🛠️ Atelier IDBDC - Administrare")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: op_admin = st.selectbox("1. Operator", list_operatori)
    with c2: tip_admin = st.selectbox("2. Tip Proiect", list_acronime)
    with c3: id_admin = st.text_input("3. ID Proiect (Filtru)", placeholder="Introduceți cod_identificare...")
    with c4: componente_sel = st.multiselect("4. Componente", ["Financiar", "Echipe", "Tehnic", "Resurse Umane"])

    # Mapare COMPLETĂ a tuturor tabelelor tale BASE
    map_base_universala = {
        "FDI": "base_proiecte_fdi", "PNRR": "base_proiecte_pnrr",
        "INTERNATIONALE": "base_proiecte_internationale", "PNCDI": "base_proiecte_pncdi",
        "INTERREG": "base_proiecte_interreg", "NONEU": "base_proiecte_noneu",
        "CEP": "base_contracte_cep", "TERTI": "base_contracte_terti",
        "EVENIMENTE": "base_evenimente_stiintifice", "PROP_INTELECT": "base_prop_intelect"
    }
    
    tabela_activa = map_base_universala.get(tip_admin)

    # 4. ZONA DE EDITARE CU CONFIGURARE FORȚATĂ (DROPDOWN)
    if tabela_activa:
        query = supabase.table(tabela_activa).select("*")
        if id_admin:
            query = query.eq("cod_identificare", id_admin)
        
        res = query.execute()
        df_initial = pd.DataFrame(res.data)

        st.markdown(f"**Editare în: `{tabela_activa}`**")
        
        # Configurație GHID - Se aplică la orice tabelă selectată
        config_ghid = {
            "cod_identificare": st.column_config.TextColumn("Cod Identificare", required=True),
            "denumire_categorie": st.column_config.SelectboxColumn("Categorie", options=list_categorii),
            "acronim_contracte_proiecte": st.column_config.SelectboxColumn("Tip", options=list_acronime),
            "status_contract_proiect": st.column_config.SelectboxColumn("Status", options=list_status),
            "data_ultimei_modificari": st.column_config.DatetimeColumn("Update", disabled=True)
        }

        edited_df = st.data_editor(
            df_initial, 
            column_config=config_ghid, 
            use_container_width=True, 
            num_rows="dynamic", 
            key=f"editor_{tabela_activa}",
            hide_index=True
        )

        # 5. BUTOANE CRUD CU SQL SPECIFIC
        st.write("---")
        b1, b2, b3, b4, b5 = st.columns(5)
        
        with b2:
            if st.button("💾 SALVARE"):
                # A. LOGICA DE ȘTERGERE (SQL DELETE)
                if not df_initial.empty:
                    ids_vechi = set(df_initial['cod_identificare'].dropna())
                    ids_noi = set(edited_df['cod_identificare'].dropna())
                    de_sters = ids_vechi - ids_noi
                    for id_s in de_sters:
                        supabase.table(tabela_activa).delete().eq("cod_identificare", id_s).execute()

                # B. LOGICA DE ACTUALIZARE/ADĂUGARE (SQL UPSERT)
                for _, row in edited_df.iterrows():
                    if pd.notna(row['cod_identificare']):
                        valori = row.to_dict()
                        valori['cod_operatori'] = op_admin # Asumare prin operator
                        supabase.table(tabela_activa).upsert(valori).execute()
                
                st.success(f"Modificările în {tabela_activa} au fost salvate!")
                st.rerun()

        with b5:
            if st.button("❌ ANULARE"):
                st.rerun()
