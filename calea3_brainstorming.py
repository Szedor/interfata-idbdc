import streamlit as st
import re
from supabase import create_client, Client

from grant_navigator.engine import internal_analytics
from grant_navigator.engine import external_radar
from grant_navigator.engine import strategy_recommendations
from grant_navigator.engine import document_generator


TITLE_LINE_1 = "Oportunitati si Analiza Cercetare"
TITLE_LINE_2 = "Departamentul Cercetare Dezvoltare Inovare"

ACADEMIC_BLUE = "#0b2a52"
UPT_EMAIL_REGEX = re.compile(r"^[a-z]+(?:\.[a-z]+)+@upt\.ro$", re.IGNORECASE)


def hide_streamlit_chrome():
    st.markdown(
        """
        <style>
          header { visibility: hidden; height: 0px; }
          #MainMenu { visibility: hidden; }
          footer { visibility: hidden; height: 0px; }
          [data-testid="stToolbar"] { display: none !important; }
          [data-testid="stDecoration"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_style_gate():
    st.markdown(
        f"""
        <style>
          .stApp {{
            background: {ACADEMIC_BLUE};
          }}

          div.block-container {{
            padding-top: 4.0rem;
            padding-bottom: 2.0rem;
            max-width: 1550px;
          }}

          .gate-box {{
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.25);
            border-radius: 18px;
            padding: 26px 22px 18px 22px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.28);
          }}

          .gate-title {{
            text-align: center;
            font-size: 1.45rem;
            font-weight: 900;
            color: #ffffff;
            margin: 0 0 0.35rem 0;
          }}

          .gate-subtitle {{
            text-align: center;
            color: rgba(255,255,255,0.92);
            font-size: 1.02rem;
            font-weight: 600;
            margin: 0 0 1.1rem 0;
          }}

          .stTextInput label {{
            color: #ffffff !important;
            font-weight: 800 !important;
          }}

          .stTextInput input {{
            background: rgba(255,255,255,0.96) !important;
            color: #0b1f3a !important;
            border-radius: 12px !important;
          }}

          .stButton > button {{
            width: 100%;
            border-radius: 12px;
            font-weight: 900;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_style_app():
    st.markdown(
        f"""
        <style>
          .stApp {{
            background: {ACADEMIC_BLUE};
          }}

          /* Card alb central (ca in Calea 1) */
          div.block-container {{
            background: rgba(255,255,255,0.97);
            border-radius: 18px;
            padding: 1.2rem 1.2rem 1.0rem 1.2rem;
            margin-top: 1.0rem;
            margin-bottom: 1.2rem;
            max-width: 1550px;
          }}

          .idbdc-header {{
            text-align: center;
            margin-top: 0.2rem;
            margin-bottom: 0.9rem;
          }}

          .idbdc-title-1 {{
            font-size: 2.05rem;
            font-weight: 900;
            line-height: 1.15;
            color: #0b1f3a;
            margin: 0;
          }}

          .idbdc-title-2 {{
            font-size: 1.78rem;
            font-weight: 800;
            line-height: 1.2;
            color: #0b1f3a;
            margin: 0.35rem 0 0 0;
            opacity: 0.95;
          }}

          /* Welcome box (30% + centru) */
          .welcome-wrap {{
            width: 30%;
            min-width: 320px;
            margin: 0.35rem auto 0.85rem auto;
          }}
          .welcome-box {{
            background: rgba(34, 139, 34, 0.12);
            border: 1px solid rgba(34, 139, 34, 0.25);
            border-radius: 14px;
            padding: 10px 12px;
            text-align: center;
            font-weight: 800;
            color: #0b1f3a;
          }}

          /* Butoane 4 sectiuni */
          .nav-row {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 0.4rem 0 0.8rem 0;
            flex-wrap: wrap;
          }}

          /* In Streamlit, stilizam butoanele standard */
          div.stButton > button {{
            border-radius: 12px;
            font-weight: 900;
            padding: 0.55rem 0.8rem;
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


def get_supabase() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        st.error("Config lipsă: setează SUPABASE_URL și SUPABASE_KEY în Streamlit Cloud → Settings → Secrets.")
        st.stop()
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


def email_gate(supabase: Client):
    if "auth_ai" not in st.session_state:
        st.session_state.auth_ai = False
    if "user_name" not in st.session_state:
        st.session_state.user_name = None

    if st.session_state.auth_ai:
        return

    hide_streamlit_chrome()
    apply_style_gate()

    left, mid, right = st.columns([1.8, 1.0, 1.8])
    with mid:
        st.markdown('<div class="gate-box">', unsafe_allow_html=True)
        st.markdown('<div class="gate-title">🛡️ Acces securizat</div>', unsafe_allow_html=True)
        st.markdown('<div class="gate-subtitle">Oportunitati si Analiza Cercetare – DCDI</div>', unsafe_allow_html=True)

        email = st.text_input("Email instituțional (prenume.nume@upt.ro)", value="")

        if st.button("Autentificare"):
            e = (email or "").strip().lower()
            if not UPT_EMAIL_REGEX.match(e):
                st.error("Email invalid. Exemplu: prenume.nume@upt.ro")
                st.stop()

            user = lookup_user(supabase, e)
            if not user:
                st.error("Emailul nu există în baza det_resurse_umane.")
                st.stop()

            st.session_state.auth_ai = True
            st.session_state.user_name = (user.get("nume_prenume") or "").strip() or e
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


def render_nav_buttons():
    if "ai_section" not in st.session_state:
        st.session_state.ai_section = "internal"

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

    supabase = get_supabase()

    # Poarta email
    email_gate(supabase)

    # Stil aplicatie
    hide_streamlit_chrome()
    apply_style_app()

    # Header
    render_header()

    # Welcome (30% + centru)
    st.markdown(
        f"""
        <div class="welcome-wrap">
          <div class="welcome-box">Bine ai venit, {st.session_state.user_name}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Navigare prin 4 butoane
    render_nav_buttons()

    st.divider()

    # Randare sectiune activa
    sec = st.session_state.get("ai_section", "internal")

    if sec == "internal":
        internal_analytics.render(supabase)

    elif sec == "radar":
        external_radar.render()

    elif sec == "strategy":
        strategy_recommendations.render(supabase)

    elif sec == "docs":
        document_generator.render(supabase)

    else:
        st.info("Selecteaza o sectiune.")


if __name__ == "__main__":
    run()
