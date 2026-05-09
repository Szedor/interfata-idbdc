# =========================================================
# IDBDC/admin/data_ops.py
# VERSIUNE: 6.1
# STATUS: CORECTAT - creat_de/modificat_de populate cu username operator
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Operațiuni asupra datelor pentru Calea2 (Administrare):
#   curățare payload, upsert, salvare globală, ștergere,
#   adăugare observații cu istoric.
#
# MODIFICĂRI VERSIUNEA 6.1:
#   - CORECȚIE: funcția cleanup_payload nu mai elimină câmpurile
#     `creat_de` și `modificat_de` dacă acestea sunt deja populate.
#   - CORECȚIE: funcția direct_upsert_single_row completează
#     automat câmpurile `creat_de` și `modificat_de` cu
#     username-ul operatorului din st.session_state.operator_username
#     înainte de trimiterea payload-ului la Supabase.
#     Logica aplicată:
#       • `modificat_de` se actualizează la FIECARE salvare.
#       • `creat_de` se completează DOAR dacă înregistrarea
#         este nouă (nu există deja în baza de date).
#     Fără această corecție, Supabase completa aceste câmpuri
#     cu utilizatorul de conexiune implicit (`anon`), deoarece
#     aplicația nu trimitea nicio valoare.
#
# MODIFICĂRI VERSIUNEA 1.1:
#   - Corecție critică sintaxă Supabase (upsert corect)
# =========================================================

import streamlit as st
import pandas as pd
from datetime import datetime


def now_iso():
    return datetime.now().isoformat()


def normalize_identifier_column(df, column_name="cod_identificare"):
    """Asigură că coloana de legătură este tratată ca string curat."""
    if column_name in df.columns:
        df[column_name] = df[column_name].astype(str).str.strip().replace("nan", "")
    return df


def cleanup_payload(row_dict):
    """
    Elimină câmpurile sistem sau nule înainte de trimiterea către bază.
    CORECȚIE [v1.2]: câmpurile `creat_de` și `modificat_de` NU mai sunt
    excluse automat — ele vor fi completate de direct_upsert_single_row
    cu username-ul operatorului autentificat.
    Sunt excluse în continuare: `id`, `creat_la`, `modificat_la`
    (acestea sunt gestionate de Supabase prin triggerele SQL).
    """
    # CORECȚIE [v1.2]: eliminat creat_de și modificat_de din lista de excludere
    to_exclude = {"id", "creat_la", "modificat_la"}
    return {k: v for k, v in row_dict.items() if k not in to_exclude and pd.notnull(v)}


def direct_upsert_single_row(supabase, table_name, row_data, match_col="cod_identificare"):
    """
    Efectuează insert/update (upsert) corect în Supabase.
    CORECȚIE [v1.2]: completează creat_de și modificat_de cu
    username-ul operatorului autentificat din session_state.
    """
    payload = cleanup_payload(row_data)
    if not payload.get(match_col):
        return False, "Lipsă cod identificare."

    # CORECȚIE [v1.2]: preluăm username-ul operatorului autentificat
    operator_username = st.session_state.get("operator_username") or "necunoscut"

    # CORECȚIE [v1.2]: completăm modificat_de la fiecare salvare
    payload["modificat_de"] = operator_username

    # CORECȚIE [v1.2]: completăm creat_de doar dacă nu există deja
    # (la prima inserare). La update, valoarea existentă se păstrează
    # prin logica upsert — câmpul este trimis numai dacă nu este deja setat.
    if not payload.get("creat_de"):
        payload["creat_de"] = operator_username

    try:
        supabase.table(table_name).upsert(payload, on_conflict=match_col).execute()
        return True, "Succes"
    except Exception as e:
        return False, str(e)


def direct_save_all_tables(supabase, cod_id, data_dict, base_table):
    """Salvează centralizat toate tabelele (Bază + Detalii)."""
    # 1. Salvare Tabel Bază
    if base_table in data_dict:
        df_base = data_dict[base_table]
        if not df_base.empty:
            row = df_base.iloc[0].to_dict()
            row["cod_identificare"] = cod_id
            row["data_ultimei_modificari"] = now_iso()
            ok, msg = direct_upsert_single_row(supabase, base_table, row)
            if not ok:
                return False, f"Eroare Bază: {msg}"

    # 2. Salvare Tabele Detaliu
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
