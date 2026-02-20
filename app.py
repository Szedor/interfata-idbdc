import streamlit as st

# Titlul oficial stabilit de tine
st.set_page_config(page_title="Consola Responsabili IDBDC", layout="wide")
st.title("🛡️ Consola Responsabili IDBDC")

# --- BARIERA 1: PAROLA GENERALĂ ---
if "autentificat" not in st.session_state:
    st.session_state["autentificat"] = False

if not st.session_state["autentificat"]:
    parola = st.text_input("Introduceți parola secretă IDBDC:", type="password")
    if st.button("Accesează Consola"):
        if parola == "parola_aleasa_de_tine": # Schimbă cu parola reală
            st.session_state["autentificat"] = True
            st.rerun()
        else:
            st.error("Parolă incorectă!")
else:
    # --- BARIERA 2: CEI 9 RESPONSABILI ---
    st.sidebar.success("Conectat cu succes!")
    responsabil_id = st.sidebar.text_input("Cod Identificare Responsabil (Cravată):")
    
    # Lista celor 9 (o vom popula cu ID-urile reale)
    specialisti_upt = ["ID_RESP_1", "ID_RESP_2", "ID_RESP_3"] # etc...

    if responsabil_id in specialisti_upt:
        st.sidebar.info(f"Bun venit, Specialist {responsabil_id}!")
        
        # --- MENIUL DE NAVIGARE (Direcția 2) ---
        categorie = st.selectbox("Alegeți Categoria de Lucru:", 
                                ["Contracte & Proiecte", "Proprietate Intelectuală", "Evenimente"])
        
        if categorie == "Contracte & Proiecte":
            # Aici am inclus toate cele 8 baze de care ai vorbit
            baza_nume = st.selectbox("Selectați Baza de Date pentru Intervenție:", [
                "base_proiecte_internationale", 
                "base_proiecte_fdi", 
                "base_proiecte_pnrr",
                "base_proiecte_pncdi",
                "base_contracte_terti",
                "base_proiecte_interreg",
                "base_proiecte_noneu",
                "base_contracte_cep"
            ])
            
            st.write(f"### Lucrați în: {baza_nume}")
            st.info("Sistemul este gata să încarce miile de înregistrări...")
    else:
        st.warning("Vă rugăm să introduceți un Cod de Responsabil valid pentru a debloca baza de date.")
