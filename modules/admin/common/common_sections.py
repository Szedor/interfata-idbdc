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


def build_section(
    section_key: str,
    title: str,
    data: dict[str, Any] | None = None,
    visible: bool = True,
    editable: bool = True,
) -> dict[str, Any]:
    """
    Constructor minim și neutru pentru o secțiune UI/admin.
    """
    return {
        "key": section_key,
        "title": title,
        "visible": visible,
        "editable": editable,
        "data": data or {},
    }


def build_date_generale_section(
    data: dict[str, Any] | None = None,
    visible: bool = True,
    editable: bool = True,
) -> dict[str, Any]:
    return build_section(
        section_key=TAB_DATE_GENERALE,
        title="Date generale",
        data=data,
        visible=visible,
        editable=editable,
    )


def build_rezultate_section(
    data: dict[str, Any] | None = None,
    visible: bool = True,
    editable: bool = True,
) -> dict[str, Any]:
    return build_section(
        section_key=TAB_REZULTATE,
        title="Rezultate",
        data=data,
        visible=visible,
        editable=editable,
    )


def build_documente_section(
    data: dict[str, Any] | None = None,
    visible: bool = True,
    editable: bool = True,
) -> dict[str, Any]:
    return build_section(
        section_key=TAB_DOCUMENTE,
        title="Documente",
        data=data,
        visible=visible,
        editable=editable,
    )


def build_observatii_section(
    data: dict[str, Any] | None = None,
    visible: bool = True,
    editable: bool = True,
) -> dict[str, Any]:
    return build_section(
        section_key=TAB_OBSERVATII,
        title="Observații",
        data=data,
        visible=visible,
        editable=editable,
    )


def build_parteneri_section(
    data: dict[str, Any] | None = None,
    visible: bool = True,
    editable: bool = True,
) -> dict[str, Any]:
    return build_section(
        section_key=TAB_PARTENERI,
        title="Parteneri",
        data=data,
        visible=visible,
        editable=editable,
    )


def build_organizare_section(
    data: dict[str, Any] | None = None,
    visible: bool = True,
    editable: bool = True,
) -> dict[str, Any]:
    return build_section(
        section_key=TAB_ORGANIZARE,
        title="Organizare",
        data=data,
        visible=visible,
        editable=editable,
    )


def build_proprietate_section(
    data: dict[str, Any] | None = None,
    visible: bool = True,
    editable: bool = True,
) -> dict[str, Any]:
    return build_section(
        section_key=TAB_PROPRIETATE,
        title="Proprietate industrială",
        data=data,
        visible=visible,
        editable=editable,
    )


def build_aspecte_tehnice_section(
    data: dict[str, Any] | None = None,
    visible: bool = True,
    editable: bool = True,
) -> dict[str, Any]:
    return build_section(
        section_key=TAB_ASPECTE_TEHNICE,
        title="Aspecte tehnice",
        data=data,
        visible=visible,
        editable=editable,
    )


def build_date_financiare_section(
    data: dict[str, Any] | None = None,
    visible: bool = True,
    editable: bool = True,
) -> dict[str, Any]:
    return build_section(
        section_key=TAB_DATE_FINANCIARE,
        title="Date financiare",
        data=data,
        visible=visible,
        editable=editable,
    )


def build_common_sections_map(
    *,
    date_generale: dict[str, Any] | None = None,
    rezultate: dict[str, Any] | None = None,
    documente: dict[str, Any] | None = None,
    observatii: dict[str, Any] | None = None,
    parteneri: dict[str, Any] | None = None,
    organizare: dict[str, Any] | None = None,
    proprietate: dict[str, Any] | None = None,
    aspecte_tehnice: dict[str, Any] | None = None,
    date_financiare: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Returnează toate secțiunile standard sub formă de mapare.
    """
    return {
        TAB_DATE_GENERALE: build_date_generale_section(date_generale),
        TAB_REZULTATE: build_rezultate_section(rezultate),
        TAB_DOCUMENTE: build_documente_section(documente),
        TAB_OBSERVATII: build_observatii_section(observatii),
        TAB_PARTENERI: build_parteneri_section(parteneri),
        TAB_ORGANIZARE: build_organizare_section(organizare),
        TAB_PROPRIETATE: build_proprietate_section(proprietate),
        TAB_ASPECTE_TEHNICE: build_aspecte_tehnice_section(aspecte_tehnice),
        TAB_DATE_FINANCIARE: build_date_financiare_section(date_financiare),
    }


def select_sections_by_keys(
    sections_map: dict[str, dict[str, Any]],
    active_keys: list[str] | tuple[str, ...],
) -> list[dict[str, Any]]:
    """
    Selectează secțiunile active în ordinea cerută.
    """
    out: list[dict[str, Any]] = []

    for key in active_keys:
        section = sections_map.get(key)
        if section is not None:
            out.append(section)

    return out


def build_sections_for_tabs(
    active_tabs: list[str] | tuple[str, ...],
    data_by_tab: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Construiește lista finală de secțiuni pentru un set de taburi active.
    """
    data_by_tab = data_by_tab or {}

    sections_map = build_common_sections_map(
        date_generale=data_by_tab.get(TAB_DATE_GENERALE),
        rezultate=data_by_tab.get(TAB_REZULTATE),
        documente=data_by_tab.get(TAB_DOCUMENTE),
        observatii=data_by_tab.get(TAB_OBSERVATII),
        parteneri=data_by_tab.get(TAB_PARTENERI),
        organizare=data_by_tab.get(TAB_ORGANIZARE),
        proprietate=data_by_tab.get(TAB_PROPRIETATE),
        aspecte_tehnice=data_by_tab.get(TAB_ASPECTE_TEHNICE),
        date_financiare=data_by_tab.get(TAB_DATE_FINANCIARE),
    )

    return select_sections_by_keys(sections_map, active_tabs)
