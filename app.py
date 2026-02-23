# ==========================================
# CALEA 2: CONSOLA DE ADMINISTRARE (SPECIALIȘTI)
# ==========================================
elif calea_activa == "admin":
    # --- 1. CONFIGURARE STĂRI (Dacă nu există deja) ---
    if 'autorizat_p1' not in st.session_state:
        st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state:
        st.session_state.operator_identificat = None

    # --- 2. POARTA 1: ACCES MASTER ---
    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'>🛡️ Acces Restricționat IDBDC</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Introduceți parola de sistem pentru a activa consola.</p>", unsafe_allow_html=True)
        
        col_st, col_ce, col_dr = st.columns([1, 1, 1])
        with col_ce:
            parola_master = st.text_input("Parola Master", type="password", label_visibility="collapsed")
            if st.button("Autorizare", use_container_width=True):
                if parola_master == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
                else:
                    st.error("Parolă incorectă!")
        st.stop() # Încetează rularea dacă nu este autorizat P1

    # --- 3. POARTA 2: IDENTIFICARE OPERATOR (SIDEBAR) ---
    st.sidebar.markdown("### 👤 Identificare Operator")
    if not st.session_state.operator_identificat:
        cod_op = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod_admin")
        if cod_op:
            try:
                # Verificăm în tabela com_operatori după cod_operatori
                res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_op).execute()
                if res_op.data:
                    st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                    st.rerun()
                else:
                    st.sidebar.error("Cod invalid!")
            except Exception as e:
                st.sidebar.error(f"Eroare DB: {e}")
        st.stop() # Încetează rularea până se identifică operatorul
    else:
        st.sidebar.success(f"Operator: {st.session_state.operator_identificat}")
        if st.sidebar.button("Ieșire / Reset"):
            st.session_state.clear()
            st.rerun()

    # --- 4. PANOU DE LUCRU ADMIN (După trecerea ambelor porți) ---
    st.markdown(f"## 🛠️ Consola de Administrare: {st.session_state.operator_identificat}")
    st.write("---")
    
    st.info("Aici urmează modulele de tip CRUD (Adăugare/Editare date).")
    
    # Aici vom pune logica de tip "Alege tabelul pentru editare"
