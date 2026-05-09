# =========================================================
# IDBDC/domenii/_baza/sectiune_baza_contracte.py
# VERSIUNE: 1.0
# STATUS: NOU - Date de bază comune pentru toate contractele
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Randează secțiunea Date de bază pentru contracte
#   (CEP, TERȚI, SPECIALE). Preia conținutul validat din
#   utils/contracte_common.py v7.0, cu o singură modificare:
#   nota de subsol înlocuită cu textul fix obligatoriu
#   "Durata se calculează automat după salvarea fișei."
#   și adăugată coloana OBSERVAȚII.
# =========================================================

import streamlit as st
import pandas as pd
from utils.date_helpers import to_date, calc_durata, add_months, sub_months


def _fmt_date(val):
    if not val:
        return None
    if hasattr(val, "isoformat"):
        return val.isoformat()
    s = str(val).strip()
    return s if s not in ("", "None", "nan") else None


@st.cache_data(show_spinner=False, ttl=600)
def _get_status_list(_supabase):
    try:
        res = _supabase.table("nom_status_proiect").select("status_contract_proiect").execute()
        return [r["status_contract_proiect"] for r in (res.data or []) if r.get("status_contract_proiect")]
    except Exception:
        return []


def render(supabase, cod_introdus, cat_sel, tip_label, tabela_nume, is_new, date_existente):
    """
    Parametri:
        tip_label   : "CEP" | "TERȚI" | "SPECIALE"
        tabela_nume : "base_contracte_cep" | "base_contracte_terti" | "base_contracte_speciale"
    Returnează: dict cu datele pentru salvare în tabela base_*
    """
    status_list = _get_status_list(supabase)

    di     = to_date(date_existente.get("data_inceput"))
    ds     = to_date(date_existente.get("data_sfarsit"))
    dur_ex = date_existente.get("durata")

    if di and ds and not dur_ex:
        dur_ex = calc_durata(di, ds)
    elif di and dur_ex and not ds:
        ds = add_months(di, dur_ex)
    elif ds and dur_ex and not di:
        di = sub_months(ds, dur_ex)
    if di and ds:
        dur_ex = calc_durata(di, ds)

    row_init = {
        "CATEGORIE":             cat_sel,
        "TIPUL DE CONTRACT":     tip_label,
        "NR.CONTRACT":           cod_introdus,
        "DATA CONTRACTULUI":     to_date(date_existente.get("data_contract")),
        "OBIECTUL CONTRACTULUI": date_existente.get("obiectul_contractului", ""),
        "BENEFICIAR":            date_existente.get("denumire_beneficiar", ""),
        "DATA DE INCEPUT":       di,
        "DATA DE SFARSIT":       ds,
        "DURATA":                int(dur_ex) if dur_ex else 0,
        "STATUS CONTRACT":       date_existente.get("status_contract_proiect", ""),
        "OBSERVAȚII":            date_existente.get("observatii", ""),
    }
    df = pd.DataFrame([row_init])

    col_cfg = {
        "CATEGORIE":             st.column_config.TextColumn("CATEGORIE", disabled=True),
        "TIPUL DE CONTRACT":     st.column_config.TextColumn("TIPUL DE CONTRACT", disabled=True),
        "NR.CONTRACT":           st.column_config.TextColumn("NR.CONTRACT", disabled=True),
        "DATA CONTRACTULUI":     st.column_config.DateColumn("📅 DATA CONTRACTULUI", format="DD-MM-YYYY"),
        "OBIECTUL CONTRACTULUI": st.column_config.TextColumn("OBIECTUL CONTRACTULUI", width="large"),
        "BENEFICIAR":            st.column_config.TextColumn("BENEFICIAR"),
        "DATA DE INCEPUT":       st.column_config.DateColumn("📅 DATA DE INCEPUT", format="DD-MM-YYYY"),
        "DATA DE SFARSIT":       st.column_config.DateColumn("📅 DATA DE SFARSIT", format="DD-MM-YYYY"),
        "DURATA":                st.column_config.NumberColumn("DURATA (luni)", format="%d", min_value=0),
        "STATUS CONTRACT":       st.column_config.SelectboxColumn("🔖 STATUS CONTRACT", options=status_list),
        "OBSERVAȚII":            st.column_config.TextColumn("📝 OBSERVAȚII", width="large"),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"{tabela_nume}_baza_editor_{cod_introdus}",
    )

    st.caption("ℹ️ Durata se calculează automat după salvarea fișei.")

    row   = df_edit.iloc[0]
    di_e  = row["DATA DE INCEPUT"]
    ds_e  = row["DATA DE SFARSIT"]
    dur_e = int(row["DURATA"]) if row["DURATA"] else 0

    if di_e and ds_e:
        dur_e = calc_durata(di_e, ds_e)
    elif di_e and dur_e and not ds_e:
        ds_e = add_months(di_e, dur_e)
    elif ds_e and dur_e and not di_e:
        di_e = sub_months(ds_e, dur_e)

    return {
        "cod_identificare":        cod_introdus,
        "denumire_categorie":      cat_sel,
        "acronim_tip_contract":    tip_label,
        "data_contract":           _fmt_date(row["DATA CONTRACTULUI"]),
        "obiectul_contractului":   str(row["OBIECTUL CONTRACTULUI"]).strip() if row["OBIECTUL CONTRACTULUI"] else None,
        "denumire_beneficiar":     str(row["BENEFICIAR"]).strip()            if row["BENEFICIAR"]            else None,
        "data_inceput":            _fmt_date(di_e),
        "data_sfarsit":            _fmt_date(ds_e),
        "durata":                  dur_e if dur_e else None,
        "status_contract_proiect": row["STATUS CONTRACT"] if row["STATUS CONTRACT"] else None,
        "observatii":              str(row["OBSERVAȚII"]).strip()            if row["OBSERVAȚII"]            else None,
    }
