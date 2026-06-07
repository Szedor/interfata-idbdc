# =========================================================
# IDBDC/domenii/evenimente_stiintifice/baza.py
# VERSIUNE: 2.0
# STATUS: RESTRUCTURAT — format tabel, autocompletare reactivă
# DATA: 2026.06.06
# =========================================================
# DATE DE BAZĂ — format data_editor (tabel), ordinea din mapare:
#  1. CATEGORIE                          (readonly)
#  2. COD EVENIMENT                      (readonly)
#  3. TITLUL EVENIMENTULUI
#  4. DATA DE INCEPUT                    ← 📅
#  5. DATA DE SFARSIT                    ← 📅
#  6. FORMATUL EVENIMENTULUI             ← 🔖 nom_format_evenimente
#     → autocompletare OBSERVATII
#  7. LOCUL DE DESFASURARE
#  8. INSTITUTIILE ORGANIZATOARE
#  9. NATURA EVENIMENTULUI STIINTIFIC    ← 🔖 nom_evenimente_stiintifice
#     → autocompletare COTATIA EVENIMENTULUI
# 10. COTATIA EVENIMENTULUI              (readonly — automat)
# 11. WEBSITE
# 12. OBSERVATII                         (readonly — exclus Calea1)
#
# Mecanism autocompletare:
#   - data_editor nu suportă reactivity inline
#   - La fiecare schimbare detectată în NATURA sau FORMAT,
#     actualizăm session_state și facem st.rerun()
#   - COTATIA și OBSERVATII sunt câmpuri disabled în tabel
# =========================================================

