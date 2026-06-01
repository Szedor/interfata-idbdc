# =========================================================
# IDBDC/domenii/proiecte_internationale/baza.py
# VERSIUNE: 1.1
# STATUS: CORECTAT - etichete vizuale și ordine exacte din mapare
# DATA: 2026.06.01
# =========================================================
# DATE DE BAZĂ — ordinea și etichetele exacte din mapare:
#  1. CATEGORIE
#  2. TIPUL DE PROIECT
#  3. ID PROIECT
#  4. TITLUL PROIECTULUI
#  5. ACRONIMUL PROIECTULUI
#  6. DATA DE INCEPUT              ← 📅
#  7. DATA DE SFARSIT              ← 📅
#  8. DURATA (luni)
#  9. STATUS PROIECT               ← 🔖
# 10. SCOR EVALUARE
# 11. NR.PARTICIPANTI
# 12. DENUMIRE PARTICIPANTI
# 13. ROL UPT                      ← 🔖
# 14. APELUL
# 15. DATA LIMITA DEPUNERE         ← 📅
# 16. PROGRAM DE FINANTARE
# 17. TEMA / TOPIC
# 18. SCHEMA DE FINANTARE
# 19. WEBSITE
# 20. OBSERVATII
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


@st.cache_data(show_spinner=False, ttl=600)
def _get_rol_upt_list(_supabase):
    try:
        res = _supabase.table("nom_rol_upt").select("rol_upt").execute()
        return [r["rol_upt"] for r in (res.data or []) if r.get("rol_upt")]
    except Exception:
        return []


def render(supabase, cod_introdus, cat_sel, tip_label, tabela_nume, is_new, date_existente):
    status_list  = _get_status_list(supabase)
    rol_upt_list = _get_rol_upt_list(supabase)

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
        "CATEGORIE":                cat_sel,
        "TIPUL DE PROIECT":         tip_label,
        "ID PROIECT":               cod_introdus,
        "TITLUL PROIECTULUI":       date_existente.get("titlul_proiect", "") or "",
        "ACRONIMUL PROIECTULUI":    date_existente.get("acronim_proiect", "") or "",
        "📅 DATA DE INCEPUT":       di,
        "📅 DATA DE SFARSIT":       ds,
        "DURATA (luni)":            int(dur_ex) if dur_ex else 0,
        "🔖 STATUS PROIECT":        date_existente.get("status_contract_proiect", "") or "",
        "SCOR EVALUARE":            date_existente.get("scor_evaluare", "") or "",
        "NR.PARTICIPANTI":          date_existente.get("numar_participanti", "") or "",
        "DENUMIRE PARTICIPANTI":    date_existente.get("denumire_participanti", "") or "",
        "🔖 ROL UPT":               date_existente.get("rol_upt", "") or "",
        "APELUL":                   date_existente.get("identificare_apel", "") or "",
        "📅 DATA LIMITA DEPUNERE":  to_date(date_existente.get("data_inchidere_apel")),
        "PROGRAM DE FINANTARE":     date_existente.get("program_finantare", "") or "",
        "TEMA / TOPIC":             date_existente.get("tema_topic", "") or "",
        "SCHEMA DE FINANTARE":      date_existente.get("schema_de_finantare", "") or "",
        "WEBSITE":                  date_existente.get("website", "") or "",
        "OBSERVATII":               date_existente.get("observatii", "") or "",
    }
    df = pd.DataFrame([row_init])

    col_cfg = {
        "CATEGORIE":             st.column_config.TextColumn("CATEGORIE", disabled=True),
        "TIPUL DE PROIECT":      st.column_config.TextColumn("TIPUL DE PROIECT", disabled=True),
        "ID PROIECT":            st.column_config.TextColumn("ID PROIECT", disabled=True),
        "TITLUL PROIECTULUI":    st.column_config.TextColumn("TITLUL PROIECTULUI", width="large"),
        "ACRONIMUL PROIECTULUI": st.column_config.TextColumn("ACRONIMUL PROIECTULUI"),
        "📅 DATA DE INCEPUT":    st.column_config.DateColumn("📅 DATA DE INCEPUT", format="YYYY-MM-DD"),
        "📅 DATA DE SFARSIT":    st.column_config.DateColumn("📅 DATA DE SFARSIT", format="YYYY-MM-DD"),
        "DURATA (luni)":         st.column_config.NumberColumn("DURATA (luni)", format="%d", min_value=0),
        "🔖 STATUS PROIECT":     st.column_config.SelectboxColumn("🔖 STATUS PROIECT", options=status_list),
        "SCOR EVALUARE":         st.column_config.TextColumn("SCOR EVALUARE"),
        "NR.PARTICIPANTI":       st.column_config.NumberColumn("NR.PARTICIPANTI", format="%d", min_value=0),
        "DENUMIRE PARTICIPANTI": st.column_config.TextColumn("DENUMIRE PARTICIPANTI", width="large"),
        "🔖 ROL UPT":            st.column_config.SelectboxColumn("🔖 ROL UPT", options=rol_upt_list),
        "APELUL":                st.column_config.TextColumn("APELUL"),
        "📅 DATA LIMITA DEPUNERE": st.column_config.DateColumn("📅 DATA LIMITA DEPUNERE", format="YYYY-MM-DD"),
        "PROGRAM DE FINANTARE":  st.column_config.TextColumn("PROGRAM DE FINANTARE"),
        "TEMA / TOPIC":          st.column_config.TextColumn("TEMA / TOPIC", width="large"),
        "SCHEMA DE FINANTARE":   st.column_config.TextColumn("SCHEMA DE FINANTARE"),
        "WEBSITE":               st.column_config.LinkColumn("WEBSITE"),
        "OBSERVATII":            st.column_config.TextColumn("OBSERVATII", width="large"),
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

    def _int(v):
        try:
            return int(v) if v else None
        except (TypeError, ValueError):
            return None

    return {
        "cod_identificare":        cod_introdus,
        "denumire_categorie":      cat_sel,
        "acronim_tip_proiecte":    tip_label,
        "titlul_proiect":          _str(row["TITLUL PROIECTULUI"]),
        "acronim_proiect":         _str(row["ACRONIMUL PROIECTULUI"]),
        "data_inceput":            fmt_date(di_e),
        "data_sfarsit":            fmt_date(ds_e),
        "durata":                  dur_e if dur_e else None,
        "status_contract_proiect": row["🔖 STATUS PROIECT"] if row["🔖 STATUS PROIECT"] else None,
        "scor_evaluare":           _str(row["SCOR EVALUARE"]),
        "numar_participanti":      _int(row["NR.PARTICIPANTI"]),
        "denumire_participanti":   _str(row["DENUMIRE PARTICIPANTI"]),
        "rol_upt":                 row["🔖 ROL UPT"] if row["🔖 ROL UPT"] else None,
        "identificare_apel":       _str(row["APELUL"]),
        "data_inchidere_apel":     fmt_date(row["📅 DATA LIMITA DEPUNERE"]),
        "program_finantare":       _str(row["PROGRAM DE FINANTARE"]),
        "tema_topic":              _str(row["TEMA / TOPIC"]),
        "schema_de_finantare":     _str(row["SCHEMA DE FINANTARE"]),
        "website":                 _str(row["WEBSITE"]),
        "observatii":              _str(row["OBSERVATII"]),
    }
