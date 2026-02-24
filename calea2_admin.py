import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
        input { color: #000000 !important; background-color: #ffffff !important; }
        div.stButton > button { border: 1px solid white !important; color: white !important; background-color: rgba(255,255,255,0.1) !important; width: 100%; font-size: 12px !important; }
        div.stButton > button:hover { background-color: white !important; color: #003366 !important; }
    </style>
    """, unsafe_allow_html=True)

    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    if not st.session_state.autorizat_p1:
        # --- ACCES (Păstrat conform sursei) ---
        st.markdown("<h2 style='text-align: center;'>  🛡️  Acces Securizat IDBDC</h2>", unsafe_allow_html=True) [cite: 112]
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3]) [cite: 113]
        with col_ce:
            parola_m = st.text_input("Parola:", type="password", key="p1_pass") [cite: 115]
            if st.button("Autorizare acces"): [cite: 116]
                if parola_m == "EverDream2SZ": [cite: 117]
                    st.session_state.autorizat_p1 = True [cite: 118]
                    st.rerun() [cite: 119]
        st.stop() [cite: 120]

    # --- SIDEBAR OPERATOR (Păstrat conform sursei) ---
    if not st.session_state.operator_identificat:
        st.sidebar.markdown("###  👤  Identificare Operator") [cite: 123]
        cod_in = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod_input") [cite: 124]
        if cod_in:
            res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_in).execute() [cite: 126]
            if res_op.data:
                st.session_state.operator_identificat = res_op.data[0]['nume_prenume'] [cite: 128]
                st.rerun() [cite: 129]
        st.stop() [cite: 130]
    else:
        st.sidebar.success(f"Operator: {st.session_state.operator_identificat}") [cite: 132]
        if st.sidebar.button("Ieșire / Resetare"): [cite: 133]
            st.session_state.clear() [cite: 134]
            st.rerun() [cite: 135]

    # --- FILTRARE (ACTUALIZATĂ) ---
    st.markdown(f"<h3 style='text-align: center;'>  🛠️  Administrare: {st.session_state.operator_identificat}</h3>", unsafe_allow_html=True) [cite: 137]
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2]) 
    
    with c1:
        cat_admin = st.selectbox("1. Categoria:", ["", "Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"], key="admin_cat") [cite: 140]
    with c2:
        optiuni_tip = ["", "FDI", "PNCDI", "ORIZONT", "POC", "POCU", "POIM", "POCA", "PNDR"] [cite: 143]
        tip_admin = st.selectbox("2. Tip:", optiuni_tip, key="admin_tip") [cite: 144]
    with c3:
        id_admin = st.text_input("3. ID Proiect (Cod Inregistrare):", key="admin_id") [cite: 146]
    
    with c4:
        # LOGICA RESTRICTIE: Caseta 4 este activă doar dacă avem ID Proiect (Caseta 3)
        este_blocat = True if not id_admin else False
        componente_com = st.multiselect(
            "4. Componente:", 
            ["Date financiare", "Resurse umane", "Aspecte tehnice"], 
            disabled=este_blocat,
            key="admin_com"
        )

    st.write("---")

    # --- LOGICA CRUD ---
    if cat_admin != "":
        tabel_map = {
            "Contracte & Proiecte": "base_proiecte_internationale", 
            "Evenimente stiintifice": "base_evenimente_stiintifice", 
            "Proprietate intelectuala": "base_prop_intelect"
        } [cite: 150]
        nume_tabela = tabel_map.get(cat_admin) [cite: 151]

        if f'df_{nume_tabela}' not in st.session_state:
            query = supabase.table(nume_tabela).select("*") [cite: 153]
            if id_admin: query = query.eq("cod_identificare", id_admin) [cite: 154]
            res = query.execute() [cite: 155]
            st.session_state[f'df_{nume_tabela}'] = pd.DataFrame(res.data) [cite: 156]

        df_curent = st.session_state[f'df_{nume_tabela}'] [cite: 157]

        # BUTOANE CRUD (Poziționare conform sursei)
        col_n, col_s, col_v, col_d, col_a = st.columns([1, 1, 1, 1, 1]) [cite: 159]
        
        with col_n:
            if st.button("RÂND NOU"): [cite: 161]
                new_row = pd.DataFrame([{col: None for col in df_curent.columns}]) [cite: 162]
                st.session_state[f'df_{nume_tabela}'] = pd.concat([new_row, df_curent], ignore_index=True) [cite: 163]
                st.rerun() [cite: 164]

        with col_s:
            if st.button("SALVARE"): [cite: 166]
                st.success("Salvare solicitată în tabelele active...") [cite: 167]

        with col_v:
            if st.button("VALIDARE"): st.info("Validare în curs...") [cite: 169]
        with col_d:
            if st.button("ȘTERGERE"): st.error("Ștergere solicitată...") [cite: 172]
        with col_a:
            if st.button("ANULARE"): [cite: 175]
                if f'df_{nume_tabela}' in st.session_state: del st.session_state[f'df_{nume_tabela}'] [cite: 176, 177]
                st.rerun() [cite: 178]

        # AFIȘARE TABEL PRINCIPAL
        st.markdown(f"**Tabel Principal: {cat_admin}**")
        st.data_editor(st.session_state[f'df_{nume_tabela}'], use_container_width=True, hide_index=True, key=f"ed_{nume_tabela}") [cite: 180]

        # AFIȘARE TABELE COM_ (Doar dacă sunt selectate în Caseta 4 și avem ID IDBDC)
        if componente_com and id_admin:
            st.write("---")
            # Mapare denumiri noi către tabelele fizice
            map_tabele_com = {
                "Date financiare": "com_date_financiare",
                "Resurse umane": "com_echipe_proiect",
                "Aspecte tehnice": "com_aspecte_tehnice"
            }
            
            for comp in componente_com:
                nume_tabel_com = map_tabele_com[comp]
                st.markdown(f"**Componenta: {comp} (Tabel: {nume_tabel_com})**")
                
                # Preluare date din Supabase pentru ID-ul curent
                res_com = supabase.table(nume_tabel_com).select("*").eq("cod_identificare", id_admin).execute()
                df_com = pd.DataFrame(res_com.data)
                
                # Dacă nu există rând pentru acest ID, pregătim unul nou
                if df_com.empty:
                    st.caption(f"ℹ️ Nu există înregistrări în {nume_tabel_com}. Se va inițializa un rând nou.")
                    df_com = pd.DataFrame([{"cod_identificare": id_admin}])
                
                st.data_editor(df_com, use_container_width=True, hide_index=True, key=f"ed_{nume_tabel_com}")

if __name__ == "__main__":
    run()
