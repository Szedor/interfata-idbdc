# =========================================================
# IDBDC/explorator/main.py
# VERSIUNE: 5.0
# STATUS: ACTUALIZAT — Tab3 conectat cu Rapoarte, Grafice, Alerte
# DATA: 2026.06.14
# =========================================================
# MODIFICĂRI VERSIUNEA 5.0:
#   - Tab3 conectat cu sub-taburi: Rapoarte | Grafice (în Rapoarte) | Alerte
#   - Număr alerte afișat dinamic pe Tab3
#   - Autentificare export identică cu Tab1
#   - Restul neatins față de versiunea 4.0
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
from explorator.explorare_avansata import render_tab2_explorare_avansata
from explorator.tab3_rapoarte import render_tab3_rapoarte
from explorator.tab3_alerte import render_tab3_alerte

ACADEMIC_BLUE = "#0b2a52"
TITLE_LINE_1 = "🔎 BAZE DE DATE  -  Interogare | Cautare | Consultare avansata"
TITLE_LINE_2 = "Departamentul Cercetare Dezvoltare Inovare - UPT"


def hide_streamlit_chrome():
    st.markdown(
        """
        <style>
          [data-testid="stHeader"] { visibility: hidden; height: 0px; }
          #MainMenu { visibility: hidden; }
          footer { visibility: hidden; height: 0px; }
          [data-testid="stToolbar"] { display: none !important; }
          [data-testid="stDecoration"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _get_theme_c1():
    return st.session_state.get("dark_mode_c1", True)


def apply_style():
    dark = _get_theme_c1()

    if dark:
        bg             = ACADEMIC_BLUE
        text_color     = "#ffffff"
        title_color    = "#ffffff"
        input_bg       = "#1a3a5c"
        input_border   = "rgba(255,255,255,0.30)"
        btn_bg         = "rgba(255,255,255,0.96)"
        btn_color      = "#0b1f3a"
        btn_hover_bg   = "#ffffff"
        btn_hover_color= "#003366"
        divider_clr    = "rgba(255,255,255,0.20)"
    else:
        bg             = "#F8FBFF"
        text_color     = "#0b2a52"
        title_color    = "#0b2a52"
        input_bg       = "#ffffff"
        input_border   = "rgba(11,42,82,0.30)"
        btn_bg         = "rgba(11,42,82,0.10)"
        btn_color      = "#0b1f3a"
        btn_hover_bg   = "#0b2a52"
        btn_hover_color= "#ffffff"
        divider_clr    = "rgba(11,42,82,0.20)"

    st.markdown(
        f"""
        <style>
          .stApp {{ background: {bg} !important; }}
          div.block-container {{ padding-top: 1.1rem; padding-bottom: 1.0rem; max-width: 1550px; }}
          .idbdc-header {{ text-align: center; margin-top: 0.2rem; margin-bottom: 0.9rem; }}
          .idbdc-title-1 {{ font-size: 2.05rem; font-weight: 900; line-height: 1.15; color: {title_color}; margin: 0; }}
          .idbdc-title-2 {{ font-size: 1.86rem; font-weight: 800; line-height: 1.2; color: {title_color}; opacity: 0.95; margin: 0.35rem 0 0 0; }}
          label, .stMarkdown, .stCaption, .stText {{ color: {text_color} !important; }}
          [data-testid="stMarkdownContainer"] p {{ color: {text_color} !important; }}
          .stTextInput > div > div, .stTextInput > div > div > input,
          .stTextInput input, .stTextInput input:hover, .stTextInput input:focus,
          .stSelectbox > div > div, .stSelectbox [data-baseweb="select"],
          .stMultiSelect > div > div, .stMultiSelect [data-baseweb="select"] > div {{
            background: {input_bg} !important; color: {"#ffffff" if dark else "#0b2a52"} !important;
            border-radius: 10px !important; border: 1px solid {input_border} !important;
            caret-color: {"#ffffff" if dark else "#0b2a52"} !important;
          }}
          .stButton > button,
          .stDownloadButton > button {{
            border-radius: 10px !important;
            font-weight: 900 !important;
            background: {btn_bg} !important;
            color: {btn_color} !important;
            -webkit-text-fill-color: {btn_color} !important;
            border: 1px solid {"rgba(255,255,255,0.55)" if dark else "rgba(11,42,82,0.35)"} !important;
          }}
          .stButton > button:hover,
          .stDownloadButton > button:hover {{
            background: {btn_hover_bg} !important;
            color: {btn_hover_color} !important;
            -webkit-text-fill-color: {btn_hover_color} !important;
          }}
          h1, h2, h3 {{ color: {title_color} !important; }}
          hr {{ border-color: {divider_clr} !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_toggle():
    dark = _get_theme_c1()
    label = "☀️ Light mode" if dark else "🌙 Dark mode"
    _, col_btn = st.columns([9, 1])
    with col_btn:
        if st.button(label, key="toggle_theme_c1"):
            st.session_state.dark_mode_c1 = not dark
            st.rerun()


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

    dark = _get_theme_c1()
    bg = ACADEMIC_BLUE if dark else "#F8FBFF"
    text_color = "#ffffff" if dark else "#0b2a52"

    st.markdown(
        f"""
        <style>
          .stApp {{ background: {bg} !important; }}
          div.block-container {{ padding-top: 4.0rem; padding-bottom: 2.0rem; }}
          .gate-box {{
            background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.25);
            border-radius: 18px; padding: 26px 22px 18px 22px;
          }}
          .gate-title {{ text-align: center; font-size: 1.45rem; font-weight: 900; color: {text_color}; }}
          .gate-subtitle {{ text-align: center; color: {"rgba(255,255,255,0.92)" if dark else "rgba(11,42,82,0.80)"}; font-size: 1.02rem; }}
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

    cod_initial = st.session_state.pop("tab2_goto_cod", "")

    c1, c2, _ = st.columns([1.2, 0.5, 3.3])
    with c1:
        cod = st.text_input(
            "Cod identificare",
            value=cod_initial,
            key="fisa_cod",
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
                st.markdown("<div style='margin-top:28px;font-size:1.4rem;'>✅</div>",
                            unsafe_allow_html=True)
            elif cod and len(cod) >= 3:
                st.markdown("<div style='margin-top:28px;font-size:1.4rem;'>❌</div>",
                            unsafe_allow_html=True)

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
        st.error("⚠️ Acest tip de contract nu este disponibil pentru interogare publică.")
        return
    elif tabela_gasita == "base_proiecte_fdi":
        from explorator.fise.proiecte_fdi import run as run_fisa_fdi
        run_fisa_fdi(supabase, cod, tabela_gasita, "FDI")
    else:
        render_fisa_generica(supabase, cod, tabela_gasita, titlu_fisa_curat)


def _render_tab3(supabase: Client):
    """
    Tab3 — Raportări cu sub-taburi: Rapoarte & Grafice | Alerte
    Numărul de alerte este afișat dinamic după calcul.
    """
    # Badge alerte din sesiunea anterioară (dacă există)
    nr_alerte_cache = st.session_state.get("tab3_nr_alerte", None)

    label_alerte = (
        f"🔔 Alerte  ({nr_alerte_cache})" if nr_alerte_cache is not None
        else "🔔 Alerte"
    )

    subtab1, subtab2 = st.tabs([
        "📊 Rapoarte & Grafice",
        label_alerte,
    ])

    with subtab1:
        render_tab3_rapoarte(supabase)

    with subtab2:
        nr = render_tab3_alerte(supabase)
        if nr > 0:
            # Salvăm numărul pentru a-l afișa pe tab la următorul rerun
            st.session_state["tab3_nr_alerte"] = nr


def _gate_tab(key_session: str, secret_key: str, titlu: str,
              descriere: str, render_fn):
    """Folosit doar pentru Tab3 — protecție cu parolă."""
    if st.session_state.get(key_session, False):
        render_fn()
        return

    parola_corecta = st.secrets.get(secret_key, "")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.22);"
        f"border-radius:14px;padding:28px 28px 24px 28px;max-width:480px;margin:0 auto;'>"
        f"<div style='text-align:center;font-size:1.8rem;margin-bottom:12px;'>🔐</div>"
        f"<div style='color:#ffffff;font-weight:800;font-size:1.05rem;text-align:center;"
        f"margin-bottom:8px;'>{titlu}</div>"
        f"<div style='color:rgba(255,255,255,0.70);font-size:0.92rem;text-align:center;"
        f"margin-bottom:18px;'>{descriere}</div>",
        unsafe_allow_html=True,
    )

    col_inp, col_btn = st.columns([3, 1])
    with col_inp:
        pwd = st.text_input(
            "Parolă",
            type="password",
            key=f"pwd_input_{key_session}",
            label_visibility="collapsed",
            placeholder="Introduceți parola de acces",
        )
    with col_btn:
        if st.button("▶ Acces", key=f"pwd_btn_{key_session}", use_container_width=True):
            if pwd and pwd == parola_corecta:
                st.session_state[key_session] = True
                st.rerun()
            else:
                st.error("Parolă incorectă.")

    st.markdown("</div>", unsafe_allow_html=True)


def run():
    st.set_page_config(page_title="IDBDC – Explorare", layout="wide")

    if "dark_mode_c1" not in st.session_state:
        st.session_state.dark_mode_c1 = True

    gate_control()
    hide_streamlit_chrome()
    apply_style()

    try:
        url = Config.SUPABASE_URL
        key = Config.SUPABASE_KEY
    except Exception:
        st.error("Config lipsă: setează SUPABASE_URL și SUPABASE_KEY în Streamlit Secrets.")
        st.stop()

    supabase: Client = create_client(url, key)

    render_toggle()
    render_header()
    st.divider()

    # Dacă Tab2 a trimis un cod spre Tab1
    if st.session_state.get("tab2_goto_tab1", False):
        st.session_state["tab2_goto_cod"] = st.session_state.pop("tab2_goto_tab1_cod", "")
        st.session_state.pop("tab2_goto_tab1", None)

    # Badge dinamic pe Tab3
    nr_alerte = st.session_state.get("tab3_nr_alerte", None)
    label_tab3 = (
        f"📊 Raportări  🔔{nr_alerte}" if nr_alerte else "📊 Raportări"
    )

    tab1, tab2, tab3 = st.tabs([
        "📄 Fișa completă (după cod)",
        "🔎 Explorare avansată",
        label_tab3,
    ])

    with tab1:
        render_fisa_completa(supabase)

    with tab2:
        render_tab2_explorare_avansata(supabase)

    with tab3:
        _gate_tab(
            key_session = "tab3_deblocat",
            secret_key  = "PASSWORD_TAB3",
            titlu       = "📊 Raportări",
            descriere   = "Această secțiune este disponibilă operatorilor autorizați.",
            render_fn   = lambda: _render_tab3(supabase),
        )


if __name__ == "__main__":
    run()
