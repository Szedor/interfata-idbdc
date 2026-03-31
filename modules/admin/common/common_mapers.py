from __future__ import annotations

from modules.admin.admin_config import (
    CONTRACT_PN_TYPES,
    CONTRACT_PROIECT_LIKE_TYPES,
    ENTITY_TYPE_CONFIG,
    ENTITY_TYPE_LABELS,
    ENTITY_TYPE_TO_FAMILY,
    EVENIMENTE_TYPES,
    FAMILY_CONTRACT_PN,
    FAMILY_CONTRACT_PROIECT_LIKE,
    FAMILY_DEFAULT_TABS,
    FAMILY_EVENIMENTE,
    FAMILY_LABELS,
    FAMILY_PROPRIETATE_INDUSTRIALA,
    PROPRIETATE_INDUSTRIALA_TYPES,
)


def get_family_for_entity_type(entity_type: str | None) -> str | None:
    """
    Returnează familia pentru tipul de entitate.
    """
    if not entity_type:
        return None
    return ENTITY_TYPE_TO_FAMILY.get(entity_type)


def get_entity_label(entity_type: str | None) -> str:
    """
    Returnează eticheta user-facing pentru tipul de entitate.
    Dacă tipul nu este cunoscut, întoarce chiar valoarea primită.
    """
    if not entity_type:
        return ""
    return ENTITY_TYPE_LABELS.get(entity_type, entity_type)


def get_family_label(family: str | None) -> str:
    """
    Returnează eticheta user-facing pentru familie.
    """
    if not family:
        return ""
    return FAMILY_LABELS.get(family, family)


def get_tabs_for_entity_type(entity_type: str | None) -> list[str]:
    """
    Returnează lista de taburi active pentru tipul de entitate.
    """
    if not entity_type:
        return []

    config = ENTITY_TYPE_CONFIG.get(entity_type, {})
    tabs = config.get("tabs", [])
    return list(tabs)


def get_default_tabs_for_family(family: str | None) -> list[str]:
    """
    Returnează taburile implicite pentru o familie.
    """
    if not family:
        return []
    return list(FAMILY_DEFAULT_TABS.get(family, []))


def has_financial_section(entity_type: str | None) -> bool:
    """
    True dacă tipul de entitate are secțiune financiară.
    """
    if not entity_type:
        return False
    return bool(ENTITY_TYPE_CONFIG.get(entity_type, {}).get("has_financial", False))


def has_technical_section(entity_type: str | None) -> bool:
    """
    True dacă tipul de entitate are secțiune tehnică.
    """
    if not entity_type:
        return False
    return bool(ENTITY_TYPE_CONFIG.get(entity_type, {}).get("has_technical", False))


def is_multianual_entity(entity_type: str | None) -> bool:
    """
    True dacă tipul de entitate folosește structură financiară multianuală.
    """
    if not entity_type:
        return False
    return bool(ENTITY_TYPE_CONFIG.get(entity_type, {}).get("is_multianual", False))


def is_contract_proiect_like(entity_type: str | None) -> bool:
    """
    True dacă tipul aparține familiei contract_proiect_like.
    """
    return entity_type in CONTRACT_PROIECT_LIKE_TYPES


def is_contract_pn(entity_type: str | None) -> bool:
    """
    True dacă tipul aparține familiei contract_pn.
    """
    return entity_type in CONTRACT_PN_TYPES


def is_eveniment(entity_type: str | None) -> bool:
    """
    True dacă tipul aparține familiei evenimente.
    """
    return entity_type in EVENIMENTE_TYPES


def is_proprietate_industriala(entity_type: str | None) -> bool:
    """
    True dacă tipul aparține familiei proprietate_industriala.
    """
    return entity_type in PROPRIETATE_INDUSTRIALA_TYPES


def get_handler_key_for_entity_type(entity_type: str | None) -> str | None:
    """
    Returnează cheia logică de handler pe baza familiei.
    Deocamdată cheia este chiar numele familiei.
    """
    family = get_family_for_entity_type(entity_type)
    if not family:
        return None

    if family == FAMILY_CONTRACT_PROIECT_LIKE:
        return FAMILY_CONTRACT_PROIECT_LIKE

    if family == FAMILY_CONTRACT_PN:
        return FAMILY_CONTRACT_PN

    if family == FAMILY_EVENIMENTE:
        return FAMILY_EVENIMENTE

    if family == FAMILY_PROPRIETATE_INDUSTRIALA:
        return FAMILY_PROPRIETATE_INDUSTRIALA

    return family


def get_entity_config(entity_type: str | None) -> dict:
    """
    Returnează config-ul declarativ complet pentru tipul de entitate.
    """
    if not entity_type:
        return {}
    return dict(ENTITY_TYPE_CONFIG.get(entity_type, {}))


def get_enabled_sections_map(entity_type: str | None) -> dict[str, bool]:
    """
    Returnează o hartă simplă a secțiunilor principale activate/dezactivate.
    Util pentru orchestrator și pentru builderele viitoare.
    """
    tabs = set(get_tabs_for_entity_type(entity_type))
    return {
        "date_generale": "date_generale" in tabs,
        "aspecte_tehnice": "aspecte_tehnice" in tabs,
        "date_financiare": "date_financiare" in tabs,
        "rezultate": "rezultate" in tabs,
        "documente": "documente" in tabs,
        "observatii": "observatii" in tabs,
        "echipa": "echipa" in tabs,
        "parteneri": "parteneri" in tabs,
        "organizare": "organizare" in tabs,
        "proprietate": "proprietate" in tabs,
    }
