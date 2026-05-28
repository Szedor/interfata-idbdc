# =========================================================
# IDBDC/domenii/_baza/upsert.py
# VERSIUNE: 2.3 - ELIMINARE an_referinta pentru contracte
# DATA: 2026.05.28
# =========================================================

import streamlit as st
import pandas as pd


TABELE_FARA_AUDIT = {
    "com_date_financiare",
    "com_aspecte_tehnice",
    "com_echipe_proiect",
}


def _cleanup(row_dict: dict, table_name: str) -> dict:
    exclude = {"id", "creat_la", "modificat_la"}
    
    # Pentru tabela com_date_financiare, eliminăm și an_referinta (nu există în toate tabelele)
    if table_name == "com_date_financiare":
        exclude.add("an_referinta")
    
    if table_name in TABELE_FARA_AUDIT:
        exclude |= {"creat_de", "modificat_de"}
    
    return {
        k: v for k, v in row_dict.items()
        if k not in exclude and v is not None and not (isinstance(v, float) and pd.isna(v))
    }


def upsert_row(supabase, table_name: str, row_data: dict, match_col="cod_identificare"):
    """
    Upsert cu suport pentru chei primare compuse.

    Args:
        match_col: string sau list/tuple cu coloanele cheie.
    """
    payload = _cleanup(row_data, table_name)

    if isinstance(match_col, (list, tuple)):
        lipsa = [col for col in match_col if not payload.get(col)]
        if lipsa:
            return False, f"Lipsă coloane cheie: {', '.join(lipsa)}"
    else:
        if not payload.get(match_col):
            return False, f"Lipsă {match_col}."

    if table_name not in TABELE_FARA_AUDIT:
        username = st.session_state.get("operator_username") or "necunoscut"
        payload["modificat_de"] = username
        if not payload.get("creat_de"):
            payload["creat_de"] = username

    try:
        on_conflict_str = ",".join(match_col) if isinstance(match_col, (list, tuple)) else match_col
        supabase.table(table_name).upsert(payload, on_conflict=on_conflict_str).execute()
        return True, "Succes"
    except Exception as e:
        return False, str(e)


def upsert_rows_batch(supabase, table_name: str, rows: list, match_col="cod_identificare"):
    """
    Upsert pentru mai multe rânduri simultan.
    """
    if not rows:
        return True, "Nimic de actualizat."

    cleaned_rows = [_cleanup(row, table_name) for row in rows]

    for row in cleaned_rows:
        if isinstance(match_col, (list, tuple)):
            lipsa = [col for col in match_col if not row.get(col)]
            if lipsa:
                return False, f"Lipsă coloane cheie: {', '.join(lipsa)}"
        else:
            if not row.get(match_col):
                return False, f"Lipsă {match_col}."

    if table_name not in TABELE_FARA_AUDIT:
        username = st.session_state.get("operator_username") or "necunoscut"
        for row in cleaned_rows:
            row["modificat_de"] = username
            if not row.get("creat_de"):
                row["creat_de"] = username

    try:
        on_conflict_str = ",".join(match_col) if isinstance(match_col, (list, tuple)) else match_col
        supabase.table(table_name).upsert(cleaned_rows, on_conflict=on_conflict_str).execute()
        return True, "Succes"
    except Exception as e:
        return False, str(e)


def delete_all_for_project(supabase, table_name: str, cod: str):
    """
    Șterge toate înregistrările unui proiect dintr-un tabel.
    Returnează (True, "Succes") sau (False, mesaj_eroare).
    """
    try:
        supabase.table(table_name).delete().eq("cod_identificare", cod).execute()
        return True, "Succes"
    except Exception as e:
        return False, str(e)


def delete_rows(supabase, table_name: str, cod: str, extra_condition: dict = None):
    """
    Șterge rânduri cu condiții suplimentare opționale.
    """
    try:
        query = supabase.table(table_name).delete().eq("cod_identificare", cod)
        if extra_condition:
            for col, val in extra_condition.items():
                query = query.eq(col, val)
        query.execute()
        return True
    except Exception:
        return False


def insert_rows(supabase, table_name: str, rows: list):
    """
    Inserează rândurile unul câte unul pentru a izola erorile.
    Returnează (True, "Succes") sau (False, mesaj_prima_eroare).
    """
    if not rows:
        return True, "Nimic de inserat."

    erori = []
    for row in rows:
        cleaned = _cleanup(row, table_name)
        try:
            supabase.table(table_name).insert(cleaned).execute()
        except Exception as e:
            erori.append(str(e))

    if erori:
        return False, erori[0]
    return True, "Succes"
