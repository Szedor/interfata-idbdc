# =========================================================
# IDBDC - MODUL ADMIN - CONFIGURARE STRUCTURĂ (admin/config.py)
# Versiune: 5.2 - Adăugat TERTI
# =========================================================

import streamlit as st

# --- MAPARE TABELE BAZĂ ---
BASE_TABLE_MAP = {
    "Contracte": {
        "TERTI": "base_contracte_terti",
        "CEP":   "base_contracte_cep",
    },
    "Proiecte": {
        "FDI":            "base_proiecte_fdi",
        "PNCDI":          "base_proiecte_pncdi",
        "PNRR":           "base_proiecte_pnrr",
        "INTERNATIONALE": "base_proiecte_internationale",
        "INTERREG":       "base_proiecte_interreg",
        "NONEU":          "base_proiecte_noneu",
        "SEE":            "base_proiecte_see",
    },
    "Evenimente stiintifice": {
        "CONFERINTE": "base_evenimente_stiintifice",
    },
    "Proprietate industriala": {
        "BREVETE": "base_prop_intelect",
    },
}

# --- TABELE COMPLEMENTARE (folosite în ștergere generică) ---
COMPLEMENTARY_TABLES = [
    ("Date financiare", "com_date_financiare"),
    ("Echipă",          "com_echipe_proiect"),
    ("Aspecte tehnice", "com_aspecte_tehnice"),
]

# --- TAB-URI PER CATEGORIE/TIP ---
TABS_MAP = {
    ("Contracte", "CEP"):   ["📋 Date de bază", "💰 Date financiare", "👥 Echipă"],
    ("Contracte", "TERTI"): ["📋 Date de bază", "💰 Date financiare", "👥 Echipă"],
}

def get_tabs_for_category(categorie, tip=None):
    key = (categorie, tip)
    if key in TABS_MAP:
        return TABS_MAP[key]
    if categorie in ["Evenimente stiintifice", "Proprietate industriala"]:
        return ["📋 Date de bază"]
    return ["📋 Date de bază", "💰 Date financiare", "👥 Echipă", "🧪 Aspecte tehnice"]

def get_base_table(categorie, tip):
    return BASE_TABLE_MAP.get(categorie, {}).get(tip)

# --- NOMENCLATOARE ---
NOMDET_WHITELIST = [
    "nom_categorie",
    "nom_status_proiect",
    "nom_contracte",
    "nom_proiecte",
    "nom_departament",
    "nom_functie_upt",
    "nom_functie_proiect",
    "nom_moneda",
    "nom_sursa_finantare",
    "nom_tip_rezultat",
    "nom_stadiu_protectie",
]

NOMDET_DROPDOWN_MAP = {
    "tip_contract":       "nom_contracte",
    "tip_proiect":        "nom_proiecte",
    "categorie_fdi":      "nom_categorie",
    "status_proiect":     "nom_status_proiect",
    "departament":        "nom_departament",
    "functie_upt":        "nom_functie_upt",
    "functie_in_proiect": "nom_functie_proiect",
    "moneda":             "nom_moneda",
    "sursa_finantare":    "nom_sursa_finantare",
    "tip_rezultat":       "nom_tip_rezultat",
    "stadiu_protectie":   "nom_stadiu_protectie",
}

CONTROL_COLS = [
    "responsabil_idbdc",
    "observatii_idbdc",
    "status_confirmare",
    "data_ultimei_modificari",
    "validat_idbdc",
]
