import streamlit as st
import pandas as pd

# 1. Denumirea oficială stabilită
st.title("🛡️ Consola Responsabili IDBDC")

# --- Aici va veni bariera de parolă și email (Cravata) ---

# 2. Selecția Categoriei Principale (Pasul 4 din planul nostru)
# Folosim nomenclatorul de categorii
categorie = st.selectbox("Selectați Categoria:", ["Contracte & Proiecte", "Proprietate Intelectuală", "Evenimente"])

if categorie == "Contracte & Proiecte":
    # 3. Selecția tabelei specifice (Cele 8 baze)
    # Aici rezolvăm problema vizibilității
    optiuni_tabele = {
        "Proiecte Internaționale (REALE)": "base_proiecte_internationale",
        "Proiecte FDI (TEST)": "base_proiecte_fdi",
        "Contracte Terți (TEST)": "base_contracte_terti",
        "Proiecte PNRR": "base_proiecte_pnrr"
    }
    
    selectie = st.radio("Alegeți baza de date pentru intervenție:", list(optiuni_tabele.keys()))
    tabela_sql = optiuni_tabele[selectie]

    # 4. Interogarea bazei de date fără LIMIT 2
    # Această funcție va rula în Supabase
    def incarca_date(nume_tabela):
        query = f"SELECT * FROM {nume_tabela}"
        # Aici se face conexiunea ta existentă la PostgreSQL
        return conexiune_supabase.query(query) 

    df = incarca_date(tabela_sql)

    # 5. Afișarea și numărarea rândurilor
    st.write(f"Sunt afișate {len(df)} înregistrări din {selectie}.")
    
    # Aici apare tabelul CRUD unde Responsabilul poate edita
    st.data_editor(df, key="editor_responsabili")
