def run():
    # ... (Conexiunea Supabase rămâne neschimbată) ...

    # 1. Stil Vizual Actualizat pentru diferențiere
    st.markdown("""
    <style>
        /* Fundalul general IDBDC */
        .stApp { background-color: #003366 !important; }
        
        /* Zona de Autentificare - Culoare complementară/mai deschisă pentru contrast */
        .auth-container {
            background-color: #1a4a7a; /* Un albastru mai deschis, mai puțin obositor */
            padding: 30px;
            border-radius: 10px;
            border: 1px solid #3d6e9e;
            margin-top: 50px;
        }
        
        .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label { color: white !important; }
        input { color: #000000 !important; background-color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

    # --- POARTA 1: PAROLA (Fostă Master) ---
    if not st.session_state.get('autorizat_p1', False):
        # Aplicăm zona vizuală distinctă pentru autentificare
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'> 🛡️ Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1, 1, 1])
        with col_ce:
            # Corecție punctul 1: Schimbare nume în 'Parola'
            parola_m = st.text_input("Parola:", type="password", key="p1_pass")
            if st.button("Autorizare acces", use_container_width=True):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
                else:
                    st.error("Parolă incorectă.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # --- POARTA 2: IDENTIFICARE OPERATOR ---
    # Aceasta rămâne în Sidebar, care are fundalul său separat
    # (Codul tău existent pentru operator...)
