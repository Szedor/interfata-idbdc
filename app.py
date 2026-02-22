# ==========================================
# POARTA 2: IDENTIFICARE OPERATOR (SIDEBAR)
# ==========================================
st.sidebar.markdown("<h1 style='text-align: center;'>🛡️👤</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-weight: bold;'>Identificare Operator</p>", unsafe_allow_html=True)

# Utilizăm coloana corectă: cod_acces
cod_introdus = st.sidebar.text_input("Cod Identificare", type="password")

if cod_introdus:
    # Verificăm operatorul în tabela com_operatori folosind coloana cod_acces
    res_op = supabase.table("com_operatori").select("nume_operator").eq("cod_acces", cod_introdus).execute()
    
    if res_op.data:
        st.session_state.operator_identificat = res_op.data[0]['nume_operator']
        st.sidebar.success(f"Salut, {st.session_state.operator_identificat}!")
    else:
        st.sidebar.error("Cod invalid!")
        st.session_state.operator_identificat = None
