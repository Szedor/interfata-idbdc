import streamlit as st
import psycopg2

# 1. DESIGN IDBDC
st.set_page_config(page_title="IDBDC Consola", layout="centered")

# --- DATE CONEXIUNE ---
# Aici pui codul lung copiat manual între ghilimele
DB_URI = "ostgresql://neondb_owner:npg_oRwnHk82CFUj@ep-silent-hill-ag8n1884-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

if "autentificat" not in st.session_state:
    st.session_state["autentificat"] = False

# BARIERA 1: ACCES GENERAL
if not st.session_state["autentificat"]:
    st.title("🛡️ Acces IDBDC")
    parola_gen = st.text_input("Cheie Acces Sistem:", type="password")
    if st.button("AUTENTIFICARE"):
        if parola_gen == "EverDream2SZ":
            st.session_state["autentificat"] = True
            st.rerun()
# BARIERA 2: TEST CONEXIUNE
else:
    st.title("🔑 Validare Server Nou")
    if st.button("TESTEAZĂ CONEXIUNEA"):
        try:
            conn = psycopg2.connect(DB_URI)
            st.balloons()
            st.success("✅ VICTORIE! Serverul Neon este conectat!")
            conn.close()
        except Exception as e:
            st.error(f"Eroare: {e}")
