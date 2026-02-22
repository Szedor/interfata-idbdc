import streamlit as st

# Configurare pagină
st.set_page_config(page_title="IDBDC UPT", layout="wide")

# Afișare Titlu ales
st.markdown(f"<h1 style='text-align: center;'>Sistemul de Gestiune IDBDC | Universitatea Politehnica Timișoara</h1>", unsafe_allow_html=True)
st.write("---")

# Centrarea casetei de parolă (folosim 5 coloane, punem caseta în cea din mijloc pentru a fi scurtă)
st.write("") 
c1, c2, c3, c4, c5 = st.columns([2, 1, 2, 1, 2])

with c3:
    parola_introdusa = st.text_input(
        label="Introdu Parola de Acces:", 
        type="password", 
        help=None, # iii) Nu apare nimic la mouse-over
        label_visibility="visible"
    )
    
    # Buton de verificare
    if st.button("Accesează Poarta 1", use_container_width=True):
        if parola_introdusa == "EverDream2SZ":
            st.success("✅ Acces permis în sistem.")
            # Aici ne oprim. Nu am adăugat logica pentru Poarta 2 încă.
        else:
            # iv) Mesajul tău personalizat
            st.warning("⚠️ Acces Neautorizat: Parola nu corespunde sistemului IDBDC.")
