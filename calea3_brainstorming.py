import streamlit as st
import re
from supabase import create_client, Client

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
            padding-top: 4rem;
            padding-bottom: 2rem;
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
            margin-bottom: 10px;
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

          div.block-container {{
            background: rgba(255,255,255,0.97);
            border-radius: 18px;
            padding: 1.2rem;
            margin-top: 1rem;
            margin-bottom: 1.2rem;
            max-width: 1550px;
          }}

          .idbdc-header {{
            text-align: center;
            margin-bottom: 1rem;
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


def email_gate(supabase: Client):

    if "auth_brainstorm" not in st.session_state:
        st.session_state.auth_brainstorm = False

    if "user_name" not in st.session_state:
        st.session_state.user_name = None

    if st.session_state.auth_brainstorm:
        return

    hide_streamlit_chrome()
    apply_style_gate()

    _, col_ce, _ = st.columns([1,1,1])

    with col_ce:

        st.markdown('<div class="gate-box">', unsafe_allow_html=True)

        st.markdown('<div class="gate-title">Acces securizat</div>', unsafe_allow_html=True)

        email = st.text_input("Email instituțional (prenume.nume@upt.ro)")

        if st.button("Autentificare"):

            e = (email or "").strip().lower()

            if not UPT_EMAIL_REGEX.match(e):
                st.error("Email invalid.")
                st.stop()

            user = lookup_user(supabase, e)

            if not user:
                st.error("Emailul nu există în baza det_resurse_umane.")
                st.stop()

            st.session_state.auth_brainstorm = True
            st.session_state.user_name = user.get("nume_prenume")

            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


def run():

    st.set_page_config(page_title="IDBDC – Oportunitati", layout="wide")

    supabase = get_supabase()

    email_gate(supabase)

    hide_streamlit_chrome()
    apply_style_app()

    render_header()

    st.success(f"Bine ai venit, {st.session_state.user_name}")

    st.divider()

    tabs = st.tabs([
        "Analiza interna IDBDC",
        "Radar finantari",
        "Recomandari strategice",
        "Generare documente"
    ])

    with tabs[0]:
        st.info("Zona de analiza interna IDBDC (in dezvoltare).")

    with tabs[1]:
        st.info("Radar finantari nationale si internationale (in dezvoltare).")

    with tabs[2]:
        st.info("Recomandari strategice pentru proiecte (in dezvoltare).")

    with tabs[3]:
        st.info("Generator documente si idei de proiect (in dezvoltare).")


if __name__ == "__main__":
    run()
