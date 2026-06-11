# =========================================================
# IDBDC/domenii/resurse_umane/baza.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.06.11
# =========================================================
# DATE PERSOANĂ — ordinea și etichetele exacte din mapare:
#  1. NUMELE SI PRENUMELE
#  2. EMAIL
#  3. TELEFON MOBIL
#  4. TELEFON FIX
#  5. ACRONIM FUNCTIE IN UPT    ← 🔖 dropdown din nom_functie_upt
#  6. ACRONIM DEPARTAMENT       ← 🔖 dropdown din nom_departament
# =========================================================

import streamlit as st


@st.cache_data(show_spinner=False, ttl=600)
def _get_functii_list(_supabase):
    try:
        res = _supabase.table("nom_functie_upt") \
            .select("acronim_functie_upt").order("acronim_functie_upt").execute()
        return [r["acronim_functie_upt"]
                for r in (res.data or []) if r.get("acronim_functie_upt")]
    except Exception:
        return []


@st.cache_data(show_spinner=False, ttl=600)
def _get_departamente_list(_supabase):
    try:
        res = _supabase.table("nom_departament") \
            .select("acronim_departament").order("acronim_departament").execute()
        return [r["acronim_departament"]
                for r in (res.data or []) if r.get("acronim_departament")]
    except Exception:
        return []


def render(supabase, nr_crt, is_new, date_existente):
    """
    Randează și colectează datele unei persoane din det_resurse_umane.

    Parametri:
        supabase       : clientul Supabase
        nr_crt         : cheia primară (int sau None pentru înregistrare nouă)
        is_new         : True dacă este persoană nouă
        date_existente : dict cu datele existente (gol dacă is_new)

    Returnează:
        dict cu valorile pentru upsert în det_resurse_umane
    """
    functii_list   = _get_functii_list(supabase)
    dep_list       = _get_departamente_list(supabase)

    # Valori inițiale
    if is_new or not date_existente:
        d = {}
    else:
        d = date_existente

    functie_ex = d.get("acronim_functie_upt", "") or ""
    dep_ex     = d.get("acronim_departament", "") or ""

    # ── R1: NUMELE SI PRENUMELE ──────────────────────────────────────
    nume = st.text_input(
        "NUMELE ȘI PRENUMELE",
        value=d.get("nume_prenume", "") or "",
        key=f"ru_nume_{nr_crt}",
    )

    # ── R2: EMAIL ───────────────────────────────────────────────────
    email = st.text_input(
        "EMAIL",
        value=d.get("email", "") or "",
        key=f"ru_email_{nr_crt}",
        placeholder="prenume.nume@upt.ro",
    )

    # ── R3: TELEFON MOBIL + TELEFON FIX ─────────────────────────────
    col_mob, col_fix = st.columns(2)
    with col_mob:
        tel_mobil = st.text_input(
            "TELEFON MOBIL",
            value=d.get("telefon_mobil", "") or "",
            key=f"ru_mob_{nr_crt}",
        )
    with col_fix:
        tel_fix = st.text_input(
            "TELEFON FIX",
            value=d.get("telefon_fix", "") or "",
            key=f"ru_fix_{nr_crt}",
        )

    # ── R4: ACRONIM FUNCTIE + ACRONIM DEPARTAMENT ───────────────────
    col_f, col_d = st.columns(2)
    with col_f:
        functii_options = [""] + functii_list
        idx_f = functii_options.index(functie_ex) if functie_ex in functii_options else 0
        functie = st.selectbox(
            "🔖 ACRONIM FUNCTIE ÎN UPT",
            options=functii_options,
            index=idx_f,
            key=f"ru_functie_{nr_crt}",
        )
    with col_d:
        dep_options = [""] + dep_list
        idx_d = dep_options.index(dep_ex) if dep_ex in dep_options else 0
        departament = st.selectbox(
            "🔖 ACRONIM DEPARTAMENT",
            options=dep_options,
            index=idx_d,
            key=f"ru_dep_{nr_crt}",
        )

    # ── Audit (read-only, vizibil dacă există) ───────────────────────
    if not is_new and d:
        creat_de     = d.get("creat_de") or "—"
        creat_la     = d.get("creat_la") or "—"
        modificat_de = d.get("modificat_de") or "—"
        modificat_la = d.get("modificat_la") or "—"
        st.markdown(
            f"""
            <div style='margin-top:14px;background:rgba(255,255,255,0.06);
            border:1px solid rgba(255,255,255,0.18);border-radius:10px;
            padding:10px 16px;'>
            <div style='color:rgba(255,255,255,0.50);font-size:0.74rem;font-weight:800;
            text-transform:uppercase;letter-spacing:0.07em;margin-bottom:8px;'>
            🔐 Audit</div>
            <table style='width:100%;border-collapse:collapse;'>
            <tr>
            <td style='width:25%;color:rgba(255,255,255,0.50);font-size:0.76rem;
            font-weight:700;text-transform:uppercase;padding:3px 12px 3px 0;'>
            Creat de</td>
            <td style='color:#ffffff;font-size:0.92rem;font-weight:700;padding:3px 0;'>
            {creat_de}</td>
            <td style='width:25%;color:rgba(255,255,255,0.50);font-size:0.76rem;
            font-weight:700;text-transform:uppercase;padding:3px 12px 3px 24px;'>
            Creat la</td>
            <td style='color:#ffffff;font-size:0.92rem;font-weight:700;padding:3px 0;'>
            {creat_la}</td>
            </tr>
            <tr>
            <td style='color:rgba(255,255,255,0.50);font-size:0.76rem;
            font-weight:700;text-transform:uppercase;padding:3px 12px 3px 0;'>
            Modificat de</td>
            <td style='color:#ffffff;font-size:0.92rem;font-weight:700;padding:3px 0;'>
            {modificat_de}</td>
            <td style='color:rgba(255,255,255,0.50);font-size:0.76rem;
            font-weight:700;text-transform:uppercase;padding:3px 12px 3px 24px;'>
            Modificat la</td>
            <td style='color:#ffffff;font-size:0.92rem;font-weight:700;padding:3px 0;'>
            {modificat_la}</td>
            </tr>
            </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def _str(v):
        return str(v).strip() if v else None

    return {
        "nume_prenume":        _str(nume),
        "email":               _str(email),
        "telefon_mobil":       _str(tel_mobil),
        "telefon_fix":         _str(tel_fix),
        "acronim_functie_upt": functie if functie else None,
        "acronim_departament": departament if departament else None,
    }
