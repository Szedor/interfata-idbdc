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

def render(supabase, cod_introdus, cat_sel, tip_label, tabela_nume, is_new, date_existente):
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
        "CATEGORIE": cat_sel,
        "TIPUL DE CONTRACT": tip_label,
        "NR.CONTRACT": cod_introdus,
        "DATA CONTRACTULUI": _safe_date(date_existente.get("data_contract")),
        "OBIECTUL CONTRACTULUI": date_existente.get("obiectul_contractului", ""),
        "BENEFICIAR": date_existente.get("denumire_beneficiar", ""),
        "DATA DE INCEPUT": di,
        "DATA DE SFARSIT": ds,
        "DURATA": dur_ex,
        "STATUS CONTRACT": date_existente.get("status_contract_proiect", ""),
    }
    df = pd.DataFrame([row_init])

    col_cfg = {
        "CATEGORIE": st.column_config.TextColumn("CATEGORIE", disabled=True),
        "TIPUL DE CONTRACT": st.column_config.TextColumn("TIPUL DE CONTRACT", disabled=True),
        "NR.CONTRACT": st.column_config.TextColumn("NR.CONTRACT", disabled=True),
        "DATA CONTRACTULUI": st.column_config.DateColumn("📅 DATA CONTRACTULUI", format="YYYY-MM-DD"),
        "OBIECTUL CONTRACTULUI": st.column_config.TextColumn("📝 OBIECTUL CONTRACTULUI", width="large"),
        "BENEFICIAR": st.column_config.TextColumn("🏢 BENEFICIAR"),
        "DATA DE INCEPUT": st.column_config.DateColumn("📅 DATA DE INCEPUT", format="YYYY-MM-DD"),
        "DATA DE SFARSIT": st.column_config.DateColumn("📅 DATA DE SFARSIT", format="YYYY-MM-DD"),
        "DURATA": st.column_config.NumberColumn("⏱️ DURATA (luni)", format="%d", min_value=0),
        "STATUS CONTRACT": st.column_config.SelectboxColumn("🔖 STATUS CONTRACT", options=status_list),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"{tabela_nume}_baza_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    di_e = row["DATA DE INCEPUT"]
    ds_e = row["DATA DE SFARSIT"]
    dur_e = int(row["DURATA"]) if row["DURATA"] else 0

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
        "data_contract": _fmt_date(row["DATA CONTRACTULUI"]),
        "obiectul_contractului": row["OBIECTUL CONTRACTULUI"],
        "denumire_beneficiar": row["BENEFICIAR"],
        "data_inceput": _fmt_date(di_e),
        "data_sfarsit": _fmt_date(ds_e),
        "durata": dur_e if dur_e else None,
        "status_contract_proiect": row["STATUS CONTRACT"] if row["STATUS CONTRACT"] else None,
    }
