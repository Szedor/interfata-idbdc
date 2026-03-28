import streamlit as st

import calea1_explorator
import calea2_admin
import calea3_brainstorming

st.set_page_config(page_title="Interfata IDBDC", layout="wide")

# Preluare query params

query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

# Router (fără validare momentan)

if calea_activa == "explorator":
calea1_explorator.main()

elif calea_activa == "admin":
calea2_admin.main()

elif calea_activa == "brainstorming":
calea3_brainstorming.main()

else:
calea1_explorator.main()
