# =========================================================
# IDBDC/domenii/_baza/upsert.py
# VERSIUNE: 1.0
# STATUS: NOU - salvare Supabase comună tuturor domeniilor
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Funcții de upsert/delete pentru PostgreSQL prin Supabase.
#   TABELE_FARA_AUDIT: tabele care nu au coloanele
#   creat_de/modificat_de — payload-ul este curățat automat
#   pentru acestea, eliminând eroarea PGRST204.
#   Toate celelalte tabele (base_*) primesc creat_de și
#   modificat_de populate cu operator_username din session_state.
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
    if table_name in TABELE_FARA_AUDIT:
        exclude |= {"creat_de", "modificat_de"}
    return {
        k: v for k, v in row_dict.items()
        if k not in exclude and v is not None and not (isinstance(v, float) and pd.isna(v))
    }


def upsert_row(supabase, table_name: str, row_data: dict, match_col: str = "cod_identificare"):
    payload = _cleanup(row_data, table_name)
    if not payload.get(match_col):
        return False, "Lipsă cod identificare."

    if table_name not in TABELE_FARA_AUDIT:
        username = st.session_state.get("operator_username") or "necunoscut"
        payload["modificat_de"] = username
        if not payload.get("creat_de"):
            payload["creat_de"] = username

    try:
        supabase.table(table_name).upsert(payload, on_conflict=match_col).execute()
        return True, "Succes"
    except Exception as e:
        return False, str(e)


def delete_rows(supabase, table_name: str, cod: str):
    try:
        supabase.table(table_name).delete().eq("cod_identificare", cod).execute()
    except Exception:
        pass


def insert_rows(supabase, table_name: str, rows: list):
    if not rows:
        return True, "Nimic de inserat."
    try:
        supabase.table(table_name).insert(rows).execute()
        return True, "Succes"
    except Exception as e:
        return False, str(e)
