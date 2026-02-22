import streamlit as st

# ==========================================
# 1. CONFIGURARE & STIL (STABILIT ȘI ÎNGHEȚAT)
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="centered")

st.markdown("""
    <style>
    .eroare-idbdc {
        color: white; background-color: #FF4B4B; 
        padding: 12px; border-radius: 8px; 
        text-align: center; font-weight: bold;
        width: 100%; display: block; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

if 'autorizat_p1' not in st.session_state:
    st.session_state.autorizat_p1 = False
if 'identificat_p2' not in st.session_state:
    st.session_state.identificat_p2 = False

# ==========================================
# 2. ANTET (CONFORM PROTOCOLULUI IDBDC)
# ==========================================
st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🛡️</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; margin-top: 0; margin-bottom: 0;'>Sistemul de Gestiune IDBDC</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; margin-top: 0; font-weight: normal;'>Universitatea Politehnica Timișoara</h3>", unsafe_allow_html=True)
st.write("---")

# ==========================================
# 3. LOGICA PORȚILOR (MODULARĂ)
# ==========================================

# --- POARTA 1: AUTORIZARE (ÎNGHEȚATĂ) ---
if not st.session_state.autorizat_p1:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("**Poarta 1: Autorizare Acces**")
        parola_p1 = st.text_input(
            "Parola", 
            type="password", 
            label_visibility="collapsed",
            autocomplete="new-password",
            key="p1_pass",
            help=None
        )
        if st.button("Verifică Poarta 1", use_container_width=True):
            if parola_p1 == "UPT_IDBDC_2026":
                st.session_state.autorizat_p1 = True
                st.rerun()
            else:
                st.markdown("<div class='eroare-idbdc'>ACCES NEAUTORIZAT! Verificați parola.</div>", unsafe_allow_html=True)

# --- POARTA 2: IDENTIFICARE (ZIDUL NOU) ---
elif st.session_state.autorizat_p1 and not st.session_state.identificat_p2:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.success("✅ Poarta 1: Autorizat")
        st.write("**Poarta 2: Identificare (cod_identificare)**")
        
        cod_id = st.text_input(
            "Identitate", 
            label_visibility="collapsed",
            placeholder="Introduceți cod_identificare...",
            key="p2_cod",
            autocomplete="off"
        )
        
        if st.button("Confirmă Identificarea", use_container_width=True):
            if cod_id:
                st.session_state.identificat_p2 = True
                st.session_state.user_cod = cod_id
                st.rerun()
            else:
                st.warning("Introduceți un cod pentru a continua.")

# --- INTERFAȚA DE LUCRU (CE URMEAZĂ) ---
else:
    st.success(f"Sistem IDBDC activ | Utilizator: **{st.session_state.user_cod}**")
    
    if st.sidebar.button("Reset / Ieșire"):
        st.session_state.autorizat_p1 = False
        st.session_state.identificat_p2 = False
        st.rerun()
    
    st.write("Aici vom implementa legătura cu `base_proiecte_fdi` prin `cod_inregistrare`.")
