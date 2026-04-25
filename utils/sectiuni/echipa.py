# =========================================================
# utils/sectiuni/echipa.py
# v.modul.3.0 - Rescris cu st.form, fără st.data_editor
# =========================================================

import streamlit as st

def render_echipa(supabase, cod_introdus, is_new, date_existente):
    """
    Versiune simplă, folosește st.form pentru a preveni rerun-urile intempestive.
    Datele de contact (departament, email, telefon) sunt afișate doar la salvare,
    nu în timpul editării.
    """
    
    # =========================================================
    # INCARCARE DATE PERSOANE
    # =========================================================
    try:
        res = supabase.table("det_resurse_umane").select(
            "nume_prenume"
        ).order("nume_prenume").execute()
        persoane_data = res.data or []
    except Exception as e:
        st.error(f"Eroare citire persoane: {e}")
        persoane_data = []

    persoane_lista = [""] + [p["nume_prenume"] for p in persoane_data if p.get("nume_prenume")]

    # =========================================================
    # INCARCARE DATE EXISTENTE SAU INITIALIZARE
    # =========================================================
    cheie_sesiune = f"echipa_form_{cod_introdus}"
    
    if cheie_sesiune not in st.session_state:
        if is_new or not date_existente:
            st.session_state[cheie_sesiune] = [
                {"nume": "", "rol": "", "contact": False}
                for _ in range(5)
            ]
        else:
            st.session_state[cheie_sesiune] = []
            for r in date_existente:
                st.session_state[cheie_sesiune].append({
                    "nume": r.get("nume_prenume", ""),
                    "rol": r.get("rol", ""),
                    "contact": bool(r.get("persoana_contact", False)),
                })
            while len(st.session_state[cheie_sesiune]) < 5:
                st.session_state[cheie_sesiune].append({"nume": "", "rol": "", "contact": False})

    # =========================================================
    # AFISARE FORMULAR
    # =========================================================
    with st.form(key=f"echipa_form_{cod_introdus}"):
        st.markdown("### 👥 Echipa proiectului")
        
        # Afișare rânduri existente
        membri = st.session_state[cheie_sesiune]
        nume_noi = []
        roluri_noi = []
        contact_noi = []
        
        for i, membru in enumerate(membri):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                nume = st.selectbox(
                    f"Nume membru {i+1}",
                    options=persoane_lista,
                    index=persoane_lista.index(membru["nume"]) if membru["nume"] in persoane_lista else 0,
                    key=f"nume_{cod_introdus}_{i}"
                )
            with col2:
                rol = st.text_input(
                    f"Rol {i+1}",
                    value=membru["rol"],
                    key=f"rol_{cod_introdus}_{i}"
                )
            with col3:
                contact = st.checkbox(
                    "Contact",
                    value=membru["contact"],
                    key=f"contact_{cod_introdus}_{i}"
                )
            nume_noi.append(nume)
            roluri_noi.append(rol)
            contact_noi.append(contact)
        
        # Buton adăugare rând nou
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            add_row = st.form_submit_button("➕ Adaugă membru")
        with col_btn2:
            submit = st.form_submit_button("💾 Salvează modificările", type="primary")
        
        if add_row:
            # Adaugă un rând nou în session_state
            st.session_state[cheie_sesiune].append({"nume": "", "rol": "", "contact": False})
            st.rerun()
        
        if submit:
            # Salvează modificările în session_state
            for i in range(len(membri)):
                st.session_state[cheie_sesiune][i]["nume"] = nume_noi[i]
                st.session_state[cheie_sesiune][i]["rol"] = roluri_noi[i]
                st.session_state[cheie_sesiune][i]["contact"] = contact_noi[i]
            st.success("✅ Modificările au fost salvate temporar. Apasă butonul principal SALVEAZĂ TOATE DATELE pentru a le salva definitiv.")
    
    # =========================================================
    # CONSTRUIRE REZULTAT PENTRU SALVARE DEFINITIVĂ
    # =========================================================
    rezultat = []
    for item in st.session_state[cheie_sesiune]:
        nume = item.get("nume", "").strip()
        if not nume:
            continue
        rezultat.append({
            "cod_identificare": cod_introdus,
            "nume_prenume": nume,
            "rol": item.get("rol", ""),
            "persoana_contact": item.get("contact", False),
            "functie_upt": "",
        })
    return rezultat
