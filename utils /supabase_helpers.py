# IDBDC - Utilitare pentru interogări Supabase
from supabase import Client

def safe_select_eq(supabase: Client, table: str, col: str, value: str, limit: int = 2000) -> list:
    try:
        res = supabase.table(table).select("*").eq(col, value).limit(limit).execute()
        return res.data or []
    except Exception:
        return []

def fetch_columns(supabase: Client, table: str) -> list:
    try:
        res = supabase.rpc("idbdc_get_columns", {"p_table": table}).execute()
        return [r["column_name"] for r in (res.data or []) if r.get("column_name")]
    except Exception:
        return []
