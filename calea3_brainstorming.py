# =========================================================
# calea3_brainstorming.py
# v.modul.2.0 - Folosește stiluri centralizate din utils.styling
# =========================================================

import re

import streamlit as st
from supabase import Client, create_client

from config import Config
from grant_navigator.engine import ai_analytics
from grant_navigator.engine import ai_documents
from grant_navigator.engine import ai_radar
from grant_navigator.engine import ai_recommendations

from _maintenance_msg import maintenance_gate as _maintenance_gate_fn
from utils.styling import apply_global_styles, hide_streamlit_chrome

TITLE_LINE_1 = "🤖 Oportunități și Analiză Cercetare — AI"
TITLE_LINE_2 = "Departamentul Cercetare Dezvoltare Inovare"

APP_BLUE = "#003366"
SIDEBAR_BLUE = "#0b2a52"

UPT_EMAIL_REGEX = re.compile(r"^[a-z]+(?:\.[a-z]+)+@upt\.ro$", re.IGNORECASE)


@st.cache_resource
def get_supabase() -> Client:
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)


# =========================================================
# LOOKUP USER
# =========================================================

def lookup_user(supabase: Client, email: str):
    try:
        res = (
            supabase.table("det_resurse_umane")
            .select("nume_prenume,email")
            .eq("email", email)
            .limit(1)
            .execute()
        )
        if res.data:
            return res.data[0]
    except Exception:
        pass
    return None


# =========================================================
# STYLE - folosește centralizat + ajustări specifice
# =========================================================

def apply_style_ai():
    """Stiluri specifice pentru modulul AI."""
    st.markdown(
        f"""
        <style>
            [data-testid="stSidebar"] {{
                background-color: {SIDEBAR_BLUE} !important;
                border-right: 2px solid rgba(255,255,255,0.20);
            }}
            .stApp h1, .stApp h2, .stApp h3, .stApp h4,
            .stApp p, .stApp label, .stApp .stMarkdown,
            [data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3 {{
                color: white !important;
            }}
            input {{
                color: #000000 !important;
                background-color: #ffffff !important;
            }}
            div.stButton > button {{
                border: 1px solid white !important;
                color: #0b1f3a !important;
                -webkit-text-fill-color: #0b1f3a !important;
                background-color: rgba(255,255,255,0.96) !important;
                opacity: 1 !important;
                width: 100%;
                font-size: 14px !important;
                font-weight: bold !important;
                height: 46px !important;
                border-radius: 12px !important;
            }}
            div.stButton > button:hover {{
                background-color: white !important;
                color: {APP_BLUE} !important;
            }}
            .idbdc-header {{
                text-align: center;
                margin-top: 0.25rem;
                margin-bottom: 0.6rem;
            }}
            .idbdc-title-1 {{
                font-size: 2.0rem;
                font-weight: 900;
                margin: 0;
                color: #ffffff;
            }}
            .idbdc-title-2 {{
                font-size: 1.7rem;
                font-weight: 800;
                margin: 4px 0 0 0;
                color: #ffffff;
                opacity: 0.95;
            }}
            .welcome-wrap {{
                width: 40%;
                min-width: 320px;
                margin: 0.6rem auto 0.8rem auto;
                text-align: center;
            }}
            .welcome-box {{
                display: inline-block;
                padding: 10px 20px;
                border-radius: 14px;
                background: rgba(255,255,255,0.12);
                border: 1px solid rgba(255,255,255,0.25);
                color: #ffffff;
                font-weight: 900;
                font-size: 1.05rem;
            }}
            .nav-note {{
                text-align: center;
                opacity: 0.92;
                margin-bottom: 0.4rem;
            }}
            .ai-badge {{
                display: inline-block;
                background: rgba(255,255,255,0.15);
                border: 1px solid rgba(255,255,255,0.30);
                border-radius: 8px;
                padding: 3px 10px;
                font-size: 0.78rem;
                font-weight: 700;
                color: #ffffff;
                margin-left: 8px;
                vertical-align: middle;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        f"""
        <div class="idbdc-header">
            <div class="idbdc-title-1">{TITLE_LINE_1}</div>
            <div class="idbdc-title-2">{TITLE_LINE_2}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# GATE EMAIL
# =========================================================

def email_gate(supabase: Client):
    if "auth_ai" not in st.session_state:
        st.session_state.auth_ai = False

    if "user_name" not in st.session_state:
        st.session_state.user_name = None

    if st.session_state.auth_ai:
        return

    render_header()

    _, mid, _ = st.columns([1.5, 1.0, 1.5])
    with mid:
        st.subheader("🔐 Acces securizat")
        st.markdown(
            "<div style='color:rgba(255,255,255,0.88);font-size:0.95rem;"
            "margin-bottom:0.6rem;'>Modulul AI este disponibil exclusiv "
            "cadrelor didactice și cercetătorilor UPT.</div>",
            unsafe_allow_html=True,
        )

        email = st.text_input(
            "Email instituțional (prenume.nume@upt.ro)",
            value="",
        )

        if st.button("Autentificare"):
            e = (email or "").strip().lower()

            if not UPT_EMAIL_REGEX.match(e):
                st.error("Email invalid. Exemplu: prenume.nume@upt.ro")
                st.stop()

            user = lookup_user(supabase, e)
            if not user:
                st.error("Emailul nu există în baza de date IDBDC.")
                st.stop()

            st.session_state.auth_ai = True
            st.session_state.user_name = (user.get("nume_prenume") or "").strip() or e
            st.session_state.user_email = e
            st.session_state.ai_section = None
            st.rerun()

    st.stop()


# =========================================================
# NAVIGARE
# =========================================================

def render_nav_buttons():
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button("🧠 Chat cu baza IDBDC", use_container_width=True):
            st.session_state.ai_section = "chat"
            st.rerun()

    with c2:
        if st.button("🛰️ Radar finanțări", use_container_width=True):
            st.session_state.ai_section = "radar"
            st.rerun()

    with c3:
        if st.button("🎯 Recomandări strategice", use_container_width=True):
            st.session_state.ai_section = "strategy"
            st.rerun()

    with c4:
        if st.button("📝 Generare documente", use_container_width=True):
            st.session_state.ai_section = "docs"
            st.rerun()


# =========================================================
# MAIN
# =========================================================

def run():
    st.set_page_config(page_title="IDBDC – Modul 3 AI", layout="wide")

    _maintenance_gate_fn(st, pwd_key="_mw_pwd_c3", btn_key="_mw_btn_c3")

    # Aplică stilurile centralizate
    hide_streamlit_chrome()
    apply_global_styles()
    apply_style_ai()

    supabase = get_supabase()

    email_gate(supabase)

    render_header()

    st.markdown(
        f"""
        <div class="welcome-wrap">
            <div class="welcome-box">
                👋 Bine ai venit, {st.session_state.user_name}
                <span class="ai-badge">AI ACTIV</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="nav-note">Alege una dintre cele 4 secțiuni:</div>',
        unsafe_allow_html=True,
    )

    render_nav_buttons()

    st.divider()

    sec = st.session_state.get("ai_section", None)

    if sec is None:
        st.info("Selectează o secțiune de mai sus pentru a începe.")
        return

    if sec == "chat":
        ai_analytics.render(supabase)
    elif sec == "radar":
        ai_radar.render(supabase)
    elif sec == "strategy":
        ai_recommendations.render(supabase)
    elif sec == "docs":
        ai_documents.render(supabase)
    else:
        st.info("Selectează o secțiune.")


if __name__ == "__main__":
    run()
