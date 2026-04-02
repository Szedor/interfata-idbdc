# modules/admin/contract_proiect_like/contract_proiect_like_tehnic.py

from __future__ import annotations

from typing import Any

import pandas as pd

from modules.admin.admin_helpers import prepare_empty_single_row


def _sanitize_nan(v: Any) -> Any:
    """Înlocuiește NaN cu None."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    return v


def build_contract_proiect_like_tehnic_df(
    *,
    df_tehnic_source: pd.DataFrame,
    cols_tehnic: list[str] | None = None,
    cod: str,
    config: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Builder standard pentru tabul de Aspecte tehnice din familia:
      - CEP
      - TERTI
      - SPECIALE
      - FDI
      - INTERNATIONALE
      - INTERREG
      - NONEU
      - SEE

    🔧 FIX: elimină NaN din DataFrame înainte de returnare
    """
    _ = config  # păstrat pentru extinderi ulterioare

    cols_tehnic = cols_tehnic or []

    if not df_tehnic_source.empty:
        df_out = df_tehnic_source.copy()
    elif cols_tehnic:
        df_out = prepare_empty_single_row(cols_tehnic, cod)
    else:
        df_out = pd.DataFrame([{"cod_identificare": cod}])

    if "cod_identificare" in df_out.columns:
        df_out["cod_identificare"] = cod

    # 🔧 FIX: înlocuiește NaN cu None în întregul DataFrame
    df_out = df_out.applymap(_sanitize_nan)

    return df_out


def normalize_contract_proiect_like_tehnic_df(
    *,
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normalizare minimă, non-invazivă, pentru editor.
    🔧 FIX: elimină NaN înainte de randare
    """
    out = df.copy()

    if "cod_identificare" in out.columns:
        out["cod_identificare"] = out["cod_identificare"].fillna("").astype(str)

    # 🔧 FIX: înlocuiește NaN cu None
    out = out.applymap(_sanitize_nan)

    return out


def prepare_contract_proiect_like_tehnic_for_editor(
    *,
    df_tehnic_source: pd.DataFrame,
    cols_tehnic: list[str] | None = None,
    cod: str,
    config: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Wrapper folosit de builder:
      1. construiește DF-ul tehnic standard;
      2. aplică normalizarea minimă pentru editor.
    """
    df_out = build_contract_proiect_like_tehnic_df(
        df_tehnic_source=df_tehnic_source,
        cols_tehnic=cols_tehnic,
        cod=cod,
        config=config,
    )

    return normalize_contract_proiect_like_tehnic_df(df=df_out)
