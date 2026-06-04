# =========================================================
# IDBDC/domenii/evenimente_stiintifice/baza.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.06.02
# =========================================================
# DATE DE BAZĂ — ordinea și etichetele exacte din mapare:
#  1. CATEGORIE
#  2. NATURA EVENIMENTULUI STIINTIFIC  ← 🔖 nom_evenimente_stiintifice
#     → completează automat COTATIA EVENIMENTULUI
#  3. COD EVENIMENT
#  4. TITLUL EVENIMENTULUI
#  5. DATA DE INCEPUT                  ← 📅
#  6. DATA DE SFARSIT                  ← 📅
#  7. FORMATUL EVENIMENTULUI           ← 🔖 nom_format_evenimente
#     → completează automat OBSERVATII
#  8. LOCUL DE DESFASURARE
#  9. INSTITUTIILE ORGANIZATOARE
# 10. CLASIFICAREA EVENIMENTULUI
# 11. WEBSITE
# 12. COTATIA EVENIMENTULUI            (readonly — automat din natura)
# 13. OBSERVATII                       (readonly — automat din format,
#                                       exclus din Calea1)
# =========================================================

import streamlit as st
import pandas as pd

from core.helpers import to_date, fmt_date


# ── Cache nomenclatoare ────────────────────────────────────────────────

@st.cache_data(show_spinner=False, ttl=600)
def _get_natura_map(_supabase):
    """Returnează dict {natura_eveniment: cotatie_eveniment}."""
    try:
        res = _supabase.table("nom_evenimente_stiintifice") \
            .select("natura_eveniment,cotatie_eveniment").execute()
        return {
            r["natura_eveniment"]: r.get("cotatie_eveniment", "") or ""
            for r in (res.data or []) if r.get("natura_eveniment")
        }
    except Exception:
        return {}


@st.cache_data(show_spinner=False, ttl=600)
def _get_format_map(_supabase):
    """Returnează dict {format_eveniment: explicatii_format_evenimente}."""
    try:
        res = _supabase.table("nom_format_evenimente") \
            .select("format_eveniment,explicatii_format_evenimente").execute()
        return {
            r["format_eveniment"]: r.get("explicatii_format_evenimente", "") or ""
            for r in (res.data or []) if r.get("format_eveniment")
        }
    except Exception:
        return {}


# ── Funcție principală ─────────────────────────────────────────────────

