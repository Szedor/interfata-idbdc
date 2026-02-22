import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Configurare pagină
st.set_page_config(page_title="IDBDC - Baze de Date Cercetare", layout="wide")

# Verificare parolă acces aplicație
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    parola_introdusa = st.text_input("Introduceți parola de acces:", type="password")
    if st.button("Acces"):
        if parola_introdusa == "EverDream2SZ":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Parolă incorectă!")
    st.stop()

st.success("✅ Acces Autorizat. Bun venit în sistemul IDBDC.")

# Conectare la Supabase prin API (Metoda HTTP - Port 443)
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]

try:
    supabase: Client = create_client(url, key)
    
    # Interogare tabel folosind API-ul
    # Tabelul stabilit în Protocolul de Lucru: base_proiecte_fdi
    response = supabase.table("base_proiecte_fdi").select("*").execute()
    
    if response.data:
        df = pd.DataFrame(response.data)
        st.write("### Date Proiecte FDI")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Conexiunea a reușit, dar tabelul nu conține date sau nu a fost găsit.")

except Exception as e:
    st.error(f"Eroare tehnică la conexiunea API: {e}")

st.divider()
st.info("Sistemul folosește acum conexiunea securizată prin API (Port 443) pentru a evita restricțiile de rețea.")
