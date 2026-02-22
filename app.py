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
# 3. LOGICA DE ACCES (AUTORIZARE ȘI IDENTIFICARE)
# ==========================================

# --- ETAPA 1: AUTORIZARE ACCES ---
if not st.session_state.autorizat_p1:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("Parola pentru autorizare acces")
        parola_p1 = st.text_input(
            "Parola", 
            type="password", 
            label_visibility="collapsed",
            autocomplete="new-password",
            key="p1_pass",
            help=None
        )
        # NOUA PAROLĂ FIXATĂ: EverDream2SZ
        if st.button("Autorizare acces", use_container_width=True):
            if parola_p1 == "EverDream2SZ":
                st.session_state.autorizat_p1 = True
                st.rerun()
            else:
                st.markdown(
                    "<div class='eroare-idbdc'>"
                    "⚠️ Acces Neautorizat: Parola nu corespunde sistemului IDBDC."
                    "</div>", 
                    unsafe_allow_html=True
                )

# --- ETAPA 2: IDENTIFICARE INDIVIDUALĂ ---
elif st.session_state.autorizat_p1 and not st.session_state.identificat_p2:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.success("✅ Autorizare reușită.")
        st.write("Introduceți cod_identificare pentru acces date")
        
        cod_id = st.text_input(
            "Identitate", 
            label_visibility="collapsed",
            placeholder="cod_identificare...",
            key="p2_cod",
            autocomplete="off"
        )
        
        if st.button("Confirmă Identitatea", use_container_width=True):
            if cod_id:
                st.session_state.identificat_p2 = True
                st.session_state.user_cod = cod_id
                st.rerun()
            else:
                st.warning("Vă rugăm să introduceți codul de identificare.")

# --- INTERFAȚA DE LUCRU IDBDC ---
else:
    st.success(f"Utilizator identificat: **{st.session_state.user_cod}**")
    
    if st.sidebar.button("Ieșire / Reset"):
        st.session_state.autorizat_p1 = False
        st.session_state.identificat_p2 = False
        st.rerun()
    
    st.info("Sistemul este pregătit pentru prelucrarea datelor din 'base_proiecte_fdi'.")
