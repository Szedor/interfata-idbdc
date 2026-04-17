import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime as dt
import html as _html
import streamlit.components.v1 as components
import io

from config import Config
from _maintenance_msg import maintenance_gate as _maintenance_gate_fn

from explorator.fisa_completa import render_fisa_completa
from explorator.explorare_avansata import render_tab2_explorare_avansata
from explorator.rapoarte_analiza import render_tab3_rapoarte_analiza


GATE_ENABLED = bool(st.secrets.get("GATE_ENABLED", True))
PASSWORD_CONSULTARE = st.secrets.get("PASSWORD_CONSULTARE", "")

TITLE_LINE_1 = "🔎 Baze de date - Interogare | Cautare | Consultare avansata"
TITLE_LINE_2 = "Departamentul Cercetare Dezvoltare Inovare"
ACADEMIC_BLUE = "#0b2a52"


CATEGORII = {
    "Contracte": {
        "tipuri": {
            "TERTI": "base_contracte_terti",
            "CEP":   "base_contracte_cep",
        }
    },
    "Proiecte": {
        "tipuri": {
            "FDI":             "base_proiecte_fdi",
            "PNCDI":           "base_proiecte_pncdi",
            "PNRR":            "base_proiecte_pnrr",
            "INTERNATIONALE":  "base_proiecte_internationale",
            "INTERREG":        "base_proiecte_interreg",
            "NONEU":           "base_proiecte_noneu",
            "SEE":             "base_proiecte_see",
        }
    },
    "Evenimente stiintifice": {
        "base_table": "base_evenimente_stiintifice",
        "tipuri": None,
    },
    "Proprietate industriala": {
        "base_table": "base_prop_intelect",
        "tipuri": None,
    },
}

TEXT_COL_CANDIDATES = [
    "cod_identificare",
    "titlu", "titlul_proiect", "titlu_proiect", "titlu_eveniment", "titlu_lucrare",
    "denumire", "denumire_proiect", "denumire_eveniment",
    "acronim", "acronim_proiect",
    "obiect_contract",
    "descriere", "observatii", "cuvinte_cheie",
]

YEAR_COL_CANDIDATES_CP  = ["data_inceput"]
YEAR_COL_CANDIDATES_EV  = ["data_inceput", "data_eveniment", "data"]
YEAR_COL_CANDIDATES_PI  = ["data_oficiala_acordare", "data_acordare", "data"]

COM_TABLES = {
    "💰 Financiar":  "com_date_financiare",
    "🧪 Tehnic":     "com_aspecte_tehnice",
    "👥 Echipă":     "com_echipe_proiect",
}

TABLE_LABELS = {
    "base_contracte_cep":           "📄 Contract CEP",
    "base_contracte_terti":         "📄 Contract TERȚI",
    "base_contracte_speciale":      "📄 Contract SPECIAL",
    "base_proiecte_fdi":            "🔬 Proiect FDI",
    "base_proiecte_pncdi":          "🔬 Proiect PNCDI",
    "base_proiecte_pnrr":           "🔬 Proiect PNRR",
    "base_proiecte_internationale": "🌍 Proiect Internațional",
    "base_proiecte_interreg":       "🌍 Proiect INTERREG",
    "base_proiecte_noneu":          "🌍 Proiect NON-EU",
    "base_proiecte_see":            "🌍 Proiect SEE",
    "base_evenimente_stiintifice":  "🎓 Eveniment Științific",
    "base_prop_intelect":           "💡 Proprietate Industrială",
}

