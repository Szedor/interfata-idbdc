from __future__ import annotations

from typing import Any

import pandas as pd

from modules.admin.admin_helpers import prepare_empty_single_row


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

    În Etapa 4 păstrăm comportamentul conservator:
      - dacă există date, le returnăm ca atare;
      - dacă nu există date, pregătim un singur rând gol;
      - nu schimbăm schema și nu introducem logică nouă de business.
    """
    _ = config  # păstrat pentru extinderi ulterioare, fără a schimba semnătura

    cols_tehnic = cols_tehnic or []

    if not df_tehnic_source.empty:
        df_out = df_tehnic_source.copy()
    elif cols_tehnic:
        df_out = prepare_empty_single_row(cols_tehnic, cod)
    else:
        df_out = pd.DataFrame([{"cod_identificare": cod}])

    if "cod_identificare" in df_out.columns:
        df_out["cod_identificare"] = cod

    return df_out


def normalize_contract_proiect_like_tehnic_df(
    *,
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normalizare minimă, non-invazivă, pentru editor.
    În această etapă nu modificăm tipuri sau valori în mod agresiv.
    """
    out = df.copy()

    if "cod_identificare" in out.columns:
        out["cod_identificare"] = out["cod_identificare"].fillna("").astype(str)

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
