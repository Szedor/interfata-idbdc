import streamlit as st


def render_admin_style():
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
            padding-top: 1.0rem;
            padding-bottom: 1.0rem;
          }
          .stRadio, .stToggle {
            margin-bottom: 0.2rem;
          }
          .stButton {
            margin-top: 0.2rem;
            margin-bottom: 0.2rem;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_admin_header(operator_identificat: str):
    st.markdown(
        f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {operator_identificat}</h3>",
        unsafe_allow_html=True,
    )


def render_divider():
    st.divider()


def render_action_selector():
    st.markdown("**Acțiune**")
    return st.radio(
        label="",
        options=["Modificare / completare fișă existentă", "Fișă nouă"],
        horizontal=True,
        label_visibility="collapsed",
    )


def render_spacing(height_px: int = 6):
    st.markdown(f"<div style='height:{height_px}px'></div>", unsafe_allow_html=True)
