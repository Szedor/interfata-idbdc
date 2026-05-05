# =========================================================
# IDBDC/admin/config.py
# VERSIUNE: 6.0
# STATUS: STABIL - BASE_TABLE_MAP și TABS_MAP complete
# DATA: 2026.05.05
# =========================================================
# CONȚINUT:
#   Configurarea centrală a modulului Admin:
#     - BASE_TABLE_MAP: mapare categorie/tip → tabelă bază de date
#     - TABS_MAP: tab-urile vizibile per categorie/tip
#     - COMPLEMENTARY_TABLES: tabelele complementare comune
#     - Nomenclatoare și coloane de control
#
# MODIFICĂRI VERSIUNEA 6.0:
#   - Adăugat STRUCTURALE în Proiecte (lipsea din BASE_TABLE_MAP).
#   - Completat TABS_MAP pentru toate tipurile de Proiecte
#     (4 tab-uri: Date de bază, Financiar, Echipă, Aspecte tehnice).
#   - Completat TABS_MAP pentru Evenimente stiintifice și
#     Proprietate industriala (2 tab-uri: Date de bază, Echipă).
# =========================================================

import streamlit as st

# --- MAPARE TABELE BAZĂ ---
BASE_TABLE_MAP = {
    "Contracte": {
        "CEP":      "base_contracte_cep",
        "TERTI":    "base_contracte_terti",
        "SPECIALE": "base_contracte_speciale",
    },
    "Proiecte": {
        "FDI":            "base_proiecte_fdi",
        "PNCDI":          "base_proiecte_pncdi",
        "PNRR":           "base_proiecte_pnrr",
        "INTERNATIONALE": "base_proiecte_internationale",
        "INTERREG":       "base_proiecte_interreg",
        "NONEU":          "base_proiecte_noneu",
        "SEE":            "base_proiecte_see",
        "STRUCTURALE":    "base_proiecte_structurale",
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
_TABS_CONTRACTE  = ["📋 Date de bază", "💰 Date financiare", "👥 Echipă"]
_TABS_PROIECTE   = ["📋 Date de bază", "💰 Date financiare", "👥 Echipă", "🧪 Aspecte tehnice"]
_TABS_EVT_PROP   = ["📋 Date de bază", "👥 Echipă"]

TABS_MAP = {
    # Contracte
    ("Contracte", "CEP"):           _TABS_CONTRACTE,
    ("Contracte", "TERTI"):         _TABS_CONTRACTE,
    ("Contracte", "SPECIALE"):      _TABS_CONTRACTE,
    # Proiecte
    ("Proiecte", "FDI"):            _TABS_PROIECTE,
    ("Proiecte", "PNCDI"):          _TABS_PROIECTE,
    ("Proiecte", "PNRR"):           _TABS_PROIECTE,
    ("Proiecte", "INTERNATIONALE"): _TABS_PROIECTE,
    ("Proiecte", "INTERREG"):       _TABS_PROIECTE,
    ("Proiecte", "NONEU"):          _TABS_PROIECTE,
    ("Proiecte", "SEE"):            _TABS_PROIECTE,
    ("Proiecte", "STRUCTURALE"):    _TABS_PROIECTE,
    # Evenimente și Proprietate
    ("Evenimente stiintifice", "CONFERINTE"):  _TABS_EVT_PROP,
    ("Proprietate industriala", "BREVETE"):    _TABS_EVT_PROP,
}


def get_tabs_for_category(categorie, tip=None):
    key = (categorie, tip)
    if key in TABS_MAP:
        return TABS_MAP[key]
    # fallback sigur
    return ["📋 Date de bază"]


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
