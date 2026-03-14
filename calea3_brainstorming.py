import streamlit as st
import re
from supabase import create_client, Client

from grant_navigator.engine import ai_analytics
from grant_navigator.engine import ai_radar
from grant_navigator.engine import ai_recommendations
from grant_navigator.engine import ai_documents

# ── MAINTENANCE LOCK ──────────────────────────────────────────────────────────
_MAINTENANCE_PASSWORD = "MW-2024-1147"

# ── DATA ȚINTĂ LANSARE — modificați doar această linie ────────────────────────
import datetime as _dt
_LAUNCH_DATE = _dt.datetime(2026, 3, 25, 9, 0, 0)   # an, lună, zi, oră, min, sec
# ─────────────────────────────────────────────────────────────────────────────

def _maintenance_gate():
    if st.session_state.get("_mw_cleared"):
        return

    now   = _dt.datetime.now()
    delta = _LAUNCH_DATE - now
    total_secs = max(int(delta.total_seconds()), 0)
    days    = total_secs // 86400
    hours   = (total_secs % 86400) // 3600
    minutes = (total_secs % 3600) // 60
    seconds = total_secs % 60

    st.markdown("""
        <style>
        .stApp { background: #06111f !important; }
        button[kind="primary"], .stButton > button {
            background: #1a4a8a !important;
            color: #fff !important;
            border: none !important;
            border-radius: 8px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style='text-align:center; margin-top:2.5rem; font-family:sans-serif;'>

            <div style='font-size:2.8rem; margin-bottom:0.3rem;'>🔬</div>
            <div style='color:#e8f0ff; font-size:1.25rem; font-weight:700;
                        letter-spacing:0.04em; margin-bottom:0.2rem;'>
                IDBDC — UPT
            </div>
            <div style='color:#7fa8d8; font-size:0.82rem; margin-bottom:2rem;
                        letter-spacing:0.06em; text-transform:uppercase;'>
                Departamentul Cercetare · Dezvoltare · Inovare
            </div>

            <div style='background:rgba(26,74,138,0.18); border:1px solid rgba(100,160,255,0.25);
                        border-radius:16px; padding:24px 32px;
                        max-width:520px; margin:0 auto 2.2rem auto; line-height:1.7;'>
                <div style='color:#c8deff; font-size:1.0rem; font-weight:600; margin-bottom:0.6rem;'>
                    ⚙️ Platformă în pregătire finală
                </div>
                <div style='color:rgba(200,222,255,0.75); font-size:0.88rem;'>
                    Echipa IDBDC finalizează încărcarea bazelor de date și ultimele ajustări.<br>
                    Platforma va fi disponibilă integral la data afișată mai jos.<br><br>
                    <span style='color:#90c0ff;'>
                        Vă mulțumim pentru răbdare!
                    </span>
                </div>
            </div>

            <div style='display:flex; justify-content:center; gap:16px; margin-bottom:2rem;
                        flex-wrap:wrap;'>
                <div style='background:rgba(255,255,255,0.06); border:1px solid rgba(100,160,255,0.20);
                            border-radius:12px; padding:14px 20px; min-width:78px;'>
                    <div id='cd-days' style='color:#60aaff; font-size:2.2rem; font-weight:800;
                                line-height:1;'>{days:02d}</div>
                    <div style='color:#7fa8d8; font-size:0.70rem; letter-spacing:0.08em;
                                margin-top:4px; text-transform:uppercase;'>Zile</div>
                </div>
                <div style='background:rgba(255,255,255,0.06); border:1px solid rgba(100,160,255,0.20);
                            border-radius:12px; padding:14px 20px; min-width:78px;'>
                    <div id='cd-hours' style='color:#60aaff; font-size:2.2rem; font-weight:800;
                                line-height:1;'>{hours:02d}</div>
                    <div style='color:#7fa8d8; font-size:0.70rem; letter-spacing:0.08em;
                                margin-top:4px; text-transform:uppercase;'>Ore</div>
                </div>
                <div style='background:rgba(255,255,255,0.06); border:1px solid rgba(100,160,255,0.20);
                            border-radius:12px; padding:14px 20px; min-width:78px;'>
                    <div id='cd-min' style='color:#60aaff; font-size:2.2rem; font-weight:800;
                                line-height:1;'>{minutes:02d}</div>
                    <div style='color:#7fa8d8; font-size:0.70rem; letter-spacing:0.08em;
                                margin-top:4px; text-transform:uppercase;'>Minute</div>
                </div>
                <div style='background:rgba(255,255,255,0.06); border:1px solid rgba(100,160,255,0.20);
                            border-radius:12px; padding:14px 20px; min-width:78px;'>
                    <div id='cd-sec' style='color:#f0c060; font-size:2.2rem; font-weight:800;
                                line-height:1;'>{seconds:02d}</div>
                    <div style='color:#7fa8d8; font-size:0.70rem; letter-spacing:0.08em;
                                margin-top:4px; text-transform:uppercase;'>Secunde</div>
                </div>
            </div>

            <div style='color:rgba(140,180,255,0.55); font-size:0.78rem; margin-bottom:2rem;'>
                Data estimată lansare:
                <strong style='color:rgba(160,200,255,0.80);'>
                    {_LAUNCH_DATE.strftime("%d %B %Y, ora %H:%M")}
                </strong>
            </div>

        </div>

        <script>
        (function() {{
            var target = new Date("{_LAUNCH_DATE.strftime('%Y-%m-%dT%H:%M:%S')}").getTime();
            function tick() {{
                var now  = Date.now();
                var diff = Math.max(0, Math.floor((target - now) / 1000));
                var d = Math.floor(diff / 86400);
                var h = Math.floor((diff % 86400) / 3600);
                var m = Math.floor((diff % 3600) / 60);
                var s = diff % 60;
                var pad = function(n) {{ return n < 10 ? '0' + n : '' + n; }};
                var el;
                if ((el = document.getElementById('cd-days')))  el.textContent = pad(d);
                if ((el = document.getElementById('cd-hours'))) el.textContent = pad(h);
                if ((el = document.getElementById('cd-min')))   el.textContent = pad(m);
                if ((el = document.getElementById('cd-sec')))   el.textContent = pad(s);
            }}
            setInterval(tick, 1000);
            tick();
        }})();
        </script>
    """, unsafe_allow_html=True)

    pwd = st.text_input("Cod acces anticipat:", type="password", key="_mw_pwd_c3")
    if st.button("Autorizare acces", key="_mw_btn_c3"):
        if pwd == _MAINTENANCE_PASSWORD:
            st.session_state["_mw_cleared"] = True
            st.rerun()
        else:
            st.error("Cod incorect.")
    st.stop()

_maintenance_gate()
# ─────────────────────────────────────────────────────────────────────────────


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
