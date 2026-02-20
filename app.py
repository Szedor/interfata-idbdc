import streamlit as st
# 1. Mai întâi definești variabila cu o valoare neutră
nume_operator = None 

# 2. Creezi câmpul de input în sidebar
cod_input = st.sidebar.text_input(
    "Cod Identificare", 
    type="password", 
    help="Introduceți codul RESP"
).upper()

# 3. Verifici codul (aici va veni interogarea SQL, dar pentru test poți folosi o condiție)
if cod_input == "RESP01":
    nume_operator = "Ioana"
elif cod_input == "RESP02":
    nume_operator = "Anamaria"

# 4. Abia acum poți folosi "if nume_operator:"
if nume_operator:
    st.sidebar.success(f"Salut, {nume_operator}!")
    # Restul codului tău pentru CRUD...
else:
    if cod_input:
        st.sidebar.error("Cod incorect!")
    else:
        st.info("Vă rugăm să introduceți codul de identificare în bara laterală.")
