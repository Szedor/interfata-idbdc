# =========================================================
# IDBDC/admin/ui.py
# VERSIUNE: 1.3
# STATUS: FUNCTIONAL
# DATA: 2026.04.28 
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


def render_base_info_box():
    st.markdown(
        """
        <div class="info-box blue-box">
            <div class="section-title">📋 DATE DE BAZĂ</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_financial_info_box(df_fin):
    val = 0
    moneda = "RON"
    if df_fin is not None and not df_fin.empty:
        row = df_fin.iloc[0]
        val    = row.get("valoare_totala_contract") or row.get("valoare_totala") or 0
        moneda = row.get("moneda") or "RON"
    try:
        val_fmt = f"{float(val):,.2f}"
    except (ValueError, TypeError):
        val_fmt = str(val)
    st.markdown(
        f"""
        <div class="info-box blue-box">
            <div class="section-title">💰 DATE FINANCIARE</div>
            <div style="font-size: 1.1rem;">
                Valoare Totală: <b>{val_fmt} {moneda}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_team_info_box(count_membri):
    st.markdown(
        f"""
        <div class="info-box blue-box">
            <div class="section-title">👥 ECHIPĂ PROIECT</div>
            <div>Membri identificați în tabelul de detaliu: <b>{count_membri}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_technical_info_box():
    st.markdown(
        """
        <div class="info-box blue-box">
            <div class="section-title">🧪 ASPECTE TEHNICE</div>
        </div>
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


def render_sidebar_info(operator, rol):
    st.sidebar.markdown("---")
    st.sidebar.success(f"👤 Operator: {operator}")
    st.sidebar.info(f"🔑 Rol: {rol}")
