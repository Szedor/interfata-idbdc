import streamlit as st

from config import Config

import calea1_explorator
import calea2_admin
import calea3_brainstorming

st.set_page_config(page_title="Interfata IDBDC", layout="wide")

# Preluare query params

query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

# Validare pagină

if calea_activa not in Config.VALID_PAGES:
calea_activa = "explorator"

# Router

if calea_activa == "explorator":
calea1_explorator.main()

elif calea_activa == "admin":
calea2_admin.main()

elif calea_activa == "brainstorming":
calea3_brainstorming.main()
