# =========================================================
# IDBDC/domenii/_baza/echipa.py
# VERSIUNE: 3.3
# STATUS: FINISAT - Corectat NameError (resultado -> rezultat)
# DATA: 2026.06.09
# =========================================================

import streamlit as st


@st.cache_data(show_spinner=False, ttl=600)
def _fetch_persoane(_supabase):
    try:
        res = _supabase.table("det_resurse_umane").select(
            "nume_prenume,email,telefon_mobil,telefon_fix,acronim_departament"
        ).order("nume_prenume").execute()
        return res.data or []
    except Exception:
        return []


@st.cache_data(show_spinner=False, ttl=600)
def _fetch_departamente(_supabase):
    try:
        res = _supabase.table("nom_departament").select(
            "acronim_departament,denumire_departament"
        ).execute()
        return {
            r["acronim_departament"]: r["denumire_departament"]
            for r in (res.data or []) if r.get("acronim_departament")
        }
    except Exception:
        return {}


def _build_info_map(persoane_data, dep_map):
    info_map = {}
    for p in persoane_data:
        n = p.get("nume_prenume", "")
        if not n:
            continue
        acronim = p.get("acronim_departament", "")
        dep_fullname = dep_map.get(acronim, acronim) if acronim else ""
        
        parts = []
        if p.get("email"):
            parts.append(p["email"])
        if p.get("telefon_mobil"):
            parts.append(p["telefon_mobil"])
        elif p.get("telefon_fix"):
            parts.append(p["telefon_fix"])
            
        contact_str = " | ".join(parts)
        info_map[n] = {
            "departament": f"{acronim} - {dep_fullname}" if acronim else "",
            "telefon": p.get("telefon_mobil") or p.get("telefon_fix") or "",
            "email": p.get("email") or "",
            "contact_string": contact_str
        }
    return info_map


def render(supabase, cod_introdus, is_new, date_existente_lista=None):
    st.markdown(
        "<div style='background-color:#0b2a52; padding:8px 15px; border-radius:6px; margin-bottom:15px; margin-top:10px;'> "
        "<h3 style='margin:0; color:#ffffff; font-size:1.2rem;'>👥 COMPONENTĂ ECHIPĂ PROIECT</h3>"
        "</div>",
        unsafe_allow_html=True
    )

    persoane_data = _fetch_persoane(supabase)
    dep_map = _fetch_departamente(supabase)
    info_map = _build_info_map(persoane_data, dep_map)
    lista_nume_ru = [""] + list(info_map.keys())

    key_nr = f"pi_echipa_nr_{cod_introdus}"
    
    if key_nr not in st.session_state:
        if date_existente_lista and len(date_existente_lista) > 0:
            st.session_state[key_nr] = len(date_existente_lista)
            for idx, m in enumerate(date_existente_lista):
                st.session_state[f"echipa_{cod_introdus}_{idx}_nume"] = m.get("nume_prenume", "")
                st.session_state[f"echipa_{cod_introdus}_{idx}_rol"] = m.get("rol", "")
        else:
            st.session_state[key_nr] = 1

    nr_membri = st.session_state[key_nr]

    for idx in range(nr_membri):
        st.markdown(f"**Membru {idx + 1}**")
        col1, col2 = st.columns([60, 40])
        
        with col1:
            saved_nume = st.session_state.get(f"echipa_{cod_introdus}_{idx}_nume", "")
            idx_nume = 0
            if saved_nume in lista_nume_ru:
                idx_nume = lista_nume_ru.index(saved_nume)
            
            nume_sel = st.selectbox(
                "Nume și prenume",
                options=lista_nume_ru,
                index=idx_nume,
                key=f"pi_ech_nume_sel_{cod_introdus}_{idx}"
            )
            st.session_state[f"echipa_{cod_introdus}_{idx}_nume"] = nume_sel
            
        with col2:
            saved_rol = st.session_state.get(f"echipa_{cod_introdus}_{idx}_rol", "")
            rol_sel = st.text_input(
                "Rol în contract/proiect",
                value=saved_rol,
                key=f"pi_ech_rol_in_{cod_introdus}_{idx}"
            )
            st.session_state[f"echipa_{cod_introdus}_{idx}_rol"] = rol_sel

        if nume_sel and nume_sel in info_map:
            info = info_map[nume_sel]
            parts = []
            if info["departament"]:
                parts.append(f"🏢 {info['departament']}")
            if info["email"]:
                parts.append(f"✉️ {info['email']}")
            if info["telefon"]:
                parts.append(f"📞 {info['telefon']}")
            if parts:
                st.markdown(
                    "<div style='background:rgba(255,255,255,0.06);border-radius:6px;padding:5px 12px;margin-top:2px;font-size:0.84rem;color:rgba(255,255,255,0.80);'>"
                    + "  &nbsp;·&nbsp;  ".join(parts) +
                    "</div>",
                    unsafe_allow_html=True,
                )

        if idx < nr_membri - 1:
            st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.10);margin-top:8px;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    if st.button("➕ Adaugă membru", key=f"add_membru_{cod_introdus}"):
        st.session_state[key_nr] += 1
        st.rerun()

    rezultat = []
    for idx in range(nr_membri):
        n = str(st.session_state.get(f"echipa_{cod_introdus}_{idx}_nume", "") or "").strip()
        if not n:
            continue
        r = str(st.session_state.get(f"echipa_{cod_introdus}_{idx}_rol", "") or "").strip()
        rezultat.append({"nume_prenume": n, "rol": r})

    return resultado if 'resultado' in locals() else rezultat
