# IDBDC - Stiluri comune
import streamlit as st

ACADEMIC_BLUE = "#0b2a52"

def apply_common_styles():
    st.markdown(
        f"""
        <style>
            .stApp {{ background: {ACADEMIC_BLUE} !important; }}
            div.block-container {{ padding-top: 1.1rem; padding-bottom: 1.0rem; max-width: 1550px; }}
            .stButton > button {{
                border-radius: 10px !important; font-weight: 900 !important;
                background: rgba(255,255,255,0.96) !important; color: #0b1f3a !important;
                border: 1px solid rgba(255,255,255,0.55) !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
