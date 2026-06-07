# =========================================================
# IDBDC/domenii/evenimente_stiintifice/baza.py
# VERSIUNE: 5.1
# STATUS: CORECTAT — Remediat sintaxă CSS, UI Optimizat structural
# DATA: 2026.06.08
# =========================================================

import streamlit as st
from core.helpers import to_date, fmt_date

# ── Cache nomenclatoare ────────────────────────────────────────────────

@st.cache_data(show_spinner=False, ttl=600)
def _get_natura_map(_supabase):
    """Dict {natura_eveniment: cotatie_eveniment}."""
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
    """Listă simplă pentru formatele disponibile."""
    try:
        res = _supabase.table("nom_format_evenimente") \
            .select("format_eveniment").execute()
        return [r["format_eveniment"] for r in (res.data or []) if r.get("format_eveniment")]
    except Exception:
        return []


# ── Funcție principală ─────────────────────────────────────────────────

def render(supabase, cod_introdus, cat_sel, tip_label, tabela_nume, is_new, date_existente):

    natura_map   = _get_natura_map(supabase)
    format_list  = [""] + sorted(_get_format_map(supabase))
    natura_list  = [""] + sorted(natura_map.keys())

    # ── [1] Injectare CSS corectă pentru forțare text NEGRU ABSOLUT în casete ──
    css_style = """
    <style>
        input, select, textarea, [data-baseweb="select"] * {
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }
    </style>
    """
    st.markdown(css_style, unsafe_allow_markup=True)

    st.markdown("### 📝 Date de Bază Eveniment Științific")

    # ── R1 -> CATEGORIE - 50%, COD EVENIMENT - 50% ────────────────────
    r1_col1, r1_col2 = st.columns([50, 50])
    with r1_col1:
        st.text_input("CATEGORIE", value=cat_sel, disabled=True)
    with r1_col2:
        st.text_input("COD EVENIMENT", value=cod_introdus, disabled=True)

    # ── R2 -> TITLUL EVENIMENTULUI - 50%, INSTITUTIILE ORGANIZATOARE - 50% ──
    r2_col1, r2_col2 = st.columns([50, 50])
    with r2_col1:
        titlu_ev = st.text_input("TITLUL EVENIMENTULUI", value=date_existente.get("titlul_eveniment", "") or "")
    with r2_col2:
        inst_org = st.text_input("INSTITUTIILE ORGANIZATOARE", value=date_existente.get("institutii_organizatoare", "") or "")

    # ── R3 -> DATA DE INCEPUT - 25%, DATA DE SFARSIT - 25%, LOCUL DE DESFASURARE - 50% ──
    r3_col1, r3_col2, r3_col3 = st.columns([25, 25, 50])
    with r3_col1:
        di_init = to_date(date_existente.get("data_inceput"))
        data_inc = st.date_input("📅 DATA DE INCEPUT", value=di_init)
    with r3_col2:
        ds_init = to_date(date_existente.get("data_sfarsit"))
        data_fail = st.date_input("📅 DATA DE SFARSIT", value=ds_init)
    with r3_col3:
        loc_desf = st.text_input("LOCUL DE DESFASURARE", value=date_existente.get("loc_desfasurare", "") or "")

    # ── R4 -> NATURA EVENIMENTULUI STIINTIFIC - 50%, COTATIA EVENIMENTULUI - 20%, FORMATUL EVENIMENTULUI - 30% ──
    r4_col1, r4_col2, r4_col3 = st.columns([50, 20, 30])
    with r4_col1:
        natura_init = date_existente.get("natura_eveniment", "") or ""
        natura_sel = st.selectbox(
            "🔖 NATURA EVENIMENTULUI STIINTIFIC", 
            options=natura_list, 
            index=natura_list.index(natura_init) if natura_init in natura_list else 0
        )
    with r4_col2:
        # [2] Am eliminat textul din paranteză de la etichetă
        cotatie_calculata = natura_map.get(natura_sel, "")
        st.text_input("COTATIA EVENIMENTULUI", value=cotatie_calculata, disabled=True)
    with r4_col3:
        format_init = date_existente.get("format_eveniment", "") or ""
        format_sel = st.selectbox(
            "🔖 FORMATUL EVENIMENTULUI", 
            options=format_list, 
            index=format_list.index(format_init) if format_init in format_list else 0
        )

    # ── R5 -> WEBSITE - 33%, OBSERVATII - 66% ─────────────────────────
    r5_col1, r5_col2 = st.columns([33, 66])
    with r5_col1:
        website_ev = st.text_input("WEBSITE", value=date_existente.get("website", "") or "")
    with r5_col2:
        # [2] Am eliminat textul din paranteză de la etichetă și am aliniat caseta la aceeași înălțime cu WEBSITE
        obs_ev = st.text_input("OBSERVATII", value=date_existente.get("observatii", "") or "")

    # Funcție ajutătoare pentru curățat textul
    def _str(v):
        return str(v).strip() if v else None

    # ── Returnare dicționar consolidat pentru salvarea în Supabase ──
    return {
        "cod_identificare":         cod_introdus,
        "denumire_categorie":       cat_sel,
        "titlul_eveniment":         _str(titlu_ev),
        "data_inceput":             fmt_date(data_inc),
        "data_sfarsit":             fmt_date(data_fail),
        "format_eveniment":         _str(format_sel) if format_sel else None,
        "loc_desfasurare":          _str(loc_desf),
        "institutii_organizatoare": _str(inst_org),
        "natura_eveniment":         _str(natura_sel) if natura_sel else None,
        "cotatie_eveniment":        _str(cotatie_calculata) if cotatie_calculata else None,
        "website":                  _str(website_ev),
        "observatii":               _str(obs_ev),
    }
