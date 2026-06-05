# =========================================================
# IDBDC/domenii/contracte_speciale/baza.py
# VERSIUNE: 2.0 | DATA: 2026.06.02
# =========================================================
# DATE DE BAZĂ — ordinea și etichetele exacte din mapare:
#  1. CATEGORIE
#  2. TIPUL DE CONTARCT
#  3. NR.CONTRACT
#  4. DATA CONTRACTULUI        ← 📅
#  5. OBIECTUL CONTRACTULUI
#  6. BENEFICIAR
#  7. DATA DE INCEPUT          ← 📅
#  8. DATA DE SFARSIT          ← 📅
#  9. DURATA (luni)
# 10. STATUS CONTRACT          ← 🔖
# 11. DERULAT PRIN
# 12. OBSERVATII               (exclus din Calea1)
# =========================================================

import streamlit as st
import pandas as pd

from core.helpers import to_date, calc_durata, add_months, sub_months, fmt_date


@st.cache_data(show_spinner=False, ttl=600)
def _get_status_list(_supabase):
    try:
        res = _supabase.table("nom_status_proiect") \
            .select("status_contract_proiect").execute()
        return [r["status_contract_proiect"]
                for r in (res.data or []) if r.get("status_contract_proiect")]
    except Exception:
        return []


def render(supabase, cod_introdus, cat_sel, tip_label, tabela_nume, is_new, date_existente):
    status_list = _get_status_list(supabase)

    di     = to_date(date_existente.get("data_inceput"))
    ds     = to_date(date_existente.get("data_sfarsit"))
    dur_ex = date_existente.get("durata")

    if di and ds and (dur_ex is None or dur_ex == 0):
        dur_ex = calc_durata(di, ds)
    elif di and dur_ex and not ds:
        ds = add_months(di, dur_ex)
    elif ds and dur_ex and not di:
        di = sub_months(ds, dur_ex)
    if di and ds:
        dur_ex = calc_durata(di, ds)

    row_init = {
        "CATEGORIE":              cat_sel,
        "TIPUL DE CONTARCT":      tip_label,
        "NR.CONTRACT":            cod_introdus,
        "📅 DATA CONTRACTULUI":   to_date(date_existente.get("data_contract")),
        "OBIECTUL CONTRACTULUI":  date_existente.get("obiectul_contractului", "") or "",
        "BENEFICIAR":             date_existente.get("denumire_beneficiar", "") or "",
        "📅 DATA DE INCEPUT":     di,
        "📅 DATA DE SFARSIT":     ds,
        "DURATA (luni)":          int(dur_ex) if dur_ex else 0,
        "🔖 STATUS CONTRACT":     date_existente.get("status_contract_proiect", "") or "",
        "DERULAT PRIN":           date_existente.get("derulat_prin", "") or "",
        "OBSERVATII":             date_existente.get("observatii", "") or "",
    }
    df = pd.DataFrame([row_init])

    col_cfg = {
        "CATEGORIE":             st.column_config.TextColumn("CATEGORIE", disabled=True),
        "TIPUL DE CONTARCT":     st.column_config.TextColumn("TIPUL DE CONTARCT", disabled=True),
        "NR.CONTRACT":           st.column_config.TextColumn("NR.CONTRACT", disabled=True),
        "📅 DATA CONTRACTULUI":  st.column_config.DateColumn("📅 DATA CONTRACTULUI", format="YYYY-MM-DD"),
        "OBIECTUL CONTRACTULUI": st.column_config.TextColumn("OBIECTUL CONTRACTULUI", width="large"),
        "BENEFICIAR":            st.column_config.TextColumn("BENEFICIAR"),
        "📅 DATA DE INCEPUT":    st.column_config.DateColumn("📅 DATA DE INCEPUT", format="YYYY-MM-DD"),
        "📅 DATA DE SFARSIT":    st.column_config.DateColumn("📅 DATA DE SFARSIT", format="YYYY-MM-DD"),
        "DURATA (luni)":         st.column_config.NumberColumn("DURATA (luni)", format="%d", min_value=0),
        "🔖 STATUS CONTRACT":    st.column_config.SelectboxColumn("🔖 STATUS CONTRACT", options=status_list),
        "DERULAT PRIN":          st.column_config.TextColumn("DERULAT PRIN"),
        "OBSERVATII":            st.column_config.TextColumn("OBSERVATII", width="large"),
    }

    df_edit = st.data_editor(
        df, column_config=col_cfg, hide_index=True,
        use_container_width=True, num_rows="fixed",
        key=f"{tabela_nume}_baza_editor_{cod_introdus}",
    )

    st.caption("ℹ️ Durata se calculează automat după salvarea fișei.")

    row = df_edit.iloc[0]

    di_e  = row["📅 DATA DE INCEPUT"]
    ds_e  = row["📅 DATA DE SFARSIT"]
    dur_e = int(row["DURATA (luni)"]) if row["DURATA (luni)"] else 0

    if di_e and ds_e:
        dur_e = calc_durata(di_e, ds_e)
    elif di_e and dur_e and not ds_e:
        ds_e = add_months(di_e, dur_e)
    elif ds_e and dur_e and not di_e:
        di_e = sub_months(ds_e, dur_e)

    def _str(v):
        return str(v).strip() if v else None

    return {
        "cod_identificare":        cod_introdus,
        "denumire_categorie":      cat_sel,
        "acronim_tip_contract":    tip_label,
        "data_contract":           fmt_date(row["📅 DATA CONTRACTULUI"]),
        "obiectul_contractului":   _str(row["OBIECTUL CONTRACTULUI"]),
        "denumire_beneficiar":     _str(row["BENEFICIAR"]),
        "data_inceput":            fmt_date(di_e),
        "data_sfarsit":            fmt_date(ds_e),
        "durata":                  dur_e if dur_e else None,
        "status_contract_proiect": row["🔖 STATUS CONTRACT"] if row["🔖 STATUS CONTRACT"] else None,
        "derulat_prin":            _str(row["DERULAT PRIN"]),
        "observatii":              _str(row["OBSERVATII"]),
    }
