import streamlit as st
import pandas as pd

# ==========================================
# 1. CONFIGURARE & SESIUNE (Păstrează starea)
# ==========================================
if 'autentificat' not in st.session_state:
    st.session_state.autentificat = False
if 'identificat' not in st.session_state:
    st.session_state.identificat = False

# ==========================================
# 2. ANTET VIZUAL (Conform Protocolului)
# ==========================================
st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>Sistemul de Gestiune IDBDC</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; margin-top: 0; font-weight: normal;'>Universitatea Politehnica Timișoara</h3>", unsafe_allow_html=True)
st.write("---")

# ==========================================
# POARTA 1: AUTORIZARE (Parola Generală)
# ==========================================
if not st.session_state.autentificat:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Poarta 1: Autorizare")
        parola = st.text_input("Parola Sistem:", type="password", autocomplete="new-password")
        if st.button("Verifică Accesul"):
            if parola == "UPT_IDBDC_2026": # Parola stabilită anterior
                st.session_state.autentificat = True
                st.rerun()
            else:
                st.error("ACCES NEAUTORIZAT!")

# ==========================================
# POARTA 2: IDENTIFICARE (Cod Identificare)
# ==========================================
elif st.session_state.autentificat and not st.session_state.identificat:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Poarta 2: Identificare")
        st.info("Sistemul este autorizat. Vă rugăm să vă identificați.")
        
        # Aici introducem codul care face legătura în IDBDC
        cod_id = st.text_input("Introduceți cod_identificare:", help="Codul unic de cercetător sau personal.")
        
        if st.button("Confirmă Identitatea"):
            if cod_id: # Aici putem adăuga o listă de coduri valide ulterior
                st.session_state.identificat = True
                st.session_state.user_cod = cod_id
                st.rerun()
            else:
                st.warning("Vă rugăm să introduceți un cod valid.")

# ==========================================
# INTERFAȚA DE LUCRU IDBDC (După ambele porți)
# ==========================================
else:
    st.success(f"Identificat cu succes: {st.session_state.user_cod}")
    st.sidebar.title("Meniu IDBDC")
    st.sidebar.write(f"Utilizator: **{st.session_state.user_cod}**")
    
    if st.sidebar.button("Log out / Reset"):
        st.session_state.autentificat = False
        st.session_state.identificat = False
        st.rerun()

    # Aici intervine legătura cu base_proiecte_fdi
    st.markdown("### Gestiune Date Cercetare")
    st.write("Sistemul este gata pentru interogarea bazei de date folosind `cod_inregistrare`.")
    
    # Placeholder pentru încărcarea fișierului FDI
    uploaded_file = st.file_uploader("Încarcă baza de date FDI (.csv sau .xlsx)", type=["csv", "xlsx"])
    
    if uploaded_file:
        st.write("Fișier detectat. Suntem gata pentru 'manevrele' pe date.")
