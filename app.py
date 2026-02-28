import streamlit as st

# Configurare generală a paginii
st.set_page_config(page_title="IDBDC UPT - Sistem Integrat", layout="wide")

# Preluare parametru pagină din URL (ex: ?pagina=brainstorming)
query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

# Direcționare către scriptul corespunzător
if calea_activa == "explorator":
    try:
        import calea1_explorator
        calea1_explorator.run()
    except Exception as e:
        st.error(f"Eroare la încărcarea modulului Explorator: {e}")

elif calea_activa == "admin":
    try:
        import calea2_admin
        calea2_admin.run()
    except Exception as e:
        st.error(f"Eroare la încărcarea modulului Admin: {e}")

elif calea_activa == "brainstorming":
    try:
        import calea3_brainstorming
        calea3_brainstorming.run()
    except Exception as e:
        st.error(f"Eroare la încărcarea modulului Brainstorming AI: {e}")

else:
    st.warning("Pagina solicitată nu a fost găsită. Revenire la Explorator...")
    import calea1_explorator
    calea1_explorator.run()
