import streamlit as st
import pandas as pd
from supabase import create_client, Client

# 1. CONFIGURARE VIZUALĂ UPT (research.upt.ro)
st.set_page_config(page_title="Sistemul de administrare IDBDC", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #003366; color: white; }
    h1, h2, h3, label { color: white !important; }
    .stButton>button { width: 100%; background-color: #f0f2f6; color: #003366; }
    /* Fundal alb pentru tabel pentru lizibilitate date economice */
    .stDataFrame { background-color: white; border-radius: 5px; }
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
    
    # BARIERA 1: Parola Unică (Master)
    parola_intrare = st.text_input("Introduceți parola de sistem:", type="password")
    
    # BARIERA 2: Cod Operator (din tabela com_operatori)
    cod_operator_introdus = st.text_input("Introduceți Codul de Operator:")

    if st.button("Verifică Acces"):
        if parola_intrare == st.secrets["MASTER_PASSWORD"]:
            try:
                # Interogare tabel operatori
                check_op = supabase.table("com_operatori").select("*").eq("cod_operator", cod_operator_introdus).execute()
                
                if len(check_op.data) > 0:
                    st.session_state.autentificat = True
                    # Salvăm numele operatorului pentru personalizarea interfeței
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
    st.title("Sistemul de administrare IDBDC")
    st.success(f"Bun venit, {st.session_state.nume_operator}!")
    
    # Selectorul de tabele (bazat pe lista ta de 34 tabele)
    lista_tabele = [
        "base_contracte_cep", "base_proiecte_fdi", "base_proiecte_pnrr", 
        "com_date_financiare", "com_operatori", "v_idbdc_centralizator"
    ]
    
    tabel_ales = st.selectbox("Alegeți tabelul pentru analiză:", lista_tabele)
    
    if st.button("Încarcă date"):
        try:
            res = supabase.table(tabel_ales).select("*").limit(10).execute()
            if res.data:
                st.dataframe(pd.DataFrame(res.data))
            else:
                st.info("Tabelul nu conține date.")
        except Exception as e:
            st.error(f"Eroare la încărcare: {e}")

    # Buton de Ieșire
    if st.sidebar.button("Ieșire (Logout)"):
        st.session_state.autentificat = False
        st.rerun()
