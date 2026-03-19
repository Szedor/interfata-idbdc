import streamlit as st
import re
from supabase import create_client, Client

from grant_navigator.engine import ai_analytics
from grant_navigator.engine import ai_radar
from grant_navigator.engine import ai_recommendations
from grant_navigator.engine import ai_documents

# ── MAINTENANCE LOCK ──────────────────────────────────────────────────────────
_MAINTENANCE_PASSWORD = "seLAN$EAZAin2026"

def _maintenance_gate():
    if st.session_state.get("_mw_cleared"):
        return
    st.markdown("""
        <style>
        .stApp { background: #0b2a52 !important; }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style='display:flex;justify-content:center;align-items:center;
                    min-height:80vh;'>
          <div style='background:rgba(255,255,255,0.07);border:2px solid rgba(255,255,255,0.25);
                      border-radius:20px;padding:40px 48px;max-width:680px;width:100%;
                      box-shadow:0 20px 60px rgba(0,0,0,0.40);text-align:center;'>

            <div style='font-size:2.8rem;margin-bottom:0.5rem;'>&#9888;&#65039;</div>

            <div style='color:#ffffff;font-size:1.55rem;font-weight:900;
                        letter-spacing:0.06em;margin-bottom:1.2rem;'>
              IMPORTANT !
            </div>

            <div style='color:rgba(255,255,255,0.90);font-size:0.97rem;
                        line-height:1.75;text-align:justify;margin-bottom:1.4rem;'>
              Platforma <strong>IDBDC-UPT</strong>
              (<em>Interogare &#8212; Dezvoltare Baze de Date Cercetare &#8211; UPT</em>)
              a intrat &#238;n testarea final&#259; a celor aproape <strong>6.000 de linii de cod</strong>,
              din <strong>11 fi&#351;iere principale Python</strong>, dintre care 5 fi&#351;iere sunt
              dedicate modulelor AI, <strong>93 de func&#355;ii &#351;i algoritmi defini&#355;i</strong>,
              <strong>24 de tabele de baze de date</strong> cu
              <strong>122 de c&#226;mpuri de date distincte</strong>, precum &#351;i a securit&#259;&#355;ii
              asigurate prin <strong>5 niveluri de autentificare</strong>.<br><br>
              Dup&#259; finalizarea procesului de testare final&#259; se va trece la &#238;nc&#259;rcarea cu
              date reale, at&#226;t curente c&#226;t &#351;i istorice. Pentru aceast&#259; etap&#259; va fi vizibil
              permanent un <strong>grafic de progres anual</strong> pentru fiecare categorie
              &#8212; contracte &#351;i proiecte pe tipuri, evenimente &#351;tiin&#355;ifice &#351;i proprietate
              industrial&#259; &#8212; dar &#351;i o <strong>num&#259;r&#259;toare invers&#259;</strong> p&#226;n&#259; la
              deschiderea accesului.
            </div>

            <div style='color:rgba(255,255,255,0.45);font-size:0.80rem;
                        margin-bottom:1.2rem;font-style:italic;'>
              Acces temporar restric&#355;ionat &#183; Introduce&#355;i parola pentru a continua
            </div>

          </div>
        </div>
    """, unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        pwd = st.text_input("Parola de acces:", type="password", key="_mw_pwd_c3")
        if st.button("Acces platform&#259;", key="_mw_btn_c3", use_container_width=True):
            if pwd == _MAINTENANCE_PASSWORD:
                st.session_state["_mw_cleared"] = True
                st.rerun()
            else:
                st.error("Parol&#259; incorect&#259;.")
    st.stop()

_maintenance_gate()# ─────────────────────────────────────────────────────────────────────────────


TITLE_LINE_1 = "🤖 Oportunități și Analiză Cercetare — AI"
TITLE_LINE_2 = "Departamentul Cercetare Dezvoltare Inovare"

APP_BLUE     = "#003366"
SIDEBAR_BLUE = "#0b2a52"

UPT_EMAIL_REGEX = re.compile(r"^[a-z]+(?:\.[a-z]+)+@upt\.ro$", re.IGNORECASE)


# =========================================================
# SUPABASE
# =========================================================

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
        if res.data:
            return res.data[0]
    except Exception:
        pass
    return None


# =========================================================
# STYLE
# =========================================================

def apply_style():
    st.markdown(
        f"""
        <style>
            .stApp {{ background-color: {APP_BLUE} !important; }}

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

            [data-testid="stToolbar"]    {{ visibility: hidden !important; height: 0px !important; }}
            [data-testid="stHeader"]     {{ visibility: hidden !important; height: 0px !important; }}
            [data-testid="stDecoration"] {{ visibility: hidden !important; height: 0px !important; }}
            #MainMenu {{ visibility: hidden !important; }}

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
        st.session_state.auth_ai   = False
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
        email = st.text_input("Email instituțional (prenume.nume@upt.ro)", value="")

        if st.button("Autentificare"):
            e = (email or "").strip().lower()

            if not UPT_EMAIL_REGEX.match(e):
                st.error("Email invalid. Exemplu: prenume.nume@upt.ro")
                st.stop()

            user = lookup_user(supabase, e)
            if not user:
                st.error("Emailul nu există în baza de date IDBDC.")
                st.stop()

            st.session_state.auth_ai    = True
            st.session_state.user_name  = (user.get("nume_prenume") or "").strip() or e
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

    apply_style()
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

    st.markdown('<div class="nav-note">Alege una dintre cele 4 secțiuni:</div>', unsafe_allow_html=True)

    render_nav_buttons()

    st.divider()

    sec = st.session_state.get("ai_section", None)

    if sec is None:
        st.info("Selectează o secțiune de mai sus pentru a începe.")
        return

    if sec == "chat":
        ai_analytics.render(supabase)
    elif sec == "radar":
        # Transmitem supabase pentru AI matching cu profilul UPT
        ai_radar.render(supabase)
    elif sec == "strategy":
        ai_recommendations.render(supabase)
    elif sec == "docs":
        ai_documents.render(supabase)
    else:
        st.info("Selectează o secțiune.")


if __name__ == "__main__":
    run()