ALL_BASE_TABLES = [
    "base_contracte_terti",
    "base_contracte_cep",
    "base_proiecte_fdi",
    "base_proiecte_pncdi",
    "base_proiecte_pnrr",
    "base_proiecte_internationale",
    "base_proiecte_interreg",
    "base_proiecte_noneu",
    "base_proiecte_see",
    "base_evenimente_stiintifice",
    "base_prop_intelect",
]


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
          [data-testid="stCaptionContainer"] {{ color: rgba(255,255,255,0.88) !important; }}
          .stTextInput > div > div, .stTextInput > div > div > input, .stTextInput input,
          .stTextInput input:hover, .stTextInput input:focus, .stTextInput input:active,
          .stTextInput input:focus-visible, .stTextInput > div > div:hover,
          .stTextInput > div > div:focus-within, .stTextInput [data-baseweb="input"],
          .stTextInput [data-baseweb="input"]:hover, .stTextInput [data-baseweb="input"]:focus-within {{
            background: #1a3a5c !important; background-color: #1a3a5c !important;
            color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
            border-radius: 10px !important; font-weight: 600 !important;
            border: 1px solid rgba(255,255,255,0.30) !important; caret-color: #ffffff !important;
          }}
          .stTextInput input:-webkit-autofill, .stTextInput input:-webkit-autofill:hover,
          .stTextInput input:-webkit-autofill:focus {{
            -webkit-box-shadow: 0 0 0px 1000px #1a3a5c inset !important;
            -webkit-text-fill-color: #ffffff !important; caret-color: #ffffff !important;
          }}
          .stTextInput input::placeholder {{
            color: rgba(255,255,255,0.50) !important;
            -webkit-text-fill-color: rgba(255,255,255,0.50) !important; opacity: 1 !important;
          }}
          .stNumberInput > div > div, .stNumberInput > div > div > input, .stNumberInput input,
          .stNumberInput input:hover, .stNumberInput input:focus, .stNumberInput input:active,
          .stNumberInput [data-baseweb="input"], .stNumberInput [data-baseweb="input"]:hover,
          .stNumberInput [data-baseweb="input"]:focus-within {{
            background: #1a3a5c !important; background-color: #1a3a5c !important;
            color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
            border-radius: 10px !important; font-weight: 600 !important; caret-color: #ffffff !important;
          }}
          .stSelectbox > div > div, .stSelectbox [data-baseweb="select"],
          .stSelectbox [data-baseweb="select"] > div, .stSelectbox [data-baseweb="select"] > div > div,
          .stSelectbox [data-baseweb="select"] > div > div > div,
          .stSelectbox [data-baseweb="select"] span, .stSelectbox [data-baseweb="select"] input,
          .stSelectbox [data-baseweb="select"] svg {{
            background: #1a3a5c !important; color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important; border-radius: 10px !important; font-weight: 600 !important;
          }}
          .stMultiSelect > div > div, .stMultiSelect [data-baseweb="select"] > div,
          .stMultiSelect [data-baseweb="select"] span, .stMultiSelect [data-baseweb="select"] input {{
            background: #1a3a5c !important; color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important; border-radius: 10px !important;
          }}
          [data-baseweb="popover"], [data-baseweb="popover"] *, [data-baseweb="menu"],
          [data-baseweb="menu"] *, [role="listbox"], [role="listbox"] *, [role="option"] {{
            background-color: #ffffff !important; color: #0b1f3a !important;
            -webkit-text-fill-color: #0b1f3a !important;
          }}
          [role="option"]:hover, [role="option"][aria-selected="true"] {{
            background-color: #dce6f5 !important;
          }}
          .stButton > button {{
            border-radius: 10px !important; font-weight: 900 !important;
            background: rgba(255,255,255,0.96) !important; color: #0b1f3a !important;
            -webkit-text-fill-color: #0b1f3a !important;
            border: 1px solid rgba(255,255,255,0.55) !important; opacity: 1 !important;
          }}
          .stButton > button p {{ color: #0b1f3a !important; -webkit-text-fill-color: #0b1f3a !important; }}
          .stButton > button:hover {{
            border: 1px solid rgba(255,255,255,0.90) !important; color: #0b1f3a !important;
            -webkit-text-fill-color: #0b1f3a !important; opacity: 1 !important;
          }}
          [data-testid="stTabs"] {{ margin-top: 0.15rem; }}
          h1, h2, h3 {{ color: #ffffff !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_style_gate():
    st.markdown(
        f"""
        <style>
          .stApp {{ background: {ACADEMIC_BLUE} !important; }}
          div.block-container {{ padding-top: 4.0rem; padding-bottom: 2.0rem; }}
          .gate-box {{
            background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.25);
            border-radius: 18px; padding: 26px 22px 18px 22px; box-shadow: 0 12px 30px rgba(0,0,0,0.28);
          }}
          .gate-title {{ text-align: center; font-size: 1.45rem; font-weight: 900; color: #ffffff; margin: 0 0 0.35rem 0; }}
          .gate-subtitle {{ text-align: center; color: rgba(255,255,255,0.92); font-size: 1.02rem; font-weight: 600; margin: 0 0 1.1rem 0; }}
          .stTextInput label {{ color: #ffffff !important; font-weight: 800 !important; }}
          .stTextInput input {{ background: rgba(255,255,255,0.96) !important; color: #0b1f3a !important; border-radius: 12px !important; }}
          .stButton > button {{ width: 100%; border-radius: 12px; font-weight: 900; background: rgba(255,255,255,0.96) !important; color: #0b1f3a !important; opacity: 1 !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        f"""
        <div class="idbdc-header">
          <div class="idbdc-title-1">{_html.escape(TITLE_LINE_1)}</div>
          <div class="idbdc-title-2">{_html.escape(TITLE_LINE_2)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def gate():
    if not GATE_ENABLED:
        st.session_state.autorizat_consultare = True
        return

    if not PASSWORD_CONSULTARE:
        hide_streamlit_chrome()
        apply_style_gate()
        st.error("Config lipsă: setează PASSWORD_CONSULTARE în Streamlit Cloud → Settings → Secrets.")
        st.stop()

    if "autorizat_consultare" not in st.session_state:
        st.session_state.autorizat_consultare = False

    if not st.session_state.autorizat_consultare:
        hide_streamlit_chrome()
        apply_style_gate()

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


def run():
    _maintenance_gate_fn(st, pwd_key="_mw_pwd_c1", btn_key="_mw_btn_c1")
    gate()
    hide_streamlit_chrome()
    apply_style_full_blue()

    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        st.error("Config lipsă: setează SUPABASE_URL și SUPABASE_KEY în Streamlit Cloud → Settings → Secrets.")
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
        render_tab2_explorare_avansata(supabase)

    with tab3:
        render_tab3_rapoarte_analiza(supabase)


if __name__ == "__main__":
    run()
