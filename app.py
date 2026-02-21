import streamlit as st
import psycopg2

# Configurare vizuală IDBDC
st.set_page_config(page_title="Consola Responsabili IDBDC", layout="wide")
st.title("🛡️ Consola Responsabili IDBDC")

# --- DATELE TALE REALE DIN SUPABASE (CONFIGURATE) ---
DB_CONFIG = {
    "host": "db.zkkkirpggtczbdzqqlyc.supabase.co",
    "database": "postgres",
    "user": "postgres",
    "password": "23elf18SKY05!", # <--- PUNE PAROLA TA AICI
    "port": "5432"
}

# Gestionare Sesiune (Bariere)
if "autentificat" not in st.session_state:
    st.session_state["autentificat"] = False
if "operator_valid" not in st.session_state:
    st.session_state["operator_valid"] = None

# BARIERA 1: ACCES GENERAL (PAROLA SITE)
if not st.session_state["autentificat"]:
    st.subheader("Bariera 1: Acces General")
    parola_gen = st.text_input("Parola secretă IDBDC:", type="password")
    if st.button("Verifică"):
        if parola_gen == "EverDream2SZ": # Poți schimba această parolă oricând
            st.session_state["autentificat"] = True
            st.rerun()
        else:
            st.error("Parolă incorectă!")

# BARIERA 2: IDENTIFICARE OPERATOR (CONEXIUNE SQL)
elif st.session_state["operator_valid"] is None:
    st.subheader("🔑 Bariera 2: Identificare Operator")
    cod_input = st.text_input("Introduceți Codul de Acces Unic:", type="password")
    
    if st.button("Validare Operator"):
        try:
            # Conectare la baza de date centrală
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            # Verificăm dacă codul există în tabela com_operatori stabilită vineri
            cur.execute("SELECT nume_operator, filtru_categorie, filtru_proiect FROM com_operatori WHERE cod_acces = %s", (cod_input,))
            res = cur.fetchone()
            
            if res:
                st.session_state["operator_valid"] = {
                    "nume": res[0], 
                    "cat": res[1], 
                    "prj": res[2]
                }
                st.success("Acces Validat!")
                st.rerun()
            else:
                st.error("❌ Codul nu a fost găsit în baza de date IDBDC!")
            
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Eroare tehnică de conectare: {e}")

# INTERFAȚA DE LUCRU (DUPĂ VALIDARE)
else:
    op = st.session_state["operator_valid"]
    st.sidebar.success(f"Logat: {op['nume']}")
    st.sidebar.info(f"Proiect: {op['prj']}\nCategorie: {op['cat']}")
    
    st.header(f"Salut, {op['nume']}!")
    st.write("Sunteți conectat la Consola de Gestionare Cercetare.")
    st.write(f"Conform bazei de date, aveți acces la datele: **{op['prj']}**.")

    if st.sidebar.button("Log Out"):
        st.session_state["autentificat"] = False
        st.session_state["operator_valid"] = None
        st.rerun()
