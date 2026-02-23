import streamlit as st
import pandas as pd
from supabase import create_client, Client

def run():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    # PAS 1: Bariera Centrală (Master)
    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'> 🛡️  Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_c, _ = st.columns([1, 0.6, 1])
        with col_c:
            parola_master = st.text_input("Parola master:", type="password", key="p_master_admin")
            if st.button("Autorizare"):
                if parola_master == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
                else:
                    st.error("Parolă incorectă!")
        st.stop()

    # PAS 2: Identificare Operator (Sidebar)
    st.sidebar.markdown("###  👤  Identificare Operator")
    if not st.session_state.operator_identificat:
        cod_op = st.sidebar.text_input("Cod Identificare", type="password", key="cod_op_admin")
        if cod_op:
            try:
                res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_op).execute()
                if res_op.data:
                    st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                    st.rerun()
                else:
                    st.sidebar.error("Cod invalid!")
            except:
                st.sidebar.error("Eroare conexiune!")
        st.stop()
    else:
        st.sidebar.success(f"Salut, {st.session_state.operator_identificat}!")
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # PAS 3: Panou de Lucru - Selectare Date pentru Editare
    st.markdown(f"### 🛠️ Administrare Date: {st.session_state.operator_identificat}")
    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        # Alegem ce tabelă edităm
        tabela_selectata = st.selectbox("Alege tabela de lucru:", ["---", "base_proiecte_fdi", "Evenimente", "Proprietate Intelectuala"])
    
    with col2:
        if tabela_selectata == "base_proiecte_fdi":
            # Exemplu de filtrare după cod_inregistrare (cum am stabilit în protocol) [cite: 5]
            st.text_input("Caută după cod înregistrare (FDI):", key="search_fdi")

    if tabela_selectata != "---":
        st.info(f"Sistemul este gata să încarce datele din {tabela_selectata}. Urmează să definim grila de editare.")
