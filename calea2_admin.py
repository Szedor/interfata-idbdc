import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    # --- SECȚIUNE VALIDATĂ / ÎNGHEȚATĂ (NU SE MODIFICĂ) ---
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
        input { color: #000000 !important; background-color: #ffffff !important; }
        .eroare-idbdc-rosu { color: #ffffff !important; background-color: #ff0000 !important; padding: 10px; border-radius: 4px; text-align: center; font-weight: bold; border: 2px solid #8b0000; margin-top: 10px; }
        div.stButton > button { border: 1px solid white !important; color: white !important; background-color: rgba(255,255,255,0.1) !important; width: 100%; font-size: 12px !important; }
        div.stButton > button:hover { background-color: white !important; color: #003366 !important; }
    </style>
    """, unsafe_allow_html=True)

    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'> 🛡️ Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola:", type="password", key="p1_pass")
            if st.button("Autorizare acces"):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
        st.stop()

    if not st.session_state.operator_identificat:
        st.sidebar.markdown("### 👤 Identificare Operator")
        cod_in = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod_input")
        if cod_in:
            res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_in).execute()
            if res_op.data:
                st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                st.rerun()
        st.stop()
    else:
        st.sidebar.success(f"Operator: {st.session_state.operator_identificat}")
        if st.sidebar.button("Ieșire / Resetare"):
            st.session_state.clear()
            st.rerun()
    # --- SFÂRȘIT SECȚIUNE ÎNGHEȚATĂ ---

    # --- RECONSTRUCȚIE LOGICĂ IDBDC ---
    st.markdown(f"<h3 style='text-align: center;'> 🛠️ Administrare: {st.session_state.operator_identificat}</h3>", unsafe_allow_html=True)
    
    # 1. Obținere Acronime din Nomenclator (Real-time)
    res_nom = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
    lista_acronime = [""] + [r['acronim_contracte_proiecte'] for r in res_nom.data] if res_nom.data else [""]

    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2])
    with c1:
        cat_admin = st.selectbox("1. Categoria:", ["", "Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"], key="admin_cat")
    with c2:
        tip_admin = st.selectbox("2. Tip:", lista_acronime, key="admin_tip")
    with c3:
        id_admin = st.text_input("3. ID Proiect (Cod Identificare):", key="admin_id")
    with c4:
        # Caseta 4 este acum activă mereu conform cerinței
        componente_com = st.multiselect(
            "Componente:", 
            ["Date financiare", "Resurse umane", "Aspecte tehnice"], 
            key="admin_com"
        )

    st.write("---")

    if cat_admin != "":
        # Mapare tabel principal (FDI sau restul proiectelor - acum toate pe cod_identificare)
        tabel_map = {
            "Contracte & Proiecte": "base_proiecte_internationale" if tip_admin != "FDI" else "base_proiecte_fdi",
            "Evenimente stiintifice": "base_evenimente_stiintifice",
            "Proprietate intelectuala": "base_prop_intelect"
        }
        nume_tabela = tabel_map.get(cat_admin)

        # Butoane Control
        col_n, col_s, col_v, col_d, col_a = st.columns([1, 1, 1, 1, 1])
        # (Logica butoanelor va fi detaliată după ce stabilim vizualizarea)

        # --- LOGICA DE AFIȘARE TABEL PRINCIPAL ---
        query = supabase.table(nume_tabela).select("*")
        if id_admin: 
            query = query.eq("cod_identificare", id_admin) # Filtrare dacă ID există
        
        res_main = query.execute()
        df_main = pd.DataFrame(res_main.data)
        
        st.markdown(f"**Tabel: {nume_tabela}**")
        st.data_editor(df_main, use_container_width=True, hide_index=True, key=f"editor_{nume_tabela}")

        # --- LOGICA DE AFIȘARE COMPONENTE (COM) ---
        if componente_com:
            map_tabele_com = {
                "Date financiare": "com_date_financiare",
                "Resurse umane": "com_echipe_proiect",
                "Aspecte tehnice": "com_aspecte_tehnice"
            }
            
            for comp in componente_com:
                nume_tabel_com = map_tabele_com[comp]
                st.write("---")
                st.markdown(f"**Componenta: {comp}**")
                
                query_com = supabase.table(nume_tabel_com).select("*")
                if id_admin:
                    query_com = query_com.eq("cod_identificare", id_admin)
                
                res_com = query_com.execute()
                df_com = pd.DataFrame(res_com.data)
                
                # Afișare tabel (complet sau filtrat)
                st.data_editor(df_com, use_container_width=True, hide_index=True, key=f"editor_{nume_tabel_com}")

if __name__ == "__main__":
    run()
