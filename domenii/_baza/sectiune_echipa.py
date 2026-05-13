# =========================================================
# IDBDC/domenii/_baza/sectiune_echipa.py
# VERSIUNE: 3.1
# STATUS: ACTUALIZAT - toate elementele pe un singur rând
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Secțiunea Echipă cu rânduri individuale per membru.
#
# MODIFICĂRI VERSIUNEA 3.1:
#   - Toate cele 4 elemente (Membru N, NUME ȘI PRENUME,
#     ROLUL ÎN ECHIPĂ, PERSOANĂ DE CONTACT) afișate
#     pe un singur rând.
#   - NUME ȘI PRENUME redus la 2/3, ROLUL ÎN ECHIPĂ
#     redus la 1/2 față de versiunea anterioară.
#   - Eticheta corectată: ROLUL ÎN ECHIPĂ (nu CONTRACT).
#   - Eliminată nota de subsol.
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
        den     = dep_map.get(acronim, "")
        mob     = p.get("telefon_mobil", "") or ""
        fix     = p.get("telefon_fix", "") or ""
        telefon = f"{mob} / {fix}" if mob and fix else mob or fix
        info_map[n] = {
            "dep":     f"{acronim} - {den}" if acronim and den else acronim,
            "email":   p.get("email", "") or "",
            "telefon": telefon,
        }
    return info_map


def render(supabase, cod_introdus, is_new, date_existente):
    persoane_data = _fetch_persoane(supabase)
    dep_map       = _fetch_departamente(supabase)
    info_map      = _build_info_map(persoane_data, dep_map)
    persoane_list = [""] + [p["nume_prenume"] for p in persoane_data if p.get("nume_prenume")]

    if not persoane_data:
        st.warning("⚠️ Nu s-au găsit persoane în tabela det_resurse_umane.")

    key_nr = f"echipa_nr_{cod_introdus}"
    if key_nr not in st.session_state:
        nr_init = max(5, len(date_existente) if date_existente else 5)
        st.session_state[key_nr] = nr_init

    if date_existente and not is_new:
        for idx, r in enumerate(date_existente):
            key_n = f"echipa_{cod_introdus}_{idx}_nume"
            key_r = f"echipa_{cod_introdus}_{idx}_rol"
            key_c = f"echipa_{cod_introdus}_{idx}_contact"
            if key_n not in st.session_state:
                st.session_state[key_n] = r.get("nume_prenume", "") or ""
            if key_r not in st.session_state:
                st.session_state[key_r] = r.get("rol", "") or ""
            if key_c not in st.session_state:
                st.session_state[key_c] = bool(r.get("persoana_contact", False))

    nr_membri = st.session_state[key_nr]

    for idx in range(nr_membri):
        key_n = f"echipa_{cod_introdus}_{idx}_nume"
        key_r = f"echipa_{cod_introdus}_{idx}_rol"
        key_c = f"echipa_{cod_introdus}_{idx}_contact"

        # Toate cele 4 elemente pe un singur rând
        # Proporții: etichetă(1) | nume(4) | rol(3) | bifa(2)
        col_lbl, col_nume, col_rol, col_contact = st.columns([1, 4, 3, 2])

        with col_lbl:
            st.markdown(
                f"<div style='color:rgba(255,255,255,0.60);font-size:0.78rem;"
                f"font-weight:700;padding-top:32px;'>"
                f"Membru {idx + 1}</div>",
                unsafe_allow_html=True,
            )

        with col_nume:
            nume_curent  = st.session_state.get(key_n, "")
            idx_selectat = persoane_list.index(nume_curent) if nume_curent in persoane_list else 0
            nume_ales = st.selectbox(
                "NUME ȘI PRENUME",
                options=persoane_list,
                index=idx_selectat,
                key=key_n,
            )

        with col_rol:
            st.text_input(
                "ROLUL ÎN ECHIPĂ",
                key=key_r,
            )

        with col_contact:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            st.checkbox(
                "⭐ PERSOANĂ DE CONTACT",
                key=key_c,
            )

        # Departament și contact sub rând
        if nume_ales and nume_ales in info_map:
            info  = info_map[nume_ales]
            parts = []
            if info["dep"]:
                parts.append(f"🏢 {info['dep']}")
            if info["email"]:
                parts.append(f"✉️ {info['email']}")
            if info["telefon"]:
                parts.append(f"📞 {info['telefon']}")
            if parts:
                st.markdown(
                    "<div style='background:rgba(255,255,255,0.06);"
                    "border-radius:6px;padding:5px 12px;margin-top:2px;"
                    "font-size:0.84rem;color:rgba(255,255,255,0.80);'>" +
                    "  &nbsp;·&nbsp;  ".join(parts) +
                    "</div>",
                    unsafe_allow_html=True,
                )

        if idx < nr_membri - 1:
            st.markdown(
                "<div style='border-top:1px solid rgba(255,255,255,0.10);"
                "margin-top:8px;'></div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    if st.button("➕ Adaugă membru", key=f"add_membru_{cod_introdus}"):
        st.session_state[key_nr] += 1
        st.rerun()

    # Colectare rezultat pentru salvare
    rezultat = []
    for idx in range(nr_membri):
        n = str(st.session_state.get(f"echipa_{cod_introdus}_{idx}_nume", "") or "").strip()
        if not n:
            continue
        r = str(st.session_state.get(f"echipa_{cod_introdus}_{idx}_rol", "") or "").strip()
        c = bool(st.session_state.get(f"echipa_{cod_introdus}_{idx}_contact", False))
        rezultat.append({
            "cod_identificare": cod_introdus,
            "nume_prenume":     n,
            "rol":              r,
            "persoana_contact": c,
            "functie_upt":      "",
        })
    return rezultat
