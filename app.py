import streamlit as st
from config import Config

# Configurare generală a paginii
st.set_page_config(page_title="IDBDC UPT - Sistem Integrat", layout="wide")

# Elimină toate elementele UI Streamlit
st.markdown(
    """
    <style>
        #MainMenu { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        header { visibility: hidden !important; }
        [data-testid="stToolbar"] { display: none !important; }
        [data-testid="stDecoration"] { display: none !important; }
        [data-testid="stStatusWidget"] { display: none !important; }
        [data-testid="manage-app-button"] { display: none !important; }
        div[class*="viewerBadge"] { display: none !important; }
        ._profilePreview_gzau3_63 { display: none !important; }
        .viewerBadge_container__r5tak { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Preluare parametru pagină din URL
query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

# Alias
if calea_activa == "ai":
    calea_activa = "brainstorming"

# Validare pagină
if calea_activa not in Config.VALID_PAGES:
    calea_activa = "explorator"

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
        st.error(f"Eroare la încărcarea modulului AI: {e}")

else:
    st.warning("Pagina solicitată nu a fost găsită. Revenire la Explorator...")
    import calea1_explorator
    calea1_explorator.run()
