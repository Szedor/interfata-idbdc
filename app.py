import streamlit as st

# Configurare pagină
st.set_page_config(page_title="IDBDC UPT", layout="centered")

# i) Simbolul și Titlul structurat pe două rânduri exacte
st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🛡️</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; margin-top: 0; margin-bottom: 0;'>Sistemul de Gestiune IDBDC</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; margin-top: 0; font-weight: normal;'>Universitatea Politehnica Timișoara</h3>", unsafe_allow_html=True)
st.write("---")

# ii) & iii) Caseta de parolă fără elemente de distragere
col1, col2, col3 = st.columns([1, 1.5, 1]) 

with col2:
    st.write("Introduceți Parola de Acces:")
    parola_introdusa = st.text_input(
        "Parola", 
        type="password", 
        help=None, 
        label_visibility="collapsed" # Elimină eticheta și minimizează interacțiunea vizuală
    )
    
    # Butonul redenumit
    if st.button("Accesează aici", use_container_width=True):
        if parola_introdusa == "EverDream2SZ":
            st.success(" ✅  Poarta 1: Acces Permis")
        else:
            # Mesaj de eroare roșu, pe un singur rând
            st.error("⚠️ Acces Neautorizat: Parola nu corespunde sistemului IDBDC.")
