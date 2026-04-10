# =========================================================
# IDBDC - MODUL ADMIN - OPERAȚIUNI DATE (admin_data_ops.py)
# Versiune: 1.0 - Logica de salvare și interogare CRUD
# =========================================================

import streamlit as st
import pandas as pd
from datetime import datetime

def now_iso():
    return datetime.now().isoformat()

def current_year():
    return datetime.now().year

def normalize_identifier_column(df, column_name="cod_identificare"):
    """Asigură că coloana de legătură este tratată ca string curat."""
    if column_name in df.columns:
        df[column_name] = df[column_name].astype(str).str.strip()
    return df

def cleanup_payload(row_dict):
    """Elimină câmpurile sistem sau nule înainte de trimiterea către Supabase."""
    to_exclude = {"id", "creat_la", "creat_de", "modificat_la", "modificat_de"}
    return {k: v for k, v in row_dict.items() if k not in to_exclude and pd.notnull(v)}

def direct_upsert_single_row(supabase, table_name, row_data, match_col="cod_identificare"):
    """Efectuează insert/update pentru un singur rând în tabelul specificat."""
    payload = cleanup_payload(row_data)
    if not payload.get(match_col):
        return False, "Lipsă cod identificare."
    
    try:
        res = supabase.table(table_name).upsert(payload, on_conflict=match_col).execute()
        return True, "Succes"
    except Exception as e:
        return False, str(e)

def direct_save_all_tables(supabase, cod_id, data_dict, base_table):
    """
    Salvează în cascadă: Tabel Bază + Tabele Detaliu.
    data_dict: { 'base_table_name': df_baza, 'det_table_1': df_det1, ... }
    """
    # 1. Salvare Tabel Bază
    if base_table in data_dict:
        df_base = data_dict[base_table]
        if not df_base.empty:
            row = df_base.iloc[0].to_dict()
            row["cod_identificare"] = cod_id
            row["data_ultimei_modificari"] = now_iso()
            ok, msg = direct_upsert_single_row(supabase, base_table, row)
            if not ok: return False, f"Eroare Bază: {msg}"

    # 2. Salvare Tabele Detaliu (Echipă, Finanțe, Tehnice)
    # Notă: Aici se pot salva multiple rânduri dacă e cazul
    for t_name, df_det in data_dict.items():
        if t_name == base_table: continue
        
        # Curățare și marcare cu cod_identificare
        df_det = normalize_identifier_column(df_det)
        df_det["cod_identificare"] = cod_id
        
        # Upsert rând cu rând (sau bulk dacă Supabase permite conflict pe multiple rânduri)
        for _, r in df_det.iterrows():
            row_payload = r.to_dict()
            ok, msg = direct_upsert_single_row(supabase, t_name, row_payload)
            if not ok: return False, f"Eroare {t_name}: {msg}"
            
    return True, "Fișa a fost salvată cu succes în toate tabelele."

def direct_delete_all_tables(supabase, cod_id, all_tables):
    """Șterge definitiv înregistrările asociate unui cod din toate tabelele listate."""
    try:
        for t_name in all_tables:
            supabase.table(t_name).delete().eq("cod_identificare", cod_id).execute()
        return True, "Înregistrarea a fost ștearsă din sistem."
    except Exception as e:
        return False, str(e)

def append_observatii(old_obs, new_text, user_name):
    """Logică pentru adăugarea de observații fără a șterge istoricul."""
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    header = f"--- {user_name} ({timestamp}) ---"
    if not old_obs:
        return f"{header}\n{new_text}"
    return f"{old_obs}\n\n{header}\n{new_text}"
