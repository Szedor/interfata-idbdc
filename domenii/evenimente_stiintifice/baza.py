# =========================================================
# IDBDC/domenii/evenimente_stiintifice/baza.py
# VERSIUNE: 4.0
# STATUS: RECONFIGURAT PE FORMULAR (STIL CARD) — Eliminare st.data_editor
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

    st.markdown("### 📝 Date de Bază Eveniment Științific")

    # Organizăm câmpurile vizual în coloane, exact ca într-o fișă/card curat
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("CATEGORIE", value=cat_sel, disabled=True)
        titlu_ev = st.text_input("TITLUL EVENIMENTULUI", value=date_existente.get("titlul_eveniment", "") or "")
        
        # Gestionare stabilă Date Calendaristice
        di_init = to_date(date_existente.get("data_inceput"))
        data_inc = st.date_input("📅 DATA DE INCEPUT", value=di_init)
        
        format_init = date_existente.get("format_eveniment", "") or ""
        format_sel = st.selectbox("🔖 FORMATUL EVENIMENTULUI", options=format_list, index=format_list.index(format_init) if format_init in format_list else 0)
        
        loc_desf = st.text_input("LOCUL DE DESFASURARE", value=date_existente.get("loc_desfasurare", "") or "")

    with col2:
        st.text_input("COD EVENIMENT", value=cod_introdus, disabled=True)
        inst_org = st.text_input("INSTITUTIILE ORGANIZATOARE", value=date_existente.get("institutii_organizatoare", "") or "")
        
        ds_init = to_date(date_existente.get("data_sfarsit"))
        data_sf = st.date_input("📅 DATA DE SFARSIT", value=ds_init)
        
        # Mecanism de autocompletare nativ și stabil pentru Natură -> Cotație
        natura_init = date_existente.get("natura_eveniment", "") or ""
        natura_sel = st.selectbox(
            "🔖 NATURA EVENIMENTULUI STIINTIFIC", 
            options=natura_list, 
            index=natura_list.index(natura_init) if natura_init in natura_list else 0
        )
        
        # Cotația se schimbă instant pe ecran în funcție de ce selectezi la Natură
        cotatie_calculata = natura_map.get(natura_sel, "")
        st.text_input("COTATIA EVENIMENTULUI (calculată automat)", value=cotatie_calculata, disabled=True)
        
        website_ev = st.text_input("WEBSITE", value=date_existente.get("website", "") or "")

    # Câmpul OBSERVATII — lăsat complet liber și mare sub formă de text_area
    obs_ev = st.text_area("OBSERVATII (la dispoziția operatorului)", value=date_existente.get("observatii", "") or "")

    # Funcție ajutătoare pentru curățat textul
    def _str(v):
        return str(v).strip() if v else None

    # ── Returnare dicționar consolidat pentru salvarea în Supabase ──
    return {
        "cod_identificare":         cod_introdus,
        "denumire_categorie":       cat_sel,
        "titlul_eveniment":         _str(titlu_ev),
        "data_inceput":             fmt_date(data_inc),
        "data_sfarsit":             fmt_date(data_sf),
        "format_eveniment":         _str(format_sel) if format_sel else None,
        "loc_desfasurare":          _str(loc_desf),
        "institutii_organizatoare": _str(inst_org),
        "natura_eveniment":         _str(natura_sel) if natura_sel else None,
        "cotatie_eveniment":        _str(cotatie_calculata) if cotatie_calculata else None,
        "website":                  _str(website_ev),
        "observatii":               _str(obs_ev),
    }
