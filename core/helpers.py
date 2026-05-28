# =========================================================
# core/helpers.py
# v.modul.1.0 - Funcții comune pentru toată aplicația
# =========================================================

import streamlit as st
import pandas as pd
import calendar as cal_lib
from datetime import date
from supabase import Client

# =========================================================
# DATE HELPERS
# =========================================================
def to_date(val):
    """Convertește o valoare în obiect date, dacă este posibil."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    try:
        return pd.to_datetime(val).date()
    except Exception:
        return None

def calc_durata(d1, d2) -> int:
    """Calculează durata în luni între două date."""
    try:
        luni = (d2.year - d1.year) * 12 + (d2.month - d1.month)
        if d2.day >= d1.day:
            luni += 1
        return max(0, luni)
    except Exception:
        return 0

def add_months(d, luni) -> date:
    """Adaugă un număr de luni la o dată."""
    try:
        m = d.month - 1 + int(luni)
        an = d.year + m // 12
        luna = m % 12 + 1
        zi = min(d.day, cal_lib.monthrange(an, luna)[1])
        return date(an, luna, zi)
    except Exception:
        return None

def sub_months(d, luni) -> date:
    """Scade un număr de luni dintr-o dată."""
    return add_months(d, -int(luni))

def fmt_date(date_val):
    """Convertește o dată în string ISO (YYYY-MM-DD) sau None."""
    if date_val is None:
        return None
    if pd.isna(date_val):
        return None
    if hasattr(date_val, 'strftime'):
        return date_val.strftime("%Y-%m-%d")
    if hasattr(date_val, 'isoformat'):
        return date_val.isoformat()
    return str(date_val)

# =========================================================
# NUMERIC HELPERS
# =========================================================
def fmt_numeric(val, col_name: str = "") -> str:
    """Formatează valorile numerice (cu sau fără zecimale, separator mii)."""
    if val is None:
        return ""
    raw = str(val).strip()
    if raw == "":
        return ""
    try:
        f = float(raw.replace(",", "."))
    except (ValueError, TypeError):
        return raw
    col_name = (col_name or "").lower().strip()
    no_decimal_fields = {
        "cod_identificare", "numar_contract", "nr_contract", "nr_contract_achizitie",
        "nr_contract_subsecvent", "numar_oficial_acordare", "numar_publicare_cerere",
        "numar_data_notificare_intern", "telefon_mobil", "telefon_upt",
        "cod_depunere", "cod_temporar",
    }
    if col_name in no_decimal_fields:
        return str(int(round(f)))
    financial_keys = ("valoare", "buget", "suma", "cost", "contributie", "cofinantare")
    is_financial = any(k in col_name for k in financial_keys)
    if is_financial:
        return f"{f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if f.is_integer():
        return str(int(f))
    return f"{f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =========================================================
# SUPABASE HELPERS
# =========================================================
def safe_select_eq(supabase: Client, table: str, col: str, value: str, limit: int = 2000) -> list:
    """Execută o interogare SELECT * FROM table WHERE col = value, cu limită."""
    try:
        res = supabase.table(table).select("*").eq(col, value).limit(limit).execute()
        return res.data or []
    except Exception:
        return []

# =========================================================
# ETICHETARE
# =========================================================
def col_label(col: str, table: str = None, COL_LABELS: dict = None, COL_LABELS_PER_TABLE: dict = None) -> str:
    """Returnează eticheta vizuală pentru o coloană."""
    if COL_LABELS_PER_TABLE and table and table in COL_LABELS_PER_TABLE:
        if col in COL_LABELS_PER_TABLE[table]:
            return COL_LABELS_PER_TABLE[table][col]
    if COL_LABELS and col in COL_LABELS:
        return COL_LABELS[col]
    return col.replace("_", " ").capitalize()
