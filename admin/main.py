# =========================================================
# admin/main.py
# v.modul.2.2 - Corectii: fundal alb pentru inputuri, text negru in dropdown-uri
# =========================================================

import streamlit as st
from supabase import Client, create_client

from config import Config
from admin.motor import porneste_motorul
from _maintenance_msg import maintenance_gate as _maintenance_gate_fn
from utils.styling import apply_global_styles, hide_streamlit_chrome, apply_admin_styles

TITLE_LINE_1 = "🛠️ Administrare baze de date"
TITLE_LINE_2 = "Departamentul Cercetare Dezvoltare Inovare"


@st.cache_resource
def get_supabase():
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)


def _check_gate_password(supabase: Client, gate: str, password: str) -> bool:
    try:
        res = supabase.rpc(
            "idbdc_check_gate_password",
            {"p_gate": gate, "p_password": password},
        ).execute()
        return bool(res.data)
    except Exception:
        return False


def render_header():
    st.markdown(
        f"""
        <div class="admin-header" style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 2.0rem; font-weight: 900; color: #ffffff; margin: 0;">{TITLE_LINE_1}</div>
            <div style="font-size: 1.7rem; font-weight: 800; color: #ffffff; margin: 4px 0 0 0; opacity: 0.95;">{TITLE_LINE_2}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def run():
    st.set_page_config(page_title="IDBDC – Administrare", layout="wide")

    _maintenance_gate_fn(st, pwd_key="_mw_pwd_c2", btn_key="_mw_btn_c2")

    hide_streamlit_chrome()
    apply_global_styles()
    apply_admin_styles()  # Stiluri specifice pentru admin

    supabase: Client = get_supabase()

    if "autorizat_p1" not in st.session_state:
        st.session_state.autorizat_p1 = False

    if "operator_identificat" not in st.session_state:
        st.session_state.operator_identificat = None

    if "operator_rol" not in st.session_state:
        st.session_state.operator_rol = None

    if "operator_filtru_categorie" not in st.session_state:
        st.session_state.operator_filtru_categorie = []

    if "operator_filtru_tipuri" not in st.session_state:
        st.session_state.operator_filtru_tipuri = []

    render_header()

    st.sidebar.markdown("## 🔐 Autentificare")

    if not st.session_state.autorizat_p1:

        st.sidebar.markdown("### Pas 1 — Parolă acces modul")

        parola_m = st.sidebar.text_input("Parola:", type="password", key="p1_pass")

        if st.sidebar.button("Autorizare acces", use_container_width=True):

            if _check_gate_password(supabase, "admin", parola_m):
                st.session_state.autorizat_p1 = True
                st.rerun()

            else:
                st.sidebar.error("Parolă greșită sau poarta este dezactivată.")

        st.info("Introduceți parola în bara din stânga pentru a continua.")
        st.stop()

    if not st.session_state.operator_identificat:

        st.sidebar.markdown("### Pas 2 — Cod operator")

        cod_in = st.sidebar.text_input(
            "Cod Identificare:", 
            type="password", 
            key="p2_cod_input",
            placeholder="Introduceți codul..."
        )

        if cod_in:

            try:
                res_op = (
                    supabase
                    .table("com_operatori")
                    .select("nume_prenume, rol, filtru_categorie, filtru_proiect")
                    .eq("cod_operatori", cod_in)
                    .execute()
                )

                if res_op.data:

                    st.session_state.operator_identificat = res_op.data[0].get("nume_prenume")
                    st.session_state.operator_rol = (res_op.data[0].get("rol") or "OPERATOR").strip()

                    raw_cat = res_op.data[0].get("filtru_categorie") or ""
                    raw_tip = res_op.data[0].get("filtru_proiect") or ""
                    st.session_state.operator_filtru_categorie = [x.strip() for x in raw_cat.split(",") if x.strip()]
                    st.session_state.operator_filtru_tipuri = [x.strip() for x in raw_tip.split(",") if x.strip()]

                    st.rerun()

                else:
                    st.sidebar.error("Cod operator invalid.")

            except Exception as e:
                st.sidebar.error(f"Eroare la verificarea operatorului: {e}")

        st.info("Introduceți codul de operator în bara din stânga pentru a intra în modul.")
        st.stop()

    # Afișare operator
    st.sidebar.markdown(
        f"""
        <div style="background-color: rgba(255,255,255,0.15); border-radius: 10px; padding: 10px; margin-bottom: 15px; text-align: center;">
            <span style="color: white; font-weight: bold;">👤 Operator: {st.session_state.operator_identificat}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Ieșire / Resetare", use_container_width=True, key="btn_iesire"):
        st.session_state.clear()
        st.rerun()

    porneste_motorul(supabase)


if __name__ == "__main__":
    run()
