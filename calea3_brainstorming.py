import streamlit as st
import re
from supabase import create_client, Client

from grant_navigator.engine import internal_analytics
from grant_navigator.engine import external_radar
from grant_navigator.engine import strategy_recommendations
from grant_navigator.engine import document_generator


APP_TITLE = "Grant Navigator – IDBDC"

UPT_EMAIL_REGEX = re.compile(r"^[a-z]+(?:\.[a-z]+)+@upt\.ro$", re.IGNORECASE)


def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def lookup_user(supabase: Client, email: str):

    try:
        res = (
            supabase
            .table("det_resurse_umane")
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

    if "gn_authed" not in st.session_state:
        st.session_state.gn_authed = False

    if "gn_user_name" not in st.session_state:
        st.session_state.gn_user_name = None

    if st.session_state.gn_authed:
        return

    st.title("🔐 Acces Grant Navigator")

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

        st.session_state.gn_authed = True
        st.session_state.gn_user_name = user.get("nume_prenume")

        st.rerun()

    st.stop()


def run():

    st.set_page_config(page_title=APP_TITLE, layout="wide")

    supabase = get_supabase()

    email_gate(supabase)

    st.title(APP_TITLE)

    st.success(f"Bine ai venit, {st.session_state.gn_user_name}")

    tabs = st.tabs([
        "Analiză internă IDBDC",
        "Radar finanțări",
        "Recomandări strategice",
        "Generare documente"
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
