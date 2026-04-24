# =========================================================
# utils/styling.py
# v.modul.1.2 - Corectii definitive pentru Calea1 si Calea2
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
            div.block-container {{ padding-top: 1.1rem; padding-bottom: 1.0rem; max-width: 1550px; }}
            
            /* Culoare text general */
            label, .stMarkdown, .stCaption, .stText, p, span, div, .stCheckbox label {{
                color: #ffffff !important;
            }}
            
            /* TAB-URI (st.tabs) - font ALB permanent */
            button[data-baseweb="tab"] {{
                color: #ffffff !important;
                font-weight: 600 !important;
                background-color: transparent !important;
            }}
            button[data-baseweb="tab"]:hover {{
                color: #ffcccc !important;
            }}
            button[data-baseweb="tab"][aria-selected="true"] {{
                color: #ff8888 !important;
                font-weight: 700 !important;
            }}
            
            /* Checkbox-uri */
            .stCheckbox label span {{
                color: #ffffff !important;
            }}
            
            /* Headings */
            h1, h2, h3, h4, h5, h6 {{
                color: #ffffff !important;
            }}
            
            /* Input-uri text generale */
            .stTextInput > div > div, .stTextInput input {{
                background-color: #1a3a5c !important;
                color: #ffffff !important;
                border-radius: 10px !important;
                border: 1px solid rgba(255,255,255,0.30) !important;
            }}
            .stTextInput input::placeholder {{
                color: rgba(255,255,255,0.70) !important;
            }}
            
            /* Dropdown-uri (Selectbox) */
            .stSelectbox > div > div {{
                background-color: #1a3a5c !important;
                border-radius: 10px !important;
                border: 1px solid rgba(255,255,255,0.30) !important;
            }}
            .stSelectbox [data-baseweb="select"] span {{
                color: #ffffff !important;
            }}
            .stSelectbox svg {{
                fill: #ffffff !important;
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

def apply_admin_styles():
    """Stiluri specifice pentru Calea2 (admin)."""
    st.markdown(
        """
        <style>
            /* Dropdown-uri in Sidebar - text negru pe fundal alb */
            .stSidebar .stSelectbox > div > div {
                background-color: #ffffff !important;
                border: 1px solid #cccccc !important;
            }
            .stSidebar .stSelectbox [data-baseweb="select"] span {
                color: #000000 !important;
            }
            .stSidebar .stSelectbox svg {
                fill: #000000 !important;
            }
            
            /* Input text in Sidebar - fundal alb, text negru */
            .stSidebar .stTextInput input {
                background-color: #ffffff !important;
                color: #000000 !important;
                border: 1px solid #cccccc !important;
            }
            .stSidebar .stTextInput input::placeholder {
                color: #888888 !important;
            }
            
            /* Input parola in Sidebar - ochi magic vizibil */
            .stSidebar .stTextInput input[type="password"] {
                background-color: #ffffff !important;
                color: #000000 !important;
                border: 1px solid #cccccc !important;
            }
            .stSidebar .stTextInput input[type="password"]::placeholder {
                color: #888888 !important;
            }
            
            /* Mesaj succes operator - latime deplina */
            .stSidebar .stSuccess {
                width: 100%;
                text-align: center;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
