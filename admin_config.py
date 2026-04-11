# =========================================================
# IDBDC - MODUL ADMIN - CONFIGURARE STRUCTURĂ (admin_config.py)
# Versiune: 1.0 - Restructurare logică (Fără modificări vizuale)
# =========================================================

import streamlit as st

# --- MAPARE TABELE BAZĂ (Identitate Vizuală păstrată) ---
BASE_TABLE_MAP = {
    "Contracte": {
        "TERTI": "base_contracte_terti",
        "CEP": "base_contracte_cep",
    },
    "Proiecte": {
        "FDI": "base_proiecte_fdi",
        "PNCDI": "base_proiecte_pncdi",
        "PNRR": "base_proiecte_pnrr",
        "INTERNATIONALE": "base_proiecte_internationale",
        "ALTE": "base_proiecte_alte",
    },
    "Evenimente stiintifice": {
        "CONFERINTE": "base_evenimente_conferinte",
    },
    "Proprietate industriala": {
        "BREVETE": "base_proprietate_brevete",
    }
}

# --- TABELE COMPLEMENTARE ---
COMPLEMENTARY_TABLES = [
    ("Date financiare", "com_date_financiare"),
    ("Echipă", "com_echipe_proiect"),
    ("Aspecte tehnice", "com_aspecte_tehnice"),
]

# --- DEFINIRE TAB-URI PER CATEGORIE (Logica stabilă) ---
def get_tabs_for_category(categorie):
    """Returnează lista de tab-uri care trebuie afișate în funcție de categorie."""
    if categorie in ["Evenimente stiintifice", "Proprietate industriala"]:
        return ["Date de bază"]
    return ["Date de bază", "Date financiare", "Echipă", "Aspecte tehnice"]

# --- NOMENCLATOARE WHITELIST (Pentru Dropdowns) ---
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

# --- MAPARE DROPDOWNS ---
NOMDET_DROPDOWN_MAP = {
    "tip_contract": "nom_contracte",
    "tip_proiect": "nom_proiecte",
    "categorie_fdi": "nom_categorie",
    "status_proiect": "nom_status_proiect",
    "departament": "nom_departament",
    "functie_upt": "nom_functie_upt",
    "functie_in_proiect": "nom_functie_proiect",
    "moneda": "nom_moneda",
    "sursa_finantare": "nom_sursa_finantare",
    "tip_rezultat": "nom_tip_rezultat",
    "stadiu_protectie": "nom_stadiu_protectie",
}

# --- COLOANE DE CONTROL (ADMIN ONLY) ---
CONTROL_COLS = [
    "responsabil_idbdc",
    "observatii_idbdc",
    "status_confirmare",
    "data_ultimei_modificari",
    "validat_idbdc",
]

# --- CONFIGURARE ETICHETE SPECIALE ---
TABELE_CONTRACTE = ["base_contracte_terti", "base_contracte_cep"]

def get_base_table(categorie, tip):
    """Returnează numele tabelului SQL pe baza selecției din UI."""
    return BASE_TABLE_MAP.get(categorie, {}).get(tip)
