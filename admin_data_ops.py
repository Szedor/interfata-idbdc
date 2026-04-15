# =========================================================
# IDBDC - MODUL ADMIN - OPERAȚIUNI DATE (admin_data_ops.py)
# Versiune: 1.1 - Corecție critică sintaxă Supabase
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
    """Elimină câmpurile sistem sau nule înainte de trimiterea către bază."""
    to_exclude = {"id", "creat_la", "creat_de", "modificat_la", "modificat_de"}
    return {k: v for k, v in row_dict.items() if k not in to_exclude and pd.notnull(v)}

def direct_upsert_single_row(supabase, table_name, row_data, match_col="cod_identificare"):
    """Efectuează insert/update (upsert) corect în Supabase."""
    payload = cleanup_payload(row_data)
    if not payload.get(match_col):
        return False, "Lipsă cod identificare."
    
    try:
        # Ordinea corectă: .table().upsert()
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
            if not ok: return False, f"Eroare Bază: {msg}"

    # 2. Salvare Tabele Detaliu
    for t_name, df_det in data_dict.items():
        if t_name == base_table: continue
        
        df_det = normalize_identifier_column(df_det)
        
        for _, r in df_det.iterrows():
            row_payload = r.to_dict()
            # Forțăm legătura cu codul principal
            row_payload["cod_identificare"] = cod_id
            if str(row_payload.get("cod_identificare")).strip() in ["", "nan"]:
                continue
                
            ok, msg = direct_upsert_single_row(supabase, t_name, row_payload)
            if not ok: return False, f"Eroare în {t_name}: {msg}"
            
    return True, "Toate datele au fost salvate cu succes."

def direct_delete_all_tables(supabase, cod_id, all_tables):
    """Șterge fișa din toate tabelele. Corecție: .table().delete().eq()"""
    try:
        for t_name in all_tables:
            # Ordinea corectă obligatorie: table -> delete -> filtru
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
