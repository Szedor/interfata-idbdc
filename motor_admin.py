import streamlit as st
import pandas as pd
from datetime import datetime

def porneste_motorul(supabase):
    # Preluare opțiuni pentru dropdown-uri
    def fetch_opt(t, c):
        res = supabase.table(t).select(c).execute()
        return sorted(list(set([r[c] for r in res.data if r[c]])))

    lista_acronime = [""] + fetch_opt("nom_contracte_proiecte", "acronim_contracte_proiecte")
    lista_categorii = fetch_opt("nom_categorie", "denumire_categorie")

    st.markdown(f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.operator_identificat}</h3>", unsafe_allow_html=True)
    
    # CASETELE 1-4
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2])
    with c1: cat_admin = st.selectbox("1. Categoria:", ["", "Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"], key="admin_cat")
    with c2: tip_admin = st.selectbox("2. Tip (Acronim):", lista_acronime, key="admin_tip")
    with c3: id_admin = st.text_input("3. ID Proiect (Cod Identificare):", key="admin_id")
    with c4: componente_com = st.multiselect("4. Componente (COM):", ["Date financiare", "Resurse umane", "Aspecte tehnice"], key="admin_com")

    st.markdown("---")

    # --- PANOU BUTOANE CRUD (MUTAT SUS CONFORM CERINȚEI) ---
    col_n, col_s, col_v, col_d, col_a = st.columns(5)
    
    with col_n: 
        if st.button("➕ RAND NOU"):
            st.toast("Folosiți '+' din subsolul tabelului.")
    
    with col_s: 
        btn_salvare = st.button("💾 SALVARE") # Definim butonul aici, logica o punem după tabel

    with col_v:
        if st.button("✅ VALIDARE"):
            st.success("Date pregătite pentru validare finală.")

    with col_d:
        if st.button("🗑️ ȘTERGERE"):
            st.warning("Ștergeți rândul din editor (tasta Delete) apoi apăsați SALVARE.")

    with col_a:
        if st.button("❌ ANULARE"):
            st.rerun()

    st.write("") # Spațiere

    # Mapare Tabela
    map_baze = {"FDI": "base_proiecte_fdi", "PNRR": "base_proiecte_pnrr", "INTERNATIONALE": "base_proiecte_internationale"}
    nume_tabela = map_baze.get(tip_admin) if cat_admin == "Contracte & Proiecte" else None

    # --- AFIȘARE TABEL ---
    if nume_tabela:
        res_main = supabase.table(nume_tabela).select("*")
        if id_admin: res_main = res_main.eq("cod_identificare", id_admin)
        df_main = pd.DataFrame(res_main.execute().data)

        st.markdown(f"**📂 Tabel Principal: {nume_tabela}**")
        # Editorul de date
        ed_df = st.data_editor(df_main, use_container_width=True, hide_index=True, key=f"ed_{nume_tabela}", num_rows="dynamic")

        # LOGICA DE SALVARE (Se execută dacă s-a apăsat butonul definit mai sus)
        if btn_salvare:
            # 1. ȘTERGERE (Dacă un ID a dispărut din tabel)
            if not df_main.empty:
                ids_vechi = set(df_main['cod_identificare'].dropna())
                ids_noi = set(ed_df['cod_identificare'].dropna())
                for s in (ids_vechi - ids_noi):
                    supabase.table(nume_tabela).delete().eq("cod_identificare", s).execute()
            
            # 2. SALVARE (Update/Insert)
            for _, r in ed_df.iterrows():
                if pd.notna(r['cod_identificare']):
                    v = r.to_dict()
                    v['data_ultimei_modificari'] = datetime.now().isoformat()
                    supabase.table(nume_tabela).upsert(v).execute()
            
            st.success("Sincronizare reușită!")
            st.rerun()
