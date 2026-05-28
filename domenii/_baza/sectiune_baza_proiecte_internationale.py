# =========================================================
# IDBDC/domenii/_baza/sectiune_baza_proiecte_internationale.py
# VERSIUNE: 1.5
# STATUS: ACTUALIZAT - ROL UPT din nom_rol_upt (BD), eliminat ROL_UPT_OPTIONS hardcodat
# DATA: 2026.05.28
# =========================================================
# MODIFICARI VERSIUNEA 1.5:
#   - ROL UPT: dropdown alimentat din tabela nom_rol_upt
#     coloana tehnica rol_upt (in loc de lista hardcodata)
#   - Eliminat complet ROL_UPT_OPTIONS
#   - Adaugat _get_rol_upt_list() cu cache 600s
#   - Logica de fallback: daca valoarea existenta nu e in lista
#     se pastreaza ca prima optiune (nu se pierde)
# =========================================================

import streamlit as st
import pandas as pd
from datetime import date as _date
from utils.date_helpers import to_date, calc_durata, add_months, sub_months


@st.cache_data(show_spinner=False, ttl=600)
def _get_status_list(_supabase):
    try:
        res = _supabase.table("nom_status_proiect").select("status_contract_proiect").execute()
        return [r["status_contract_proiect"] for r in (res.data or []) if r.get("status_contract_proiect")]
    except Exception:
        return []


@st.cache_data(show_spinner=False, ttl=600)
def _get_rol_upt_list(_supabase):
    try:
        res = _supabase.table("nom_rol_upt").select("rol_upt").order("id").execute()
        return [r["rol_upt"] for r in (res.data or []) if r.get("rol_upt")]
    except Exception:
        return []


def _fmt_date(v):
    if v is None:
        return None
    if hasattr(v, 'strftime'):
        return v.strftime("%Y-%m-%d")
    if hasattr(v, 'isoformat'):
        return v.isoformat()
    s = str(v).strip()
    return s if s not in ("", "None", "nan") else None


def _safe_date(v):
    if v is None:
        return None
    if isinstance(v, _date):
        return v
    try:
        return to_date(v)
    except Exception:
        return None


def _safe_int(v):
    if v is None:
        return 0
    try:
        f = float(str(v).replace(",", ".").strip())
        return int(f)
    except (ValueError, TypeError):
        return 0


def _safe_str(v):
    if v is None:
        return ""
    return str(v).strip()


