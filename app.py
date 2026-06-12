# =========================================================
# IDBDC/appy.py
# VERSIUNE: 1.0
# STATUS: CORECTAT - Calea2 importată din calea2_admin/main.py
# DATA: 2026.05.09
# =========================================================
# MODIFICĂRI IN VERSIUNE:
#   - Importul Căii2 modificat din `admin.main` în
#     `calea2_admin.main` pentru noua structură modulară.
#     O singură linie schimbată — restul neatins.
# =========================================================

import streamlit as st
from config import Config

st.set_page_config(page_title="IDBDC UPT - Sistem Integrat", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] { display: block !important; visibility: visible !important; opacity: 1 !important; width: auto !important; transform: none !important; }
        #MainMenu { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        header { visibility: hidden !important; }
        [data-testid="stToolbar"] { display: none !important; }
        [data-testid="stDecoration"] { display: none !important; }
        [data-testid="stStatusWidget"] { display: none !important; }
        [data-testid="manage-app-button"] { display: none !important; }
        div[class*="manage"] { display: none !important; }
        button[kind="managedApp"] { display: none !important; }
        .stAppDeployButton { display: none !important; }
        iframe[title="streamlit_app"] ~ div { display: none !important; }
        [data-testid="stActionButtonIcon"] { display: none !important; }
        div[class*="viewerBadge"] { display: none !important; }
        ._profilePreview_gzau3_63 { display: none !important; }
        .viewerBadge_container__r5tak { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

if calea_activa == "ai":
    calea_activa = "brainstorming"

if calea_activa not in Config.VALID_PAGES:
    calea_activa = "explorator"

if calea_activa == "explorator":
    from explorator import main as explorator_main
    explorator_main.run()
elif calea_activa == "admin":
    from calea2_admin import main as admin_main
    admin_main.run()
elif calea_activa == "brainstorming":
    import calea3_brainstorming
    calea3_brainstorming.run()
else:
    st.warning("Pagina solicitată nu a fost găsită. Revenire la Explorator...")
    from explorator import main as explorator_main
    explorator_main.run()
