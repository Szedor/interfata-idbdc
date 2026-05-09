# =========================================================
# IDBDC/core/db.py
# VERSIUNE: 1.0
# STATUS: NOU - conexiune Supabase centralizată
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Furnizează clientul Supabase ca resursă cached.
#   Înlocuiește apelurile directe create_client din main.py.
#   Importat de calea2_admin/main.py și calea1_explorator/main.py.
# =========================================================

import streamlit as st
from supabase import create_client
from config import Config


@st.cache_resource
def get_supabase():
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
