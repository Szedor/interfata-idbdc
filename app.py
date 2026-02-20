Python
import streamlit as st

# 1. Identitatea Vizuală
st.set_page_config(page_title="Consola Responsabili IDBDC", layout="wide")
st.title("🛡️ Consola Responsabili IDBDC")

# Inițializăm starea sesiunii pentru a nu cere parola la fiecare click
if "autentificat" not in st.session_state:
    st.session_state["autentificat"] = False
