import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title="Consola IDBDC", layout="wide")
st.title("🛡️ Consola Operatori IDBDC")

# Preluăm conexiunea din Secrets
if "postgres_url" in st.secrets:
    try:
        engine = create_engine(st.secrets["postgres_url"])
        
        # Interogarea SQL pentru tabelul tău
        query = "SELECT * FROM base_proiecte_fdi" 
        df = pd.read_sql(query, engine)

        st.success("✅ Datele au fost încărcate cu succes!")
        
        # Afișăm tabelul interactiv
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Eroare la citirea datelor: {e}")
else:
    st.warning("⚠️ Conexiunea nu este configurată în Secrets.")
