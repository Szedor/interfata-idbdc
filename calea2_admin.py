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

    # --- SISTEM AUTORIZARE (ÎNGHEȚAT) ---
    if 'autorizat_p1' not in st.session_state:
        st.session_state.autorizat_p1 = False

    if not st.session_state.autorizat_p1:
        st.subheader("🔒 Acces Securizat - Consola Admin")
        cod_acces = st.text_input("Introduceți codul de autorizare", type="password")
        if st.button("Validare Acces"):
            if cod_acces == "IDBDC2024":
                st.session_state.autorizat_p1 = True
                st.rerun()
            else:
                st.error("Cod incorect!")
        return

    # --- 2. MOTORUL DE NOMENCLATOARE (INTEGRAT) ---
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

    # --- 3. CELE 4 CASETE (CONFORM CODULUI TĂU) ---
    st.markdown("### 🛠️ CONSOLA DE ADMINISTRARE - IDBDC")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: op_admin = st.selectbox("1. Operator", list_operatori)
    with c2: tip_admin = st.selectbox("2. Tip Proiect", list_acronime)
    with c3: id_admin = st.text_input("3. ID Proiect (Filtru)", placeholder="ex: PN-III-P1...")
    with c4: componente_com = st.multiselect("4. Componente", ["Date financiare", "Resurse umane", "Aspecte tehnice"])

    # Mapare completă tabele BASE
    map_base = {
        "FDI": "base_proiecte_fdi", "PNRR": "base_proiecte_pnrr",
        "INTERNATIONALE": "base_proiecte_internationale", "PNCDI": "base_proiecte_pncdi",
        "INTERREG": "base_proiecte_interreg", "NONEU": "base_proiecte_noneu",
        "CEP": "base_contracte_cep", "TERTI": "base_contracte_terti",
        "EVENIMENTE": "base_evenimente_stiintifice", "PROP_INTELECT": "base_prop_intelect"
    }
    nume_tabela = map_base.get(tip_admin)

    # --- 4. ZONA DE EDITARE (CU FILTRE ȘI DROPDOWN) ---
    if nume_tabela:
        st.write("---")
        st.markdown(f"**📄 Tabela Principală: {nume_tabela}**")
        
        query_base = supabase.table(nume_tabela).select("*")
        if id_admin:
            query_base = query_base.eq("cod_identificare", id_admin)
        
        res_base = query_base.execute()
        df_initial = pd.DataFrame(res_base.data)

        # CONFIGURARE COLOANE - "Ghidul" care forțează dropdown-ul
        config_ghid = {
            "cod_identificare": st.column_config.TextColumn("Cod Identificare", required=True),
            "denumire_categorie": st.column_config.SelectboxColumn("Categorie", options=list_categorii, required=True),
            "acronim_contracte_proiecte": st.column_config.SelectboxColumn("Tip", options=list_acronime),
            "status_contract_proiect": st.column_config.SelectboxColumn("Status", options=list_status),
            "data_ultimei_modificari": st.column_config.DatetimeColumn("Update", disabled=True)
        }

        # Editorul de date - permite rânduri noi și ștergere
        edited_df = st.data_editor(
            df_initial, 
            column_config=config_ghid, 
            use_container_width=True, 
            hide_index=True, 
            key=f"ed_{nume_tabela}", 
            num_rows="dynamic" # Aici apare rândul nou la finalul listei
        )

        # --- 5. COMPONENTE (COM) ---
        if componente_com and id_admin:
            map_tabele_com = {
                "Date financiare": "com_date_financiare",
                "Resurse umane": "com_echipe_proiect",
                "Aspecte tehnice": "com_aspecte_tehnice"
            }
            for comp in componente_com:
                tabel_com = map_tabele_com[comp]
                st.write("---")
                st.markdown(f"**🔍 Componenta: {comp}**")
                res_com = supabase.table(tabel_com).select("*").eq("cod_identificare", id_admin).execute()
                df_com = pd.DataFrame(res_com.data)
                
                if df_com.empty: df_com = pd.DataFrame([{"cod_identificare": id_admin}])
                
                # Dropdown pentru membrii echipei dacă e cazul
                config_com = {"cod_identificare": st.column_config.TextColumn("ID Proiect", disabled=True)}
                if comp == "Resurse umane":
                    config_com["nume_prenume"] = st.column_config.SelectboxColumn("Membru", options=list_personal)
                
                st.data_editor(df_com, column_config=config_com, use_container_width=True, hide_index=True, key=f"ed_{tabel_com}", num_rows="dynamic")

        # --- 6. BUTOANE CRUD (CU SQL SPECIFIC) ---
        st.write("---")
        btn_rand_nou, btn_salvare, btn_validare, btn_stergere, btn_anulare = st.columns(5)
        
        with btn_salvare:
            if st.button("💾 SALVARE"):
                # A. LOGICA DE ȘTERGERE (Identifică ce lipsește din tabelul editat față de cel inițial)
                if not df_initial.empty:
                    ids_vechi = set(df_initial['cod_identificare'].dropna())
                    ids_noi = set(edited_df['cod_identificare'].dropna())
                    de_sters = ids_vechi - ids_noi
                    for id_s in de_sters:
                        supabase.table(nume_tabela).delete().eq("cod_identificare", id_s).execute()

                # B. LOGICA DE UPSERT (Adăugare / Modificare)
                for _, row in edited_df.iterrows():
                    if pd.notna(row['cod_identificare']):
                        valori = row.to_dict()
                        valori['cod_operatori'] = op_admin # Asumare automată
                        supabase.table(nume_tabela).upsert(valori).execute()
                
                st.success("Sincronizare completă cu baza de date!")
                st.rerun()

        with btn_anulare:
            if st.button("❌ ANULARE"):
                st.rerun()

if __name__ == "__main__":
    run()
