from __future__ import annotations

from typing import Any

import pandas as pd

from modules.admin.admin_helpers import to_float_safe
from modules.admin.admin_config import STANDARD_FINANCIAL_FIELDS


def get_standard_financial_fields() -> list[str]:
    """
    Returnează lista standard de câmpuri financiare comune.
    """
    return list(STANDARD_FINANCIAL_FIELDS)


def build_empty_financial_row(
    cod_identificare: str | None = None,
    extra_fields: list[str] | None = None,
) -> dict[str, Any]:
    """
    Construiește un rând financiar gol, neutru.
    """
    fields = ["cod_identificare"] + get_standard_financial_fields()
    if extra_fields:
        fields.extend([field for field in extra_fields if field not in fields])

    row = {field: None for field in fields}
    if cod_identificare:
        row["cod_identificare"] = cod_identificare

    return row


def build_empty_financial_df(
    cod_identificare: str | None = None,
    extra_fields: list[str] | None = None,
) -> pd.DataFrame:
    """
    Construiește un DataFrame financiar gol cu un singur rând.
    """
    row = build_empty_financial_row(
        cod_identificare=cod_identificare,
        extra_fields=extra_fields,
    )
    return pd.DataFrame([row])


def normalize_financial_payload(
    payload: dict[str, Any] | None,
    cod_identificare: str | None = None,
    extra_fields: list[str] | None = None,
) -> dict[str, Any]:
    """
    Normalizează payload-ul financiar la schema standard.
    """
    base = build_empty_financial_row(
        cod_identificare=cod_identificare,
        extra_fields=extra_fields,
    )

    if not payload:
        return base

    for key, value in payload.items():
        if key in base:
            base[key] = value

    if cod_identificare and not base.get("cod_identificare"):
        base["cod_identificare"] = cod_identificare

    return base


def normalize_financial_df(
    df_source: pd.DataFrame | None,
    cod_identificare: str | None = None,
    extra_fields: list[str] | None = None,
) -> pd.DataFrame:
    """
    Normalizează un DataFrame financiar la schema standard și păstrează doar primul rând.
    """
    if df_source is None or df_source.empty:
        return build_empty_financial_df(
            cod_identificare=cod_identificare,
            extra_fields=extra_fields,
        )

    row = df_source.iloc[0].to_dict()
    normalized = normalize_financial_payload(
        payload=row,
        cod_identificare=cod_identificare,
        extra_fields=extra_fields,
    )

    return pd.DataFrame([normalized])


def calculate_total_from_components(
    payload: dict[str, Any],
    component_fields: list[str],
) -> float:
    """
    Calculează totalul ca sumă a unor câmpuri componente.
    Valorile lipsă sunt tratate ca 0.
    """
    total = 0.0

    for field in component_fields:
        value = to_float_safe(payload.get(field))
        total += value or 0.0

    return total


def inject_total_field(
    payload: dict[str, Any],
    target_field: str,
    component_fields: list[str],
) -> dict[str, Any]:
    """
    Scrie totalul calculat într-un câmp țintă și returnează payload-ul.
    """
    result = dict(payload)
    result[target_field] = calculate_total_from_components(result, component_fields)
    return result


def dataframe_row_to_financial_payload(df_source: pd.DataFrame | None) -> dict[str, Any]:
    """
    Extrage primul rând dintr-un DataFrame financiar sub formă de dict.
    """
    if df_source is None or df_source.empty:
        return {}

    return dict(df_source.iloc[0].to_dict())


def build_financial_section_data(
    df_source: pd.DataFrame | None,
    cod_identificare: str | None = None,
    extra_fields: list[str] | None = None,
) -> dict[str, Any]:
    """
    Produce payload-ul standard pentru secțiunea financiară.
    """
    normalized_df = normalize_financial_df(
        df_source=df_source,
        cod_identificare=cod_identificare,
        extra_fields=extra_fields,
    )

    return {
        "type": "table",
        "rows": normalized_df.to_dict(orient="records"),
        "columns": list(normalized_df.columns),
    }


def has_financial_content(payload: dict[str, Any] | None, fields: list[str] | None = None) -> bool:
    """
    Verifică dacă există cel puțin un câmp financiar completat.
    """
    if not payload:
        return False

    candidate_fields = fields or get_standard_financial_fields()

    for field in candidate_fields:
        value = payload.get(field)
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        return True

    return False
