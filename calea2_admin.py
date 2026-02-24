# 1. TOOLBAR SUPERIOR (Doar 2 butoane)
        c_btn1, c_btn2, _ = st.columns([1, 1, 5])
        
        with c_btn1:
            st.button("➕ NOU", type="primary", use_container_width=True) # Iconiță colorată specific
        
        with c_btn2:
            # Editarea se activează doar dacă avem un proiect selectat
            edit_activ = 'proiect_de_lucru' in st.session_state and st.session_state.proiect_de_lucru is not None
            btn_edit = st.button("📝 EDITARE", use_container_width=True, disabled=not edit_activ)

        # 2. TABELA (unde click-ul pe linie face magia)
        # (Logica de on_select="rerun" rămâne aici pentru a detectat selecția)

        # 3. OPȚIUNI DE INTERVENȚIE (Apar doar la click pe EDITARE)
        if edit_activ and btn_edit:
            st.markdown("""
                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 2px solid #ffaa00;">
                    <h4 style="color: #003366;">Intervenție Proiect: """ + st.session_state.proiect_de_lucru['cod_identificare'] + """</h4>
                </div>
            """, unsafe_allow_html=True)
            
            c_act, c_del, _ = st.columns([1.5, 1.5, 4])
            with c_act:
                st.button("🔄 ACTUALIZARE", use_container_width=True) # Culoare dedicată
            with c_del:
                st.button("🗑️ ȘTERGERE", use_container_width=True)   # Roșu critic
