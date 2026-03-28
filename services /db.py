import streamlit as st
from supabase import create_client
from config import Config


@st.cache_resource
def get_supabase():
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
