# =========================================================
# IDBDC/domenii/_baza/sectiune_baza_evenimente_stiintifice.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.05.23
# =========================================================
# LOGICA SPECIALA:
#   [1] NATURA EVENIMENTULUI STIINTIFIC — dropdown din
#       nom_evenimente_stiintifice.natura_eveniment
#   [2] La selectia naturii, se completeaza automat
#       CLASIFICAREA EVENIMENTULUI din
#       nom_evenimente_stiintifice.clasificare_eveniment
#   [3] FORMATUL EVENIMENTULUI — dropdown din
#       nom_format_evenimente.format_eveniment
# =========================================================

import streamlit as st
import pandas as pd
from datetime import date


# ── Helpers ───────────────────────────────────────────────────────────────────

def _to_date(v):
    if v is None: return None
    if isinstance(v, date): return v
    if isinstance(v, str) and v:
        try: return date.fromisoformat(v[:10])
        except: return None
    return None

def _fmt_date(v):
    if v is None: return None
    if hasattr(v, 'strftime'): return v.strftime("%Y-%m-%d")
    if hasattr(v, 'isoformat'): return v.isoformat()
    return str(v)

def _s(v): return str(v).strip() if v else None


# ── Cache nomenclatoare ───────────────────────────────────────────────────────

@st.cache_data(show_spinner=False, ttl=600)
def _get_nom_natura(_supabase):
    """
    Returneaza lista din nom_evenimente_stiintifice:
    [{"natura_eveniment": "...", "clasificare_eveniment": "..."}, ...]
    """
    try:
        res = _supabase.table("nom_evenimente_stiintifice").select(
            "natura_eveniment, clasificare_eveniment"
        ).execute()
        return res.data or []
    except Exception:
        return []


@st.cache_data(show_spinner=False, ttl=600)
def _get_nom_format(_supabase):
    """
    Returneaza lista de formate din nom_format_evenimente:
    ["Online", "Fizic", "Hibrid", ...]
    """
    try:
        res = _supabase.table("nom_format_evenimente").select("format_eveniment").execute()
        return [r["format_eveniment"] for r in (res.data or []) if r.get("format_eveniment")]
    except Exception:
        return []


# ── Render principal ──────────────────────────────────────────────────────────

def render(supabase, cod_introdus, cat_sel, tabela_nume, is_new, date_existente):
    nom_natura  = _get_nom_natura(supabase)
    formate     = _get_nom_format(supabase)

    natura_list      = [r["natura_eveniment"]    for r in nom_natura if r.get("natura_eveniment")]
    map_clasificare  = {r["natura_eveniment"]: r.get("clasificare_eveniment", "") for r in nom_natura}

    # Valori existente
    natura_ex       = date_existente.get("natura_eveniment", "")
    format_ex       = date_existente.get("format_eveniment", "")
    clasificare_ex  = date_existente.get("clasificare_eveniment", "")

    # ── Dropdown NATURA ───────────────────────────────────────────────────────
    st.markdown("##### Natura și clasificarea evenimentului")

    idx_natura = natura_list.index(natura_ex) if natura_ex in natura_list else 0
    natura_sel = st.selectbox(
        "NATURA EVENIMENTULUI STIINTIFIC",
        options=natura_list,
        index=idx_natura,
        key=f"natura_ev_{cod_introdus}",
    )

    # Completare automata clasificare
    clasificare_auto = map_clasificare.get(natura_sel, clasificare_ex or "")
    st.info(f"**CLASIFICAREA EVENIMENTULUI:** {clasificare_auto or '—'}")

    # ── Dropdown FORMAT ───────────────────────────────────────────────────────
    st.markdown("##### Date generale")

    idx_format = formate.index(format_ex) if format_ex in formate else 0
    format_sel = st.selectbox(
        "FORMATUL EVENIMENTULUI",
        options=formate,
        index=idx_format,
        key=f"format_ev_{cod_introdus}",
    )

    # ── Restul campurilor ─────────────────────────────────────────────────────
    df = pd.DataFrame([{
        "CATEGORIE":                  cat_sel,
        "COD EVENIMENT":              cod_introdus,
        "TITLUL EVENIMENTULUI":       date_existente.get("titlul_eveniment", ""),
        "DATA DE INCEPUT":            _to_date(date_existente.get("data_inceput")),
        "DATA DE SFARSIT":            _to_date(date_existente.get("data_sfarsit")),
        "LOCUL DE DESFASURARE":       date_existente.get("loc_desfasurare", ""),
        "INSTITUTIILE ORGANIZATOARE": date_existente.get("institutii_organizatoare", ""),
        "WEBSITEA WEBSITEULUI":       date_existente.get("website", ""),
        "OBSERVATII":                 date_existente.get("observatii", ""),
    }])

    col_cfg = {
        "CATEGORIE":                  st.column_config.TextColumn("CATEGORIE", disabled=True),
        "COD EVENIMENT":              st.column_config.TextColumn("COD EVENIMENT", disabled=True),
        "TITLUL EVENIMENTULUI":       st.column_config.TextColumn("TITLUL EVENIMENTULUI", width="large"),
        "DATA DE INCEPUT":            st.column_config.DateColumn("📅 DATA DE INCEPUT", format="YYYY-MM-DD"),
        "DATA DE SFARSIT":            st.column_config.DateColumn("📅 DATA DE SFARSIT", format="YYYY-MM-DD"),
        "LOCUL DE DESFASURARE":       st.column_config.TextColumn("LOCUL DE DESFASURARE", width="large"),
        "INSTITUTIILE ORGANIZATOARE": st.column_config.TextColumn("INSTITUTIILE ORGANIZATOARE", width="large"),
        "WEBSITEA WEBSITEULUI":       st.column_config.TextColumn("WEBSITEA WEBSITEULUI"),
        "OBSERVATII":                 st.column_config.TextColumn("📝 OBSERVATII", width="large"),
    }

    df_edit = st.data_editor(
        df, column_config=col_cfg, hide_index=True,
        use_container_width=True, num_rows="fixed",
        key=f"{tabela_nume}_baza_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    return {
        "cod_identificare":        cod_introdus,
        "denumire_categorie":      cat_sel,
        "natura_eveniment":        natura_sel,
        "clasificare_eveniment":   clasificare_auto,
        "format_eveniment":        format_sel,
        "titlul_eveniment":        _s(row["TITLUL EVENIMENTULUI"]),
        "data_inceput":            _fmt_date(row["DATA DE INCEPUT"]),
        "data_sfarsit":            _fmt_date(row["DATA DE SFARSIT"]),
        "loc_desfasurare":         _s(row["LOCUL DE DESFASURARE"]),
        "institutii_organizatoare":_s(row["INSTITUTIILE ORGANIZATOARE"]),
        "website":                 _s(row["WEBSITEA WEBSITEULUI"]),
        "observatii":              _s(row["OBSERVATII"]),
    }
