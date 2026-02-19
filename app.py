import streamlit as st

# --- LOGICA DE MAPPING (Rămâne neschimbată și corectă) ---
mapping_specialisti = {
    "RESP01": "ioana", "RESP02": "anamaria", "RESP03": "adina",
    "RESP04": "andreia", "RESP05": "vio", "RESP06": "anca",
    "RESP07": "claudia", "RESP08": "agi", "RESP09": "eugen"
}

def get_friendly_name(cod):
    nume_raw = mapping_specialisti.get(cod.upper(), "Specialist")
    return nume_raw.capitalize()

# --- RECONSTRUCȚIE DESIGN (Restaurarea Titlului) ---

if "autentificat_site" not in st.session_state:
    st.session_state["autentificat_site"] = False

if not st.session_state["autentificat_site"]:
    # Aceasta este partea care a dispărut: Titlul mare, stilizat și centrat
    st.markdown("""
        <h1 style='text-align: center; color: #1E3A8A; font-size: 3rem; margin-bottom: 0.5rem;'>
            🛡️ Consola Responsabili IDBDC
        </h1>
        <p style='text-align: center; color: #6B7280; font-size: 1.2rem; margin-bottom: 2rem;'>
            Sistem Integrat de Gestiune a Bazelor de Date Cercetare
        </p>
        <hr style='border: 1px solid #E5E7EB; margin-bottom: 3rem;'>
    """, unsafe_allow_html=True)

    # Centrarea casetei de login
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("<h3 style='text-align: center;'>Acces Restricționat</h3>", unsafe_allow_html=True)
        parola_introdusa = st.text_input("Introduceți parola de acces:", type="password", help="Contactați administratorul pentru acces.")
        
        if st.button("🔓 Deschide Consola", use_container_width=True):
            if parola_introdusa == "EverDream2SZ":
                st.session_state["autentificat_site"] = True
                st.rerun()
            else:
                st.error("Parolă incorectă!")
    st.stop()

# --- RESTUL CONSOLEI (După logare) ---
st.sidebar.title("Meniu Specialist")
cod_input = st.sidebar.text_input("Cod Identificare").upper()

if cod_input in mapping_specialisti:
    nume_fain = get_friendly_name(cod_input)
    st.sidebar.success(f"Salut, {nume_fain}!")
    st.markdown(f"# 🤝 Bine ai venit, **{nume_fain}**!")
