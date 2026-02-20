import streamlit as st
import psycopg2
import pandas as pd

def connect_db():
    try:
        return psycopg2.connect(
            host="ADRESA_HOST",
            database="NUME_BAZA_DATE",
            user="UTILIZATOR",
            password="PAROLA"
        )
    except Exception as e:
        st.error(f"Eroare de conexiune: {e}")
        return None

def main():
    st.set_page_config(page_title="Interfață IDBDC", layout="wide")
    
    # Titlul și antetul conform Protocolului de Lucru IDBDC
    st.title("Interfață IDBDC")
    st.markdown("---")
    
    conn = connect_db()
    
    if conn:
        st.success("Conexiune stabilă cu baza de date.")
        
        # Aici se va implementa logica pentru cod_identificare 
        # și legătura cu cod_inregistrare din base_proiecte_fdi
        
        # Exemplu de placeholder pentru interogare:
        # query = "SELECT * FROM base_proiecte_fdi"
        # df = pd.read_sql(query, conn)
        # st.dataframe(df)
        
        conn.close()
    else:
        st.warning("Așteptare configurare corectă parametri conexiune.")

if __name__ == "__main__":
    main()
