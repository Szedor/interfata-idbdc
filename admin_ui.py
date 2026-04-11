# =========================================================
# IDBDC - MODUL ADMIN - INTERFAȚĂ VIZUALĂ (admin_ui.py)
# Versiune: 1.1 - Titluri toate tab-uri + corecție valoare financiară
# =========================================================

import streamlit as st

def apply_admin_styles():
    """Aplică stilul CSS specific pentru Calea 2 (Admin)."""
    st.markdown(
        """
        <style>
            /* Stil containere info */
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
            /* Ajustări tabele editor */
            [data-testid="stDataEditor"] {
                background-color: white;
                border-radius: 4px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_base_info_box():
    """Afișează titlul pentru tab-ul Date de bază."""
    st.markdown(
        """
        <div class="info-box blue-box">
            <div class="section-title">📋 DATE DE BAZĂ</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_financial_info_box(df_base):
    """Afișează titlul și valoarea totală pentru tab-ul Date financiare."""
    if df_base is None or df_base.empty:
        return

    row = df_base.iloc[0]
    val = row.get("valoare_totala_contract") or row.get("valoare_totala") or 0
    moneda = row.get("moneda", "RON") or "RON"

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
        unsafe_allow_html=True
    )

def render_team_info_box(count_membri):
    """Afișează titlul și numărul de membri pentru tab-ul Echipă."""
    st.markdown(
        f"""
        <div class="info-box blue-box">
            <div class="section-title">👥 ECHIPĂ PROIECT</div>
            <div>Membri identificați în tabelul de detaliu: <b>{count_membri}</b></div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_technical_info_box():
    """Afișează titlul pentru tab-ul Aspecte tehnice."""
    st.markdown(
        """
        <div class="info-box blue-box">
            <div class="section-title">🧪 ASPECTE TEHNICE</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def display_admin_message():
    """Afișează mesajele de succes/eroare din session_state."""
    if "admin_msg" in st.session_state:
        msg_type, msg_text = st.session_state["admin_msg"]
        if msg_type == "success":
            st.success(msg_text)
        else:
            st.error(msg_text)
        del st.session_state["admin_msg"]

def render_sidebar_info(operator, rol):
    """Afișează info operator în sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.success(f"👤 Operator: {operator}")
    st.sidebar.info(f"🔑 Rol: {rol}")
