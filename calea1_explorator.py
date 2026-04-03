import streamlit as st
from supabase import create_client

from config import Config
from tab1_fisa_completa import render_fisa_completa
from tab2_explorare_avansata import render_tab2_explorare_avansata
from tab3_rapoarte_analiza import render_tab3_rapoarte_analiza


def render_calea1_explorator(supabase):
    st.markdown(
        """
        <div style='margin-bottom:1.2rem;'>
            <div style='font-size:2rem;font-weight:800;color:#ffffff;'>
                Calea 1 — Explorator
            </div>
            <div style='font-size:1rem;color:rgba(255,255,255,0.72);margin-top:0.35rem;'>
                Consultare individuală, explorare avansată și analiză agregată a bazei de date.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(
        [
            "Fișă completă",
            "Explorare avansată",
            "Rapoarte și analiză",
        ]
    )

    with tab1:
        render_fisa_completa(supabase)

    with tab2:
        render_tab2_explorare_avansata(supabase)

    with tab3:
        render_tab3_rapoarte_analiza(supabase)


def run():
    try:
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    except Exception as e:
        st.error(f"Eroare la inițializarea conexiunii Supabase: {e}")
        return

    render_calea1_explorator(supabase)
