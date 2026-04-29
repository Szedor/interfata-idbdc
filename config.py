# =========================================================
# IDBDC/admin/ui.py
# VERSIUNE: 5.1
# STATUS: in adaptare
# DATA: 2026.04.30
# =========================================================

import streamlit as st

class Config:
    try:
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
        MAINTENANCE_PASSWORD = st.secrets["MAINTENANCE_PASSWORD"]
    except:
        SUPABASE_URL = ""
        SUPABASE_KEY = ""
        MAINTENANCE_PASSWORD = ""
    VALID_PAGES = {"explorator", "admin", "brainstorming"}
