# =========================================================
# IDBDC/domenii/_baza/upsert.py
# VERSIUNE: 1.1
# STATUS: CORECTAT - suport pentru chei primare compuse
# DATA: 2026.05.27
# =========================================================
# MODIFICĂRI VERSIUNEA 1.1:
#   - Adăugat suport pentru chei primare compuse în upsert
#   - Parametrul on_conflict poate fi string (coloană unică)
#     sau listă/tuplu (cheie compusă)
#   - Pentru com_date_financiare: on_conflict = ["cod_identificare", "an_referinta"]
#   - Adăugat delete_all_for_project() pentru ștergere completă
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


def upsert_row(supabase, table_name: str, row_data: dict, match_col = "cod_identificare"):
    """
    Upsert cu suport pentru chei primare compuse.
    
    Args:
        match_col: poate fi:
            - string: o singură coloană (ex: "cod_identificare")
            - list/tuple: cheie compusă (ex: ["cod_identificare", "an_referinta"])
    """
    payload = _cleanup(row_data, table_name)
    
    # Verificăm că toate coloanele cheie sunt prezente
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
        supabase.table(table_name).upsert(payload, on_conflict=match_col).execute()
        return True, "Succes"
    except Exception as e:
        return False, str(e)


def delete_rows(supabase, table_name: str, cod: str, extra_condition: dict = None):
    """
    Șterge rânduri dintr-un tabel.
    
    Args:
        extra_condition: dicționar cu condiții suplimentare (ex: {"an_referinta": "2024"})
    """
    try:
        query = supabase.table(table_name).delete().eq("cod_identificare", cod)
        if extra_condition:
            for col, val in extra_condition.items():
                query = query.eq(col, val)
        query.execute()
    except Exception:
        pass


def delete_all_for_project(supabase, table_name: str, cod: str):
    """Șterge toate înregistrările unui proiect dintr-un tabel."""
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
