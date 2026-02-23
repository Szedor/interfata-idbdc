# ==========================================
# CALEA 2: ADMINISTRARE
# ==========================================
elif calea_activa == "admin":
    # GESTIUNE SESIUNE - CORECTAT (Fără tăieri de cuvinte)
    if 'autorizat_p1' not in st.session_state: 
        st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: 
        st.session_state.operator_identificat = None

    # PAS 1: PAROLA MASTER (POARTA 1)
    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'>🛡️ Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola master:", type="password", key="p1_pass")
            if st.button("Autorizare acces", use_container_width=True):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
                else: 
                    st.markdown("<div class='eroare-idbdc'>⚠️ Parolă incorectă.</div>", unsafe_allow_html=True)
        st.stop()

    # PAS 2: IDENTIFICARE ECONOMIST (SIDEBAR)
    st.sidebar.markdown("### 👤 Identificare Operator")
    if not st.session_state.operator_identificat:
        # Legătura cu tabela com_operatori, coloana cod_operatori
        cod_in = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod_input")
        
        if cod_in:
            try:
                # Verificăm codul în baza de date
                res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_in).execute()
                
                if res_op.data and len(res_op.data) > 0:
                    st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                    st.rerun()
                else:
                    st.sidebar.error("Cod operator invalid!")
            except Exception as e:
                st.sidebar.error("Eroare tehnică la conexiunea cu baza de date.")
        st.stop()
    else:
        # INTERFAȚĂ DUPĂ LOGARE REUȘITĂ
        st.sidebar.success(f"Salut, {st.session_state.operator_identificat}!")
        if st.sidebar.button("Ieșire / Resetare"):
            st.session_state.clear()
            st.rerun()

    # PANOU DE LUCRU ADMIN (După Poarta 2)
    st.markdown(f"### 🛠️ Panou de Administrare: {st.session_state.operator_identificat}")
    st.write("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        try:
            res_c = supabase.table("nom_categorie").select("denumire_categorie").execute()
            l_cat = [i["denumire_categorie"] for i in res_c.data]
            cat_admin = st.selectbox("Selectați Categoria:", ["---"] + l_cat)
        except: 
            st.error("Eroare la încărcarea categoriilor din baza de date.")
    
    with col_b:
        if cat_admin == "Contracte & Proiecte":
            try:
                res_s = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                l_sub = [i["acronim_contracte_proiecte"] for i in res_s.data]
                st.selectbox("Tip contract/proiect:", ["---"] + l_sub)
            except: 
                st.error("Eroare la încărcarea tipurilor de proiecte.")
        else:
            st.selectbox("Tip:", ["---"], disabled=True)
