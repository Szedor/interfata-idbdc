import streamlit as st
import psycopg2

# Funcție care verifică în SQL cine este operatorul
def verifica_operator(cod_introdus):
    try:
        cur = conn.cursor()
        cur.execute("SELECT nume_prenume FROM com_operatori WHERE cod_acces = %s", (cod_introdus,))
        result = cur.fetchone()
        return result[0] if result else None
    except:
        return None

# Bariera 2 (Sidebar)
cod_input = st.sidebar.text_input("Cod Identificare", type="password").upper()
nume_operator = verifica_operator(cod_input)

if nume_operator:
    st.sidebar.success(f"Salut, {nume_operator}!")
    # Aici începe CRUD
else:
    if cod_input:
        st.sidebar.error("Cod incorect!")
