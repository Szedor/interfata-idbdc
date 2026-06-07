# =========================================================
# IDBDC/domenii/evenimente_stiintifice/baza.py
# VERSIUNE: 3.0
# STATUS: RECONSTRUIT INTEGRAL — Sincronizare nativă, OBSERVATII libere
# DATA: 2026.06.08
# =========================================================
# DATE DE BAZĂ — format data_editor (tabel), ordinea din mapare:
#  1. CATEGORIE                          (readonly)
#  2. COD EVENIMENT                      (readonly)
#  3. TITLUL EVENIMENTULUI
#  4. DATA DE INCEPUT                    ← 📅
#  5. DATA DE SFARSIT                    ← 📅
#  6. FORMATUL EVENIMENTULUI             ← 🔖 nom_format_evenimente
#  7. LOCUL DE DESFASURARE
#  8. INSTITUTIILE ORGANIZATOARE
#  9. NATURA EVENIMENTULUI STIINTIFIC    ← 🔖 nom_evenimente_stiintifice
#     → autocompletare COTATIA EVENIMENTULUI
# 10. COTATIA EVENIMENTULUI              (readonly — automat)
# 11. WEBSITE
# 12. OBSERVATII                         (la dispoziția operatorului)
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

    # Cheia unică pentru starea stabilă din session_state
    key_row = f"ev_row_stabil_{cod_introdus}"
    key_editor = f"ev_editor_stabil_{cod_introdus}"

    # Inițializare rând o singură dată la deschiderea fișei
    if key_row not in st.session_state:
        natura_init  = date_existente.get("natura_eveniment", "") or ""
        cotatie_init = natura_map.get(natura_init, "") or date_existente.get("cotatie_eveniment", "") or ""

        st.session_state[key_row] = {
            "CATEGORIE":                          cat_sel,
            "COD EVENIMENT":                      cod_introdus,
            "TITLUL EVENIMENTULUI":               date_existente.get("titlul_eveniment", "") or "",
            "📅 DATA DE INCEPUT":                 to_date(date_existente.get("data_inceput")),
            "📅 DATA DE SFARSIT":                 to_date(date_existente.get("data_sfarsit")),
            "🔖 FORMATUL EVENIMENTULUI":          date_existente.get("format_eveniment", "") or "",
            "LOCUL DE DESFASURARE":               date_existente.get("loc_desfasurare", "") or "",
            "INSTITUTIILE ORGANIZATOARE":         date_existente.get("institutii_organizatoare", "") or "",
            "🔖 NATURA EVENIMENTULUI STIINTIFIC": natura_init,
            "COTATIA EVENIMENTULUI":              cotatie_init,
            "WEBSITE":                            date_existente.get("website", "") or "",
            "OBSERVATII":                         date_existente.get("observatii", "") or "",  # Rămâne goală sau ce era salvat, editabilă liber
        }

    # Callback nativ Streamlit: rulează DOAR când utilizatorul modifică ceva în tabel și schimbă celula
    def on_table_change():
        if key_editor in st.session_state and st.session_state[key_editor]["edited_rows"]:
            changes = st.session_state[key_editor]["edited_rows"].get(0, {})
            current_data = st.session_state[key_row]
            
            # Actualizăm doar câmpurile care au fost efectiv modificate de operator
            for col, val in changes.items():
                current_data[col] = val
                
                # Autocompletare strictă pentru Cotație dacă s-a schimbat Natura
                if col == "🔖 NATURA EVENIMENTULUI STIINTIFIC":
                    current_data["COTATIA EVENIMENTULUI"] = natura_map.get(val, "")
            
            st.session_state[key_row] = current_data

    # Construim DataFrame pe baza stării salvate stabil
    df = pd.DataFrame([st.session_state[key_row]])

    # Forțare tip de date nativ Datetime pentru a asigura funcționarea selectorului calendar
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
            "OBSERVATII", disabled=False, width="large"  # Activată complet pentru operator
        ),
    }

    # Randare tabel cu legătură directă la funcția de salvare în fundal
    st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=key_editor,
        on_change=on_table_change
    )

    # Extragem valorile finale consolidate din session_state
    row_final = st.session_state[key_row]

    def _str(v):
        return str(v).strip() if v else None

    # ── Returnare dicționar curat pentru salvarea în Supabase ──
    return {
        "cod_identificare":         cod_introdus,
        "denumire_categorie":       cat_sel,
        "titlul_eveniment":         _str(row_final["TITLUL EVENIMENTULUI"]),
        "data_inceput":             fmt_date(row_final["📅 DATA DE INCEPUT"]),
        "data_sfarsit":             fmt_date(row_final["📅 DATA DE SFARSIT"]),
        "format_eveniment":         _str(row_final["🔖 FORMATUL EVENIMENTULUI"]),
        "loc_desfasurare":          _str(row_final["LOCUL DE DESFASURARE"]),
        "institutii_organizatoare": _str(row_final["INSTITUTIILE ORGANIZATOARE"]),
        "natura_eveniment":         _str(row_final["🔖 NATURA EVENIMENTULUI STIINTIFIC"]),
        "cotatie_eveniment":        _str(row_final["COTATIA EVENIMENTULUI"]),
        "website":                  _str(row_final["WEBSITE"]),
        "observatii":               _str(row_final["OBSERVATII"]),
    }
