import streamlit as st

# 1. Identitatea Vizuală
st.set_page_config(page_title="Consola Responsabili IDBDC", layout="wide")
st.title("🛡️ Consola Responsabili IDBDC")

# Inițializăm starea sesiunii pentru a nu cere parola la fiecare click
if "autentificat" not in st.session_state:
    st.session_state["autentificat"] = False

# --- PASUL 1: BARIERA DE PAROLĂ ---
if not st.session_state["autentificat"]:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.subheader("Acces Restricționat")
        parola = st.text_input("Introduceți parola de acces:", type="password")
        if st.button("Validare"):
            if parola == "UPT_CERCETARE_2026": # Poți schimba parola aici
                st.session_state["autentificat"] = True
                st.rerun()
            else:
                st.error("Parolă incorectă!")
else:
    # --- PASUL 2: IDENTIFICARE RESPONSABIL (Cei 9) ---
    st.sidebar.image("https://www.research.upt.ro/img/logo.png", width=150) # Dacă vrei logo-ul tău
    st.sidebar.header("Meniu Specialist")
    
    # Aici definim "Cravatele"
    responsabili_autorizati = ["ID001", "ID002", "ID003", "ID004", "ID005", "ID006", "ID007", "ID008", "ID009"]
    
    user_id = st.sidebar.text_input("Introduceți Cod Identificare Responsabil:")
    
    if user_id in responsabili_autorizati:
        st.sidebar.success(f"Autorizat: Responsabil {user_id}")
        
        # --- PASUL 3: NAVIGARE (Direcția 2) ---
        st.markdown("---")
        categorie = st.sidebar.selectbox("1. Categorie:", ["Contracte & Proiecte", "Proprietate Intelectuală", "Evenimente"])
        
        if categorie == "Contracte & Proiecte":
            baza_selectata = st.sidebar.selectbox("2. Sursă Date (Cele 8 baze):", [
                "base_proiecte_internationale", 
                "base_proiecte_fdi", 
                "base_proiecte_pnrr",
                "base_proiecte_pncdi",
                "base_contracte_terti",
                "base_proiecte_interreg",
                "base_proiecte_noneu",
                "base_contracte_cep"
            ])
            
            # --- AFIȘARE REZULTATE (Aici dispar cele 2 rânduri!) ---
            st.header(f"📂 Lucrați în: {baza_selectata}")
            
            # Aici vom injecta interogarea SQL care aduce toate miile de rânduri
            st.info("Sistemul este pregătit pentru interogarea totală a bazei de date.")
            
    elif user_id == "":
        st.sidebar.warning("Așteptare cod responsabil...")
    else:
        st.sidebar.error("Cod neautorizat! Accesul AI și Editarea sunt blocate.")

# Buton de Logout (pentru siguranță)
if st.session_state["autentificat"]:
    if st.sidebar.button("Ieșire (Logout)"):
        st.session_state["autentificat"] = False
        st.rerun()
