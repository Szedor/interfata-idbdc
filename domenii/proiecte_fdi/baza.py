# =========================================================
# IDBDC/domenii/proiecte_fdi/baza.py
# VERSIUNE: 1.1
# STATUS: CORECTAT - ordinea câmpurilor identică cu maparea
# DATA: 2026.06.01
# =========================================================
# MODIFICĂRI VERSIUNEA 1.1:
#   - Ordinea câmpurilor în row_init și col_cfg respectă
#     exact ordinea din maparea oficială:
#     1. CATEGORIE
#     2. TIPUL DE PROIECT
#     3. COD FINAL ÎNREGISTRARE
#     4. TITLUL PROIECTULUI
#     5. ACRONIMUL PROIECTULUI
#     6. DATA DE INCEPUT
#     7. DATA DE SFARSIT
#     8. DURATA (luni)
#     9. STATUS CONTRACT
#    10. PROGRAM DE FINANTARE
#    11. DOMENIU
#    12. COD DEPUNERE
#    13. OBSERVATII
#   - Corectat câmpul returnat: acronim_tip_proiecte
#     (nu acronim_tip_contract — greșit pentru proiecte)
# =========================================================

import streamlit as st
import pandas as pd

from core.helpers import to_date, calc_durata, add_months, sub_months, fmt_date


# ── Cache nomenclatoare ────────────────────────────────────────────────

@st.cache_data(show_spinner=False, ttl=600)
def _get_status_list(_supabase):
    try:
        res = _supabase.table("nom_status_proiect") \
            .select("status_contract_proiect").execute()
        return [
            r["status_contract_proiect"]
            for r in (res.data or [])
            if r.get("status_contract_proiect")
        ]
    except Exception:
        return []


@st.cache_data(show_spinner=False, ttl=600)
def _get_domenii_fdi(_supabase):
    try:
        res = _supabase.table("nom_domenii_fdi") \
            .select("cod_domeniu_fdi") \
            .order("cod_domeniu_fdi").execute()
        return [
            r["cod_domeniu_fdi"]
            for r in (res.data or [])
            if r.get("cod_domeniu_fdi")
        ]
    except Exception:
        return []


# ── Funcție principală ─────────────────────────────────────────────────

