import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    # --- STIL VIZUAL ---
    st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
        input { color: #000000 !important; background-color: #ffffff !important; }
        div.stButton > button { border: 1px solid white !important; color: white !important; background-color: rgba(255,255,255,0.1) !important; width: 100%; }
        .eroare-idbdc-rosu { color: #ffffff !important; background-color: #ff0000 !important; padding: 10px; border-radius: 4px; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    # --- LOGICA ACCES ---
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    if not st.session_state.autorizat_p1:
        # (Codul de parola master ramane neschimbat)
        st.stop()

    if not st.session_state.operator_identificat:
        # (Codul de identificare operator ramane neschimbat)
        st.stop()

    # --- ZONA DE FILTRARE EXTINSĂ (4 CASETE) ---
    st.markdown(f"<h3 style='text-align: center;'> 🛠️ Administrare Proiecte IDBDC</h3>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        cat_admin = st.selectbox("Categoria:", ["", "Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"], key="admin_cat")
    with c2:
        tip_admin = st.selectbox("Tip proiect:", ["", "FDI", "PNCDI", "ORIZONT"], key="admin_tip")
    with c3:
        id_admin = st.text_input("Cod Identificare:", key="admin_id")
    with c4:
        # ACEASTA ESTE CASETA NOUĂ: Selectăm ce tabelă secundară vizualizăm
        sectiune = st.selectbox("Secțiune Date:", ["Date Identificare", "Date Financiare", "Echipa Proiect", "Date Tehnice"], key="admin_sectiune")
    
    st.write("---")

    # --- LOGICA DE MAPARE TABELE ---
    if cat_admin != "" and id_admin != "":
        # Maparea tabelelor în funcție de Secțiunea aleasă
        map_sectiuni = {
            "Date Identificare": "base_proiecte_internationale", # Sau tabelul principal corespunzator
            "Date Financiare": "detalii_financiare",
            "Echipa Proiect": "detalii_echipa",
            "Date Tehnice": "detalii_tehnice"
        }
        
        nume_tabela = map_sectiuni.get(sectiune)

        # Încărcare date
        if f'df_{nume_tabela}_{id_admin}' not in st.session_state:
            res = supabase.table(nume_tabela).select("*").eq("cod_identificare", id_admin).execute()
            st.session_state[f'df_{nume_tabela}_{id_admin}'] = pd.DataFrame(res.data)

        df_curent = st.session_state[f'df_{nume_tabela}_{id_admin}']

        # BUTOANE CRUD
        col_n, col_s, col_a, col_v, col_d = st.columns(5)
        
        with col_n:
            if st.button("RÂND NOU"):
                # Aici vom pune logica care creează rânduri în TOATE cele 4 tabele deodată
                st.info("Logica de multi-insert pregătită...")
        
        with col_a:
            if st.button("ANULARE"):
                del st.session_state[f'df_{nume_tabela}_{id_admin}']
                st.rerun()

        # Editorul de date pentru secțiunea selectată
        edited_df = st.data_editor(df_curent, use_container_width=True, hide_index=True, key=f"ed_{nume_tabela}")

        if not df_curent.equals(edited_df):
            with col_s:
                if st.button("SALVARE"):
                    # Aici salvăm doar în tabela activă în caseta 4
                    st.success(f"Salvare în {sectiune}...")

if __name__ == "__main__":
    run()
