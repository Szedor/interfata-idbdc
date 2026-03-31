from __future__ import annotations

from typing import Any

from modules.admin.admin_config import STANDARD_TECHNICAL_FIELDS


def get_standard_technical_fields() -> list[str]:
    """
    Returnează lista standard de câmpuri tehnice comune.
    """
    return list(STANDARD_TECHNICAL_FIELDS)


def build_empty_technical_payload(
    extra_fields: list[str] | None = None,
) -> dict[str, Any]:
    """
    Construiește payload tehnic gol, neutru.
    """
    fields = get_standard_technical_fields()
    if extra_fields:
        fields.extend([field for field in extra_fields if field not in fields])

    return {field: None for field in fields}


def normalize_technical_payload(
    payload: dict[str, Any] | None,
    extra_fields: list[str] | None = None,
) -> dict[str, Any]:
    """
    Normalizează payload-ul tehnic la schema standard.
    """
    base = build_empty_technical_payload(extra_fields=extra_fields)

    if not payload:
        return base

    for key, value in payload.items():
        if key in base:
            base[key] = value

    return base


def has_technical_content(
    payload: dict[str, Any] | None,
    fields: list[str] | None = None,
) -> bool:
    """
    Verifică dacă există cel puțin un câmp tehnic completat.
    """
    if not payload:
        return False

    candidate_fields = fields or get_standard_technical_fields()

    for field in candidate_fields:
        value = payload.get(field)
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        return True

    return False


def build_technical_section_data(
    payload: dict[str, Any] | None,
    extra_fields: list[str] | None = None,
) -> dict[str, Any]:
    """
    Produce payload-ul standard pentru secțiunea tehnică.
    """
    normalized = normalize_technical_payload(
        payload=payload,
        extra_fields=extra_fields,
    )

    return {
        "type": "form",
        "fields": normalized,
    }


def merge_technical_payloads(
    base_payload: dict[str, Any] | None,
    override_payload: dict[str, Any] | None,
    extra_fields: list[str] | None = None,
) -> dict[str, Any]:
    """
    Combină două payload-uri tehnice.
    Valorile din override suprascriu valorile din base.
    """
    result = normalize_technical_payload(
        payload=base_payload,
        extra_fields=extra_fields,
    )

    if not override_payload:
        return result

    for key, value in override_payload.items():
        if key in result:
            result[key] = value

    return result
