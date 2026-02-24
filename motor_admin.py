import streamlit as st
import pandas as pd

def executa_logica(supabase):
    # 1. FETCH OPTIUNI (Preluare nomenclatoare pentru Dropdown)
    def fetch(t, c):
        try:
            res = supabase.table(t).select(c).execute()
            return sorted(list(set([i[c] for i in res.data if i[c]])))
        except: return []

    opts = {
        "cat": fetch("nom_categorie", "denumire_categorie"),
        "tip": fetch("nom_contracte_proiecte", "acronim_contracte_proiecte"),
        "stat": fetch("nom_status_proiect", "status_contract_proiect"),
        "op": fetch("com_operatori", "cod_operatori"),
        "pers": fetch("det_resurse_umane", "nume_prenume")
    }

    # 2. CELE 4 CASETE (Interfața de control)
    st.markdown("### 🛠️ CONSOLA DE ADMINISTRARE - IDBDC")
    c1, c2, c3, c4 = st.columns(4)
    with c1: op_admin = st.selectbox("1. Operator", opts["op"])
    with c2: tip_admin = st.selectbox("2. Tip Proiect", opts["tip"])
    with c3: id_admin = st.text_input("3. ID Proiect (Filtru)", placeholder="ex: PN-III...")
    with c4: comp_sel = st.multiselect("4. Componente", ["Date financiare", "Echipe", "Aspecte tehnice"])

    # 3. MAPARE TABELE BASE (Inclusiv INTERNATIONALE)
    map_base = {
        "FDI": "base_proiecte_fdi", "PNRR": "base_proiecte_pnrr",
        "INTERNATIONALE": "base_proiecte_internationale", "PNCDI": "base_proiecte_pncdi",
        "INTERREG": "base_proiecte_interreg", "NONEU": "base_proiecte_noneu",
        "CEP": "base_contracte_cep", "TERTI": "base_contracte_terti",
        "EVENIMENTE": "base_evenimente_stiintifice", "PROP_INTELECT": "base_prop_intelect"
    }
    tabela = map_base.get(tip_admin)

    if tabela:
        st.write("---")
        query = supabase.table(tabela).select("*")
        if id_admin: query = query.eq("cod_identificare", id_admin)
        
        df_init = pd.DataFrame(query.execute().data)

        # CONFIGURARE COLOANE (Dropdown-ul care a lipsit la Internationale)
        config = {
            "cod_identificare": st.column_config.TextColumn("ID", required=True),
            "denumire_categorie": st.column_config.SelectboxColumn("Categorie", options=opts["cat"], required=True),
            "acronim_contracte_proiecte": st.column_config.SelectboxColumn("Tip", options=opts["tip"]),
            "status_contract_proiect": st.column_config.SelectboxColumn("Status", options=opts["stat"]),
            "data_ultimei_modificari": st.column_config.DatetimeColumn("Update", disabled=True)
        }

        # Editorul de date - Randul nou apare jos la "Add item"
        ed_df = st.data_editor(df_init, column_config=config, use_container_width=True, hide_index=True, num_rows="dynamic", key=f"editor_{tabela}")

        # 4. BUTOANE CRUD (SQL pentru Salvare și Ștergere)
        st.write("---")
        b1, b2, b3, b4, b5 = st.columns(5)
        with b2:
            if st.button("💾 SALVARE"):
                # LOGICA ȘTERGERE SQL
                if not df_init.empty:
                    vechi = set(df_init['cod_identificare'].dropna())
                    noi = set(ed_df['cod_identificare'].dropna())
                    for s in (vechi - noi): 
                        supabase.table(tabela).delete().eq("cod_identificare", s).execute()
                
                # LOGICA UPSERT SQL (Adăugare/Modificare)
                for _, r in ed_df.iterrows():
                    if pd.notna(r['cod_identificare']):
                        vals = r.to_dict()
                        vals['cod_operatori'] = op_admin
                        supabase.table(tabela).upsert(vals).execute()
                
                st.success(f"Tabela {tabela} a fost actualizată!")
                st.rerun()

        with b5:
            if st.button("❌ ANULARE"):
                st.rerun()
