# =========================================================
# IDBDC/calea2_admin/ui.py
# VERSIUNE: 1.0
# STATUS: NOU - copie independentă, elimină dependența de admin/ui.py
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Funcții UI pentru Calea2 (noua structură modulară).
#   Copie independentă din admin/ui.py v1.3 — calea2_admin/
#   nu mai depinde de folderul admin/ (vechea structură).
#   Modificările în admin/ui.py nu afectează noua structură.
# =========================================================

import streamlit as st


def apply_admin_styles():
    st.markdown(
        """
        <style>
            .info-box {
                padding: 1.2rem;
                border-radius: 8px;
                margin-bottom: 1.5rem;
                border: 1px solid rgba(255,255,255,0.1);
            }
            .blue-box { background-color: rgba(11, 42, 82, 0.5); }
            .section-title {
                color: #ffffff;
                font-weight: bold;
                margin-bottom: 0.8rem;
                border-bottom: 1px solid #4a90e2;
                padding-bottom: 4px;
            }
            [data-testid="stDataEditor"] {
                background-color: white;
                border-radius: 4px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def display_admin_message():
    """Afișează mesajele de succes/eroare din session_state."""
    if "admin_msg" in st.session_state:
        msg_type, msg_text = st.session_state["admin_msg"]
        if msg_type == "success":
            st.markdown(
                f"""
                <div style='background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.45);
                border-radius:10px;padding:10px 16px;margin-bottom:12px;display:inline-block;'>
                <span style='color:#4ade80;font-weight:700;font-size:0.95rem;'>
                ✅ {msg_text}
                </span></div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.error(msg_text)
        del st.session_state["admin_msg"]
