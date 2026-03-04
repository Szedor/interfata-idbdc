# calea3_brainstorming.py
import re
import streamlit as st
import pandas as pd
from supabase import create_client, Client

from grant_navigator.engine import (
    internal_analytics,
    external_radar,
    strategy_recommendations,
    document_generator,
)

APP_TITLE = "Grant Navigator – IDBDC"
UPT_EMAIL_REGEX = re.compile(r"^[a-z]+(?:\.[a-z]+)+@upt\.ro$", re.IGNORECASE)


def _style():
    st.markdown(
        """
        <style>
          .stApp { background: #0b2a52; }
          div.block-container {
            background: rgba(255,255,255,0.97);
            border-radius: 18px;
            padding: 1.2rem 1.2rem 1.0rem 1.2rem;
            margin-top: 1.0rem;
            margin-bottom: 1.2rem;
            max-width: 1550px;
          }
          header, footer, #MainMenu { visibility: hidden; height: 0px; }
          [data-testid="stToolbar"] { display: none !important; }
          .gn-header {
            background: linear-gradient(90deg, #0b2a52, #134a8a);
            color: #fff;
            border-radius: 16px;
            padding: 16px 18px;
            margin-bottom: 14px;
          }
          .gn-title { font-size: 1.65rem; font-weight: 900; margin: 0; }
          .gn-sub { margin: 6px 0 0 0; opacity: 0.92; font-weight: 600; }
          .gn-welcome {
            background: rgba(19,74,138,0.10);
            border: 1px solid rgba(19,74,138,0.20);
            border-radius: 14px;
            padding: 12px 14px;
            margin: 10px 0 16px 0;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _get_supabase() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        st.error("Config lipsă: setează SUPABASE_URL și SUPABASE_KEY în Streamlit Cloud → Settings → Secrets.")
        st.stop()
    return create_client(url, key)


def _lookup_user(supabase: Client, email: str) -> dict | None:
    # caută în det_resurse_umane.email
    try:
        res = (
            supabase.table("det_resurse_umane")
            .select("nume_prenume,email")
            .eq("email", email.strip())
            .limit(1)
            .execute()
        )
        if res.data and isinstance(res.data, list) and len(res.data) > 0:
            return res.data[0]
        return None
    except Exception:
        return None


def _gate_email(supabase: Client):
    if "gn_authed" not in st.session_state:
        st.session_state.gn_authed = False
    if "gn_user_email" not in st.session_state:
        st.session_state.gn_user_email = None
    if "gn_user_name" not in st.session_state:
        st.session_state.gn_user_name = None

    if st.session_state.gn_authed:
        return

    st.markdown(
        f"""
        <div class="gn-header">
          <div class="gn-title">🧭 {APP_TITLE}</div>
          <div class="gn-sub">Acces pe baza emailului instituțional (UPT) + validare în resurse umane</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1.2, 1.6, 1.2])
    with c2:
        st.subheader("🔐 Autentificare")
        email = st.text_input("Email instituțional (prenume.nume@upt.ro)", placeholder="prenume.nume@upt.ro")

        if st.button("Continuă"):
            e = (email or "").strip().lower()
            if not e:
                st.error("Introdu un email.")
                st.stop()

            if not UPT_EMAIL_REGEX.match(e):
                st.error("Format invalid. Exemplu valid: prenume.nume@upt.ro")
                st.stop()

            user = _lookup_user(supabase, e)
            if not user:
                st.error("Emailul nu există în det_resurse_umane.email. Acces refuzat.")
                st.stop()

            st.session_state.gn_authed = True
            st.session_state.gn_user_email = e
            st.session_state.gn_user_name = (user.get("nume_prenume") or "").strip() or e
            st.rerun()

    st.stop()


def run():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    _style()

    supabase = _get_supabase()

    # Gate email (înlocuiește parola hardcodata din versiunea precedentă)
    _gate_email(supabase)

    # Header principal
    st.markdown(
        f"""
        <div class="gn-header">
          <div class="gn-title">🧭 {APP_TITLE}</div>
          <div class="gn-sub">Instrument practic pentru operatorii IDBDC: analiză internă + radar finanțări + recomandări + documente</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="gn-welcome">
          <b>Bine ai venit, {st.session_state.gn_user_name}.</b><br/>
          <span style="opacity:0.85;">Autentificat ca: {st.session_state.gn_user_email}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Navigare pe 4 direcții
    tabs = st.tabs([
        "1) Analiză internă IDBDC",
        "2) Radar finanțări (Open Sources)",
        "3) Recomandări strategice",
        "4) Generare documente",
    ])

    with tabs[0]:
        internal_analytics.render(supabase)

    with tabs[1]:
        external_radar.render()

    with tabs[2]:
        strategy_recommendations.render(supabase)

    with tabs[3]:
        document_generator.render(supabase)


if __name__ == "__main__":
    run()
