import streamlit as st

# --- DATE OFICIALE ---
mapping_specialisti = {
    "RESP01": "ioana", "RESP02": "anamaria", "RESP03": "adina",
    "RESP04": "andreia", "RESP05": "vio", "RESP06": "anca",
    "RESP07": "claudia", "RESP08": "agi", "RESP09": "eugen"
}

def get_friendly_name(cod):
    nume_raw = mapping_specialisti.get(cod.upper(), "Specialist")
    return nume_raw.capitalize()

# --- BARIERA 1: DESIGN ȘI LOGARE ---
if "autentificat_site" not in st.session_state:
    st.session_state["autentificat_site"] = False

if not st.session_state["autentificat_site"]:
    st.markdown("""
        <h1 style='text-align: center; color: #1E3A8A; font-size: 3rem; margin-bottom: 0.5rem;'>
            🛡️ Consola Responsabili IDBDC
        </h1>
    """, unsafe_allow_html=True)
    
    # i) LINK CĂTRE WEBSITE (Centrat sub titlu)
    st.markdown("<p style='text-align: center;'><a href='https://research.upt.ro' target='_blank' style='color: #2563EB; text-decoration: none;'>⬅️ Înapoi la Research UPT</a></p>", unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid #E5E7EB; margin-bottom: 2rem;'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<h3 style='text-align: center;'>Acces Restricționat</h3>", unsafe_allow_html=True)
        parola_introdusa = st.text_input("Introduceți parola de acces:", type="password")
        if st.button("🔓 Deschide Consola", use_container_width=True):
            if parola_introdusa == "EverDream2SZ":
                st.session_state["autentificat_site"] = True
                st.rerun()
            else:
                st.error("Parolă incorectă!")
    st.stop()

# --- BARIERA 2: LOGARE SPECIALIST (După ce treci de poartă) ---
st.sidebar.title("👤 Profil Specialist")
cod_input = st.sidebar.text_input("Cod Identificare").upper()

if cod_input in mapping_specialisti:
    nume_fain = get_friendly_name(cod_input)
    st.sidebar.success(f"Salut, {nume_fain}!")
    
    # ii) UNDE ACCESEZI MAI DEPARTE?
    st.markdown(f"# 🤝 Bine ai venit, **{nume_fain}**!")
    st.write("---")
    
    # Panoul de lucru (Filtrarea în cascadă)
    st.subheader("🛠️ Spațiu de Lucru")
    
    col_a, col_b = st.columns(2)
    with col_a:
        categorie = st.selectbox("1. Alege Categoria:", ["Contracte & Proiecte", "Proprietate Intelectuală", "Evenimente"])
    
    with col_b:
        # Aici punem cele 8 tabele discutate
        tabel = st.selectbox("2. Selectează Tabelul:", [
            "base_proiecte_fdi", "base_proiecte_internationale", 
            "base_proiecte_pnrr", "base_contracte_terti", 
            "base_proiecte_pncdi", "base_proiecte_interreg", 
            "base_proiecte_noneu", "base_contracte_cep"
        ])

    st.info(f"Sistemul este gata să încarce datele din **{tabel}** unde responsabil este **{cod_input}**.")
    
    # Buton pentru activare tabel
    if st.button(f"🔍 Încarcă Date {nume_fain}"):
        st.write(f"Aici va apărea tabelul tău filtrat pentru {tabel}...")

elif cod_input != "":
    st.sidebar.error("Cod neautorizat!")
