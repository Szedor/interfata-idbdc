# =========================================================
# utils/styling.py
# v.modul.1.1 - Corectii culori: font alb pentru taburi si sectiuni
# =========================================================

import streamlit as st

ACADEMIC_BLUE = "#0b2a52"

def apply_global_styles():
    """Aplică stilurile comune pentru toate modulele."""
    st.markdown(
        f"""
        <style>
            /* Fundal general */
            .stApp {{ background: {ACADEMIC_BLUE} !important; }}
            
            /* Container principal */
            div.block-container {{ padding-top: 1.1rem; padding-bottom: 1.0rem; max-width: 1550px; }}
            
            /* Culoare text general */
            label, .stMarkdown, .stCaption, .stText, p, span, div {{
                color: #ffffff !important;
            }}
            
            /* Tab-uri (st.tabs) - font alb */
            button[data-baseweb="tab"] {{
                color: #ffffff !important;
                font-weight: 600 !important;
            }}
            button[data-baseweb="tab"]:hover {{
                color: #ffcccc !important;
            }}
            button[data-baseweb="tab"][aria-selected="true"] {{
                color: #ff6666 !important;
                font-weight: 700 !important;
            }}
            
            /* Checkbox-uri si etichete sectiuni */
            .stCheckbox label, .stCheckbox span {{
                color: #ffffff !important;
            }}
            
            /* Input-uri text */
            .stTextInput > div > div, .stTextInput > div > div > input,
            .stTextInput input, .stTextInput input:hover, .stTextInput input:focus,
            .stSelectbox > div > div, .stSelectbox [data-baseweb="select"],
            .stMultiSelect > div > div, .stMultiSelect [data-baseweb="select"] > div {{
                background: #1a3a5c !important;
                color: #ffffff !important;
                border-radius: 10px !important;
                border: 1px solid rgba(255,255,255,0.30) !important;
            }}
            
            /* Placeholder-uri */
            .stTextInput input::placeholder {{
                color: rgba(255,255,255,0.70) !important;
            }}
            
            /* Butoane */
            .stButton > button {{
                border-radius: 10px !important;
                font-weight: 900 !important;
                background: rgba(255,255,255,0.96) !important;
                color: #0b1f3a !important;
                border: 1px solid rgba(255,255,255,0.55) !important;
            }}
            .stButton > button p {{
                color: #0b1f3a !important;
            }}
            
            /* Headings */
            h1, h2, h3, h4, h5, h6 {{
                color: #ffffff !important;
            }}
            
            /* Ascundere elemente Streamlit */
            [data-testid="stToolbar"] {{ display: none !important; }}
            [data-testid="stDecoration"] {{ display: none !important; }}
            #MainMenu {{ visibility: hidden !important; }}
            footer {{ visibility: hidden !important; }}
            header {{ visibility: hidden !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def hide_streamlit_chrome():
    """Ascunde elementele implicite Streamlit (header, footer, toolbar)."""
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
