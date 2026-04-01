# modules/admin/contract_proiect_like/contract_proiect_like_dropdowns.py

from __future__ import annotations

STATIC_OPTIONS = {
    "VALUTA_3": ["LEI", "EUR", "USD"],
}


CONTRACT_PROIECT_LIKE_DROPDOWN_MAP = {
    "base_contracte_cep": {
        "denumire_categorie": ("nom_categorie", "denumire_categorie"),
        "acronim_contracte_proiecte": ("nom_contracte", "acronim_tip_contract"),
        "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
    },
    "base_contracte_terti": {
        "denumire_categorie": ("nom_categorie", "denumire_categorie"),
        "acronim_contracte_proiecte": ("nom_contracte", "acronim_tip_contract"),
        "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
    },
    "base_contracte_speciale": {
        "denumire_categorie": ("nom_categorie", "denumire_categorie"),
        "acronim_contracte_proiecte": ("nom_contracte", "acronim_tip_contract"),
        "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
    },
    "base_proiecte_fdi": {
        "denumire_categorie": ("nom_categorie", "denumire_categorie"),
        "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
        "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
        "cod_domeniu_fdi": ("nom_domenii_fdi", "cod_domeniu_fdi"),
    },
    "base_proiecte_internationale": {
        "denumire_categorie": ("nom_categorie", "denumire_categorie"),
        "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
        "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
    },
    "base_proiecte_interreg": {
        "denumire_categorie": ("nom_categorie", "denumire_categorie"),
        "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
        "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
    },
    "base_proiecte_noneu": {
        "denumire_categorie": ("nom_categorie", "denumire_categorie"),
        "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
        "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
    },
    "base_proiecte_see": {
        "denumire_categorie": ("nom_categorie", "denumire_categorie"),
        "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
        "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
    },
    "com_echipe_proiect": {
        "nume_prenume": ("det_resurse_umane", "nume_prenume"),
        "status_personal": ("nom_status_personal", "status_personal"),
    },
    "com_date_financiare": {
        "valuta": ("__STATIC__", "VALUTA_3"),
    },
}


AUTO_FILLED_COLS = {
    "denumire_categorie",
    "acronim_contracte_proiecte",
}


def get_static_options() -> dict[str, list[str]]:
    return {k: list(v) for k, v in STATIC_OPTIONS.items()}


def get_auto_filled_cols() -> set[str]:
    return set(AUTO_FILLED_COLS)


def get_contract_proiect_like_dropdown_map() -> dict[str, dict[str, tuple[str, str]]]:
    return {
        table_name: mapping.copy()
        for table_name, mapping in CONTRACT_PROIECT_LIKE_DROPDOWN_MAP.items()
    }


def get_dropdown_mapping_for_table(table_name: str) -> dict[str, tuple[str, str]]:
    return CONTRACT_PROIECT_LIKE_DROPDOWN_MAP.get(table_name, {}).copy()


def resolve_dropdown_source(
    *,
    table_name: str,
    column_name: str,
) -> tuple[str, str] | None:
    return CONTRACT_PROIECT_LIKE_DROPDOWN_MAP.get(table_name, {}).get(column_name)


def is_auto_filled_column(column_name: str) -> bool:
    return column_name in AUTO_FILLED_COLS


def uses_static_source(source_table: str) -> bool:
    return source_table == "__STATIC__"


def resolve_dropdown_options(
    *,
    source_table: str,
    source_col: str,
    load_dropdown_options_callable,
) -> list[str]:
    """
    Resolver generic de opțiuni.

    - pentru surse statice: returnează STATIC_OPTIONS[source_col]
    - pentru surse DB: apelează load_dropdown_options_callable(source_table, source_col)
    """
    if uses_static_source(source_table):
        return list(STATIC_OPTIONS.get(source_col, []))

    return list(load_dropdown_options_callable(source_table, source_col) or [])


def build_dropdown_options_for_table(
    *,
    table_name: str,
    available_columns: list[str],
    load_dropdown_options_callable,
) -> dict[str, list[str]]:
    """
    Returnează:
        {
            "coloana_x": ["opt1", "opt2"],
            ...
        }

    Nu aplică labels și nu construiește st.column_config.
    Doar rezolvă sursele de opțiuni pentru tabela dată.
    """
    result: dict[str, list[str]] = {}
    mapping = get_dropdown_mapping_for_table(table_name)

    for target_col, (source_table, source_col) in mapping.items():
        if target_col not in available_columns:
            continue

        options = resolve_dropdown_options(
            source_table=source_table,
            source_col=source_col,
            load_dropdown_options_callable=load_dropdown_options_callable,
        )

        if options:
            result[target_col] = options

    return result
