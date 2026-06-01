# =========================================================
# IDBDC/domenii/_baza/upsert.py
# v.modul.1.1 - Elimină an_referinta pentru com_date_financiare
# =========================================================

import streamlit as st
import pandas as pd


TABELE_FARA_AUDIT = {
    "com_date_financiare",
    "com_aspecte_tehnice",
    "com_echipe_proiect",
}


def _cleanup(row_dict: dict, table_name: str) -> dict:
    # data_ultimei_modificari este gestionat exclusiv de un trigger in BD — nu se trimite din Python
    exclude = {"id", "creat_la", "modificat_la", "data_ultimei_modificari"}
    
    # Pentru tabela com_date_financiare, eliminăm și an_referinta (dacă există)
    if table_name == "com_date_financiare":
        exclude.add("an_referinta")
    
    if table_name in TABELE_FARA_AUDIT:
        exclude |= {"creat_de", "modificat_de"}
    
    return {
        k: v for k, v in row_dict.items()
        if k not in exclude and v is not None and not (isinstance(v, float) and pd.isna(v))
    }


def upsert_row(supabase, table_name: str, row_data: dict, match_col="cod_identificare"):
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


def delete_all_for_project(supabase, table_name: str, cod: str):
    try:
        supabase.table(table_name).delete().eq("cod_identificare", cod).execute()
        return True, "Succes"
    except Exception as e:
        return False, str(e)


def insert_rows(supabase, table_name: str, rows: list):
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
