import streamlit as st
from supabase import create_client, Client

def run():
    # Conexiune Supabase (folosind datele tale din secrets)
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    # CSS pentru Admin (Albastru UPT și vizibilitate sidebar conform cerințelor tale)
    st.markdown("""
    <style>
        .stApp { background-color: #003366; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { color: white !important; }
        [data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 3px solid #ddd; }
        [data-testid="stSidebar"] label p { color: #003366 !important; font-weight: 900 !important; font-size: 16px !important; }
        [data-testid="stSidebar"] input { color: #000000 !important; background-color: #ffffff !important; border: 2px solid #003366 !important; }
        .eroare-idbdc-rosu { color: #ffffff !important; background-color: #ff0000 !important; padding: 10px; border-radius: 4px; text-align: center; font-weight: bold; border: 2px solid #8b0000; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

    # Inițializare variabile de sesiune
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    # PAS 1: POARTA MASTER (Conform fișierului tău)
    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'> 🛡️  Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola master:", type="password", key="p1_pass")
            if st.button("Autorizare acces", use_container_width=True):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
                else:
                    st.markdown("<div class='eroare-idbdc-rosu'> ⚠️  Parolă incorectă.</div>", unsafe_allow_html=True)
        st.stop()

    # PAS 2: IDENTIFICARE OPERATOR (SIDEBAR - corelată cu tabela com_operatori)
    st.sidebar.markdown("###  👤  Identificare Operator")
    if not st.session_state.operator_identificat:
        cod_in = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod_input")
        if cod_in:
            try:
                # Verificăm codul în tabela com_operatori folosind coloana cod_operatori [cite: 172]
                res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_in).execute()
                if res_op.data:
                    st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                    st.rerun()
                else:
                    st.sidebar.markdown("<div class='eroare-idbdc-rosu'>Cod invalid!</div>", unsafe_allow_html=True)
            except Exception as e:
                st.sidebar.markdown(f"<div class='eroare-idbdc-rosu'>Eroare conexiune DB.</div>", unsafe_allow_html=True)
        st.stop()
    else:
        # Afișarea operatorului autentificat în sidebar [cite: 182]
        st.sidebar.success(f"Salut, {st.session_state.operator_identificat}!")
        if st.sidebar.button("Ieșire / Resetare"):
            st.session_state.clear()
            st.rerun()

    # ZONA DE LUCRU (Urmează să fie construită aici)
    st.markdown(f"<h3 style='text-align: center;'> 🛠️  Administrare: {st.session_state.operator_identificat}</h3>", unsafe_allow_html=True)
    st.write("---")
