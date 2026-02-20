import streamlit as st
import pandas as pd

def check_idbdc_status(conn):
    st.subheader("🔍 Status Sistem IDBDC")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**Platformă:** GitHub + Streamlit Cloud")
        st.info("**Bază de date:** PostgreSQL")

    with col2:
        try:
            # Verificăm prezența tabelei principale
            query = "SELECT COUNT(*) as total FROM base_proiecte_fdi"
            df = conn.query(query, ttl="10m")
            st.success(f"✅ Conexiune DB Activă: {df['total'][0]} proiecte în FDI")
        except Exception as e:
            st.error(f"❌ Eroare conexiune: {e}")

    # Verificare Coloană Cheie
    try:
        check_cols = "SELECT * FROM base_proiecte_fdi LIMIT 1"
        df_cols = conn.query(check_cols)
        if 'cod_inregistrare' in df_cols.columns:
            st.success("✅ Coloana 'cod_inregistrare' identificată în FDI.")
        else:
            st.warning("⚠️ 'cod_inregistrare' nu a fost găsită în tabelă.")
    except:
        pass

# Notă: Acest script presupune că ai configurat deja st.connection("postgresql")
    if st.sidebar.button("Ieșire (Logout)"):
        st.session_state["autentificat"] = False
        st.rerun()
