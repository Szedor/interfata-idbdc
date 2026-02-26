import streamlit as st

# Configurare generală
st.set_page_config(page_title="IDBDC UPT", layout="wide")

# Preluare parametru pagină
query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

# Direcționare către scriptul corespunzător
if calea_activa == "explorator":
    try:
        import calea1_explorator
        calea1_explorator.run()
    except Exception as e:
        st.error(f"Eroare la încărcarea Căii 1: {e}")

elif calea_activa == "admin":
    try:
        import calea2_admin
        calea2_admin.run()
    except Exception as e:
        st.error(f"Eroare la încărcarea Căii 2: {e}")
        
