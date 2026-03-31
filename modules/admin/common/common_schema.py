from __future__ import annotations

from typing import Any

from modules.admin.admin_config import (
    TAB_ASPECTE_TEHNICE,
    TAB_DATE_FINANCIARE,
    TAB_DATE_GENERALE,
    TAB_DOCUMENTE,
    TAB_OBSERVATII,
    TAB_ORGANIZARE,
    TAB_PARTENERI,
    TAB_PROPRIETATE,
    TAB_REZULTATE,
)


SCHEMA_VERSION = "1.0"


DEFAULT_SECTION_ORDER = [
    TAB_DATE_GENERALE,
    TAB_ASPECTE_TEHNICE,
    TAB_DATE_FINANCIARE,
    TAB_REZULTATE,
    TAB_DOCUMENTE,
    TAB_OBSERVATII,
    TAB_PARTENERI,
    TAB_ORGANIZARE,
    TAB_PROPRIETATE,
]


def build_base_admin_payload(
    entity_type: str,
    entity_id: str | int | None = None,
    cod_identificare: str | None = None,
) -> dict[str, Any]:
    """
    Payload minim standard pentru noua arhitectură admin.
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "cod_identificare": cod_identificare,
        "sections": [],
        "meta": {},
    }


def build_meta_payload(
    family: str | None = None,
    active_tabs: list[str] | None = None,
    editable: bool = True,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Meta-informații standard pentru payload-ul admin.
    """
    meta = {
        "family": family,
        "active_tabs": list(active_tabs or []),
        "editable": editable,
    }

    if extra:
        meta.update(extra)

    return meta


def with_sections(
    payload: dict[str, Any],
    sections: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Atașează lista de secțiuni la payload.
    """
    result = dict(payload)
    result["sections"] = list(sections or [])
    return result


def with_meta(
    payload: dict[str, Any],
    meta: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Atașează blocul meta la payload.
    """
    result = dict(payload)
    result["meta"] = dict(meta or {})
    return result


def build_admin_payload(
    *,
    entity_type: str,
    entity_id: str | int | None = None,
    cod_identificare: str | None = None,
    sections: list[dict[str, Any]] | None = None,
    family: str | None = None,
    active_tabs: list[str] | None = None,
    editable: bool = True,
    meta_extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Constructor complet pentru payload-ul standard admin.
    """
    payload = build_base_admin_payload(
        entity_type=entity_type,
        entity_id=entity_id,
        cod_identificare=cod_identificare,
    )

    payload = with_sections(payload, sections or [])
    payload = with_meta(
        payload,
        build_meta_payload(
            family=family,
            active_tabs=active_tabs,
            editable=editable,
            extra=meta_extra,
        ),
    )

    return payload


def get_section_order_index(section_key: str) -> int:
    """
    Returnează indexul standard al unei secțiuni.
    Secțiunile necunoscute merg la final.
    """
    try:
        return DEFAULT_SECTION_ORDER.index(section_key)
    except ValueError:
        return len(DEFAULT_SECTION_ORDER)


def sort_sections(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Sortează secțiunile după ordinea standard.
    """
    return sorted(
        sections or [],
        key=lambda section: get_section_order_index(section.get("key", "")),
    )


def filter_visible_sections(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Păstrează doar secțiunile vizibile.
    Dacă cheia 'visible' lipsește, secțiunea este considerată vizibilă.
    """
    result: list[dict[str, Any]] = []

    for section in sections or []:
        if section.get("visible", True):
            result.append(section)

    return result


def get_section_by_key(
    sections: list[dict[str, Any]],
    section_key: str,
) -> dict[str, Any] | None:
    """
    Returnează prima secțiune cu cheia cerută.
    """
    for section in sections or []:
        if section.get("key") == section_key:
            return section
    return None


def upsert_section(
    sections: list[dict[str, Any]],
    new_section: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Înlocuiește secțiunea cu aceeași cheie sau o adaugă dacă nu există.
    """
    result: list[dict[str, Any]] = []
    target_key = new_section.get("key")
    replaced = False

    for section in sections or []:
        if section.get("key") == target_key:
            result.append(new_section)
            replaced = True
        else:
            result.append(section)

    if not replaced:
        result.append(new_section)

    return result


def normalize_sections_payload(
    sections: list[dict[str, Any]] | None,
    *,
    visible_only: bool = False,
    sort: bool = True,
) -> list[dict[str, Any]]:
    """
    Normalizează lista de secțiuni pentru payload-ul final.
    """
    result = list(sections or [])

    if visible_only:
        result = filter_visible_sections(result)

    if sort:
        result = sort_sections(result)

    return result
