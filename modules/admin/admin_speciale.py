SPECIAL_CONTRACT_TABLE = "base_contracte_speciale"


SPECIAL_FILTERS = {
    "status_contract_proiect": [
        "In pregatire",
        "Depus",
        "In evaluare",
        "Contractat",
        "Respins",
        "Finalizat",
    ],
    "acronim_contracte_proiecte": [
        "SPECIAL",
        "SPECIAL-INTERN",
        "SPECIAL-EXTERN",
    ],
}


SPECIAL_COLUMNS_PRIORITY = [
    "cod_identificare",
    "acronim_contracte_proiecte",
    "titlul_proiect",
    "status_contract_proiect",
    "data_contract",
    "data_inceput",
    "data_sfarsit",
    "valoare_totala_contract",
    "valoare_anuala_contract",
    "persoana_contact",
]


def is_special_contract_table(table_name: str) -> bool:
    return table_name == SPECIAL_CONTRACT_TABLE


def get_special_filters() -> dict:
    return SPECIAL_FILTERS


def get_special_priority_columns() -> list:
    return SPECIAL_COLUMNS_PRIORITY
