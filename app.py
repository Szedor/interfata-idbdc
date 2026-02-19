import streamlit as st

# --- DATE OFICIALE (tabel_responsabili.csv) ---
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
    st.markdown("<h1 style='text-align: center; color: #1E3A8A; font-size: 3rem; margin-bottom: 0.5rem;'>🛡️ Consola Responsabili IDBDC</h1>", unsafe_allow_html=True)
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

# --- BARIERA 2: LOGARE SPECIALIST ---
st.sidebar.title("👤 Profil Specialist")
cod_input = st.sidebar.text_input("Cod Identificare").upper()

if cod_input in mapping_specialisti:
    nume_fain = get_friendly_name(cod_input)
    st.sidebar.success(f"Salut, {nume_fain}!")
    
    st.markdown(f"# 🤝 Bine ai venit, **{nume_fain}**!")
    st.write("---")
    
    # --- SPAȚIU DE LUCRU (CRUD) ---
    st.subheader("🛠️ Spațiu de Lucru")
    
    col_a, col_b = st.columns(2)
    with col_a:
        # i) Corecție: Evenimente științifice
        categorie = st.selectbox("1. Alege Categoria:", ["Contracte & Proiecte", "Proprietate Intelectuală", "Evenimente științifice"])
    
    with col_b:
        # i) Corecție: Dacă nu e Contracte, lista e goală
        optiuni_tabel = []
        if categorie == "Contracte & Proiecte":
            optiuni_tabel = [
                "base_proiecte_fdi", "base_proiecte_internationale", 
                "base_proiecte_pnrr", "base_contracte_terti", 
                "base_proiecte_pncdi", "base_proiecte_interreg", 
                "base_proiecte_noneu", "base_contracte_cep"
            ]
        
        tabel_selectat = st.selectbox("2. Selectează Tabelul:", optiuni_tabel if optiuni_tabel else ["Fără tabele disponibile"])

    # ii) Corecție mesaj: Sistemul este pregatit... pentru Eugen.
    if optiuni_tabel:
        st.info(f"Sistemul este pregătit să încarce datele din **{tabel_selectat}** pentru **{nume_fain}**.")
        
        # iii) Corecție buton: Activeaza incarcarea datelor
        if st.button("🔄 Activează încărcarea datelor"):
            # iv) Rezolvare: Simulare încărcare (Aici vom pune codul SQL)
            st.success(f"Se interoghează baza de date PostgreSQL pentru tabelul {tabel_selectat}...")
            st.warning("Urmează afișarea tabelului cu funcțiile de Editare (Creion) și Ștergere.")
    else:
        st.warning(f"Momentan nu există tabele configurate pentru categoria '{categorie}'.")

elif cod_input != "":
    st.sidebar.error("Cod neautorizat!")
