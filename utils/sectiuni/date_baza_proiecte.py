# =========================================================
# utils/sectiuni/date_baza_proiecte.py
# VERSIUNE: 1.0
# STATUS: STABIL - Secțiunea DATE DE BAZĂ pentru proiecte
# DATA: 2026.05.04
# =========================================================
# CONȚINUT:
#   Secțiunea DATE DE BAZĂ pentru toate tipurile de proiecte
#   (FDI, PNCDI, PNRR, Internaționale, Interreg, NonUE,
#   SEE, Structurale). Randează tabelul editabil cu datele
#   de bază ale proiectului și returnează datele pentru
#   salvare în PostgreSQL (tabela base_contracte_cep).
#
#   Diferențe față de date_baza.py (contracte):
#   - Eticheta "TIPUL DE PROIECT" în loc de "TIPUL DE CONTRACT"
#   - Eticheta "COD FINAL ÎNREGISTRARE" în loc de "NR.CONTRACT"
#   - Câmpuri specifice proiect: titlul_proiect, acronim_proiect,
#     program, cod_domeniu_fdi, cod_temporar
#   - Nu există câmpul "OBIECTUL CONTRACTULUI" / "BENEFICIAR"
#   - Logică dată reciprocă identică (început ↔ sfârșit ↔ durată)
#
# MODIFICĂRI VERSIUNEA 1.0:
#   - Creare inițială, fișier independent de date_baza.py.
# =========================================================

import streamlit as st
import pandas as pd
from utils.date_helpers import to_date, calc_durata, add_months, sub_months
from utils.supabase_helpers import safe_select_eq


@st.cache_data(show_spinner=False, ttl=600)
def _get_status_list(_supabase):
    """Preia lista de statusuri din nomenclatorul nom_status_proiect."""
    try:
        res = _supabase.table("nom_status_proiect").select(
            "status_contract_proiect"
        ).execute()
        return [
            r["status_contract_proiect"]
            for r in (res.data or [])
            if r.get("status_contract_proiect")
        ]
    except Exception:
        return []


def _fmt_date(date_val):
    """Formatează o dată la șirul ISO 8601 (AAAA-LL-ZZ) sau None."""
    if date_val is None:
        return None
    if pd.isna(date_val):
        return None
    if hasattr(date_val, 'strftime'):
        return date_val.strftime("%Y-%m-%d")
    if hasattr(date_val, 'isoformat'):
        return date_val.isoformat()
    return str(date_val)


