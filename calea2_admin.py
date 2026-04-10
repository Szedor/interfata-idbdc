# =========================================================
# IDBDC - CALEA 2 - ADMIN (calea2_admin.py)
# Versiune: 2.1 (Corectată integral conform Protocolului)
# =========================================================

import streamlit as st
from supabase import Client, create_client
from config import Config
from motor_admin import porneste_motorul

# ── MAINTENANCE LOCK ──
from _maintenance_msg import maintenance_gate as _maintenance_gate_fn

TITLE_LINE_1 = "🛠️ Administrare baze de date"
TITLE_LINE_2 = "Departamentul Cercetare Dezvoltare Inovare"

@st.cache_resource
def get_supabase():
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def run():
    # ── MAINTENANCE LOCK ──
    st.set_page_config(page_title="IDBDC – Administrare", layout="wide")
    _maintenance_gate_fn(st, pwd_key="_mw_pwd_c2", btn_key="_mw_btn_c2")

    supabase: Client = get_supabase()

    # Stil vizual neschimbat
    st.markdown(
        """
        <style>
            .stApp { background-color: #0b2a52 !important; }
            [data-testid="stSidebar"] { background-color: #0b2a52 !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.get("operator_identificat"):
        st.sidebar.title("Autentificare")
        cod_in = st.sidebar.text_input("Cod Operator", type="password")
        
        if st.sidebar.button("Intră în sistem"):
            try:
                # CORECȚIE CRITICĂ: table() înainte de select() și eq()
                res_op = (
                    supabase
                    .table("com_operatori")
                    .select("nume_prenume, rol, filtru_categorie, filtru_proiect")
                    .eq("cod_operatori", cod_in)
                    .execute()
                )

                if res_op.data:
                    op_data = res_op.data[0]
                    st.session_state.operator_identificat = op_data.get("nume_prenume")
                    st.session_state.operator_rol = (op_data.get("rol") or "OPERATOR").strip()

                    raw_cat = op_data.get("filtru_categorie") or ""
                    raw_tip = op_data.get("filtru_proiect") or ""
                    st.session_state.operator_filtru_categorie = [x.strip() for x in raw_cat.split(",") if x.strip()]
                    st.session_state.operator_filtru_tipuri = [x.strip() for x in raw_tip.split(",") if x.strip()]
                    st.rerun()
                else:
                    st.sidebar.error("Cod operator invalid.")
            except Exception as e:
                st.sidebar.error(f"Eroare tehnică: {e}")

        st.info("Vă rugăm să introduceți codul de operator pentru a accesa baza de date.")
        st.stop()

    # Dacă operatorul este identificat, pornește motorul modular
    porneste_motorul(supabase)
