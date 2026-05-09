# =========================================================
# IDBDC/calea2_admin/main.py
# VERSIUNE: 1.0
# STATUS: NOU - intrare Calea2 pentru noua structură modulară
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Punct de intrare al Căii2 (Administrare).
#   Autentificare în două etape prin core/auth.py.
#   Conexiune Supabase prin core/db.py.
#   Lansează calea2_admin/motor.py după autentificare.
# =========================================================

import streamlit as st
from core.db   import get_supabase
from core.auth import check_gate_password, identify_operator
from calea2_admin.motor import porneste_motorul
from _maintenance_msg import maintenance_gate as _maintenance_gate_fn

TITLE_LINE_1 = "🛠️ Administrare baze de date"
TITLE_LINE_2 = "Departamentul Cercetare Dezvoltare Inovare"

_CSS = """
<style>
    .stApp { background-color: #003366 !important; }
    [data-testid="stSidebar"] {
        background-color: #0b2a52 !important;
        border-right: 2px solid rgba(255,255,255,0.20);
        display: block !important; visibility: visible !important;
        min-width: 320px !important; max-width: 320px !important; width: 320px !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        min-width: 320px !important; max-width: 320px !important; width: 320px !important;
    }
    .stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp p,.stApp label,.stApp .stMarkdown,
    [data-testid="stSidebar"] p,[data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 {
        color: white !important;
    }
    input { color: #000000 !important; background-color: #ffffff !important; }
    div.stButton > button {
        border: 1px solid white !important;
        color: #0b1f3a !important; -webkit-text-fill-color: #0b1f3a !important;
        background-color: rgba(255,255,255,0.96) !important;
        opacity: 1 !important; width: 100%;
        font-size: 14px !important; font-weight: bold !important; height: 42px !important;
    }
    div.stButton > button:hover { background-color: white !important; color: #003366 !important; }
    [data-testid="stToolbar"]    { visibility: hidden !important; height: 0px !important; }
    [data-testid="stHeader"]     { background-color: transparent !important; }
    [data-testid="stDecoration"] { visibility: hidden !important; height: 0px !important; }
    #MainMenu { visibility: hidden !important; }
    .admin-header { text-align: center; margin-bottom: 20px; }
    .admin-title-1 { font-size:2.0rem; font-weight:900; color:#ffffff; margin:0; }
    .admin-title-2 { font-size:1.7rem; font-weight:800; color:#ffffff; margin:4px 0 0 0; opacity:0.95; }
</style>
"""


def run():
    st.set_page_config(page_title="IDBDC – Administrare", layout="wide", initial_sidebar_state="expanded")
    _maintenance_gate_fn(st, pwd_key="_mw_pwd_c2", btn_key="_mw_btn_c2")

    supabase = get_supabase()
    st.markdown(_CSS, unsafe_allow_html=True)

    for key, val in [
        ("autorizat_p1", False),
        ("operator_identificat", None),
        ("operator_rol", None),
        ("operator_username", None),
        ("operator_filtru_categorie", []),
        ("operator_filtru_tipuri", []),
    ]:
        if key not in st.session_state:
            st.session_state[key] = val

    st.markdown(
        f'<div class="admin-header">'
        f'<div class="admin-title-1">{TITLE_LINE_1}</div>'
        f'<div class="admin-title-2">{TITLE_LINE_2}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("## 🔐 Autentificare")

    if not st.session_state.autorizat_p1:
        st.sidebar.markdown("### Pas 1 — Parolă acces modul")
        parola = st.sidebar.text_input("Parola:", type="password", key="p1_pass")
        if st.sidebar.button("Autorizare acces", use_container_width=True):
            if check_gate_password(supabase, "admin", parola):
                st.session_state.autorizat_p1 = True
                st.rerun()
            else:
                st.sidebar.error("Parolă greșită sau poarta este dezactivată.")
        st.info("Introduceți parola în bara din stânga pentru a continua.")
        st.stop()

    if not st.session_state.operator_identificat:
        st.sidebar.markdown("### Pas 2 — Cod operator")
        cod = st.sidebar.text_input("Cod Identificare:", type="password", key="p2_cod_input")
        if cod:
            if identify_operator(supabase, cod):
                st.rerun()
            else:
                st.sidebar.error("Cod operator invalid.")
        st.info("Introduceți codul de operator în bara din stânga.")
        st.stop()

    st.sidebar.success(f"Operator: {st.session_state.operator_identificat}")
    if st.sidebar.button("Ieșire / Resetare", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    porneste_motorul(supabase)


if __name__ == "__main__":
    run()
