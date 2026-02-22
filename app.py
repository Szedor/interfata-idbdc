import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Configurare pagină
st.set_page_config(page_title="Interfață IDBDC", layout="wide")

# 1. BARIERA DE ACCES (Login)
if "autentificat" not in st.session_state:
    st.session_state["autentificat"] = False

if not st.session_state["autentificat"]:
    st.title("🔒 Acces Securizat IDBDC")
    user = st.text_input("Utilizator")
    parola = st.text_input("Parolă", type="password")
    
    if st.button("Deblochează Poarta 1"):
        # Verificăm parola stabilită de tine
        if user == "admin" and parola == "EverDream2026IDBDC":
            st.session_state["autentificat"] = True
            st.rerun()
        else:
            st.error("Acces respins. Date incorecte.")
else:
    # 2. INTERFAȚA DUPĂ AUTENTIFICARE
    st.title("🔄 Interfață IDBDC - Operatori")
    st.sidebar.success("Conectat la Supabase")
    
    if st.sidebar.button("Ieșire (Logout)"):
        st.session_state["autentificat"] = False
        st.rerun()

    # Conexiunea la baza de date
    try:
        engine = create_engine(st.secrets["DB_URL"])
        
        # Citirea datelor din Supabase
        query = "SELECT * FROM base_proiecte_internationale"
        df = pd.read_sql(query, engine)

        st.subheader(f"📋 Proiecte Internaționale ({len(df)} înregistrări)")
        
        # Afișarea tabelului cu funcție de căutare
        search = st.text_input("Caută după Cod Identificare sau Acronim:", "")
        if search:
            df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Eroare la conectarea cu Supabase: {e}")
        st.info("Verifică dacă 'Secrets' în Streamlit Cloud sunt configurate corect.")

    # Aici vom adăuga secțiunea Vizitatori după ce ești mulțumit de Operatori