def render(supabase, cod_introdus, cat_sel, tip_label, tabela_nume, is_new, date_existente):
    """
    Randează și colectează Date de bază pentru Evenimente Științifice.
    Logică specială:
      - Selectarea NATURII completează automat COTATIA
      - Selectarea FORMATULUI completează automat OBSERVATII
    """
    natura_map  = _get_natura_map(supabase)
    format_map  = _get_format_map(supabase)

    natura_list = [""] + sorted(natura_map.keys())
    format_list = [""] + sorted(format_map.keys())

    # ── Chei session_state ─────────────────────────────────────────────
    key_natura   = f"ev_natura_{cod_introdus}"
    key_format   = f"ev_format_{cod_introdus}"
    key_cotatie  = f"ev_cotatie_{cod_introdus}"
    key_obs      = f"ev_obs_{cod_introdus}"

    # Inițializare session_state la prima deschidere
    if key_natura not in st.session_state:
        st.session_state[key_natura]  = date_existente.get("natura_eveniment", "") or ""
    if key_format not in st.session_state:
        st.session_state[key_format]  = date_existente.get("format_eveniment", "") or ""
    if key_cotatie not in st.session_state:
        natura_init = st.session_state[key_natura]
        st.session_state[key_cotatie] = natura_map.get(natura_init, "") if natura_init else \
                                        (date_existente.get("clasificare_eveniment", "") or "")
    if key_obs not in st.session_state:
        format_init = st.session_state[key_format]
        st.session_state[key_obs] = format_map.get(format_init, "") if format_init else \
                                    (date_existente.get("observatii", "") or "")

    # ── Rând 1: CATEGORIE (readonly) ───────────────────────────────────
    st.markdown(
        f"<div style='color:rgba(255,255,255,0.55);font-size:0.78rem;font-weight:700;"
        f"text-transform:uppercase;margin-bottom:2px;'>CATEGORIE</div>"
        f"<div style='color:#ffffff;font-size:0.95rem;margin-bottom:12px;'>{cat_sel}</div>",
        unsafe_allow_html=True,
    )

    # ── Rând 2: NATURA + COTATIA (pe același rând) ────────────────────
    col_nat, col_cot = st.columns([2, 1])

    with col_nat:
        idx_nat = natura_list.index(st.session_state[key_natura]) \
                  if st.session_state[key_natura] in natura_list else 0
        natura_aleasa = st.selectbox(
            "🔖 NATURA EVENIMENTULUI STIINTIFIC",
            options=natura_list,
            index=idx_nat,
            key=key_natura,
        )

    with col_cot:
        cotatie_auto = natura_map.get(natura_aleasa, "") if natura_aleasa else ""
        st.session_state[key_cotatie] = cotatie_auto
        st.text_input(
            "COTATIA EVENIMENTULUI",
            value=cotatie_auto,
            disabled=True,
            key=f"ev_cotatie_display_{cod_introdus}",
        )

    # ── Rând 3: COD + TITLU ────────────────────────────────────────────
    col_cod, col_tit = st.columns([1, 3])
    with col_cod:
        st.text_input(
            "COD EVENIMENT",
            value=cod_introdus,
            disabled=True,
            key=f"ev_cod_{cod_introdus}",
        )
    with col_tit:
        titlu = st.text_input(
            "TITLUL EVENIMENTULUI",
            value=date_existente.get("titlul_eveniment", "") or "",
            key=f"ev_titlu_{cod_introdus}",
        )

    # ── Rând 4: DATE + FORMAT ──────────────────────────────────────────
    col_di, col_ds, col_fmt = st.columns([1, 1, 2])

    with col_di:
        data_inceput = st.date_input(
            "📅 DATA DE INCEPUT",
            value=to_date(date_existente.get("data_inceput")),
            format="YYYY-MM-DD",
            key=f"ev_di_{cod_introdus}",
        )
    with col_ds:
        data_sfarsit = st.date_input(
            "📅 DATA DE SFARSIT",
            value=to_date(date_existente.get("data_sfarsit")),
            format="YYYY-MM-DD",
            key=f"ev_ds_{cod_introdus}",
        )
    with col_fmt:
        idx_fmt = format_list.index(st.session_state[key_format]) \
                  if st.session_state[key_format] in format_list else 0
        format_ales = st.selectbox(
            "🔖 FORMATUL EVENIMENTULUI",
            options=format_list,
            index=idx_fmt,
            key=key_format,
        )
        # Autocompletare OBSERVATII din format ales
        obs_auto = format_map.get(format_ales, "") if format_ales else ""
        st.session_state[key_obs] = obs_auto

    # ── Rând 5: LOC + INSTITUTII ───────────────────────────────────────
    col_loc, col_inst = st.columns([1, 2])
    with col_loc:
        loc = st.text_input(
            "LOCUL DE DESFASURARE",
            value=date_existente.get("loc_desfasurare", "") or "",
            key=f"ev_loc_{cod_introdus}",
        )
    with col_inst:
        institutii = st.text_input(
            "INSTITUTIILE ORGANIZATOARE",
            value=date_existente.get("institutii_organizare", "") or "",
            key=f"ev_inst_{cod_introdus}",
        )

    # ── Rând 6: CLASIFICARE + WEBSITE ─────────────────────────────────
    col_cls, col_web = st.columns([1, 2])
    with col_cls:
        clasificare = st.text_input(
            "CLASIFICAREA EVENIMENTULUI",
            value=date_existente.get("clasificare_eveniment", "") or "",
            key=f"ev_cls_{cod_introdus}",
        )
    with col_web:
        website = st.text_input(
            "WEBSITE",
            value=date_existente.get("website", "") or "",
            key=f"ev_web_{cod_introdus}",
        )

    # ── OBSERVATII — readonly, completat automat, exclus din Calea1 ────
    st.text_area(
        "OBSERVATII (completat automat din formatul evenimentului — exclus din Calea1)",
        value=obs_auto,
        disabled=True,
        height=80,
        key=f"ev_obs_display_{cod_introdus}",
    )

    # ── Returnare dict pentru upsert ──────────────────────────────────
    def _str(v):
        return str(v).strip() if v else None

    return {
        "cod_identificare":       cod_introdus,
        "denumire_categorie":     cat_sel,
        "natura_eveniment":       natura_aleasa if natura_aleasa else None,
        "clasificare_eveniment":  cotatie_auto if cotatie_auto else _str(clasificare),
        "titlul_eveniment":       _str(titlu),
        "data_inceput":           fmt_date(data_inceput),
        "data_sfarsit":           fmt_date(data_sfarsit),
        "format_eveniment":       format_ales if format_ales else None,
        "loc_desfasurare":        _str(loc),
        "institutii_organizare":  _str(institutii),
        "website":                _str(website),
        "observatii":             obs_auto if obs_auto else None,
    }
