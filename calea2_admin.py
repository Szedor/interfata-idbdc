import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    # --- 1. SECȚIUNE VALIDATĂ / ÎNGHEȚATĂ (STIL ȘI CONEXIUNE) ---
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
        input { color: #000000 !important; background-color: #ffffff !important; }
        div.stButton > button { border: 1px solid white !important; color: white !important; background-color: rgba(255,255,255,0.1) !important; width: 100%; font-size: 14px !important; font-weight: bold !important; height: 45px !important; }
        div.stButton > button:hover { background-color: white !important; color: #003366 !important; }
    </style>
    """, unsafe_allow_html=True)

    # --- SISTEM AUTORIZARE (RESTAURAT) ---
    if 'autorizat_p1' not in st.session_state:
        st.session_state.autorizat_p1 = False

    if not st.session_state.autorizat_p1:
        st.subheader("🔒 Acces Securizat - Consola Admin")
        cod_acces = st.text_input("Introduceți codul de autorizare", type="password")
        if st.button("Validare Acces"):
            if cod_acces == "IDBDC2024": # Codul stabilit anterior
                st.session_state.autorizat_p1 = True
                st.rerun()
            else:
                st.error("Cod incorect!")
        return

    # --- 2. MOTORUL DE NOMENCLATOARE (FUNCȚII SUPORT) ---
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

    # --- 3. CELE 4 CASETE (INTERFAȚA DE CONTROL) ---
    st.markdown("### 🛠️ CONSOLA DE ADMINISTRARE - IDBDC")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        op_admin = st.selectbox("1. Operator", list_operatori)
    with c2:
        tip_admin = st.selectbox("2. Tip Proiect", list_acronime)
    with c3:
        id_admin = st.text_input("3. ID Proiect (Filtru)", placeholder="ex: PN-III-P1...")
    with c4:
        componente_sel = st.multiselect("4. Componente", ["Date financiare", "Echipe", "Aspecte tehnice", "Resurse umane"])

    # Mapare COMPLETĂ (Asigurăm că niciun tabel nu este omis)
    map_base = {
        "FDI": "base_proiecte_fdi", "PNRR": "base_proiecte_pnrr",
        "INTERNATIONALE": "base_proiecte_internationale", "PNCDI": "base_proiecte_pncdi",
        "INTERREG": "base_proiecte_interreg", "NONEU": "base_proiecte_noneu",
        "CEP": "base_contracte_cep", "TERTI": "base_contracte_terti",
        "EVENIMENTE": "base_evenimente_stiintifice", "PROP_INTELECT": "base_prop_intelect"
    }
    tabela_activa = map_base.get(tip_admin)

    # --- 4. AFIȘARE ȘI EDITARE CU DROPDOWN ---
    if tabela_activa:
        st.write("---")
        query = supabase.table(tabela_activa).select("*")
        if id_admin:
            query = query.eq("cod_identificare", id_admin)
        
        res = query.execute()
        df_initial = pd.DataFrame(res.data)

        # Configurare Ghid (Dropdown-uri active peste tot)
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
            hide_index=True, 
            key=f"editor_{tabela_activa}", 
            num_rows="dynamic"
        )

        # --- 5. BUTOANE CRUD (SQL SPECIFIC) ---
        st.write("---")
        b1, b2, b3, b4, b5 = st.columns(5)
        
        with b2:
            if st.button("💾 SALVARE"):
                # 1. Comanda DELETE pentru rândurile eliminate vizual
                if not df_initial.empty:
                    ids_vechi = set(df_initial['cod_identificare'].dropna())
                    ids_noi = set(edited_df['cod_identificare'].dropna())
                    de_sters = ids_vechi - ids_noi
                    for id_s in de_sters:
                        supabase.table(tabela_activa).delete().eq("cod_identificare", id_s).execute()

                # 2. Comanda UPSERT pentru restul
                for _, row in edited_df.iterrows():
                    if pd.notna(row['cod_identificare']):
                        valori = row.to_dict()
                        valori['cod_operatori'] = op_admin
                        supabase.table(tabela_activa).upsert(valori).execute()
                
                st.success("Datele au fost sincronizate cu succes!")
                st.rerun()

        with b3:
            st.button("✅ VALIDARE")

        with b5:
            if st.button("❌ ANULARE"):
                st.rerun()

if __name__ == "__main__":
    run()
