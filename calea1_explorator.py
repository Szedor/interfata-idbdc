import streamlit as st
from supabase import create_client

from config import Config
from tab1_fisa_completa import render_fisa_completa


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

    mesaj_blocare = "Această secțiune se află în faza de testare finală. Accesul va fi reactivat în curând. Vă mulțumim pentru înțelegere."

    tab1, tab2, tab3 = st.tabs(
        [
            "Fișă completă",
            "Explorare avansată (indisponibil temporar)",
            "Rapoarte și analiză (indisponibil temporar)",
        ]
    )

    with tab1:
        render_fisa_completa(supabase)

    with tab2:
        st.info(mesaj_blocare)
        st.markdown(
            f"""
            <div style='background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.22);
            border-radius:12px;padding:24px 20px;text-align:center;margin-top:20px;'>
                <span style='font-size:2rem;display:block;margin-bottom:12px;'>🔧</span>
                <span style='color:rgba(255,255,255,0.88);font-size:1.05rem;font-weight:500;'>
                    {mesaj_blocare}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab3:
        st.info(mesaj_blocare)
        st.markdown(
            f"""
            <div style='background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.22);
            border-radius:12px;padding:24px 20px;text-align:center;margin-top:20px;'>
                <span style='font-size:2rem;display:block;margin-bottom:12px;'>📊</span>
                <span style='color:rgba(255,255,255,0.88);font-size:1.05rem;font-weight:500;'>
                    {mesaj_blocare}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def run():
    try:
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    except Exception as e:
        st.error(f"Eroare la inițializarea conexiunii Supabase: {e}")
        return

    render_calea1_explorator(supabase)
