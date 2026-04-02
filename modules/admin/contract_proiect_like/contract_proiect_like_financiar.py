# modules/admin/contract_proiect_like/contract_proiect_like_financiar.py

from __future__ import annotations

from typing import Any

import pandas as pd

from modules.admin.admin_helpers import (
    build_fdi_financial_df as _build_fdi_financial_df,
    prepare_empty_single_row,
)

FDI_FINANCIAL_FIELDS = [
    "suma_solicitata_fdi",
    "suma_aprobata_mec",
    "cofinantare_upt_fdi",
]

FDI_BASE_PRIORITY_FIELDS = [
    "cod_identificare",
    "denumire_categorie",
    "acronim_contracte_proiecte",
    "cod_domeniu_fdi",
    "abreviere_domeniu_fdi",
    "denumire_domeniu_fdi",
    "status_contract_proiect",
    "titlul_proiect",
    "data_depunere",
    "data_inceput",
    "data_sfarsit",
    "durata_luni",
    "durata",
    "director_proiect",
    "director",
    "director_contract",
    "rol_upt",
    "obiectiv_general",
    "obiective_specifice",
    "activitati_proiect",
    "rezultate_proiect",
    "parteneri",
    "institutii_organizare",
    "comentarii_diverse",
    "comentarii_document",
]


def build_standard_financial_df(
    *,
    df_fin_source: pd.DataFrame,
    cols_fin: list[str] | None = None,
    cod: str,
) -> pd.DataFrame:
    """
    Financiar standard pentru:
      - CEP
      - TERTI
      - SPECIALE
      - INTERNATIONALE
      - INTERREG
      - NONEU
      - SEE

    Dacă nu există date:
      - folosește prepare_empty_single_row(...)
      - fallback minimal cu cod_identificare
    🔧 FIX: adaugă valuta default "LEI" dacă coloana există
    """
    cols_fin = cols_fin or []

    if not df_fin_source.empty:
        df_out = df_fin_source.copy()
    elif cols_fin:
        df_out = prepare_empty_single_row(cols_fin, cod)
    else:
        df_out = pd.DataFrame([{"cod_identificare": cod}])

    if "cod_identificare" in df_out.columns:
        df_out["cod_identificare"] = cod

    # 🔧 FIX: valuta default
    if "valuta" in df_out.columns:
        df_out["valuta"] = df_out["valuta"].fillna("LEI")

    return df_out


def build_fdi_financial_df(
    *,
    df_fin_source: pd.DataFrame,
    cod: str,
) -> pd.DataFrame:
    """
    Wrapper peste helper-ul existent din admin_helpers.py.

    Păstrează comportamentul actual din motor_admin.py:
      - FDI folosește build_fdi_financial_df(...)
      - financiarul FDI este construit pe baza câmpurilor dedicate
    """
    return _build_fdi_financial_df(
        df_fin_source,
        cod,
        FDI_FINANCIAL_FIELDS,
    )


def build_contract_proiect_like_financial_df(
    *,
    df_fin_source: pd.DataFrame,
    df_base_source: pd.DataFrame,
    cod: str,
    tabela_baza: str,
    config: dict[str, Any],
) -> pd.DataFrame:
    """
    Resolver unic pentru financiarul familiei contract_proiect_like.

    Decide:
      - financiar standard;
      - financiar FDI.
    """
    if config.get("uses_fdi_financial", False):
        return build_fdi_financial_df(
            df_fin_source=df_fin_source,
            cod=cod,
        )

    cols_fin = list(df_fin_source.columns) if not df_fin_source.empty else []

    return build_standard_financial_df(
        df_fin_source=df_fin_source,
        cols_fin=cols_fin,
        cod=cod,
    )


def get_fdi_base_priority_fields() -> list[str]:
    """
    Folosit dacă vrei să reordonezi coloanele de bază FDI
    înainte de randare sau salvare.
    """
    return FDI_BASE_PRIORITY_FIELDS.copy()
