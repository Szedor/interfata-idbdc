import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime as dt
import html as _html
import streamlit.components.v1 as components


# =========================================================
# CONFIG
# =========================================================

TITLE_GATE = "🛡️ Acces securizat – Interogare Baze de Date"
SUBTITLE_GATE = "Departamentul Cercetare Dezvoltare Inovare"

TITLE_MAIN = "🔎 Baze de Date – Departamentul Cercetare Dezvoltare Inovare"
SUBTITLE_MAIN = "Interogare | Căutare | Consultare avansată"

GATE_ENABLED = bool(st.secrets.get("GATE_ENABLED", True))
PASSWORD_CONSULTARE = st.secrets.get("PASSWORD_CONSULTARE", "")


# =========================================================
# STYLE (academic blue)
# =========================================================

def apply_style():

    st.markdown(
        """
        <style>

        [data-testid="stSidebar"] {
            background: #0b2a52 !important;
            border-right: 2px solid rgba(255,255,255,0.20);
        }

        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #ffffff !important;
        }

        div.block-container {
            padding-top: 1.5rem;
            padding-bottom: 1rem;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# GATE
# =========================================================

def gate():

    if not GATE_ENABLED:
        st.session_state.autorizat_consultare = True
        return

    if "autorizat_consultare" not in st.session_state:
        st.session_state.autorizat_consultare = False

    if not st.session_state.autorizat_consultare:

        apply_style()

        col1, col2, col3 = st.columns([1.5,1,1.5])

        with col2:

            st.markdown(
                "<h3 style='text-align:center;'>🛡️ Acces securizat</h3>",
                unsafe_allow_html=True
            )

            st.caption(
                "Interogare baze de date – Departamentul Cercetare Dezvoltare Inovare"
            )

            parola = st.text_input(
                "Parola acces:",
                type="password"
            )

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            if st.button("Autorizare acces", use_container_width=True):

                if parola == PASSWORD_CONSULTARE:

                    st.session_state.autorizat_consultare = True
                    st.rerun()

                else:
                    st.error("Parolă greșită.")

        st.stop()


# =========================================================
# TABLE MAP
# =========================================================

CATEGORII = {
    "Evenimente stiintifice": {
        "base_table": "base_evenimente_stiintifice",
        "tipuri": None,
    },
    "Proprietate intelectuala": {
        "base_table": "base_prop_intelect",
        "tipuri": None,
    },
    "Contracte & Proiecte": {
        "tipuri": {
            "TERTI": "base_contracte_terti",
            "CEP": "base_contracte_cep",
            "PNCDI": "base_proiecte_pncdi",
            "PNRR": "base_proiecte_pnrr",
            "FDI": "base_proiecte_fdi",
            "INTERNATIONALE": "base_proiecte_internationale",
            "INTERREG": "base_proiecte_interreg",
            "NONEU": "base_proiecte_noneu",
        }
    }
}


# =========================================================
# HELPERS
# =========================================================

@st.cache_data(show_spinner=False, ttl=600)
def get_table_columns(_supabase: Client, table_name: str):

    try:
        res = _supabase.rpc("idbdc_get_columns", {"p_table": table_name}).execute()
        return [r["column_name"] for r in (res.data or [])]

    except:
        return []


# =========================================================
# MAIN
# =========================================================

def run():

    st.set_page_config(
        page_title="IDBDC – Explorator",
        layout="wide"
    )

    apply_style()

    gate()

    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

    supabase: Client = create_client(url, key)

    st.markdown(f"# {TITLE_MAIN}")
    st.caption(SUBTITLE_MAIN)

    st.divider()

    nav1, nav2 = st.columns([1.2,2])

    with nav1:

        categorie = st.selectbox(
            "Alege categorie documente",
            list(CATEGORII.keys())
        )

    tip = None
    base_table = None

    if categorie == "Contracte & Proiecte":

        with nav2:

            tip = st.selectbox(
                "Tip contract / proiect",
                list(CATEGORII[categorie]["tipuri"].keys())
            )

        base_table = CATEGORII[categorie]["tipuri"][tip]

    else:

        base_table = CATEGORII[categorie]["base_table"]

    st.info("Continuarea logicii Exploratorului rămâne identică cu versiunea ta actuală.")

    # restul codului Explorator rămâne neschimbat


if __name__ == "__main__":
    run()
