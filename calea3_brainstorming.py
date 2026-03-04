import streamlit as st
import re
from supabase import create_client, Client

from grant_navigator.engine import internal_analytics
from grant_navigator.engine import external_radar
from grant_navigator.engine import strategy_recommendations
from grant_navigator.engine import document_generator


TITLE_LINE_1 = "Oportunitati si Analiza Cercetare"
TITLE_LINE_2 = "Departamentul Cercetare Dezvoltare Inovare"

APP_BLUE = "#003366"      # identic cu calea2_admin
SIDEBAR_BLUE = "#0b2a52"  # identic cu calea2_admin

UPT_EMAIL_REGEX = re.compile(r"^[a-z]+(?:\.[a-z]+)+@upt\.ro$", re.IGNORECASE)


def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def lookup_user(supabase: Client, email: str):
    try:
        res = (
            supabase.table("det_resurse_umane")
            .select("nume_prenume,email")
            .eq("email", email)
            .limit(1)
            .execute()
        )
        if res.data and len(res.data) > 0:
            return res.data[0]
    except Exception:
        pass
    return None


def apply_style():
    st.markdown(
        f"""
        <style>
            /* Fundal aplicație (identic calea 1/2) */
            .stApp {{ background-color: {APP_BLUE} !important; }}

            /* Sidebar */
            [data-testid="stSidebar"] {{
                background-color: {SIDEBAR_BLUE} !important;
                border-right: 2px solid rgba(255,255,255,0.20);
            }}

            /* Text alb */
            .stApp h1, .stApp h2, .stApp h3, .stApp h4,
            .stApp p, .stApp label, .stApp .stMarkdown,
            [data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
                color: white !important;
            }}

            /* Input-uri */
            input {{
                color: #000000 !important;
                background-color: #ffffff !important;
            }}

            /* Butoane */
            div.stButton > button {{
                border: 1px solid white !important;
                color: white !important;
                background-color: rgba(255,255,255,0.10) !important;
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

            /* Ascunde bara Streamlit */
            [data-testid="stToolbar"] {{ visibility: hidden !important; height: 0px !important; }}
            [data-testid="stHeader"]  {{ visibility: hidden !important; height: 0px !important; }}
            [data-testid="stDecoration"] {{ visibility: hidden !important; height: 0px !important; }}
            #MainMenu {{ visibility: hidden !important; }}

            /* Titlu 2 randuri */
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

            /* Welcome: 30% si centrat */
            .welcome-wrap {{
                width: 30%;
                min-width: 320px;
                margin: 0.6rem auto 0.8rem auto;
                text-align: center;
            }}
            .welcome-box {{
                display: inline-block;
                padding: 10px 14px;
                border-radius: 14px;
                background: rgba(255,255,255,0.12);
                border: 1px solid rgba(255,255,255,0.25);
                color: #ffffff;
                font-weight: 900;
            }}

            /* Butoane sectiuni: mai compacte */
            .nav-note {{
                text-align:center;
                opacity:0.92;
                margin-bottom: 0.4rem;
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
        email = st.text_input("Email instituțional (prenume.nume@upt.ro)", value="")

        if st.button("Autentificare"):
            e = (email or "").strip().lower()

            if not UPT_EMAIL_REGEX.match(e):
                st.error("Email invalid. Exemplu: prenume.nume@upt.ro")
                st.stop()

            user = lookup_user(supabase, e)
            if not user:
                st.error("Emailul nu există în det_resurse_umane.email")
                st.stop()

            st.session_state.auth_ai = True
            st.session_state.user_name = (user.get("nume_prenume") or "").strip() or e

            # foarte important: la intrare, nu afisam automat nicio sectiune
            st.session_state.ai_section = None

            st.rerun()

    st.stop()


def render_nav_buttons():
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])

    with c1:
        if st.button("📊 Analiza interna IDBDC", use_container_width=True):
            st.session_state.ai_section = "internal"
            st.rerun()

    with c2:
        if st.button("🛰️ Radar finantari", use_container_width=True):
            st.session_state.ai_section = "radar"
            st.rerun()

    with c3:
        if st.button("🎯 Recomandari strategice", use_container_width=True):
            st.session_state.ai_section = "strategy"
            st.rerun()

    with c4:
        if st.button("📝 Generare documente", use_container_width=True):
            st.session_state.ai_section = "docs"
            st.rerun()


def run():
    st.set_page_config(page_title="IDBDC – AI", layout="wide")

    apply_style()
    supabase = get_supabase()

    # Gate email
    email_gate(supabase)

    # Header + welcome
    render_header()

    st.markdown(
        f"""
        <div class="welcome-wrap">
            <div class="welcome-box">Bine ai venit, {st.session_state.user_name}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="nav-note">Alege una dintre cele 4 sectiuni:</div>', unsafe_allow_html=True)

    render_nav_buttons()

    st.divider()

    sec = st.session_state.get("ai_section", None)

    if sec is None:
        st.info("Selecteaza o sectiune de mai sus.")
        return

    if sec == "internal":
        internal_analytics.render(supabase)
        return

    if sec == "radar":
        external_radar.render()
        return

    if sec == "strategy":
        strategy_recommendations.render(supabase)
        return

    if sec == "docs":
        document_generator.render(supabase)
        return

    st.info("Selecteaza o sectiune.")


if __name__ == "__main__":
    run()
