from __future__ import annotations

from datetime import datetime, date
from typing import Any, Iterable

import pandas as pd


def now_iso() -> str:
    """Returnează timestamp ISO pentru audit/update."""
    return datetime.now().isoformat()


def current_year() -> int:
    """Returnează anul curent."""
    return datetime.now().year


def fmt_numeric(val: Any) -> str:
    """
    Formatează numeric în stil românesc:
    - separator mii: .
    - separator zecimal: ,
    - 2 zecimale
    """
    if val is None:
        return ""
    try:
        f = float(str(val).replace(",", ".").strip())
        return f"{f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return str(val)


def is_date_col(col: str) -> bool:
    """
    Detectează coloanele de tip dată după nume.
    Exclude explicit coloanele care nu trebuie tratate ca date editabile.
    """
    c = (col or "").lower()
    if c in {"data_ultimei_modificari"}:
        return False
    return c.startswith("data_") or c.endswith("_data") or c.startswith("dt_")


def is_year_col(col: str) -> bool:
    """Detectează coloanele care reprezintă an/an_*."""
    c = (col or "").lower()
    return c == "an" or c.startswith("an_")


def is_numeric_col(col: str, df: pd.DataFrame) -> bool:
    """
    Detectează coloane numerice după:
    - convenția numelui
    - dtype-ul DataFrame-ului
    """
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
    """
    Construiește un rând gol cu valori implicite minime.
    """
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
    """
    Construiește un DataFrame cu un singur rând gol,
    inițializat cu cod_identificare dacă există coloana.
    """
    if not cols:
        return pd.DataFrame()

    row = empty_row(cols)
    if "cod_identificare" in row:
        row["cod_identificare"] = cod

    df = pd.DataFrame([row], columns=cols)

    for c in df.columns:
        if is_date_col(c):
            df[c] = df[c].apply(
                lambda v: None if v is None else (v if isinstance(v, date) else None)
            )

    return df


def append_observatii(existing: str | None, msg: str) -> str:
    """
    Adaugă un mesaj nou în câmpul de observații.
    """
    base = (existing or "").strip()
    if not base:
        return msg
    return base + "\n" + msg


def to_float_safe(val: Any) -> float | None:
    """
    Conversie robustă la float.
    Acceptă și formate de tip:
    - 1234.56
    - 1234,56
    - 1.234,56
    """
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
    """
    Reordonează coloanele:
    - păstrează întâi coloanele prioritare existente
    - elimină opțional anumite coloane
    """
    if df is None or df.empty:
        return df

    cols = [c for c in df.columns if not drop_cols or c not in drop_cols]
    ordered = [c for c in priority_cols if c in cols]
    ordered += [c for c in cols if c not in ordered]

    return df[ordered]


def fmt_bool(v: Any) -> str:
    """Formatează boolean pentru afișare."""
    return "DA" if bool(v) else "NU"


def is_row_effectively_empty(row_data: dict[str, Any]) -> bool:
    """
    În forma actuală, rândul este considerat util doar dacă are cod_identificare.
    Păstrăm exact aceeași logică din motorul existent.
    """
    cod = row_data.get("cod_identificare")
    if cod is None:
        return True
    if isinstance(cod, str) and cod.strip() == "":
        return True
    return False


def cleanup_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Curăță payload-ul înainte de persistare:
    - elimină None
    - elimină stringuri goale
    - păstrează controlat nr_crt
    - normalizează cod_identificare
    """
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
    """
    Construiește DataFrame-ul financiar FDI și calculează total_buget
    = suma_aprobata_mec + cofinantare_upt_fdi
    """
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