def render(supabase, cod_introdus, cat_sel, tip_label, tabela_nume, is_new, date_existente):
    status_list   = _get_status_list(supabase)
    rol_upt_list  = _get_rol_upt_list(supabase)

    di     = _safe_date(date_existente.get("data_inceput"))
    ds     = _safe_date(date_existente.get("data_sfarsit"))
    dur_ex = _safe_int(date_existente.get("durata"))

    if di and ds and not dur_ex:
        dur_ex = calc_durata(di, ds)
    elif di and dur_ex and not ds:
        ds = add_months(di, dur_ex)
    elif ds and dur_ex and not di:
        di = sub_months(ds, dur_ex)
    if di and ds:
        dur_ex = calc_durata(di, ds)

    rol_upt_initial = _safe_str(date_existente.get("rol_upt"))
    # Daca valoarea existenta nu e in lista (ex: date vechi), o adaugam temporar
    if rol_upt_initial and rol_upt_initial not in rol_upt_list:
        rol_upt_options = [rol_upt_initial] + rol_upt_list
    else:
        rol_upt_options = rol_upt_list if rol_upt_list else [""]

    if not rol_upt_initial or rol_upt_initial not in rol_upt_options:
        rol_upt_initial = rol_upt_options[0] if rol_upt_options else ""

    row_init = {
        "CATEGORIE":             cat_sel,
        "TIPUL DE PROIECT":      tip_label,
        "ID PROIECT":            cod_introdus,
        "TITLUL PROIECTULUI":    _safe_str(date_existente.get("titlul_proiect")),
        "ACRONIMUL PROIECTULUI": _safe_str(date_existente.get("acronim_proiect")),
        "DATA DE INCEPUT":       di,
        "DATA DE SFARSIT":       ds,
        "DURATA (luni)":         dur_ex,
        "STATUS PROIECT":        _safe_str(date_existente.get("status_contract_proiect")),
        "SCOR EVALUARE":         _safe_str(date_existente.get("scor_evaluare")),
        "NR.PARTICIPANTI":       _safe_str(date_existente.get("numar_participanti")),
        "DENUMIRE PARTICIPANTI": _safe_str(date_existente.get("denumire_participanti")),
        "ROL UPT":               rol_upt_initial,
        "APELUL":                _safe_str(date_existente.get("identificare_apel")),
        "DATA LIMITA DEPUNERE":  _safe_date(date_existente.get("data_inchidere_apel")),
        "PROGRAM DE FINANTARE":  _safe_str(date_existente.get("program_finantare")),
        "TEMA / TOPIC":          _safe_str(date_existente.get("tema_topic")),
        "SCHEMA DE FINANTARE":   _safe_str(date_existente.get("schema_de_finantare")),
        "WEBSITE":               _safe_str(date_existente.get("website")),
        "OBSERVATII":            _safe_str(date_existente.get("observatii")),
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
        "SCOR EVALUARE":         st.column_config.TextColumn("SCOR EVALUARE"),
        "NR.PARTICIPANTI":       st.column_config.TextColumn("NR.PARTICIPANTI"),
        "DENUMIRE PARTICIPANTI": st.column_config.TextColumn("DENUMIRE PARTICIPANTI", width="large"),
        "ROL UPT":               st.column_config.SelectboxColumn("ROL UPT", options=rol_upt_options),
        "APELUL":                st.column_config.TextColumn("APELUL"),
        "DATA LIMITA DEPUNERE":  st.column_config.DateColumn("📅 DATA LIMITA DEPUNERE", format="YYYY-MM-DD"),
        "PROGRAM DE FINANTARE":  st.column_config.TextColumn("PROGRAM DE FINANTARE"),
        "TEMA / TOPIC":          st.column_config.TextColumn("TEMA / TOPIC", width="large"),
        "SCHEMA DE FINANTARE":   st.column_config.TextColumn("SCHEMA DE FINANTARE"),
        "WEBSITE":               st.column_config.TextColumn("WEBSITE"),
        "OBSERVATII":            st.column_config.TextColumn("📝 OBSERVATII", width="large"),
    }

    df_edit = st.data_editor(
        df, column_config=col_cfg, hide_index=True,
        use_container_width=True, num_rows="fixed",
        key=f"{tabela_nume}_baza_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]
    st.caption("ℹ️ Durata se calculează automat după salvarea fișei.")

    di_e  = row["DATA DE INCEPUT"]
    ds_e  = row["DATA DE SFARSIT"]
    dur_e = _safe_int(row["DURATA (luni)"])

    if di_e and ds_e:
        dur_e = calc_durata(di_e, ds_e)
    elif di_e and dur_e and not ds_e:
        ds_e = add_months(di_e, dur_e)
    elif ds_e and dur_e and not di_e:
        di_e = sub_months(ds_e, dur_e)

    def _s(v):
        return str(v).strip() if v else None

    return {
        "cod_identificare":        cod_introdus,
        "denumire_categorie":      cat_sel,
        "acronim_tip_proiecte":    tip_label,
        "titlul_proiect":          _s(row["TITLUL PROIECTULUI"]),
        "acronim_proiect":         _s(row["ACRONIMUL PROIECTULUI"]),
        "data_inceput":            _fmt_date(di_e),
        "data_sfarsit":            _fmt_date(ds_e),
        "durata":                  dur_e if dur_e else None,
        "status_contract_proiect": _s(row["STATUS PROIECT"]),
        "scor_evaluare":           _s(row["SCOR EVALUARE"]),
        "numar_participanti":      _s(row["NR.PARTICIPANTI"]),
        "denumire_participanti":   _s(row["DENUMIRE PARTICIPANTI"]),
        "rol_upt":                 _s(row["ROL UPT"]),
        "identificare_apel":       _s(row["APELUL"]),
        "data_inchidere_apel":     _fmt_date(row["DATA LIMITA DEPUNERE"]),
        "program_finantare":       _s(row["PROGRAM DE FINANTARE"]),
        "tema_topic":              _s(row["TEMA / TOPIC"]),
        "schema_de_finantare":     _s(row["SCHEMA DE FINANTARE"]),
        "website":                 _s(row["WEBSITE"]),
        "observatii":              _s(row["OBSERVATII"]),
    }
