# =========================================================
# IDBDC/domenii/_baza/sectiune_baza_proiecte_fdi.py
# VERSIUNE: 1.0
# STATUS: NOU - Date de bază pentru Proiecte FDI
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Randează secțiunea Date de bază pentru Proiecte FDI.
#   Conținut preluat din utils/sectiuni/date_baza_proiect.py
#   v2.0, neatins.
# =========================================================

import streamlit as st
import pandas as pd
from utils.date_helpers import to_date, calc_durata, add_months, sub_months


@st.cache_data(show_spinner=False, ttl=600)
def _get_status_list(_supabase):
    try:
        res = _supabase.table("nom_status_proiect").select("status_contract_proiect").execute()
        return [r["status_contract_proiect"] for r in (res.data or []) if r.get("status_contract_proiect")]
    except Exception:
        return []


@st.cache_data(show_spinner=False, ttl=600)
def _get_domenii_fdi(_supabase):
    try:
        res = _supabase.table("nom_domenii_fdi").select("cod_domeniu_fdi").order("cod_domeniu_fdi").execute()
        return [r["cod_domeniu_fdi"] for r in (res.data or []) if r.get("cod_domeniu_fdi")]
    except Exception:
        return []


def _fmt_date(date_val):
    if date_val is None:
        return None
    if pd.isna(date_val):
        return None
    if hasattr(date_val, 'strftime'):
        return date_val.strftime("%Y-%m-%d")
    if hasattr(date_val, 'isoformat'):
        return date_val.isoformat()
    return str(date_val)


def render(supabase, cod_introdus, cat_sel, tip_label, tabela_nume, is_new, date_existente):
    status_list  = _get_status_list(supabase)
    domenii_list = _get_domenii_fdi(supabase)

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

    domeniu_ex = date_existente.get("cod_domeniu_fdi", "") or ""
    if domeniu_ex and domeniu_ex not in domenii_list:
        domenii_list = [domeniu_ex] + domenii_list
    domenii_options = [""] + domenii_list

    row_init = {
        "CATEGORIE":              cat_sel,
        "TIPUL DE PROIECT":       tip_label,
        "COD FINAL INREGISTRARE": cod_introdus,
        "TITLUL PROIECTULUI":     date_existente.get("titlul_proiect", ""),
        "ACRONIMUL PROIECTULUI":  date_existente.get("acronim_proiect", ""),
        "DATA DE INCEPUT":        di,
        "DATA DE SFARSIT":        ds,
        "DURATA (luni)":          int(dur_ex) if dur_ex else 0,
        "STATUS CONTRACT":        date_existente.get("status_contract_proiect", ""),
        "PROGRAM DE FINANTARE":   date_existente.get("program", ""),
        "DOMENIU":                domeniu_ex,
        "COD DEPUNERE":           date_existente.get("cod_temporar", ""),
        "OBSERVATII":             date_existente.get("observatii", ""),
    }
    df = pd.DataFrame([row_init])

    col_cfg = {
        "CATEGORIE":              st.column_config.TextColumn("CATEGORIE", disabled=True),
        "TIPUL DE PROIECT":       st.column_config.TextColumn("TIPUL DE PROIECT", disabled=True),
        "COD FINAL INREGISTRARE": st.column_config.TextColumn("COD FINAL INREGISTRARE", disabled=True),
        "TITLUL PROIECTULUI":     st.column_config.TextColumn("TITLUL PROIECTULUI", width="large"),
        "ACRONIMUL PROIECTULUI":  st.column_config.TextColumn("ACRONIMUL PROIECTULUI"),
        "DATA DE INCEPUT":        st.column_config.DateColumn("📅 DATA DE INCEPUT", format="YYYY-MM-DD"),
        "DATA DE SFARSIT":        st.column_config.DateColumn("📅 DATA DE SFARSIT", format="YYYY-MM-DD"),
        "DURATA (luni)":          st.column_config.NumberColumn("DURATA (luni)", format="%d", min_value=0),
        "STATUS CONTRACT":        st.column_config.SelectboxColumn("🔖 STATUS CONTRACT", options=status_list),
        "PROGRAM DE FINANTARE":   st.column_config.TextColumn("PROGRAM DE FINANTARE"),
        "DOMENIU":                st.column_config.SelectboxColumn("DOMENIU", options=domenii_options, required=False),
        "COD DEPUNERE":           st.column_config.TextColumn("COD DEPUNERE"),
        "OBSERVATII":             st.column_config.TextColumn("📝 OBSERVATII", width="large"),
    }

    df_edit = st.data_editor(
        df, column_config=col_cfg, hide_index=True,
        use_container_width=True, num_rows="fixed",
        key=f"{tabela_nume}_baza_proiect_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    st.caption("ℹ️ Durata se calculează automat după salvarea fișei.")

    di_e  = row["DATA DE INCEPUT"]
    ds_e  = row["DATA DE SFARSIT"]
    dur_e = int(row["DURATA (luni)"]) if row["DURATA (luni)"] else 0

    if di_e and ds_e:
        dur_e = calc_durata(di_e, ds_e)
    elif di_e and dur_e and not ds_e:
        ds_e = add_months(di_e, dur_e)
    elif ds_e and dur_e and not di_e:
        di_e = sub_months(ds_e, dur_e)

    return {
        "cod_identificare":        cod_introdus,
        "denumire_categorie":      cat_sel,
        "acronim_tip_proiecte":    tip_label,
        "titlul_proiect":          str(row["TITLUL PROIECTULUI"]).strip()    if row["TITLUL PROIECTULUI"]    else None,
        "acronim_proiect":         str(row["ACRONIMUL PROIECTULUI"]).strip() if row["ACRONIMUL PROIECTULUI"] else None,
        "data_inceput":            _fmt_date(di_e),
        "data_sfarsit":            _fmt_date(ds_e),
        "durata":                  dur_e if dur_e else None,
        "status_contract_proiect": row["STATUS CONTRACT"]      if row["STATUS CONTRACT"]      else None,
        "program":                 str(row["PROGRAM DE FINANTARE"]).strip() if row["PROGRAM DE FINANTARE"] else None,
        "cod_domeniu_fdi":         str(row["DOMENIU"]).strip()              if row["DOMENIU"]              else None,
        "cod_temporar":            str(row["COD DEPUNERE"]).strip()         if row["COD DEPUNERE"]         else None,
        "observatii":              str(row["OBSERVATII"]).strip()           if row["OBSERVATII"]           else None,
    }
