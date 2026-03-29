from modules.admin.admin_config import NOMDET_WHITELIST


def is_allowed_nomenclator(table_name: str) -> bool:
    return table_name in NOMDET_WHITELIST


def get_default_nomenclatoare():
    return {
        "nom_categorie": "denumire_categorie",
        "nom_status_proiect": "status_contract_proiect",
        "nom_contracte": "acronim_tip_contract",
        "nom_proiecte": "acronim_tip_proiect",
        "nom_departament": "acronim_departament",
        "nom_functie_upt": "acronim_functie_upt",
        "nom_domenii_fdi": "cod_domeniu_fdi",
        "nom_universitati": "cod_universitate",
    }


def get_nomenclator_label(table_name: str) -> str:
    labels = {
        "nom_categorie": "Categorii",
        "nom_status_proiect": "Status contract / proiect",
        "nom_contracte": "Tipuri contracte",
        "nom_proiecte": "Tipuri proiecte",
        "nom_departament": "Departamente",
        "nom_functie_upt": "Funcții UPT",
        "nom_domenii_fdi": "Domenii FDI",
        "nom_universitati": "Universități",
        "det_resurse_umane": "Resurse umane",
    }
    return labels.get(table_name, table_name)


def get_nomenclator_sort_column(table_name: str) -> str:
    mapping = {
        "nom_categorie": "denumire_categorie",
        "nom_status_proiect": "status_contract_proiect",
        "nom_contracte": "acronim_tip_contract",
        "nom_proiecte": "acronim_tip_proiect",
        "nom_departament": "acronim_departament",
        "nom_functie_upt": "acronim_functie_upt",
        "nom_domenii_fdi": "cod_domeniu_fdi",
        "nom_universitati": "cod_universitate",
        "det_resurse_umane": "nume_prenume",
    }
    return mapping.get(table_name, "id")
