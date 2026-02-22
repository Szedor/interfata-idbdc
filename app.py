# ==========================================
# 2. POARTA 1: ACCES SISTEM (ECRAN CENTRAL)
# ==========================================
if not st.session_state.autorizat_p1:
    # Centrare logo/simbol
    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🛡️</h1>", unsafe_allow_html=True)
    
    # Titlurile ierarhice
    st.markdown("<h2 style='text-align: center; margin-top: 0;'>Sistemul de Gestiune IDBDC</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #555;'>Universitatea Politehnica Timișoara</h3>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #CC0000;'>Acces restricționat</h4>", unsafe_allow_html=True)
    
    st.write("") # Spațiu gol

    # Creăm coloane pentru a îngusta caseta (0.5 + 1 + 0.5 = 2, deci coloana centrală e 50% din lățime)
    # Putem ajusta raportul [1, 0.8, 1] pentru o casetă și mai scurtă
    col_stanga, col_centru, col_dreapta = st.columns([1.2, 0.6, 1.2])
    
    with col_centru:
        st.write("Introduceți parola de acces:")
        parola_introdusa = st.text_input("Parola", type="password", label_visibility="collapsed", key="p1_pass")
        
        # Buton de validare (va avea aceeași lățime cu caseta)
        if st.button("Autorizare acces", use_container_width=True):
            if parola_introdusa == "EverDream2SZ":
                st.session_state.autorizat_p1 = True
                st.rerun()
            else:
                st.markdown("<div class='eroare-idbdc'>⚠️ Parolă incorectă.</div>", unsafe_allow_html=True)
    
    st.stop()
