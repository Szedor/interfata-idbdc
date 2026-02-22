import streamlit as st

# Configurare pagină
st.set_page_config(page_title="IDBDC UPT", layout="centered")

# i) Simbolul scutului și Titlul ales de tine
st.markdown("<h1 style='text-align: center;'>🛡️</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Sistemul de Gestiune IDBDC | Universitatea Politehnica Timișoara</h2>", unsafe_allow_html=True)
st.write("---")

# ii) & iii) Caseta de parolă optimizată
col1, col2, col3 = st.columns([1, 1, 1]) 

with col2:
    parola_introdusa = st.text_input(
        "Introduceți Parola de Acces:",
        type="password",
        help="" # Nu apare nimic la mouse-over
    )
    
    # iii) Butonul redenumit
    if st.button("Accesează aici"):
        if parola_introdusa == "EverDream2SZ":
            st.success(" ✅  Poarta 1: Acces Permis")
            # Aici se va deschide ulterior Poarta 2
        else:
            # iv) Mesajul tău personalizat pentru eroare
            st.warning(" ⚠️  Acces Neautorizat: Parola nu corespunde sistemului IDBDC.")
