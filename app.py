# ==========================================
# POARTA 2: IDENTIFICARE OPERATOR (SIDEBAR 1/8)
# ==========================================
st.sidebar.markdown("<h1 style='text-align: center;'>🛡️👤</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-weight: bold;'>Identificare Operator</p>", unsafe_allow_html=True)

cod_introdus = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod")

if cod_introdus:
    try:
        # Corecție conform sugestiei DB: cod_operatori (cu 'i' la final)
        res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_introdus).execute()
        
        if res_op.data:
            st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
            st.sidebar.success(f"Salut, {st.session_state.operator_identificat}!")
        else:
            st.sidebar.error("Cod operator invalid!")
            st.session_state.operator_identificat = None
    except Exception as e:
        st.sidebar.error(f"Eroare DB: {e}")
