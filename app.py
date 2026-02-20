import streamlit as st
import psycopg2
import pandas as pd

# CONFIGURARE PARAMETRI CONEXIUNE (Introdu datele tale aici)
DB_CONFIG = {
    "host": "localhost",          # Sau IP-ul serverului tău
    "database": "nume_baza_ta",   # Numele bazei de date
    "user": "postgres",           # Utilizatorul tău
    "password": "parola_ta"       # Parola ta
}

def connect_db():
    try:
        return psycopg2.connect(
            host=DB_CONFIG["host"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
    except Exception as e:
        # Mesaj tehnic pentru depanare, afișat doar dacă conexiunea eșuează
        st.error(f"Eroare de conexiune la baza de date: {e}")
        return None

def main():
    # Setări de pagină pentru un aspect curat, conform IDBDC
    st.set_page_config(page_title="IDBDC - Gestiune Cercetare", layout="wide")
    
    st.title("Sistem IDBDC")
    st.subheader("Interogare și Dezvoltare Baze Date Cercetare")
    st.markdown("---")
    
    # Tentativă de conectare
    conn = connect_db()
    
    if conn:
        st.success("✅ Conexiune stabilită cu succes.")
        
        # ZONA DE OPERARE IDBDC
        # Aici vom integra logica pentru cod_identificare 
        # și legătura cu cod_inregistrare din base_proiecte_fdi
        
        st.info("Sistemul este gata pentru prelucrarea datelor din base_proiecte_fdi.")
        
        # Închidem conexiunea la finalul execuției
        conn.close()
    else:
        st.warning("⚠️ Atenție: Verificați parametrii de conectare în cod (Host, Database, User, Password).")

if __name__ == "__main__":
    main()
