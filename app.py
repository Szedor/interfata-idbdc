import streamlit as st
import psycopg2

def connect_db():
    try:
        # Aici trebuie să introduci datele tale reale de acces
        return psycopg2.connect(
            host="localhost", 
            database="nume_baza_date", 
            user="postgres", 
            password="parola"
        )
    except Exception as e:
        st.error(f"Eroare de conexiune la baza de date: {e}")
        return None

def main():
    # Revenire la aspectul minim stabilit: titlul simplu
    st.title("Interfață IDBDC")

    conn = connect_db()

    if conn:
        st.success("Conexiune stabilită.")
        
        # Aici se va face interogarea folosind cod_identificare 
        # legat de cod_inregistrare din base_proiecte_fdi
        
        conn.close()
    else:
        st.warning("⚠️ Serverul PostgreSQL nu a fost găsit. Verifică dacă serviciul este pornit.")

if __name__ == "__main__":
    main()
