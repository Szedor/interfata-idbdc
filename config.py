import streamlit as st

class Config:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    MAINTENANCE_PASSWORD = st.secrets["MAINTENANCE_PASSWORD"]

    VALID_PAGES = {"explorator", "admin", "brainstorming"}
