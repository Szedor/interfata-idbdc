import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="IDBDC UPT", layout="wide")
st.title("🛡️ Consola Operatori IDBDC")

# Mesaj de verificare
st.info("Dacă vezi acest mesaj, interfața funcționează. Urmează conectarea la date.")

# Încercăm să citim datele din Supabase
try:
    conn = psycopg2.connect(st.secrets["postgres_url"])
    st.success("✅ Conexiune reușită la baza de date!")
    
    query = "SELECT id_tehnic, titlul, validat_idbdc FROM base_proiecte_fdi LIMIT 10"
    df = pd.read_sql(query, conn)
    st.write("### Ultimele 10 proiecte FDI:")
    st.table(df)
    
    conn.close()
except Exception as e:
    st.error(f"❌ Încă nu am configurat conexiunea. Eroare: {e}")
