# =========================================================
# IDBDC/admin/data_ops.py
# VERSIUNE: 6.2
# STATUS: CORECTAT - creat_de/modificat_de excluse pentru tabele fără audit;
#                    username_sistem folosit la salvare
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Operațiuni asupra datelor pentru Calea2 (Administrare):
#   curățare payload, upsert, salvare globală, ștergere,
#   adăugare observații cu istoric.
#
# MODIFICĂRI VERSIUNEA 6.2:
#   - Definit set TABELE_FARA_AUDIT cu tabelele SQL care nu au
#     coloanele creat_de/modificat_de (ex: com_date_financiare,
#     com_aspecte_tehnice, com_echipe_proiect). Pentru acestea,
#     câmpurile de audit sunt excluse din payload înainte de
#     trimiterea la Supabase, eliminând eroarea PGRST204.
#   - Pentru tabelele base_* (care au coloane de audit),
#     creat_de și modificat_de sunt populate cu
#     st.session_state.operator_username.
#
# MODIFICĂRI VERSIUNEA ANTERIOARA:
#   - Corecție critică sintaxă Supabase (upsert corect)
# =========================================================

import streamlit as st
import pandas as pd
from datetime import datetime


# Tabele SQL care NU au coloanele creat_de / modificat_de
TABELE_FARA_AUDIT = {
    "com_date_financiare",
    "com_aspecte_tehnice",
    "com_echipe_proiect",
}


def now_iso():
    return datetime.now().isoformat()


def normalize_identifier_column(df, column_name="cod_identificare"):
    """Asigură că coloana de legătură este tratată ca string curat."""
    if column_name in df.columns:
        df[column_name] = df[column_name].astype(str).str.strip().replace("nan", "")
    return df


def cleanup_payload(row_dict, table_name=None):
    """Elimină câmpurile sistem sau nule înainte de trimiterea către bază."""
    to_exclude = {"id", "creat_la", "modificat_la"}
    if table_name in TABELE_FARA_AUDIT:
        to_exclude |= {"creat_de", "modificat_de"}
    return {k: v for k, v in row_dict.items() if k not in to_exclude and pd.notnull(v)}


def direct_upsert_single_row(supabase, table_name, row_data, match_col="cod_identificare"):
    """Efectuează insert/update (upsert) corect în Supabase."""
    payload = cleanup_payload(row_data, table_name=table_name)
    if not payload.get(match_col):
        return False, "Lipsă cod identificare."

    if table_name not in TABELE_FARA_AUDIT:
        operator_username = st.session_state.get("operator_username") or "necunoscut"
        payload["modificat_de"] = operator_username
        if not payload.get("creat_de"):
            payload["creat_de"] = operator_username

    try:
        supabase.table(table_name).upsert(payload, on_conflict=match_col).execute()
        return True, "Succes"
    except Exception as e:
        return False, str(e)


def direct_save_all_tables(supabase, cod_id, data_dict, base_table):
    """Salvează centralizat toate tabelele (Bază + Detalii)."""
    if base_table in data_dict:
        df_base = data_dict[base_table]
        if not df_base.empty:
            row = df_base.iloc[0].to_dict()
            row["cod_identificare"] = cod_id
            row["data_ultimei_modificari"] = now_iso()
            ok, msg = direct_upsert_single_row(supabase, base_table, row)
            if not ok:
                return False, f"Eroare Bază: {msg}"

    for t_name, df_det in data_dict.items():
        if t_name == base_table:
            continue

        df_det = normalize_identifier_column(df_det)

        for _, r in df_det.iterrows():
            row_payload = r.to_dict()
            row_payload["cod_identificare"] = cod_id
            if str(row_payload.get("cod_identificare")).strip() in ["", "nan"]:
                continue

            ok, msg = direct_upsert_single_row(supabase, t_name, row_payload)
            if not ok:
                return False, f"Eroare în {t_name}: {msg}"

    return True, "Toate datele au fost salvate cu succes."


def direct_delete_all_tables(supabase, cod_id, all_tables):
    """Șterge fișa din toate tabelele."""
    try:
        for t_name in all_tables:
            supabase.table(t_name).delete().eq("cod_identificare", cod_id).execute()
        return True, "Înregistrare ștearsă."
    except Exception as e:
        return False, str(e)


def append_observatii(old_obs, new_text, user_name):
    """Adaugă observații noi păstrând istoricul."""
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    header = f"--- {user_name} ({timestamp}) ---"
    if not old_obs or str(old_obs) == "nan":
        return f"{header}\n{new_text}"
    return f"{old_obs}\n\n{header}\n{new_text}"
