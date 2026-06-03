# =========================================================
# IDBDC/domenii/proiecte_pncdi/baza.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.06.02
# =========================================================
# DATE DE BAZĂ — ordinea și etichetele exacte din mapare:
#  1. CATEGORIE
#  2. TIPUL DE PROIECT
#  3. COD PROIECT
#  4. DATA CONTRACT                ← 📅
#  5. TITLUL PROIECTULUI
#  6. ACRONIMUL PROIECTULUI
#  7. DOMENIUL DE CERCETARE
#  8. DATA DE INCEPUT              ← 📅
#  9. DATA DE SFARSIT              ← 📅
# 10. DURATA (luni)
# 11. STATUS PROIECT               ← 🔖
# 12. NR.PARTICIPANTI
# 13. DENUMIRE PARTICIPANTI
# 14. ROL UPT                      ← 🔖
# 15. APELUL
# 16. DATA LIMITA DEPUNERE         ← 📅
# 17. PROGRAMUL
# 18. SUBPROGRAMUL
# 19. INSTRUMENTUL DE FINANTARE
# 20. WEBSITE
# 21. OBSERVATII
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
        "CATEGORIE":                  cat_sel,
        "TIPUL DE PROIECT":           tip_label,
        "COD PROIECT":                cod_introdus,
        "📅 DATA CONTRACT":           to_date(date_existente.get("data_contract")),
        "TITLUL PROIECTULUI":         date_existente.get("titlul_proiect", "") or "",
        "ACRONIMUL PROIECTULUI":      date_existente.get("acronim_proiect", "") or "",
        "DOMENIUL DE CERCETARE":      date_existente.get("domeniu_cercetare", "") or "",
        "📅 DATA DE INCEPUT":         di,
        "📅 DATA DE SFARSIT":         ds,
        "DURATA (luni)":              int(dur_ex) if dur_ex else 0,
        "🔖 STATUS PROIECT":          date_existente.get("status_contract_proiect", "") or "",
        "NR.PARTICIPANTI":            date_existente.get("numar_participanti", "") or "",
        "DENUMIRE PARTICIPANTI":      date_existente.get("denumire_participanti", "") or "",
        "🔖 ROL UPT":                 date_existente.get("rol_upt", "") or "",
        "APELUL":                     date_existente.get("identificare_apel", "") or "",
        "📅 DATA LIMITA DEPUNERE":    to_date(date_existente.get("data_inchidere_apel")),
        "PROGRAMUL":                  date_existente.get("programul", "") or "",
        "SUBPROGRAMUL":               date_existente.get("subprogramul", "") or "",
        "INSTRUMENTUL DE FINANTARE":  date_existente.get("instrument_finantare", "") or "",
        "WEBSITE":                    date_existente.get("website", "") or "",
        "OBSERVATII":                 date_existente.get("observatii", "") or "",
    }
    df = pd.DataFrame([row_init])

    col_cfg = {
        "CATEGORIE":                 st.column_config.TextColumn("CATEGORIE", disabled=True),
        "TIPUL DE PROIECT":          st.column_config.TextColumn("TIPUL DE PROIECT", disabled=True),
        "COD PROIECT":               st.column_config.TextColumn("COD PROIECT", disabled=True),
        "📅 DATA CONTRACT":          st.column_config.DateColumn("📅 DATA CONTRACT", format="YYYY-MM-DD"),
        "TITLUL PROIECTULUI":        st.column_config.TextColumn("TITLUL PROIECTULUI", width="large"),
        "ACRONIMUL PROIECTULUI":     st.column_config.TextColumn("ACRONIMUL PROIECTULUI"),
        "DOMENIUL DE CERCETARE":     st.column_config.TextColumn("DOMENIUL DE CERCETARE"),
        "📅 DATA DE INCEPUT":        st.column_config.DateColumn("📅 DATA DE INCEPUT", format="YYYY-MM-DD"),
        "📅 DATA DE SFARSIT":        st.column_config.DateColumn("📅 DATA DE SFARSIT", format="YYYY-MM-DD"),
        "DURATA (luni)":             st.column_config.NumberColumn("DURATA (luni)", format="%d", min_value=0),
        "🔖 STATUS PROIECT":         st.column_config.SelectboxColumn("🔖 STATUS PROIECT", options=status_list),
        "NR.PARTICIPANTI":           st.column_config.NumberColumn("NR.PARTICIPANTI", format="%d", min_value=0),
        "DENUMIRE PARTICIPANTI":     st.column_config.TextColumn("DENUMIRE PARTICIPANTI", width="large"),
        "🔖 ROL UPT":                st.column_config.SelectboxColumn("🔖 ROL UPT", options=rol_upt_list),
        "APELUL":                    st.column_config.TextColumn("APELUL"),
        "📅 DATA LIMITA DEPUNERE":   st.column_config.DateColumn("📅 DATA LIMITA DEPUNERE", format="YYYY-MM-DD"),
        "PROGRAMUL":                 st.column_config.TextColumn("PROGRAMUL"),
        "SUBPROGRAMUL":              st.column_config.TextColumn("SUBPROGRAMUL"),
        "INSTRUMENTUL DE FINANTARE": st.column_config.TextColumn("INSTRUMENTUL DE FINANTARE"),
        "WEBSITE":                   st.column_config.LinkColumn("WEBSITE"),
        "OBSERVATII":                st.column_config.TextColumn("OBSERVATII", width="large"),
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

    def _int(v):
        try:
            return int(v) if v else None
        except (TypeError, ValueError):
            return None

    return {
        "cod_identificare":        cod_introdus,
        "denumire_categorie":      cat_sel,
        "acronim_tip_proiecte":    tip_label,
        "data_contract":           fmt_date(row["📅 DATA CONTRACT"]),
        "titlul_proiect":          _str(row["TITLUL PROIECTULUI"]),
        "acronim_proiect":         _str(row["ACRONIMUL PROIECTULUI"]),
        "domeniu_cercetare":       _str(row["DOMENIUL DE CERCETARE"]),
        "data_inceput":            fmt_date(di_e),
        "data_sfarsit":            fmt_date(ds_e),
        "durata":                  dur_e if dur_e else None,
        "status_contract_proiect": row["🔖 STATUS PROIECT"] if row["🔖 STATUS PROIECT"] else None,
        "numar_participanti":      _int(row["NR.PARTICIPANTI"]),
        "denumire_participanti":   _str(row["DENUMIRE PARTICIPANTI"]),
        "rol_upt":                 row["🔖 ROL UPT"] if row["🔖 ROL UPT"] else None,
        "identificare_apel":       _str(row["APELUL"]),
        "data_inchidere_apel":     fmt_date(row["📅 DATA LIMITA DEPUNERE"]),
        "programul":               _str(row["PROGRAMUL"]),
        "subprogramul":            _str(row["SUBPROGRAMUL"]),
        "instrument_finantare":    _str(row["INSTRUMENTUL DE FINANTARE"]),
        "website":                 _str(row["WEBSITE"]),
        "observatii":              _str(row["OBSERVATII"]),
    }
