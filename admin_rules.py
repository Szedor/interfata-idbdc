# admin_rules.py

```python
# =========================================================
# ADMIN RULES — reguli speciale pe categorii / tipuri
# =========================================================


# ---------------------------------------------------------
# TIPURI CU BUGETE MULTIANUALE
# ---------------------------------------------------------

MULTIYEAR_FINANCIAL_TYPES = {
    "PNRR",
    "PNCDI",
}


# ---------------------------------------------------------
# CATEGORII FARA TAB-URI DE ECHIPA / TEHNIC
# ---------------------------------------------------------

LIGHT_CATEGORIES = {
    "Evenimente stiintifice",
    "Proprietate intelectuala",
}


# ---------------------------------------------------------
# TAB-URI ASCUNSE PE CATEGORII
# ---------------------------------------------------------

HIDDEN_TABS_BY_CATEGORY = {
    "Evenimente stiintifice": [
        "Echipa",
        "Aspecte tehnice",
    ],

    "Proprietate intelectuala": [
        "Echipa",
        "Aspecte tehnice",
    ],
}


# ---------------------------------------------------------
# REGULI PENTRU TAB-UL FINANCIAR
# ---------------------------------------------------------

FINANCIAL_MODE_BY_TYPE = {
    "CEP": "standard",
    "TERTI": "standard",
    "SPECIALE": "standard",

    "FDI": "standard",
    "INTERNATIONALE": "standard",
    "INTERREG": "standard",
    "NONEU": "standard",
    "SEE": "standard",

    "PNCDI": "multianual",
    "PNRR": "multianual",
}


# ---------------------------------------------------------
# HELPER
# ---------------------------------------------------------

def is_multiyear_financial_type(project_type: str) -> bool:
    return (project_type or "").strip().upper() in MULTIYEAR_FINANCIAL_TYPES


def is_light_category(category: str) -> bool:
    return (category or "").strip() in LIGHT_CATEGORIES


def get_hidden_tabs(category: str) -> list:
    return HIDDEN_TABS_BY_CATEGORY.get(category, [])


def get_financial_mode(project_type: str) -> str:
    return FINANCIAL_MODE_BY_TYPE.get(
        (project_type or "").strip().upper(),
        "standard"
    )


def tab_is_visible(category: str, tab_name: str) -> bool:
    hidden_tabs = get_hidden_tabs(category)
    return tab_name not in hidden_tabs
```
