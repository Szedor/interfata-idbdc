from pathlib import Path
content = """ADMIN_ONLY_COLS = {
    "responsabil_idbdc",
    "observatii_idbdc",
    "status_confirmare",
    "data_ultimei_modificari",
    "validat_idbdc",
    "creat_de",
    "creat_la",
    "modificat_de",
    "modificat_la",
}

CONTROL_COLS = [
    "responsabil_idbdc",
    "observatii_idbdc",
    "status_confirmare",
    "data_ultimei_modificari",
    "validat_idbdc",
]

NOMDET_WHITELIST = [
    "nom_categorie",
    "nom_status_proiect",
    "nom_contracte",
    "nom_proiecte",
    "nom_departament",
    "nom_functie_upt",
    "nom_domenii_fdi",
    "nom_universitati",
    "det_resurse_umane",
]

NOMDET_DROPDOWN_MAP = {
    "det_resurse_umane": {
        "acronim_functie_upt": ("nom_functie_upt", "acronim_functie_upt"),
        "acronim_departament": ("nom_departament", "acronim_departament"),
    }
}

STATIC_OPTIONS = {"VALUTA_3": ["LEI", "EUR", "USD"]}

TABELE_CONTRACTE = {
    "base_contracte_cep",
    "base_contracte_terti",
    "base_contracte_speciale",
}

MAP_BAZE = {
    "CEP": "base_contracte_cep",
    "TERTI": "base_contracte_terti",
    "SPECIALE": "base_contracte_speciale",
    "FDI": "base_proiecte_fdi",
    "PNRR": "base_proiecte_pnrr",
    "INTERNATIONALE": "base_proiecte_internationale",
    "INTERREG": "base_proiecte_interreg",
    "NONEU": "base_proiecte_noneu",
    "SEE": "base_proiecte_see",
    "PNCDI": "base_proiecte_pncdi",
}

MAP_CATEGORIE_LABEL = {
    "Contracte": "Contracte",
    "Proiecte": "Proiecte",
    "Evenimente stiintifice": "Evenimente stiintifice",
    "Proprietate intelectuala": "Proprietate intelectuala",
}

MAP_TIP_LABEL = {
    "CEP": "CEP",
    "TERTI": "TERTI",
    "SPECIALE": "SPECIALE",
    "FDI": "FDI",
    "PNRR": "PNRR",
    "PNCDI": "PNCDI",
    "INTERNATIONALE": "INTERNATIONALE",
    "INTERREG": "INTERREG",
    "NONEU": "NONEU",
    "SEE": "SEE",
}

DROPDOWN_MAP = {
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
    "base_proiecte_pncdi": {
        "denumire_categorie": ("nom_categorie", "denumire_categorie"),
        "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
        "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
    },
    "base_proiecte_pnrr": {
        "denumire_categorie": ("nom_categorie", "denumire_categorie"),
        "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
        "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
    },
    "base_evenimente_stiintifice": {
        "denumire_categorie": ("nom_categorie", "denumire_categorie"),
        "natura_eveniment": ("nom_evenimente_stiintifice", "natura_eveniment"),
        "format_eveniment": ("nom_format_evenimente", "format_eveniment"),
    },
    "base_prop_intelect": {
        "denumire_categorie": ("nom_categorie", "denumire_categorie"),
        "acronim_prop_intelect": ("nom_prop_intelect", "acronim_prop_intelect"),
    },
    "com_echipe_proiect": {
        "nume_prenume": ("det_resurse_umane", "nume_prenume"),
        "status_personal": ("nom_status_personal", "status_personal"),
    },
    "com_date_financiare": {"valuta": ("__STATIC__", "VALUTA_3")},
    "det_resurse_umane": {
        "acronim_functie_upt": ("nom_functie_upt", "acronim_functie_upt"),
        "acronim_departament": ("nom_departament", "acronim_departament"),
    },
    "det_evaluare_fdi": {"cod_universitate": ("nom_universitati", "cod_universitate")},
}

AUTO_FILLED_COLS = {
    "denumire_categorie",
    "acronim_contracte_proiecte",
}
"""
path = Path("/mnt/data/admin_config.py")
path.write_text(content, encoding="utf-8")
print(path)

