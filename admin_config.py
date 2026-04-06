# =========================================================
# ADMIN CONFIG — configurari stabile pentru c2
# =========================================================

# ---------------------------------------------------------
# TABELE BAZA
# ---------------------------------------------------------

BASE_TABLE_MAP = {
    # CONTRACTE
    ("Contracte", "CEP"): "base_contracte_cep",
    ("Contracte", "TERTI"): "base_contracte_terti",
    ("Contracte", "SPECIALE"): "base_contracte_speciale",

    # PROIECTE
    ("Proiecte", "FDI"): "base_proiecte_fdi",
    ("Proiecte", "PNCDI"): "base_proiecte_pncdi",
    ("Proiecte", "PNRR"): "base_proiecte_pnrr",
    ("Proiecte", "INTERNATIONALE"): "base_proiecte_internationale",
    ("Proiecte", "INTERREG"): "base_proiecte_interreg",
    ("Proiecte", "NONEU"): "base_proiecte_noneu",
    ("Proiecte", "SEE"): "base_proiecte_see",

    # EVENIMENTE
    ("Evenimente stiintifice", ""): "base_evenimente_stiintifice",

    # PROPRIETATE INDUSTRIALA
    ("Proprietate intelectuala", ""): "base_prop_intelect",
}


# ---------------------------------------------------------
# TABELE COMPLEMENTARE
# ---------------------------------------------------------

COMPLEMENTARY_TABLES = {
    "Date financiare": "com_date_financiare",
    "Echipa": "com_echipe_proiect",
    "Aspecte tehnice": "com_aspecte_tehnice",
}


# ---------------------------------------------------------
# TAB-URI AFISATE PE CATEGORIE
# ---------------------------------------------------------

CATEGORY_TABS = {
    "Contracte": [
        "Date de baza",
        "Date financiare",
        "Echipa",
        "Aspecte tehnice",
    ],

    "Proiecte": [
        "Date de baza",
        "Date financiare",
        "Echipa",
        "Aspecte tehnice",
    ],

    "Evenimente stiintifice": [
        "Date de baza",
        "Date financiare",
    ],

    "Proprietate intelectuala": [
        "Date de baza",
        "Date financiare",
    ],
}


# ---------------------------------------------------------
# TIPURI DISPONIBILE PE CATEGORII
# ---------------------------------------------------------

CATEGORY_TYPES = {
    "Contracte": [
        "CEP",
        "TERTI",
        "SPECIALE",
    ],

    "Proiecte": [
        "FDI",
        "PNCDI",
        "PNRR",
        "INTERNATIONALE",
        "INTERREG",
        "NONEU",
        "SEE",
    ],

    "Evenimente stiintifice": [],
    "Proprietate intelectuala": [],
}


# ---------------------------------------------------------
# LABEL-URI AFISARE
# ---------------------------------------------------------

CATEGORY_LABELS = {
    "Contracte": "📄 Contracte",
    "Proiecte": "🔬 Proiecte",
    "Evenimente stiintifice": "🎓 Evenimente stiintifice",
    "Proprietate intelectuala": "💡 Proprietate industriala",
}


# ---------------------------------------------------------
# HELPER
# ---------------------------------------------------------


def get_base_table(category: str, tip: str = "") -> str:
    return BASE_TABLE_MAP.get((category, tip), "")


def get_tabs_for_category(category: str) -> list:
    return CATEGORY_TABS.get(category, [])


def get_types_for_category(category: str) -> list:
    return CATEGORY_TYPES.get(category, [])
