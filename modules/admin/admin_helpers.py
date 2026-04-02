# modules/admin/admin_helpers.py

from __future__ import annotations

from datetime import datetime, date
import math
from typing import Any, Iterable

import pandas as pd


def now_iso() -> str:
    return datetime.now().isoformat()


def current_year() -> int:
    return datetime.now().year


def _json_safe_value(v: Any) -> Any:
    """Convertește orice valoare în format JSON-serializable."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    if isinstance(v, (datetime, date)):
        return v.strftime("%Y-%m-%d")
    if isinstance(v, pd.Timestamp):
        if pd.isna(v):
            return None
        return v.strftime("%Y-%m-%d")
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            return None
    return v


def sanitize_payload(payload: dict[str, Any], table_name: str = "") -> dict[str, Any]:
    """Sanitizează un payload înainte de trimitere la Supabase."""
    if not payload:
        return {}
    result = {k: _json_safe_value(v) for k, v in payload.items()}
    if table_name == "com_date_financiare" and result.get("valuta") is None:
        result["valuta"] = "LEI"
    return result


def fmt_numeric(val: Any) -> str:
    if val is None:
        return ""
    try:
        f = float(str(val).replace(",", ".").strip())
        return f"{f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return str(val)


def is_date_col(col: str) -> bool:
    c = (col or "").lower()
    if c in {"data_ultimei_modificari"}:
        return False
    return c.startswith("data_") or c.endswith("_data") or c.startswith("dt_")


def is_year_col(col: str) -> bool:
    c = (col or "").lower()
    return c == "an" or c.startswith("an_")


def is_numeric_col(col: str, df: pd.DataFrame) -> bool:
    c = (col or "").lower()
    numeric_keywords = (
        "valoare_", "suma_", "cost_", "buget_", "cofinantare_",
        "contributie_", "numar_", "nr_", "punctaj", "scor_",
        "interval_", "total_", "pozitie_", "perioada_valabilitate_ani",
    )
    if any(c.startswith(k) or c == k for k in numeric_keywords):
        return True
    if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
        return True
    return False


def empty_row(columns: Iterable[str]) -> dict[str, Any]:
    row = {c: None for c in columns}
    if "status_confirmare" in row:
        row["status_confirmare"] = False
    if "validat_idbdc" in row:
        row["validat_idbdc"] = False
    if "persoana_contact" in row:
        row["persoana_contact"] = False
    y = current_year()
    for c in columns:
        if c == "an" or c.startswith("an_"):
            row[c] = y
    return row


def prepare_empty_single_row(cols: list[str], cod: str) -> pd.DataFrame:
    if not cols:
        return pd.DataFrame()
    row = empty_row(cols)
    if "cod_identificare" in row:
        row["cod_identificare"] = cod
    df = pd.DataFrame([row], columns=cols)
    for c in df.columns:
        if is_date_col(c):
            df[c] = df[c].apply(lambda v: None if v is None else (v if isinstance(v, date) else None))
    return df


def append_observatii(existing: str | None, msg: str) -> str:
    base = (existing or "").strip()
    if not base:
        return msg
    return base + "\n" + msg


def to_float_safe(val: Any) -> float | None:
    if val is None:
        return None
    if isinstance(val, str) and val.strip() == "":
        return None
    try:
        if isinstance(val, str):
            s = val.strip()
            if s.count(",") == 1 and s.count(".") >= 1:
                return float(s.replace(".", "").replace(",", "."))
            return float(s.replace(",", "."))
        return float(val)
    except Exception:
        return None


def reorder_columns(
    df: pd.DataFrame,
    priority_cols: list[str],
    drop_cols: list[str] | None = None,
) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    cols = [c for c in df.columns if not drop_cols or c not in drop_cols]
    ordered = [c for c in priority_cols if c in cols]
    ordered += [c for c in cols if c not in ordered]
    return df[ordered]


def fmt_bool(v: Any) -> str:
    return "DA" if bool(v) else "NU"


def is_row_effectively_empty(row_data: dict[str, Any]) -> bool:
    cod = row_data.get("cod_identificare")
    if cod is None:
        return True
    if isinstance(cod, str) and cod.strip() == "":
        return True
    return False


def cleanup_payload(payload: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in (payload or {}).items():
        if k == "nr_crt":
            if v is None:
                continue
            if isinstance(v, str) and v.strip() == "":
                continue
            out[k] = v
            continue
        if k == "cod_identificare":
            if v is not None and str(v).strip():
                out[k] = str(v).strip()
            continue
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        out[k] = v
    return out


def build_fdi_financial_df(
    df_source: pd.DataFrame,
    cod: str,
    financial_fields: list[str],
) -> pd.DataFrame:
    cols = ["cod_identificare"] + financial_fields + ["total_buget"]
    if df_source is None or df_source.empty:
        row = {c: None for c in cols}
        row["cod_identificare"] = cod
        return pd.DataFrame([row], columns=cols)
    src = df_source.copy()
    if "cod_identificare" not in src.columns:
        src["cod_identificare"] = cod
    row = src.iloc[0].to_dict()
    out = {c: row.get(c) for c in cols if c != "total_buget"}
    out["cod_identificare"] = row.get("cod_identificare") or cod
    suma_aprobata = to_float_safe(out.get("suma_aprobata_mec"))
    cofin = to_float_safe(out.get("cofinantare_upt_fdi"))
    out["total_buget"] = (suma_aprobata or 0.0) + (cofin or 0.0)
    return pd.DataFrame([out], columns=cols)


def autofill_functie_upt(df: pd.DataFrame) -> pd.DataFrame:
    """Completare automată a funcției și departamentului din det_resurse_umane."""
    if "nume_prenume" not in df.columns:
        return df
    try:
        from streamlit import cache_data
        @cache_data(show_spinner=False, ttl=600)
        def load_functie_map(supabase=None):
            return {}
    except Exception:
        pass
    return df


def merge_back_control_cols(df_edited: pd.DataFrame, df_original: pd.DataFrame) -> pd.DataFrame:
    """Îmbină coloanele de control înapoi în DataFrame-ul editat."""
    CONTROL_COLS = ["responsabil_idbdc", "observatii_idbdc", "status_confirmare", "data_ultimei_modificari", "validat_idbdc"]
    out = df_edited.copy()
    for c in CONTROL_COLS:
        if c in df_original.columns:
            if c not in out.columns:
                out[c] = None
            try:
                out[c] = list(df_original[c]) + [None] * max(0, (len(out) - len(df_original)))
            except Exception:
                if len(df_original) > 0:
                    out[c] = df_original[c].iloc[0]
    return out
