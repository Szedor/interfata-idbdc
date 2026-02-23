import streamlit as st
import pandas as pd
from supabase import create_client, Client

# 1. CONFIGURARE VIZUALĂ UPT
st.set_page_config(page_title="Sistemul de administrare IDBDC", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #003366; color: white; }
    h1, h2, h3, label { color: white !important; }
    .stButton>button { width: 100%; background-color: #f0f2f6; color: #003366; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIUNE SUPABASE
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 3. LOGICA DE ACCES (CELE DOUĂ BARIERE)
if 'autentificat' not in st.session_state:
    st.session_state.autentificat = False

if not st.session_state.autentificat:
    st.title("🛡️ Acces Sistem IDBDC")
    
    # BARIERA 1: Parola Unică
    parola_intrare = st.text_input("Introduceți parola de sistem:", type="password")
    
    # BARIERA 2: Cod Operator
    cod_operator_introdus = st.text_input("Introduceți Codul de Operator:")

    if st.button("Verifică Acces"):
        # Verificăm Parola (o poți schimba ulterior în Secrets)
        if parola_intrare == st.secrets["MASTER_PASSWORD"]:
            
            # Verificăm Codul în tabela com_operatori
            try:
                check_op = supabase.table("com_operatori").select("*").eq("cod_operator", cod_operator_introdus).execute()
                
                if len(check_op.data) > 0:
                    st.session_state.autentificat = True
                    st.session_state.nume_operator = check_op.data[0].get('nume_operator', 'Utilizator')
                    st.rerun()
                else:
                    st.error("Cod Operator invalid!")
            except Exception as e:
                st.error(f"Eroare la validarea operatorului: {e}")
        else:
            st.error("Parolă de sistem incorectă!")
            
else:
    # --- INTERFAȚA DUPĂ AUTENTIFICARE ---
    st.title(f"Sistemul de administrare IDBDC")
    st.success(f"Bun venit, {st.session_state.nume_operator}!")
    
    # Selecție tabel
    lista_tabele = ["base_contracte_cep", "base_proiecte_fdi", "com_date_financiare", "v_idbdc_centralizator"]
    tabel_ales = st.selectbox("Alegeți tabelul pentru analiză:", lista_tabele)
    
    if st.button("Încarcă date"):
        res = supabase.table(tabel_ales).select("*").limit(10).execute()
        st.dataframe(pd.DataFrame(res.data))

    if st.button("Ieșire (Logout)"):
        st.session_state.autentificat = False
        st.rerun()
