import streamlit as st

# Configurare pagină
st.set_page_config(page_title="IDBDC UPT", layout="centered")

# i) Titlul: Universitatea Politehnica Timișoara pe un singur rând
st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🛡️</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; margin-top: 0; margin-bottom: 0;'>Sistemul de Gestiune IDBDC</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; margin-top: 0; font-weight: normal;'>Universitatea Politehnica Timișoara</h3>", unsafe_allow_html=True)
st.write("---")

# Definirea parolei (exemplu)
PAROLA_CORECTA = "secret123"

col1, col2, col3 = st.columns([1, 1.5, 1])

with col2:
    st.write("Introduceți Parola de Acces:")
    
    # iii) Eliminarea sugestiilor browserului (autocomplete="new-password")
    # și a oricărui text de ajutor (help=None)
    parola_introdusa = st.text_input(
        "Parola", 
        type="password", 
        label_visibility="collapsed",
        autocomplete="new-password",
        key="password_input",
        help=None
    )
    
    buton_acces = st.button("Autentificare", use_container_width=True)

# ii) Mesajul de acces neautorizat - Puternic vizual (Roșu, un singur rând)
if buton_acces:
    if parola_introdusa == PAROLA_CORECTA:
        st.success("Acces permis! Se încarcă baza de date IDBDC...")
        # Aici va urma logica de încărcare a fișierelor
    else:
        st.markdown(
            "<p style='color: white; background-color: #FF4B4B; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold;'>"
            "ACCES NEAUTORIZAT! Vă rugăm să verificați parola și să încercați din nou."
            "</p>", 
            unsafe_allow_html=True
        )
