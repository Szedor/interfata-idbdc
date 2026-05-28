# =========================================================
# domenii/_baza/sectiune_baza.py
# v.modul.1.0 - Secțiune Date de bază (generică)
# =========================================================

import streamlit as st
import pandas as pd
from utils.date_helpers import to_date, calc_durata, add_months, sub_months

def _get_status_list(supabase):
    @st.cache_data(show_spinner=False, ttl=600)
    def _fetch():
        try:
            res = supabase.table("nom_status_proiect").select("status_contract_proiect").execute()
            return [r["status_contract_proiect"] for r in (res.data or []) if r.get("status_contract_proiect")]
        except Exception:
            return []
    return _fetch()

def _fmt_date(date_val):
    if date_val is None:
        return None
    if hasattr(date_val, 'strftime'):
        return date_val.strftime("%Y-%m-%d")
    if hasattr(date_val, 'isoformat'):
        return date_val.isoformat()
    return str(date_val) if date_val else None

def _safe_date(v):
    if v is None:
        return None
    if hasattr(v, 'strftime'):
        return v
    try:
        return to_date(v)
    except Exception:
        return None

def _safe_int(v):
    if v is None:
        return 0
    try:
        return int(float(str(v).replace(",", ".")))
    except:
        return 0

def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_label, tabela_nume, fields, is_new, date_existente):
    status_list = _get_status_list(supabase)

    di = _safe_date(date_existente.get("data_inceput"))
    ds = _safe_date(date_existente.get("data_sfarsit"))
    dur_ex = _safe_int(date_existente.get("durata"))

    if di and ds and (dur_ex == 0):
        dur_ex = calc_durata(di, ds)
    elif di and dur_ex and not ds:
        ds = add_months(di, dur_ex)
    elif ds and dur_ex and not di:
        di = sub_months(ds, dur_ex)
    if di and ds:
        dur_ex = calc_durata(di, ds)

    row_init = {
        "cod_identificare": cod_introdus,
        "data_contract": _safe_date(date_existente.get("data_contract")),
        "obiectul_contractului": date_existente.get("obiectul_contractului", ""),
        "denumire_beneficiar": date_existente.get("denumire_beneficiar", ""),
        "data_inceput": di,
        "data_sfarsit": ds,
        "durata": dur_ex,
        "status_contract_proiect": date_existente.get("status_contract_proiect", ""),
    }

    # Construim DataFrame pentru afișare
    display_row = {
        fields.get(k, k.replace("_", " ").capitalize()): v 
        for k, v in row_init.items() if k in fields
    }
    df = pd.DataFrame([display_row])

    # Configurare coloane
    col_cfg = {}
    for k, label in fields.items():
        if k == "cod_identificare":
            col_cfg[label] = st.column_config.TextColumn(label, disabled=True)
        elif k == "data_contract":
            col_cfg[label] = st.column_config.DateColumn(label, format="YYYY-MM-DD")
        elif k == "data_inceput":
            col_cfg[label] = st.column_config.DateColumn(label, format="YYYY-MM-DD")
        elif k == "data_sfarsit":
            col_cfg[label] = st.column_config.DateColumn(label, format="YYYY-MM-DD")
        elif k == "durata":
            col_cfg[label] = st.column_config.NumberColumn(label, format="%d", min_value=0)
        elif k == "status_contract_proiect":
            col_cfg[label] = st.column_config.SelectboxColumn(label, options=status_list)
        else:
            col_cfg[label] = st.column_config.TextColumn(label, width="large")

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"{tabela_nume}_baza_editor_{cod_introdus}",
    )

    row = df_edit.iloc[0]
    
    # Extragem valorile
    di_e = row[fields.get("data_inceput", "DATA DE INCEPUT")] if "data_inceput" in fields else None
    ds_e = row[fields.get("data_sfarsit", "DATA DE SFARSIT")] if "data_sfarsit" in fields else None
    dur_e = row[fields.get("durata", "DURATA (luni)")] if "durata" in fields else 0
    if isinstance(dur_e, str):
        dur_e = _safe_int(dur_e)

    if di_e and ds_e:
        dur_e = calc_durata(di_e, ds_e)
        st.caption(f"📅 Durată calculată automat: {dur_e} luni")
    elif di_e and dur_e and not ds_e:
        ds_e = add_months(di_e, dur_e)
        st.caption(f"📅 Data de sfarsit calculată automat: {ds_e}")
    elif ds_e and dur_e and not di_e:
        di_e = sub_months(ds_e, dur_e)
        st.caption(f"📅 Data de inceput calculată automat: {di_e}")

    return {
        "cod_identificare": cod_introdus,
        "data_contract": _fmt_date(row[fields.get("data_contract", "DATA CONTRACTULUI")]) if "data_contract" in fields else None,
        "obiectul_contractului": row[fields.get("obiectul_contractului", "OBIECTUL CONTRACTULUI")] if "obiectul_contractului" in fields else "",
        "denumire_beneficiar": row[fields.get("denumire_beneficiar", "BENEFICIAR")] if "denumire_beneficiar" in fields else "",
        "data_inceput": _fmt_date(di_e),
        "data_sfarsit": _fmt_date(ds_e),
        "durata": dur_e if dur_e else None,
        "status_contract_proiect": row[fields.get("status_contract_proiect", "STATUS CONTRACT")] if "status_contract_proiect" in fields else None,
    }
