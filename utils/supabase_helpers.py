# =========================================================
# utils/supabase_helpers.py
# v.modul.1.0 - Funcții ajutătoare pentru interogări Supabase
# =========================================================

from supabase import Client

def safe_select_eq(supabase: Client, table: str, col: str, value: str, limit: int = 2000) -> list:
    """Execută o interogare SELECT * FROM table WHERE col = value, cu limită."""
    try:
        res = supabase.table(table).select("*").eq(col, value).limit(limit).execute()
        return res.data or []
    except Exception:
        return []
