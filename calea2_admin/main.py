# =========================================================
# IDBDC/calea2_admin/main.py
# VERSIUNE: 1.2 - Adăugat toggle Dark/Light mode
# DATA: 2026.06.09
# =========================================================

import streamlit as st
from core.db   import get_supabase
from core.auth import check_gate_password, identify_operator
from calea2_admin.motor import porneste_motorul

TITLE_LINE_1 = "🛠️ Administrare baze de date"
TITLE_LINE_2 = "Departamentul Cercetare Dezvoltare Inovare"


def _get_theme_c2():
    return st.session_state.get("dark_mode_c2", True)


def _apply_style():
    dark = _get_theme_c2()

    if dark:
        bg             = "#003366"
        sidebar_bg     = "#0b2a52"
        text_color     = "#ffffff"
        title_color    = "#ffffff"
        input_bg       = "#ffffff"
        btn_bg         = "rgba(255,255,255,0.96)"
        btn_color      = "#0b1f3a"
        btn_hover_bg   = "white"
        btn_hover_color= "#003366"
        border_color   = "rgba(255,255,255,0.20)"
    else:
        bg             = "#F8FBFF"
        sidebar_bg     = "#0b2a52"   # sidebar rămâne întunecat în ambele moduri
        text_color     = "#0b2a52"
        title_color    = "#0b2a52"
        input_bg       = "#ffffff"
        btn_bg         = "rgba(11,42,82,0.10)"
        btn_color      = "#0b1f3a"
        btn_hover_bg   = "#0b2a52"
        btn_hover_color= "#ffffff"
        border_color   = "rgba(11,42,82,0.20)"

    st.markdown(
        f"""
        <style>
            .stApp {{ background-color: {bg} !important; }}
            [data-testid="stSidebar"] {{
                background-color: {sidebar_bg} !important;
                border-right: 2px solid rgba(255,255,255,0.20);
                display: block !important; visibility: visible !important;
                min-width: 320px !important; max-width: 320px !important; width: 320px !important;
            }}
            [data-testid="stSidebar"] > div:first-child {{
                min-width: 320px !important; max-width: 320px !important; width: 320px !important;
            }}
            .stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp p,.stApp label,.stApp .stMarkdown {{
                color: {text_color} !important;
            }}
            [data-testid="stSidebar"] p,[data-testid="stSidebar"] label,
            [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 {{
                color: #ffffff !important;
            }}
            input {{ color: #000000 !important; background-color: {input_bg} !important; }}
            div.stButton > button {{
                border: 1px solid {"white" if dark else "rgba(11,42,82,0.35)"} !important;
                color: {btn_color} !important; -webkit-text-fill-color: {btn_color} !important;
                background-color: {btn_bg} !important;
                opacity: 1 !important; width: 100%;
                font-size: 14px !important; font-weight: bold !important; height: 42px !important;
            }}
            div.stButton > button:hover {{
                background-color: {btn_hover_bg} !important;
                color: {btn_hover_color} !important;
                -webkit-text-fill-color: {btn_hover_color} !important;
            }}
            [data-testid="stToolbar"]    {{ visibility: hidden !important; height: 0px !important; }}
            [data-testid="stHeader"]     {{ background-color: transparent !important; }}
            [data-testid="stDecoration"] {{ visibility: hidden !important; height: 0px !important; }}
            #MainMenu {{ visibility: hidden !important; }}
            .admin-header {{ text-align: center; margin-bottom: 20px; }}
            .admin-title-1 {{ font-size:2.0rem; font-weight:900; color:{title_color}; margin:0; }}
            .admin-title-2 {{ font-size:1.7rem; font-weight:800; color:{title_color}; margin:4px 0 0 0; opacity:0.95; }}
            hr {{ border-color: {border_color} !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_toggle():
    dark = _get_theme_c2()
    label = "☀️ Light mode" if dark else "🌙 Dark mode"
    _, col_btn = st.columns([7, 1])
    with col_btn:
        if st.button(label, key="toggle_theme_c2"):
            st.session_state.dark_mode_c2 = not dark
            st.rerun()


def run():
    st.set_page_config(page_title="IDBDC – Administrare", layout="wide", initial_sidebar_state="expanded")

    if "dark_mode_c2" not in st.session_state:
        st.session_state.dark_mode_c2 = True

    supabase = get_supabase()
    _apply_style()

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

    _render_toggle()

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
