# =========================================================
# explorator/main.py
# vers.modul.1.2
# 2026.04.28
# Fix culoare text butoane export
# =========================================================

import streamlit as st
from supabase import Client, create_client
from config import Config

from _maintenance_msg import maintenance_gate as _maintenance_gate_fn

from utils.display_config import ALL_BASE_TABLES, TABLE_LABELS
from utils.supabase_helpers import safe_select_eq
from utils.fisa_completa_orchestrator import render_fisa_completa as render_fisa_generica

from explorator.fise.contracte_cep import run as run_fisa_cep
from explorator.fise.contracte_terti import run as run_fisa_terti
from explorator.fise.contracte_speciale import run as run_fisa_speciale

ACADEMIC_BLUE = "#0b2a52"
TITLE_LINE_1 = "🔎 Baze de date - Interogare | Cautare | Consultare avansata"
TITLE_LINE_2 = "Departamentul Cercetare Dezvoltare Inovare"


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


def apply_style_full_blue():
    st.markdown(
        f"""
        <style>
          .stApp {{ background: {ACADEMIC_BLUE} !important; }}
          div.block-container {{ padding-top: 1.1rem; padding-bottom: 1.0rem; max-width: 1550px; }}
          .idbdc-header {{ text-align: center; margin-top: 0.2rem; margin-bottom: 0.9rem; }}
          .idbdc-title-1 {{ font-size: 2.05rem; font-weight: 900; line-height: 1.15; color: #ffffff; margin: 0; }}
          .idbdc-title-2 {{ font-size: 1.86rem; font-weight: 800; line-height: 1.2; color: rgba(255,255,255,0.95); margin: 0.35rem 0 0 0; }}
          label, .stMarkdown, .stCaption, .stText {{ color: #ffffff !important; }}
          [data-testid="stMarkdownContainer"] p {{ color: #ffffff !important; }}
          .stTextInput > div > div, .stTextInput > div > div > input,
          .stTextInput input, .stTextInput input:hover, .stTextInput input:focus,
          .stSelectbox > div > div, .stSelectbox [data-baseweb="select"],
          .stMultiSelect > div > div, .stMultiSelect [data-baseweb="select"] > div {{
            background: #1a3a5c !important; color: #ffffff !important;
            border-radius: 10px !important; border: 1px solid rgba(255,255,255,0.30) !important;
          }}
          /* Butoane normale si butoane download — text inchis pe fond deschis */
          .stButton > button,
          .stDownloadButton > button {{
            border-radius: 10px !important;
            font-weight: 900 !important;
            background: rgba(255,255,255,0.96) !important;
            color: #0b1f3a !important;
            -webkit-text-fill-color: #0b1f3a !important;
            border: 1px solid rgba(255,255,255,0.55) !important;
          }}
          .stButton > button:hover,
          .stDownloadButton > button:hover {{
            background: #ffffff !important;
            color: #0b1f3a !important;
            -webkit-text-fill-color: #0b1f3a !important;
          }}
          h1, h2, h3 {{ color: #ffffff !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    import html as _html
    st.markdown(
        f"""
        <div class="idbdc-header">
          <div class="idbdc-title-1">{_html.escape(TITLE_LINE_1)}</div>
          <div class="idbdc-title-2">{_html.escape(TITLE_LINE_2)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_export_auth_tab1(supabase):
    return True


def gate_control():
    GATE_ENABLED = bool(st.secrets.get("GATE_ENABLED", True))
    PASSWORD_CONSULTARE = st.secrets.get("PASSWORD_CONSULTARE", "")

    if not GATE_ENABLED:
        st.session_state.autorizat_consultare = True
        return

    if "autorizat_consultare" not in st.session_state:
        st.session_state.autorizat_consultare = False

    if st.session_state.autorizat_consultare:
        return

    hide_streamlit_chrome()
    st.markdown(
        f"""
        <style>
          .stApp {{ background: {ACADEMIC_BLUE} !important; }}
          div.block-container {{ padding-top: 4.0rem; padding-bottom: 2.0rem; }}
          .gate-box {{
            background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.25);
            border-radius: 18px; padding: 26px 22px 18px 22px;
          }}
          .gate-title {{ text-align: center; font-size: 1.45rem; font-weight: 900; color: #ffffff; }}
          .gate-subtitle {{ text-align: center; color: rgba(255,255,255,0.92); font-size: 1.02rem; }}
          .stTextInput input {{ background: rgba(255,255,255,0.96) !important; color: #0b1f3a !important; }}
          .stButton > button {{
            width: 100%;
            background: rgba(255,255,255,0.96) !important;
            color: #0b1f3a !important;
            -webkit-text-fill-color: #0b1f3a !important;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, mid, right = st.columns([1.8, 1.0, 1.8])
    with mid:
        st.markdown('<div class="gate-box">', unsafe_allow_html=True)
        st.markdown('<div class="gate-title">🛡️ Acces securizat</div>', unsafe_allow_html=True)
        st.markdown('<div class="gate-subtitle">Interogare baze de date – DCDI</div>', unsafe_allow_html=True)
        parola = st.text_input("Parola acces:", type="password")
        if st.button("Autorizare acces", use_container_width=True):
            if parola == PASSWORD_CONSULTARE:
                st.session_state.autorizat_consultare = True
                st.rerun()
            else:
                st.error("Parolă greșită.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


def render_fisa_completa(supabase: Client):
    st.markdown("## 📄 Fișă completă")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.88);font-size:1.02rem;font-weight:600;"
        "margin-bottom:0.85rem;'>Introduceți codul și consultați toate informațiile asociate.</div>",
        unsafe_allow_html=True,
    )

    c1, c2, _ = st.columns([1.2, 0.5, 3.3])
    with c1:
        cod = st.text_input(
            "Cod identificare", value="", key="fisa_cod",
            placeholder="Ex: 998877 sau 26FDI26",
        ).strip()

    cod_found = False
    tabela_gasita = None

    if cod and len(cod) >= 3:
        for t in ALL_BASE_TABLES:
            rows_check = safe_select_eq(supabase, t, "cod_identificare", cod, limit=1)
            if rows_check:
                cod_found = True
                tabela_gasita = t
                break
        with c2:
            if cod_found:
                st.markdown("<div style='margin-top:28px;font-size:1.4rem;'>✅</div>", unsafe_allow_html=True)
            elif cod and len(cod) >= 3:
                st.markdown("<div style='margin-top:28px;font-size:1.4rem;'>❌</div>", unsafe_allow_html=True)

    if not cod or len(cod) < 3:
        st.info("Introduceți codul identificare (minim 3 caractere).", icon="ℹ️")
        return

    if cod_found:
        st.markdown(
            "<div style='background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.45);"
            "border-radius:10px;padding:7px 14px;margin-bottom:4px;display:inline-block;'>"
            "<span style='color:#4ade80;font-weight:700;font-size:0.92rem;'>"
            "✅ Înregistrarea este confirmată — fișa este disponibilă și pregătită pentru consultare."
            "</span></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='background:rgba(255,100,100,0.15);border:1px solid rgba(255,100,100,0.60);"
            "border-radius:10px;padding:7px 14px;margin-bottom:4px;display:inline-block;'>"
            "<span style='color:#ff8888;font-weight:700;font-size:0.92rem;'>"
            "❌ Codul introdus nu a fost găsit în baza de date."
            "</span></div>",
            unsafe_allow_html=True,
        )
        return

    st.divider()
    titlu_fisa = TABLE_LABELS.get(tabela_gasita, "Fișă")
    titlu_fisa_curat = titlu_fisa.split(" ", 1)[-1] if " " in titlu_fisa else titlu_fisa
    st.markdown(
        f"<div style='color:#ffffff;font-size:1.35rem;font-weight:900;"
        f"letter-spacing:0.03em;margin-bottom:1rem;'>"
        f"INFORMAȚII {titlu_fisa_curat.upper()}</div>",
        unsafe_allow_html=True,
    )

    if tabela_gasita == "base_contracte_cep":
        run_fisa_cep(supabase, cod, tabela_gasita, "CEP")
    elif tabela_gasita == "base_contracte_terti":
        run_fisa_terti(supabase, cod, tabela_gasita, "TERȚI")
    elif tabela_gasita == "base_contracte_speciale":
        run_fisa_speciale(supabase, cod, tabela_gasita, "SPECIALE")
    else:
        render_fisa_generica(supabase, cod, tabela_gasita, titlu_fisa_curat)


def render_explorare_criteriu(supabase):
    st.markdown("## 🔎 Explorare universală")
    st.info("Această secțiune este în curs de dezvoltare.", icon="ℹ️")


def render_raportari(supabase):
    st.markdown("## 📊 Raportări")
    st.info("Această secțiune este în curs de dezvoltare.", icon="ℹ️")


def run():
    st.set_page_config(page_title="IDBDC – Explorare", layout="wide")
    _maintenance_gate_fn(st, pwd_key="_mw_pwd_c1", btn_key="_mw_btn_c1")
    gate_control()
    hide_streamlit_chrome()
    apply_style_full_blue()

    try:
        url = Config.SUPABASE_URL
        key = Config.SUPABASE_KEY
    except Exception:
        st.error("Config lipsă: setează SUPABASE_URL și SUPABASE_KEY în Streamlit Secrets.")
        st.stop()

    supabase: Client = create_client(url, key)
    render_header()
    st.divider()

    tab1, tab2, tab3 = st.tabs([
        "📄 Fișa completă (după cod)",
        "🔎 Explorare universală",
        "📊 Raportări",
    ])

    with tab1:
        render_fisa_completa(supabase)
    with tab2:
        render_explorare_criteriu(supabase)
    with tab3:
        render_raportari(supabase)


if __name__ == "__main__":
    run()
