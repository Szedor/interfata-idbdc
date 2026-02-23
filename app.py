import streamlit as st

# Configurare generală (rămâne valabilă pentru toate căile)
st.set_page_config(page_title="IDBDC UPT", layout="wide")

# Citim calea din URL (ex: ?pagina=explorator sau ?pagina=admin)
query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

# Arhitectura pe 3 căi
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

elif calea_activa == "analiza":
    try:
        import calea3_analiza
        calea3_analiza.run()
    except Exception as e:
        st.error(f"Eroare la încărcarea Căii 3: {e}")