def render_date_de_baza_proiect(
    supabase,
    cod_introdus,
    cat_sel,
    tip_label,
    tabela_nume,
    is_new,
    date_existente,
):
    """
    Randare și colectare date de bază pentru orice tip de proiect.

    Parametri:
        supabase      : clientul Supabase
        cod_introdus  : codul identificator (COD FINAL ÎNREGISTRARE)
        cat_sel       : categoria selectată — se inscrie automat ("Proiecte")
        tip_label     : eticheta tipului — se inscrie automat (ex: "FDI")
        tabela_nume   : numele tabelei SQL (ex: "base_contracte_cep")
        is_new        : True dacă este înregistrare nouă
        date_existente: dict cu datele existente din PostgreSQL

    Returnează:
        dict cu valorile pentru salvare în tabela base_contracte_cep
    """
    status_list = _get_status_list(supabase)

    # ── Citire date existente ──────────────────────────────────
    di     = to_date(date_existente.get("data_inceput"))
    ds     = to_date(date_existente.get("data_sfarsit"))
    dur_ex = date_existente.get("durata")

    # ── Calcule automate dată reciprocă ───────────────────────
    # Regula: dacă lipsește una din cele trei valori, se calculează
    # din celelalte două. Prioritate: dacă există toate trei,
    # durata se recalculează din date.
    if di and ds and (dur_ex is None or dur_ex == 0):
        dur_ex = calc_durata(di, ds)
    elif di and dur_ex and not ds:
        ds = add_months(di, dur_ex)
    elif ds and dur_ex and not di:
        di = sub_months(ds, dur_ex)
    if di and ds:
        dur_ex = calc_durata(di, ds)

    # ── Construire rând inițial ────────────────────────────────
    row_init = {
        "CATEGORIE":             cat_sel,           # automat
        "TIPUL DE PROIECT":      tip_label,          # automat
        "COD FINAL ÎNREGISTRARE": cod_introdus,       # automat / readonly
        "TITLUL PROIECTULUI":    date_existente.get("titlul_proiect", ""),
        "ACRONIMUL PROIECTULUI": date_existente.get("acronim_proiect", ""),
        "DATA DE INCEPUT":       di,
        "DATA DE SFARSIT":       ds,
        "DURATA (nr.luni)":      int(dur_ex) if dur_ex else 0,
        "STATUS PROIECT":        date_existente.get("status_contract_proiect", ""),
        "PROGRAM DE FINANTARE":  date_existente.get("program", ""),
        "DOMENIU":               date_existente.get("cod_domeniu_fdi", ""),
        "COD DEPUNERE":          date_existente.get("cod_temporar", ""),
        "OBSERVATII":            date_existente.get("observatii", ""),
    }
    df = pd.DataFrame([row_init])

    # ── Configurare coloane editor ─────────────────────────────
    col_cfg = {
        "CATEGORIE": st.column_config.TextColumn(
            "CATEGORIE", disabled=True
        ),
        "TIPUL DE PROIECT": st.column_config.TextColumn(
            "TIPUL DE PROIECT", disabled=True
        ),
        "COD FINAL ÎNREGISTRARE": st.column_config.TextColumn(
            "COD FINAL ÎNREGISTRARE", disabled=True
        ),
        "TITLUL PROIECTULUI": st.column_config.TextColumn(
            "TITLUL PROIECTULUI", width="large"
        ),
        "ACRONIMUL PROIECTULUI": st.column_config.TextColumn(
            "ACRONIMUL PROIECTULUI"
        ),
        "DATA DE INCEPUT": st.column_config.DateColumn(
            "📅 DATA DE INCEPUT", format="YYYY-MM-DD"
        ),
        "DATA DE SFARSIT": st.column_config.DateColumn(
            "📅 DATA DE SFARSIT", format="YYYY-MM-DD"
        ),
        "DURATA (nr.luni)": st.column_config.NumberColumn(
            "DURATA (nr.luni)", format="%d", min_value=0
        ),
        "STATUS PROIECT": st.column_config.SelectboxColumn(
            "🔖 STATUS PROIECT", options=status_list
        ),
        "PROGRAM DE FINANTARE": st.column_config.TextColumn(
            "PROGRAM DE FINANTARE"
        ),
        "DOMENIU": st.column_config.TextColumn(
            "DOMENIU"
        ),
        "COD DEPUNERE": st.column_config.TextColumn(
            "COD DEPUNERE"
        ),
        "OBSERVATII": st.column_config.TextColumn(
            "📝 OBSERVATII", width="large"
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
    row = df_edit.iloc[0]

    # ── Calcule automate post-editare ─────────────────────────
    di_e  = row["DATA DE INCEPUT"]
    ds_e  = row["DATA DE SFARSIT"]
    dur_e = int(row["DURATA (nr.luni)"]) if row["DURATA (nr.luni)"] else 0

    if di_e and ds_e:
        dur_e = calc_durata(di_e, ds_e)
        st.caption(f"📅 Durată calculată automat: {dur_e} luni")
    elif di_e and dur_e and not ds_e:
        ds_e = add_months(di_e, dur_e)
        st.caption(f"📅 Data de sfârșit calculată automat: {_fmt_date(ds_e)}")
    elif ds_e and dur_e and not di_e:
        di_e = sub_months(ds_e, dur_e)
        st.caption(f"📅 Data de început calculată automat: {_fmt_date(di_e)}")

    # ── Returnare dict pentru salvare PostgreSQL ───────────────
    return {
        "cod_identificare":       cod_introdus,
        "denumire_categorie":     cat_sel,
        "acronim_tip_proiecte":   tip_label,
        "titlul_proiect":         str(row["TITLUL PROIECTULUI"]).strip()    if row["TITLUL PROIECTULUI"]    else None,
        "acronim_proiect":        str(row["ACRONIMUL PROIECTULUI"]).strip() if row["ACRONIMUL PROIECTULUI"] else None,
        "data_inceput":           _fmt_date(di_e),
        "data_sfarsit":           _fmt_date(ds_e),
        "durata":                 dur_e if dur_e else None,
        "status_contract_proiect": row["STATUS PROIECT"] if row["STATUS PROIECT"] else None,
        "program":                str(row["PROGRAM DE FINANTARE"]).strip() if row["PROGRAM DE FINANTARE"] else None,
        "cod_domeniu_fdi":        str(row["DOMENIU"]).strip()              if row["DOMENIU"]              else None,
        "cod_temporar":           str(row["COD DEPUNERE"]).strip()         if row["COD DEPUNERE"]         else None,
        "observatii":             str(row["OBSERVATII"]).strip()           if row["OBSERVATII"]           else None,
    }
