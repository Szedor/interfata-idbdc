import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    # --- STILIZARE (Păstrată intactă) ---
    st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
        input { color: #000000 !important; background-color: #ffffff !important; }
        div.stButton > button { border: 1px solid white !important; color: white !important; background-color: rgba(255,255,255,0.1) !important; width: 100%; font-size: 12px !important; }
        div.stButton > button:hover { background-color: white !important; color: #003366 !important; }
    </style>
    """, unsafe_allow_html=True)

    # --- LOGICA ACCES & OPERATOR (Păstrată intactă) ---
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    if not st.session_state.autorizat_p1:
        # ... (codul de login existent)
        st.stop()

    # --- FILTRARE (ACTUALIZATĂ CU CASETA 4) ---
    st.markdown(f"<h3 style='text-align: center;'> 🛠️ Administrare: {st.session_state.operator_identificat}</h3>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2]) # Am adăugat a patra coloană
    
    with c1:
        cat_admin = st.selectbox("1. Categoria:", ["", "Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"], key="admin_cat")
    with c2:
        optiuni_tip = ["", "FDI", "PNCDI", "ORIZONT", "POC", "POCU", "POIM", "POCA", "PNDR"]
        tip_admin = st.selectbox("2. Tip:", optiuni_tip, key="admin_tip")
    with c3:
        id_admin = st.text_input("3. ID Proiect (Cod Inregistrare):", key="admin_id")
    
    with c4:
        # Logica de restricție Caseta 4: activă doar dacă avem ID Proiect (id_admin)
        dezactivat_com = True if not id_admin else False
        componente_com = st.multiselect(
            "4. Detalii (Tabele COM):", 
            ["Financiar", "Tehnic", "Echipe"], 
            disabled=dezactivat_com,
            help="Activ doar când un ID Proiect este specificat"
        )

    st.write("---")

    # --- LOGICA CRUD & SINCRONIZARE TABELE ---
    if cat_admin != "":
        tabel_map = {
            "Contracte & Proiecte": "base_proiecte_internationale", 
            "Evenimente stiintifice": "base_evenimente_stiintifice", 
            "Proprietate intelectuala": "base_prop_intelect"
        }
        nume_tabela = tabel_map.get(cat_admin)

        # Incarcare date tabela principala
        if f'df_{nume_tabela}' not in st.session_state:
            query = supabase.table(nume_tabela).select("*")
            if id_admin: query = query.eq("cod_identificare", id_admin)
            res = query.execute()
            st.session_state[f'df_{nume_tabela}'] = pd.DataFrame(res.data)

        df_curent = st.session_state[f'df_{nume_tabela}']

        # Butoane CRUD (Poziționare înghețată)
        col_n, col_s, col_v, col_d, col_a = st.columns([1, 1, 1, 1, 1])
        
        with col_n:
            if st.button("RÂND NOU"):
                # Creare rând în tabela de bază
                new_row = pd.DataFrame([{col: None for col in df_curent.columns}])
                st.session_state[f'df_{nume_tabela}'] = pd.concat([new_row, df_curent], ignore_index=True)
                st.info("S-a pregătit rând nou. Introduceți cod_identificare pentru a genera automat intrările în COM_.")
                st.rerun()

        # ... (restul butoanelor SALVARE, VALIDARE, STERGERE, ANULARE raman neschimbate ca design)

        # AFIȘARE TABEL PRINCIPAL
        st.markdown(f"**Tabela Principală: {cat_admin}**")
        st.data_editor(st.session_state[f'df_{nume_tabela}'], use_container_width=True, hide_index=True, key=f"ed_{nume_tabela}")

        # AFIȘARE TABELE COM_ (Dacă sunt selectate în Caseta 4)
        if componente_com and id_admin:
            st.write("---")
            map_com = {
                "Financiar": "com_date_financiare",
                "Tehnic": "com_aspecte_tehnice",
                "Echipe": "com_echipe_proiect"
            }
            
            for comp in componente_com:
                tab_nume = map_com[comp]
                st.markdown(f"**Componenta: {comp} (Sursă: {tab_nume})**")
                
                # Preluăm datele specifice codului de identificare
                res_com = supabase.table(tab_nume).select("*").eq("cod_identificare", id_admin).execute()
                df_com = pd.DataFrame(res_com.data)
                
                if df_com.empty:
                    st.warning(f"Nu există date în {tab_nume} pentru codul {id_admin}. Se va crea la salvare.")
                    # Cream un template gol daca nu exista
                    df_com = pd.DataFrame([{"cod_identificare": id_admin}])
                
                st.data_editor(df_com, use_container_width=True, hide_index=True, key=f"ed_{tab_nume}")

if __name__ == "__main__":
    run()
