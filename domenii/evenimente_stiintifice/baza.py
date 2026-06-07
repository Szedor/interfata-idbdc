# =========================================================
# IDBDC/domenii/evenimente_stiintifice/baza.py
# VERSIUNE: 2.3
# STATUS: CORECTAT — Sincronizare stabilă data_editor fără salturi
# DATA: 2026.06.08
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
# 12. OBSERVATII                         (readonly — automat)
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

    # ── Chei unice session_state salvate stabil ──────────────────────
    key_row      = f"ev_row_stabil_{cod_introdus}"

    # Construire rând inițial o singură dată (la prima încărcare a fișei)
    if key_row not in st.session_state:
        natura_init  = date_existente.get("natura_eveniment", "") or ""
        format_init  = date_existente.get("format_eveniment", "") or ""
        cotatie_init = natura_map.get(natura_init, "") or date_existente.get("cotatie_eveniment", "") or ""
        obs_init     = format_map.get(format_init, "") or date_existente.get("observatii", "") or ""

        st.session_state[key_row] = {
            "CATEGORIE":                          cat_sel,
            "COD EVENIMENT":                      cod_introdus,
            "TITLUL EVENIMENTULUI":               date_existente.get("titlul_eveniment", "") or "",
            "📅 DATA DE INCEPUT":                 to_date(date_existente.get("data_inceput")),
            "📅 DATA DE SFARSIT":                 to_date(date_existente.get("data_sfarsit")),
            "🔖 FORMATUL EVENIMENTULUI":          format_init,
            "LOCUL DE DESFASURARE":               date_existente.get("loc_desfasurare", "") or "",
            "INSTITUTIILE ORGANIZATOARE":         date_existente.get("institutii_organizatoare", "") or "",
            "🔖 NATURA EVENIMENTULUI STIINTIFIC": natura_init,
            "COTATIA EVENIMENTULUI":              cotatie_init,
            "WEBSITE":                            date_existente.get("website", "") or "",
            "OBSERVATII":                         obs_init,
        }

    # Creăm DataFrame direct din starea stabilă
    df = pd.DataFrame([st.session_state[key_row]])

    # Forțăm coloanele de tip dată să fie native Datetime înainte de st.data_editor
    if "📅 DATA DE INCEPUT" in df.columns:
        df["📅 DATA DE INCEPUT"] = pd.to_datetime(df["📅 DATA DE INCEPUT"], errors="coerce")
    if "📅 DATA DE SFARSIT" in df.columns:
        df["📅 DATA DE SFARSIT"] = pd.to_datetime(df["📅 DATA DE SFARSIT"], errors="coerce")

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
        key=f"ev_editor_stabil_{cod_introdus}",
    )

    # Extragem rândul editat în timp real de utilizator
    row = df_edit.iloc[0]

    # Determinăm valorile curente introduse
    natura_curenta = row.get("🔖 NATURA EVENIMENTULUI STIINTIFIC", "") or ""
    format_curent  = row.get("🔖 FORMATUL EVENIMENTULUI", "") or ""

    # Calculăm automat cotația și observațiile pe baza a ceea ce a selectat utilizatorul acum pe ecran
    cotatie_calculata = natura_map.get(natura_curenta, "")
    observatii_calculate = format_map.get(format_curent, "")

    # Sincronizăm starea din memorie cu absolut tot ce a modificat utilizatorul, inclusiv autocompletările
    st.session_state[key_row] = {
        "CATEGORIE":                          cat_sel,
        "COD EVENIMENT":                      cod_introdus,
        "TITLUL EVENIMENTULUI":               row.get("TITLUL EVENIMENTULUI", ""),
        "📅 DATA DE INCEPUT":                 row.get("📅 DATA DE INCEPUT"),
        "📅 DATA DE SFARSIT":                 row.get("📅 DATA DE SFARSIT"),
        "🔖 FORMATUL EVENIMENTULUI":          format_curent,
        "LOCUL DE DESFASURARE":               row.get("LOCUL DE DESFASURARE", ""),
        "INSTITUTIILE ORGANIZATOARE":         row.get("INSTITUTIILE ORGANIZATOARE", ""),
        "🔖 NATURA EVENIMENTULUI STIINTIFIC": natura_curenta,
        "COTATIA EVENIMENTULUI":              cotatie_calculata,
        "WEBSITE":                            row.get("WEBSITE", ""),
        "OBSERVATII":                         observatii_calculate,
    }

    # ── Returnare dict pentru introducere în baza de date Supabase ──
    def _str(v):
        return str(v).strip() if v else None

    return {
        "cod_identificare":         cod_introdus,
        "denumire_categorie":       cat_sel,
        "titlul_eveniment":         _str(row["TITLUL EVENIMENTULUI"]),
        "data_inceput":             fmt_date(row["📅 DATA DE INCEPUT"]),
        "data_sfarsit":             fmt_date(row["📅 DATA DE SFARSIT"]),
        "format_eveniment":         _str(format_curent),
        "loc_desfasurare":          _str(row["LOCUL DE DESFASURARE"]),
        "institutii_organizatoare": _str(row["INSTITUTIILE ORGANIZATOARE"]),
        "natura_eveniment":         _str(natura_curenta),
        "cotatie_eveniment":        _str(cotatie_calculata),
        "website":                  _str(row["WEBSITE"]),
        "observatii":               _str(observatii_calculate),
    }