def render(supabase, cod_introdus, cat_sel, tip_label, tabela_nume, is_new, date_existente):
    """
    Randează și colectează Date de bază pentru Proiecte FDI.
    Ordinea câmpurilor respectă exact maparea oficială.
    """
    status_list  = _get_status_list(supabase)
    domenii_list = _get_domenii_fdi(supabase)

    # ── Calcul inițial date ────────────────────────────────────────────
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

    # ── Domeniu FDI: asigurăm că valoarea existentă e în listă ────────
    domeniu_ex = date_existente.get("cod_domeniu_fdi", "") or ""
    if domeniu_ex and domeniu_ex not in domenii_list:
        domenii_list = [domeniu_ex] + domenii_list
    domenii_options = [""] + domenii_list

    # ── Construire rând inițial — ORDINEA EXACTĂ DIN MAPARE ───────────
    # 1. CATEGORIE
    # 2. TIPUL DE PROIECT
    # 3. COD FINAL ÎNREGISTRARE
    # 4. TITLUL PROIECTULUI
    # 5. ACRONIMUL PROIECTULUI
    # 6. DATA DE INCEPUT
    # 7. DATA DE SFARSIT
    # 8. DURATA (luni)
    # 9. STATUS CONTRACT
    # 10. PROGRAM DE FINANTARE
    # 11. DOMENIU
    # 12. COD DEPUNERE
    # 13. OBSERVATII
    row_init = {
        "CATEGORIE":                    cat_sel,
        "TIPUL DE PROIECT":             tip_label,
        "🆔 COD FINAL ÎNREGISTRARE":    cod_introdus,
        "🏷️ TITLUL PROIECTULUI":        date_existente.get("titlul_proiect", "") or "",
        "🏷️ ACRONIMUL PROIECTULUI":     date_existente.get("acronim_proiect", "") or "",
        "📅 DATA DE INCEPUT":           di,
        "📅 DATA DE SFARSIT":           ds,
        "DURATA (luni)":                int(dur_ex) if dur_ex else 0,
        "🔖 STATUS PROIECT":            date_existente.get("status_contract_proiect", "") or "",
        "🏷️ PROGRAM DE FINANȚARE":      date_existente.get("program", "") or "",
        "🔖 DOMENIU":                   domeniu_ex,
        "🏷️ COD DEPUNERE":              date_existente.get("cod_temporar", "") or "",
        "🏷️ OBSERVAȚII":               date_existente.get("observatii", "") or "",
    }
    df = pd.DataFrame([row_init])

    # ── Configurare coloane — ACEEAȘI ORDINE ──────────────────────────
    col_cfg = {
        "CATEGORIE": st.column_config.TextColumn(
            "CATEGORIE", disabled=True
        ),
        "TIPUL DE PROIECT": st.column_config.TextColumn(
            "TIPUL DE PROIECT", disabled=True
        ),
        "🆔 COD FINAL ÎNREGISTRARE": st.column_config.TextColumn(
            "🆔 COD FINAL ÎNREGISTRARE", disabled=True
        ),
        "🏷️ TITLUL PROIECTULUI": st.column_config.TextColumn(
            "🏷️ TITLUL PROIECTULUI", width="large"
        ),
        "🏷️ ACRONIMUL PROIECTULUI": st.column_config.TextColumn(
            "🏷️ ACRONIMUL PROIECTULUI"
        ),
        "📅 DATA DE INCEPUT": st.column_config.DateColumn(
            "📅 DATA DE INCEPUT", format="YYYY-MM-DD"
        ),
        "📅 DATA DE SFARSIT": st.column_config.DateColumn(
            "📅 DATA DE SFARSIT", format="YYYY-MM-DD"
        ),
        "DURATA (luni)": st.column_config.NumberColumn(
            "DURATA (luni)", format="%d", min_value=0
        ),
        "🔖 STATUS PROIECT": st.column_config.SelectboxColumn(
            "🔖 STATUS PROIECT", options=status_list
        ),
        "🏷️ PROGRAM DE FINANȚARE": st.column_config.TextColumn(
            "🏷️ PROGRAM DE FINANȚARE"
        ),
        "🔖 DOMENIU": st.column_config.SelectboxColumn(
            "🔖 DOMENIU", options=domenii_options, required=False
        ),
        "🏷️ COD DEPUNERE": st.column_config.TextColumn(
            "🏷️ COD DEPUNERE"
        ),
        "🏷️ OBSERVAȚII": st.column_config.TextColumn(
            "🏷️ OBSERVAȚII", width="large"
        ),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"{tabela_nume}_baza_proiect_editor_{cod_introdus}",
    )

    st.caption("ℹ️ Durata se calculează automat după salvarea fișei.")

    row = df_edit.iloc[0]

    # ── Recalcul date după editare ─────────────────────────────────────
    di_e  = row["📅 DATA DE INCEPUT"]
    ds_e  = row["📅 DATA DE SFARSIT"]
    dur_e = int(row["DURATA (luni)"]) if row["DURATA (luni)"] else 0

    if di_e and ds_e:
        dur_e = calc_durata(di_e, ds_e)
    elif di_e and dur_e and not ds_e:
        ds_e = add_months(di_e, dur_e)
    elif ds_e and dur_e and not di_e:
        di_e = sub_months(ds_e, dur_e)

    # ── Returnare dict pentru upsert ──────────────────────────────────
    def _str(v):
        return str(v).strip() if v else None

    return {
        "cod_identificare":        cod_introdus,
        "denumire_categorie":      cat_sel,
        "acronim_tip_proiecte":    tip_label,
        "titlul_proiect":          _str(row["🏷️ TITLUL PROIECTULUI"]),
        "acronim_proiect":         _str(row["🏷️ ACRONIMUL PROIECTULUI"]),
        "data_inceput":            fmt_date(di_e),
        "data_sfarsit":            fmt_date(ds_e),
        "durata":                  dur_e if dur_e else None,
        "status_contract_proiect": row["🔖 STATUS PROIECT"] if row["🔖 STATUS PROIECT"] else None,
        "program":                 _str(row["🏷️ PROGRAM DE FINANȚARE"]),
        "cod_domeniu_fdi":         _str(row["🔖 DOMENIU"]),
        "cod_temporar":            _str(row["🏷️ COD DEPUNERE"]),
        "observatii":              _str(row["🏷️ OBSERVAȚII"]),
    }