import streamlit as st
import pandas as pd

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
    """Dict {format_eveniment: explicatii_format_evenimente}."""
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

    natura_map   = _get_natura_map(supabase)
    format_map   = _get_format_map(supabase)

    natura_list  = [""] + sorted(natura_map.keys())
    format_list  = [""] + sorted(format_map.keys())

    # ── Chei session_state pentru valori autocompletate ───────────────
    key_row      = f"ev_row_{cod_introdus}"
    key_natura   = f"ev_nat_{cod_introdus}"
    key_format   = f"ev_fmt_{cod_introdus}"

    # Inițializare la prima deschidere
    natura_init  = date_existente.get("natura_eveniment", "") or ""
    format_init  = date_existente.get("format_eveniment", "") or ""
    cotatie_init = natura_map.get(natura_init, "") or \
                   date_existente.get("cotatie_eveniment", "") or ""
    obs_init     = format_map.get(format_init, "") or \
                   date_existente.get("observatii", "") or ""

    if key_natura not in st.session_state:
        st.session_state[key_natura] = natura_init
    if key_format not in st.session_state:
        st.session_state[key_format] = format_init

    # Valori curente autocompletate
    cotatie_cur = natura_map.get(st.session_state[key_natura], "")
    obs_cur     = format_map.get(st.session_state[key_format], "")

    # ── Construire rând pentru data_editor ────────────────────────────
    row_init = {
        "CATEGORIE":                          cat_sel,
        "COD EVENIMENT":                      cod_introdus,
        "TITLUL EVENIMENTULUI":               date_existente.get("titlul_eveniment", "") or "",
        "📅 DATA DE INCEPUT":                 to_date(date_existente.get("data_inceput")),
        "📅 DATA DE SFARSIT":                 to_date(date_existente.get("data_sfarsit")),
        "🔖 FORMATUL EVENIMENTULUI":          st.session_state[key_format],
        "LOCUL DE DESFASURARE":               date_existente.get("loc_desfasurare", "") or "",
        "INSTITUTIILE ORGANIZATOARE":         date_existente.get("institutii_organizatoare", "") or "",
        "🔖 NATURA EVENIMENTULUI STIINTIFIC": st.session_state[key_natura],
        "COTATIA EVENIMENTULUI":              cotatie_cur,
        "WEBSITE":                            date_existente.get("website", "") or "",
        "OBSERVATII":                         obs_cur,
    }

    if key_row not in st.session_state:
        st.session_state[key_row] = row_init

    df = pd.DataFrame([st.session_state[key_row]])

    col_cfg = {
        "CATEGORIE": st.column_config.TextColumn(
            "CATEGORIE", disabled=True
        ),
        "COD EVENIMENT": st.column_config.TextColumn(
            "COD EVENIMENT", disabled=True
        ),
        "TITLUL EVENIMENTULUI": st.column_config.TextColumn(
            "TITLUL EVENIMENTULUI", width="large"
        ),
        "📅 DATA DE INCEPUT": st.column_config.DateColumn(
            "📅 DATA DE INCEPUT", format="YYYY-MM-DD"
        ),
        "📅 DATA DE SFARSIT": st.column_config.DateColumn(
            "📅 DATA DE SFARSIT", format="YYYY-MM-DD"
        ),
        "🔖 FORMATUL EVENIMENTULUI": st.column_config.SelectboxColumn(
            "🔖 FORMATUL EVENIMENTULUI", options=format_list
        ),
        "LOCUL DE DESFASURARE": st.column_config.TextColumn(
            "LOCUL DE DESFASURARE"
        ),
        "INSTITUTIILE ORGANIZATOARE": st.column_config.TextColumn(
            "INSTITUTIILE ORGANIZATOARE", width="large"
        ),
        "🔖 NATURA EVENIMENTULUI STIINTIFIC": st.column_config.SelectboxColumn(
            "🔖 NATURA EVENIMENTULUI STIINTIFIC", options=natura_list
        ),
        "COTATIA EVENIMENTULUI": st.column_config.TextColumn(
            "COTATIA EVENIMENTULUI", disabled=True
        ),
        "WEBSITE": st.column_config.LinkColumn(
            "WEBSITE"
        ),
        "OBSERVATII": st.column_config.TextColumn(
            "OBSERVATII (completat automat)", disabled=True, width="large"
        ),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"ev_editor_{cod_introdus}",
    )

    row = df_edit.iloc[0]

    # ── Detectare schimbări și autocompletare ─────────────────────────
    natura_noua = row.get("🔖 NATURA EVENIMENTULUI STIINTIFIC", "") or ""
    format_nou  = row.get("🔖 FORMATUL EVENIMENTULUI", "") or ""
    needs_rerun = False

    if natura_noua != st.session_state[key_natura]:
        st.session_state[key_natura] = natura_noua
        cotatie_noua = natura_map.get(natura_noua, "")
        # Actualizăm rândul cu noua cotație
        row_upd = dict(st.session_state[key_row])
        row_upd["🔖 NATURA EVENIMENTULUI STIINTIFIC"] = natura_noua
        row_upd["COTATIA EVENIMENTULUI"] = cotatie_noua
        st.session_state[key_row] = row_upd
        needs_rerun = True

    if format_nou != st.session_state[key_format]:
        st.session_state[key_format] = format_nou
        obs_noua = format_map.get(format_nou, "")
        row_upd = dict(st.session_state.get(key_row, row_init))
        row_upd["🔖 FORMATUL EVENIMENTULUI"] = format_nou
        row_upd["OBSERVATII"] = obs_noua
        st.session_state[key_row] = row_upd
        needs_rerun = True

    if needs_rerun:
        st.rerun()

    # ── Sincronizare câmpuri editabile în session_state ───────────────
    row_sync = dict(st.session_state.get(key_row, row_init))
    for camp in [
        "TITLUL EVENIMENTULUI", "📅 DATA DE INCEPUT", "📅 DATA DE SFARSIT",
        "LOCUL DE DESFASURARE", "INSTITUTIILE ORGANIZATOARE", "WEBSITE",
    ]:
        row_sync[camp] = row.get(camp, row_sync.get(camp))
    st.session_state[key_row] = row_sync

    # ── Returnare dict pentru upsert ──────────────────────────────────
    def _str(v):
        return str(v).strip() if v else None

    return {
        "cod_identificare":       cod_introdus,
        "denumire_categorie":     cat_sel,
        "titlul_eveniment":       _str(row["TITLUL EVENIMENTULUI"]),
        "data_inceput":           fmt_date(row["📅 DATA DE INCEPUT"]),
        "data_sfarsit":           fmt_date(row["📅 DATA DE SFARSIT"]),
        "format_eveniment":       st.session_state[key_format] or None,
        "loc_desfasurare":        _str(row["LOCUL DE DESFASURARE"]),
        "institutii_organizatoare": _str(row["INSTITUTIILE ORGANIZATOARE"]),
        "natura_eveniment":       st.session_state[key_natura] or None,
        "cotatie_eveniment":      natura_map.get(st.session_state[key_natura], "") or None,
        "website":                _str(row["WEBSITE"]),
        "observatii":             format_map.get(st.session_state[key_format], "") or None,
    }
