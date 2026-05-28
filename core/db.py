# =========================================================
# IDBDC/core/db.py
# v.modul.1.0 - Conexiune Supabase centralizată
# =========================================================

import streamlit as st
from supabase import create_client
from config import Config


@st.cache_resource
def get_supabase():
    """Furnizează clientul Supabase ca resursă cached (unică per sesiune)."""
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
