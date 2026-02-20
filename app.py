import streamlit as st
import psycopg2

# 1. ZONA DE DEFINIȚII (Aici "învățăm" programul ce să facă)
def connect_db():
    return psycopg2.connect(
        host="host_ul_tau",
        database="nume_db",
        user="utilizator",
        password="parola"
    )

# 2. ZONA DE EXECUȚIE (Aici îi spunem să afișeze efectiv pe ecran)
# Aceasta este partea care trebuie să fie "la final", sub funcție
st.title("Sistem IDBDC")
st.subheader("Gestionare Proiecte FDI")

# Apelăm funcția definită mai sus
try:
    conn = connect_db()
    st.success("Conexiunea la baza de date este activă!")
    
    # Aici vom adăuga ulterior logica pentru cod_identificare
    # și legătura cu cod_inregistrare din base_proiecte_fdi
    
except Exception as e:
    st.error(f"Nu am putut conecta baza de date: {e}")
