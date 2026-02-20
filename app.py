import streamlit as st
import psycopg2

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(page_title="Consola IDBDC", layout="wide")

# --- CONEXIUNE BAZĂ DE DATE ---
# Folosim datele tale de conectare (asigură-te că sunt setate în Secrets pe Streamlit Cloud)
def get_connection():
    return psycopg2.connect(
        host=st.secrets["postgres"]["host"],
        database=st.secrets["postgres"]["database"],
        user=st.secrets["postgres"]["user"],
        password=st.secrets["postgres"]["password"],
        port=st.secrets["postgres"]["port"]
    )

# --- LOGICA DE VERIFICARE OPERATOR ---
def verifica_operator_in_sql(cod_introdus):
    if not cod_introdus:
        return None
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Căutăm în coloana 'cod_acces' pe care am creat-o în SQL
        query = "SELECT nume_prenume FROM com_operatori WHERE cod_acces = %s"
        cur.execute(query, (cod_introdus,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        st.error(f"Eroare la conectarea cu baza de date: {e}")
        return None

# --- BARIERA 1: PAROLA GENERALĂ (EverDream2SZ) ---
if "autentificat_poarta1" not in st.session_state:
    st.session_state["autentificat_poarta1"] = False

if not st.session_state["autentificat_poarta1"]:
    st.title("🛡️ Acces Securizat IDBDC")
    parola_gen = st.text_input("Introduceți parola de sistem:", type="password")
    if st.button("Validare"):
        if parola_gen == "EverDream2SZ":
            st.session_state["autentificat_poarta1"] = True
            st.rerun()
        else:
            st.error("Parolă incorectă!")
else:
    # --- BARIERA 2: IDENTIFICARE SPECIALIST (RESP) ---
    st.sidebar.title("👤 Identificare")
    
    # Folosim type="password" pentru a ascunde codul și a preveni auto-complete-ul browserului
    cod_input = st.sidebar.text_input(
        "Cod Identificare", 
        type="password", 
        help="Introduceți codul personal (ex: RESP01)"
    ).upper()

    nume_operator = verifica_operator_in_sql(cod_input)

    if nume_operator:
        st.sidebar.success(f"Salut, {nume_operator}!")
        
        # --- AICI ÎNCEPE LUPTA CRUD ---
        st.title(f"Atelier de Lucru: {nume_operator}")
        st.write(f"Sunteți logat cu drepturi de validare și editare (CRUD).")
        
        # Exemplu de încărcare date pentru prima tabelă
        incarca_date = st.sidebar.button("🔄 Activează încărcarea datelor")
        
        if incarca_date:
            st.info("Datele sunt pregătite pentru validare...")
            # Aici vom insera formularul de editare pentru base_proiecte_fdi
            
    else:
        if cod_input:
            st.sidebar.error("Cod RESP neautorizat!")
        else:
            st.sidebar.info("Aștept codul de identificare...")
