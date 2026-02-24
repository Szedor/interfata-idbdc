import streamlit as st
import pandas as pd
from datetime import datetime

def porneste_motorul(supabase):
    # 1. PRELUARE NOMENCLATOARE (Pentru dropdown-uri funcționale)
    def fetch_opt(t, c):
        res = supabase.table(t).select(c).execute()
        return sorted(list(set([r[c] for r in res.data if r[c]])))

    lista_acronime = [""] + fetch_opt("nom_contracte_proiecte", "acronim_contracte_proiecte")
    lista_categorii = fetch_opt("nom_categorie", "denumire_categorie")
    lista_status = fetch_opt("nom_status_proiect", "status_contract_proiect")

    # 2. ZONA FILTRE (CASETELE 1-4) - Păstrăm aspectul tău
    st.markdown(f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.operator_identificat}</h3>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2])
    with c1: cat_admin = st.selectbox("1. Categoria:", ["", "Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"], key="admin_cat")
    with c2: tip_admin = st.selectbox("2. Tip (Acronim):", lista_acronime, key="admin_tip")
    with c3: id_admin = st.text_input("3. ID Proiect (Cod Identificare):", key="admin_id")
    with c4: componente_com = st.multiselect("4. Componente (COM):", ["Date financiare", "Resurse umane", "Aspecte tehnice"], key="admin_com")

    st.markdown("---")

    # 3. IDENTIFICARE TABELA (Rezolvăm aici problema cu toate tabelele)
    map_baze = {
        "FDI": "base_proiecte_fdi", "PNRR": "base_proiecte_pnrr",
        "INTERNATIONALE": "base_proiecte_internationale", "PNCDI": "base_proiecte_pncdi",
        "INTERREG": "base_proiecte_interreg", "NONEU": "base_proiecte_noneu",
        "CEP": "base_contracte_cep", "TERTI": "base_contracte_terti"
    }
    
    nume_tabela = map_baze.get(tip_admin) if cat_admin == "Contracte & Proiecte" else None
    if cat_admin == "Evenimente stiintifice": nume_tabela = "base_evenimente_stiintifice"
    if cat_admin == "Proprietate intelectuala": nume_tabela = "base_prop_intelect"

    # 4. AFIȘARE ȘI CRUD
    if nume_tabela:
        res_main = supabase.table(nume_tabela).select("*")
        if id_admin: res_main = res_main.eq("cod_identificare", id_admin)
        df_main = pd.DataFrame(res_main.execute().data)

        # CONFIGURARE COLOANE (Ghidul care forțează dropdown-ul în tabel)
        config_ghid = {
            "cod_identificare": st.column_config.TextColumn("ID", required=True),
            "denumire_categorie": st.column_config.SelectboxColumn("Categorie", options=lista_categorii),
            "status_contract_proiect": st.column_config.SelectboxColumn("Status", options=lista_status)
        }

        st.markdown(f"**📂 Tabel Principal: {nume_tabela}**")
        edited_df = st.data_editor(df_main, column_config=config_ghid, use_container_width=True, hide_index=True, key=f"ed_{nume_tabela}", num_rows="dynamic")

        # BUTOANELE CRUD (Logica cerută)
        col_n, col_s, col_v, col_d, col_a = st.columns(5)
        with col_s:
            if st.button("💾 SALVARE"):
                # A. ȘTERGERE (SQL Real)
                if not df_main.empty:
                    ids_initiale = set(df_main['cod_identificare'].dropna())
                    ids_actuale = set(edited_df['cod_identificare'].dropna())
                    de_sters = ids_initiale - ids_actuale
                    for id_s in de_sters:
                        supabase.table(nume_tabela).delete().eq("cod_identificare", id_s).execute()

                # B. UPSERT (Update + Insert)
                for _, row in edited_df.iterrows():
                    if pd.notna(row['cod_identificare']):
                        data = row.to_dict()
                        data['data_ultimei_modificari'] = datetime.now().isoformat()
                        supabase.table(nume_tabela).upsert(data).execute()
                st.success("Baza de date sincronizată!")
                st.rerun()
