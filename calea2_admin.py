import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    # STIL VIZUAL (IDBDC Standard)
    st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
        input { color: #000000 !important; background-color: #ffffff !important; }
        .stDataFrame { background-color: white !important; border-radius: 5px; }
        /* Stil special pentru butoane CRUD */
        .stButton>button { border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    # GESTIUNE SESIUNE & PAZNICI
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    # POARTA 1: PAROLA
    if not st.session_state.autorizat_p1:
        st.markdown('<div style="background-color: #1a4a7a; padding: 40px; border-radius: 15px;">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'> 🛡️ Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola:", type="password", key="p1_pass")
            if st.button("Autorizare acces", use_container_width=True):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
                else:
                    st.error("Parolă incorectă.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # POARTA 2: AUTENTIFICARE OPERATOR
    st.sidebar.markdown("### 👤 Autentificare")
    if not st.session_state.operator_identificat:
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

    # ZONA DE LUCRU
    st.markdown(f"<h3 style='text-align: center;'> 🛠️ Administrare: {st.session_state.operator_identificat}</h3>", unsafe_allow_html=True)
    st.write("---")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        list_cat = [i["denumire_categorie"] for i in res_cat.data]
        cat_admin = st.selectbox("Categoria de informatii:", [""] + list_cat, key="admin_cat")
    with c2:
        list_tip = []
        if cat_admin == "Contracte & Proiecte":
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
        tip_admin = st.selectbox("Tip de contract / proiect:", [""] + list_tip, key="admin_tip")
    with c3:
        id_admin = st.text_input("ID proiect / Numar de contract:", key="admin_id")

    # INTEGRARE BUTOANE CRUD
    if cat_admin != "":
        st.write("---")
        
        # Butonul CREATE (Adăugare)
        col_btn1, col_btn2 = st.columns([1, 5])
        with col_btn1:
            if st.button("➕ Proiect Nou", type="primary", use_container_width=True):
                st.toast("Deschidere formular adăugare...") # Placeholder pentru Create

        tabel_map = {"Contracte & Proiecte": "base_proiecte_internationale", "Evenimente stiintifice": "base_evenimente_stiintifice", "Proprietate intelectuala": "base_prop_intelect"}
        nume_tabela = tabel_map.get(cat_admin)
        
        if nume_tabela:
            query = supabase.table(nume_tabela).select("*")
            if tip_admin: query = query.eq("acronim_contracte_proiecte", tip_admin)
            if id_admin: query = query.eq("cod_identificare", id_admin)
            
            res = query.execute()
            if res.data:
                df = pd.DataFrame(res.data)
                
                # Afișarea tabelului cu butoane de acțiune simulate prin coloane Streamlit
                st.write(f"Înregistrări găsite: {len(df)}")
                
                # Limităm afișarea pentru performanță în administrare (primele 10 rânduri pentru editare rapidă)
                for index, row in df.head(10).iterrows():
                    with st.expander(f"📌 {row.get('cod_identificare', 'Fără ID')} - {row.get('titlu_proiect', 'Fără Titlu')[:50]}..."):
                        col_edit, col_del, col_info = st.columns([1, 1, 4])
                        with col_edit:
                            if st.button(f"📝 Editează", key=f"edit_{index}"):
                                st.session_state.edit_id = row['cod_identificare']
                                st.info(f"Editare activată pentru: {row['cod_identificare']}")
                        with col_del:
                            if st.button(f"🗑️ Șterge", key=f"del_{index}"):
                                st.warning(f"Confirmați ștergerea pentru {row['cod_identificare']}?")
                        with col_info:
                            st.write(f"**Director:** {row.get('director_proiect', 'N/A')}")
            else:
                st.info("Nu s-au găsit date.")

if __name__ == "__main__":
    run()
