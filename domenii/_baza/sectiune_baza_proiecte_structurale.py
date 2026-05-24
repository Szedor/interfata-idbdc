# =========================================================
# IDBDC/domenii/_baza/sectiune_baza_proiecte_structurale.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.05.23
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


def _fmt_date(v):
    if v is None: return None
    if hasattr(v, 'strftime'): return v.strftime("%Y-%m-%d")
    if hasattr(v, 'isoformat'): return v.isoformat()
    return str(v)


def render(supabase, cod_introdus, cat_sel, tip_label, tabela_nume, is_new, date_existente):
    status_list = _get_status_list(supabase)
    di     = to_date(date_existente.get("data_inceput"))
    ds     = to_date(date_existente.get("data_sfarsit"))
    dur_ex = date_existente.get("durata")
    if di and ds and (dur_ex is None or dur_ex == 0): dur_ex = calc_durata(di, ds)
    elif di and dur_ex and not ds: ds = add_months(di, dur_ex)
    elif ds and dur_ex and not di: di = sub_months(ds, dur_ex)
    if di and ds: dur_ex = calc_durata(di, ds)

    row_init = {
        "CATEGORIE":              cat_sel,
        "TIPUL DE PROIECT":       tip_label,
        "ID PROIECT":             cod_introdus,
        "TITLUL PROIECTULUI":     date_existente.get("titlul_proiect", ""),
        "ACRONIMUL PROIECTULUI":  date_existente.get("acronim_proiect", ""),
        "DATA DE INCEPUT":        di,
        "DATA DE SFARSIT":        ds,
        "DURATA (luni)":          int(dur_ex) if dur_ex else 0,
        "STATUS PROIECT":         date_existente.get("status_contract_proiect", ""),
        "NR.PARTICIPANTI":        date_existente.get("numar_participanti", ""),
        "DENUMIRE PARTICIPANTI":  date_existente.get("denumire_participanti", ""),
        "ROL UPT":                date_existente.get("rol_upt", ""),
        "APELUL":                 date_existente.get("identificare_apel", ""),
        "DATA LIMITA DEPUNERE":   to_date(date_existente.get("data_inchidere_apel")),
        "PROGRAMUL OPERATIONAL":  date_existente.get("programul", ""),
        "AXA SPECIFICA":          date_existente.get("axa_specifica", ""),
        "PRIORITATEA":            date_existente.get("prioritatea", ""),
        "OBIECTIVUL":             date_existente.get("obiectivul", ""),
        "WEBSITE":                date_existente.get("website", ""),
        "OBSERVATII":             date_existente.get("observatii", ""),
    }
    df = pd.DataFrame([row_init])

    col_cfg = {
        "CATEGORIE":             st.column_config.TextColumn("CATEGORIE", disabled=True),
        "TIPUL DE PROIECT":      st.column_config.TextColumn("TIPUL DE PROIECT", disabled=True),
        "ID PROIECT":            st.column_config.TextColumn("ID PROIECT", disabled=True),
        "TITLUL PROIECTULUI":    st.column_config.TextColumn("TITLUL PROIECTULUI", width="large"),
        "ACRONIMUL PROIECTULUI": st.column_config.TextColumn("ACRONIMUL PROIECTULUI"),
        "DATA DE INCEPUT":       st.column_config.DateColumn("📅 DATA DE INCEPUT", format="YYYY-MM-DD"),
        "DATA DE SFARSIT":       st.column_config.DateColumn("📅 DATA DE SFARSIT", format="YYYY-MM-DD"),
        "DURATA (luni)":         st.column_config.NumberColumn("DURATA (luni)", format="%d", min_value=0),
        "STATUS PROIECT":        st.column_config.SelectboxColumn("🔖 STATUS PROIECT", options=status_list),
        "NR.PARTICIPANTI":       st.column_config.TextColumn("NR.PARTICIPANTI"),
        "DENUMIRE PARTICIPANTI": st.column_config.TextColumn("DENUMIRE PARTICIPANTI", width="large"),
        "ROL UPT":               st.column_config.TextColumn("ROL UPT"),
        "APELUL":                st.column_config.TextColumn("APELUL"),
        "DATA LIMITA DEPUNERE":  st.column_config.DateColumn("📅 DATA LIMITA DEPUNERE", format="YYYY-MM-DD"),
        "PROGRAMUL OPERATIONAL": st.column_config.TextColumn("PROGRAMUL OPERATIONAL"),
        "AXA SPECIFICA":         st.column_config.TextColumn("AXA SPECIFICA"),
        "PRIORITATEA":           st.column_config.TextColumn("PRIORITATEA", width="large"),
        "OBIECTIVUL":            st.column_config.TextColumn("OBIECTIVUL", width="large"),
        "WEBSITE":               st.column_config.TextColumn("WEBSITE"),
        "OBSERVATII":            st.column_config.TextColumn("📝 OBSERVATII", width="large"),
    }

    df_edit = st.data_editor(df, column_config=col_cfg, hide_index=True,
                              use_container_width=True, num_rows="fixed",
                              key=f"{tabela_nume}_baza_editor_{cod_introdus}")
    row = df_edit.iloc[0]
    st.caption("ℹ️ Durata se calculează automat după salvarea fișei.")

    di_e  = row["DATA DE INCEPUT"]
    ds_e  = row["DATA DE SFARSIT"]
    dur_e = int(row["DURATA (luni)"]) if row["DURATA (luni)"] else 0
    if di_e and ds_e: dur_e = calc_durata(di_e, ds_e)
    elif di_e and dur_e and not ds_e: ds_e = add_months(di_e, dur_e)
    elif ds_e and dur_e and not di_e: di_e = sub_months(ds_e, dur_e)

    def _s(v): return str(v).strip() if v else None
    return {
        "cod_identificare":        cod_introdus,
        "denumire_categorie":      cat_sel,
        "acronim_tip_proiecte":    tip_label,
        "titlul_proiect":          _s(row["TITLUL PROIECTULUI"]),
        "acronim_proiect":         _s(row["ACRONIMUL PROIECTULUI"]),
        "data_inceput":            _fmt_date(di_e),
        "data_sfarsit":            _fmt_date(ds_e),
        "durata":                  dur_e if dur_e else None,
        "status_contract_proiect": row["STATUS PROIECT"] if row["STATUS PROIECT"] else None,
        "numar_participanti":      _s(row["NR.PARTICIPANTI"]),
        "denumire_participanti":   _s(row["DENUMIRE PARTICIPANTI"]),
        "rol_upt":                 _s(row["ROL UPT"]),
        "identificare_apel":       _s(row["APELUL"]),
        "data_inchidere_apel":     _fmt_date(row["DATA LIMITA DEPUNERE"]),
        "programul":               _s(row["PROGRAMUL OPERATIONAL"]),
        "axa_specifica":           _s(row["AXA SPECIFICA"]),
        "prioritatea":             _s(row["PRIORITATEA"]),
        "obiectivul":              _s(row["OBIECTIVUL"]),
        "website":                 _s(row["WEBSITE"]),
        "observatii":              _s(row["OBSERVATII"]),
    }
