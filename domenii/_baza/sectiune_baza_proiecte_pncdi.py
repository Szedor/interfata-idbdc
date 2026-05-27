# =========================================================
# IDBDC/domenii/_baza/sectiune_baza_proiecte_pncdi.py
# VERSIUNE: 1.1
# STATUS: CORECTAT - forțare tip datetime pentru DateColumn
# DATA: 2026.05.27
# =========================================================
# MODIFICĂRI VERSIUNEA 1.1:
#   - CORECȚIE: după salvare și reîncărcare din Supabase,
#     coloanele de dată veneau ca string și Streamlit nou
#     (Python 3.13) arunca StreamlitAPIException la
#     _check_type_compatibilities. Adăugat _force_date_cols()
#     care convertește explicit toate coloanele DateColumn
#     la dtype datetime64 în DataFrame înainte de data_editor.
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
    if pd.isna(v) if not isinstance(v, str) else False: return None
    if hasattr(v, 'strftime'): return v.strftime("%Y-%m-%d")
    if hasattr(v, 'isoformat'): return v.isoformat()
    s = str(v).strip()
    return s if s not in ("", "None", "nan", "NaT") else None


def _force_date_cols(df, cols):
    """Forțează coloanele de dată la obiecte datetime.date sau None —
    necesar pentru compatibilitate cu st.column_config.DateColumn în Streamlit nou."""
    for col in cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda v: to_date(v) if v is not None and str(v).strip() not in ("", "nan", "NaT") else None)
    return df


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
        "CATEGORIE":                cat_sel,
        "TIPUL DE PROIECT":         tip_label,
        "COD PROIECT":              cod_introdus,
        "DATA CONTRACT":            to_date(date_existente.get("data_contract")),
        "TITLUL PROIECTULUI":       date_existente.get("titlul_proiect", ""),
        "ACRONIMUL PROIECTULUI":    date_existente.get("acronim_proiect", ""),
        "DOMENIUL DE CERCETARE":    date_existente.get("domeniu_cercetare", ""),
        "DATA DE INCEPUT":          di,
        "DATA DE SFARSIT":          ds,
        "DURATA (luni)":            int(dur_ex) if dur_ex else 0,
        "STATUS PROIECT":           date_existente.get("status_contract_proiect", ""),
        "NR.PARTICIPANTI":          date_existente.get("numar_participanti", ""),
        "DENUMIRE PARTICIPANTI":    date_existente.get("denumire_participanti", ""),
        "ROL UPT":                  date_existente.get("rol_upt", ""),
        "APELUL":                   date_existente.get("identificare_apel", ""),
        "DATA LIMITA DEPUNERE":     to_date(date_existente.get("data_inchidere_apel")),
        "PROGRAMUL":                date_existente.get("programul", ""),
        "SUBPROGRAMUL":             date_existente.get("subprogramul", ""),
        "INSTRUMENTUL DE FINANTARE": date_existente.get("instrument_finantare", ""),
        "WEBSITE":                  date_existente.get("website", ""),
        "OBSERVATII":               date_existente.get("observatii", ""),
    }
    df = pd.DataFrame([row_init])
    df = _force_date_cols(df, ["DATA CONTRACT", "DATA DE INCEPUT", "DATA DE SFARSIT", "DATA LIMITA DEPUNERE"])

    col_cfg = {
        "CATEGORIE":                 st.column_config.TextColumn("CATEGORIE", disabled=True),
        "TIPUL DE PROIECT":          st.column_config.TextColumn("TIPUL DE PROIECT", disabled=True),
        "COD PROIECT":               st.column_config.TextColumn("COD PROIECT", disabled=True),
        "DATA CONTRACT":             st.column_config.DateColumn("📅 DATA CONTRACT", format="YYYY-MM-DD"),
        "TITLUL PROIECTULUI":        st.column_config.TextColumn("TITLUL PROIECTULUI", width="large"),
        "ACRONIMUL PROIECTULUI":     st.column_config.TextColumn("ACRONIMUL PROIECTULUI"),
        "DOMENIUL DE CERCETARE":     st.column_config.TextColumn("DOMENIUL DE CERCETARE"),
        "DATA DE INCEPUT":           st.column_config.DateColumn("📅 DATA DE INCEPUT", format="YYYY-MM-DD"),
        "DATA DE SFARSIT":           st.column_config.DateColumn("📅 DATA DE SFARSIT", format="YYYY-MM-DD"),
        "DURATA (luni)":             st.column_config.NumberColumn("DURATA (luni)", format="%d", min_value=0),
        "STATUS PROIECT":            st.column_config.SelectboxColumn("🔖 STATUS PROIECT", options=status_list),
        "NR.PARTICIPANTI":           st.column_config.TextColumn("NR.PARTICIPANTI"),
        "DENUMIRE PARTICIPANTI":     st.column_config.TextColumn("DENUMIRE PARTICIPANTI", width="large"),
        "ROL UPT":                   st.column_config.TextColumn("ROL UPT"),
        "APELUL":                    st.column_config.TextColumn("APELUL"),
        "DATA LIMITA DEPUNERE":      st.column_config.DateColumn("📅 DATA LIMITA DEPUNERE", format="YYYY-MM-DD"),
        "PROGRAMUL":                 st.column_config.TextColumn("PROGRAMUL"),
        "SUBPROGRAMUL":              st.column_config.TextColumn("SUBPROGRAMUL"),
        "INSTRUMENTUL DE FINANTARE": st.column_config.TextColumn("INSTRUMENTUL DE FINANTARE"),
        "WEBSITE":                   st.column_config.TextColumn("WEBSITE"),
        "OBSERVATII":                st.column_config.TextColumn("📝 OBSERVATII", width="large"),
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
        "data_contract":           _fmt_date(row["DATA CONTRACT"]),
        "titlul_proiect":          _s(row["TITLUL PROIECTULUI"]),
        "acronim_proiect":         _s(row["ACRONIMUL PROIECTULUI"]),
        "domeniu_cercetare":       _s(row["DOMENIUL DE CERCETARE"]),
        "data_inceput":            _fmt_date(di_e),
        "data_sfarsit":            _fmt_date(ds_e),
        "durata":                  dur_e if dur_e else None,
        "status_contract_proiect": row["STATUS PROIECT"] if row["STATUS PROIECT"] else None,
        "numar_participanti":      _s(row["NR.PARTICIPANTI"]),
        "denumire_participanti":   _s(row["DENUMIRE PARTICIPANTI"]),
        "rol_upt":                 _s(row["ROL UPT"]),
        "identificare_apel":       _s(row["APELUL"]),
        "data_inchidere_apel":     _fmt_date(row["DATA LIMITA DEPUNERE"]),
        "programul":               _s(row["PROGRAMUL"]),
        "subprogramul":            _s(row["SUBPROGRAMUL"]),
        "instrument_finantare":    _s(row["INSTRUMENTUL DE FINANTARE"]),
        "website":                 _s(row["WEBSITE"]),
        "observatii":              _s(row["OBSERVATII"]),
    }
