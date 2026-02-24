import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    # --- CONEXIUNE ȘI STIL (CONFORM PROTOCOLULUI) ---
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
        input { color: #000000 !important; background-color: #ffffff !important; }
        .eroare-idbdc-rosu { color: #ffffff !important; background-color: #ff0000 !important; padding: 10px; border-radius: 4px; text-align: center; font-weight: bold; border: 2px solid #8b0000; margin-top: 10px; }
        
        /* Stil butoane text CRUD */
        div.stButton > button { 
            border: 1px solid white !important; 
            color: white !important; 
            background-color: rgba(255, 255, 255, 0.1) !important;
            width: 100%;
        }
        div.stButton > button:hover { 
            background-color: white !important; 
            color: #003366 !important; 
        }
    </style>
    """, unsafe_allow_html=True)

    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    # --- PAS 1: POARTA MASTER (IDENTIC DOCX) ---
    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'> 🛡️ Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola master:", type="password", key="p1_pass")
            if st.button("Autorizare acces", use_container_width=True):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
                else:
                    st.markdown("<div class='eroare-idbdc-rosu'> ⚠️ Parolă incorectă.</div>", unsafe_allow_html=True)
        st.stop()

    # --- PAS 2: IDENTIFICARE OPERATOR (SIDEBAR - IDENTIC DOCX) ---
    st.sidebar.markdown("### 👤 Identificare Operator")
    if not st.session_state.operator_identificat:
        cod_in = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod_input")
        if cod_in:
            try:
                # Căutare în tabela com_operatori folosind coloana cod_operatori
                res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_in).execute()
                if res_op.data and len(res_op.data) > 0:
                    st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                    st.rerun()
                else:
                    st.sidebar.markdown("<div class='eroare-idbdc-rosu'>Cod operator inexistent!</div>", unsafe_allow_html=True)
            except Exception:
                st.sidebar.markdown("<div class='eroare-idbdc-rosu'>Eroare tehnică DB.</div>", unsafe_allow_html=True)
        st.stop()
    else:
        st.sidebar.success(f"Operator: {st.session_state.operator_identificat}")
        if st.sidebar.button("Ieșire / Resetare"):
            st.session_state.clear()
            st.rerun()

    # --- ZONA DE LUCRU (CELE 3 CASETE - LINIA 75-93 DOCX) ---
    st.markdown(f"<h3 style='text-align: center;'> 🛠️ Administrare: {st.session_state.operator_identificat}</h3>", unsafe_allow_html=True)
    st.write("---")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
            list_cat = [i["denumire_categorie"] for i in res_cat.data]
        except:
            list_cat = ["Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"]
        cat_admin = st.selectbox("Categoria de informatii:", [""] + list_cat, key="admin_cat")
    
    with c2:
        list_tip = []
        if cat_admin == "Contracte & Proiecte":
            try:
                res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
            except:
                list_tip = []
        tip_admin = st.selectbox("Tip de contract / proiect:", [""] + list_tip, key="admin_tip")
    
    with c3:
        id_admin = st.text_input("ID proiect / Numar de contract:", key="admin_id")
    st.write("---")

    # --- ATRIBUTE CRUD TEXT ---
    if cat_admin != "":
        tabel_map = {
            "Contracte & Proiecte": "base_proiecte_internationale", 
            "Evenimente stiintifice": "base_evenimente_stiintifice", 
            "Proprietate intelectuala": "base_prop_intelect"
        }
        nume_tabela = tabel_map.get(cat_admin)

        if f'df_{nume_tabela}' not in st.session_state:
            try:
                query = supabase.table(nume_tabela).select("*")
                if id_admin: query = query.eq("cod_identificare", id_admin)
                res = query.execute()
                st.session_state[f'df_{nume_tabela}'] = pd.DataFrame(res.data)
            except:
                st.session_state[f'df_{nume_tabela}'] = pd.DataFrame()

        df_curent = st.session_state[f'df_{nume_tabela}']

        # Rând butoane CRUD
        col_n, col_s, col_v, col_d = st.columns([1, 1, 1, 1])
        
        with col_n:
            if st.button("RÂND NOU"):
                if not df_curent.empty:
                    new_row = pd.DataFrame([{col: None for col in df_curent.columns}])
                    st.session_state[f'df_{nume_tabela}'] = pd.concat([new_row, df_curent], ignore_index=True)
                st.rerun()

        # Editorul de date activ
        edited_df = st.data_editor(
            st.session_state[f'df_{nume_tabela}'],
            use_container_width=True,
            hide_index=True,
            key=f"ed_{nume_tabela}"
        )

        # Logică butoane după modificare
        if not st.session_state[f'df_{nume_tabela}'].equals(edited_df):
            with col_s:
                if st.button("SALVARE"): 
                    st.success("Date pregătite")
            with col_v:
                if st.button("VALIDARE"): 
                    st.info("Protocol OK")
            with col_d:
                if st.button("ȘTERGERE"): 
                    st.error("Marcat")

if __name__ == "__main__":
    run()
