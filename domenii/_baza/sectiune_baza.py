# =========================================================
# IDBDC/domenii/_baza/sectiune_baza.py
# v.modul.1.0 - Secțiune Date de bază (generică)
# =========================================================

import streamlit as st
import pandas as pd
from core.helpers import to_date, calc_durata, add_months, sub_months, fmt_date, safe_select_eq


def _get_status_list(supabase):
    @st.cache_data(show_spinner=False, ttl=600)
    def _fetch():
        try:
            res = supabase.table("nom_status_proiect").select("status_contract_proiect").execute()
            return [r["status_contract_proiect"] for r in (res.data or []) if r.get("status_contract_proiect")]
        except Exception:
            return []
    return _fetch()


def render(supabase, cod_introdus, cat_sel, tip_label, tabela_nume, fields_map, is_new, date_existente):
    """
    Randare Date de bază pentru orice tip de domeniu.
    
    fields_map: dict cu maparea {coloana_tehnica: eticheta_vizuala}
    """
    status_list = _get_status_list(supabase)

    di = to_date(date_existente.get("data_inceput"))
    ds = to_date(date_existente.get("data_sfarsit"))
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
        fields_map.get("categorie", "CATEGORIE"): cat_sel,
        fields_map.get("tip", "TIP"): tip_label,
        fields_map.get("cod", "COD"): cod_introdus,
        fields_map.get("data_contract", "DATA CONTRACTULUI"): to_date(date_existente.get("data_contract")),
        fields_map.get("obiect", "OBIECT"): date_existente.get("obiectul_contractului", ""),
        fields_map.get("beneficiar", "BENEFICIAR"): date_existente.get("denumire_beneficiar", ""),
        fields_map.get("data_inceput", "DATA DE INCEPUT"): di,
        fields_map.get("data_sfarsit", "DATA DE SFARSIT"): ds,
        fields_map.get("durata", "DURATA"): int(dur_ex) if dur_ex else 0,
        fields_map.get("status", "STATUS"): date_existente.get("status_contract_proiect", ""),
    }
    
    # Adaugă observații dacă există în mapare
    if "observatii" in fields_map:
        row_init[fields_map["observatii"]] = date_existente.get("observatii", "")
    
    df = pd.DataFrame([row_init])

    # Construim configurația coloanelor dinamic
    col_cfg = {}
    for tech_col, label in fields_map.items():
        if tech_col == "categorie" or tech_col == "tip" or tech_col == "cod":
            col_cfg[label] = st.column_config.TextColumn(label, disabled=True)
        elif tech_col in ["data_contract", "data_inceput", "data_sfarsit"]:
            col_cfg[label] = st.column_config.DateColumn(label, format="YYYY-MM-DD")
        elif tech_col == "durata":
            col_cfg[label] = st.column_config.NumberColumn(label, format="%d", min_value=0)
        elif tech_col == "status":
            col_cfg[label] = st.column_config.SelectboxColumn(label, options=status_list)
        elif tech_col == "observatii":
            col_cfg[label] = st.column_config.TextColumn(label, width="large")
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

    di_e = row[fields_map.get("data_inceput", "DATA DE INCEPUT")]
    ds_e = row[fields_map.get("data_sfarsit", "DATA DE SFARSIT")]
    dur_e = int(row[fields_map.get("durata", "DURATA")]) if row[fields_map.get("durata", "DURATA")] else 0

    if di_e and ds_e:
        dur_e = calc_durata(di_e, ds_e)
        st.caption(f"📅 Durată calculată automat: {dur_e} luni")
    elif di_e and dur_e and not ds_e:
        ds_e = add_months(di_e, dur_e)
        st.caption(f"📅 Data de sfarsit calculată automat: {ds_e}")
    elif ds_e and dur_e and not di_e:
        di_e = sub_months(ds_e, dur_e)
        st.caption(f"📅 Data de inceput calculată automat: {di_e}")

    # Construim rezultatul pentru salvare
    rezultat = {
        "cod_identificare": cod_introdus,
        "denumire_categorie": cat_sel,
        "acronim_tip_contract": tip_label,
        "data_contract": fmt_date(row[fields_map.get("data_contract", "DATA CONTRACTULUI")]) if "data_contract" in fields_map else None,
        "obiectul_contractului": row[fields_map.get("obiect", "OBIECT")] if "obiect" in fields_map else None,
        "denumire_beneficiar": row[fields_map.get("beneficiar", "BENEFICIAR")] if "beneficiar" in fields_map else None,
        "data_inceput": fmt_date(di_e),
        "data_sfarsit": fmt_date(ds_e),
        "durata": dur_e if dur_e else None,
        "status_contract_proiect": row[fields_map.get("status", "STATUS")] if "status" in fields_map else None,
    }
    
    if "observatii" in fields_map:
        rezultat["observatii"] = row[fields_map["observatii"]] if row[fields_map["observatii"]] else None
    
    return rezultat
