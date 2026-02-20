import streamlit as st
import psycopg2
import pandas as pd

# CONFIGURARE ACCES IDBDC
# Înlocuiește valorile de mai jos cu datele tale reale de acces
DB_PARAMS = {
    "host": "localhost",
    "database": "nume_baza_date",
    "user": "utilizator",
    "password": "parola"
}

def connect_db():
    try:
        return psycopg2.connect(**DB_PARAMS)
    except Exception as e:
        st.error(f"Eroare de conexiune la baza de date: {e}")
        return None

def main():
    # Aspectul IDBDC stabilit anterior
    st.title("Interfață IDBDC")
    
    conn = connect_db()
    
    if conn:
        st.success("Conexiune stabilită.")
        
        # Logica de corelare cod_identificare (IDBDC) -> cod_inregistrare (base_proiecte_fdi)
        # Se va adăuga aici interogarea specifică
        
        conn.close()
    else:
        st.warning("⚠️ Serverul PostgreSQL nu a fost găsit. Verifică dacă serviciul este pornit și parametrii de host/port sunt corecți.")

if __name__ == "__main__":
    main()
