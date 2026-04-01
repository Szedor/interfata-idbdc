# modules/admin/contract_proiect_like/contract_proiect_like_labels.py

from __future__ import annotations


TABELE_CONTRACTE = {
    "base_contracte_cep",
    "base_contracte_terti",
    "base_contracte_speciale",
}


COL_LABELS_ADMIN = {
    "denumire_categorie": "🔽 CATEGORIE",
    "acronim_contracte_proiecte": "🔽 TIPUL DE CONTRACT / PROIECT",
    "status_contract_proiect": "🔽 STATUS CONTRACT/PROIECT",
    "cod_domeniu_fdi": "🔽 COD DOMENIU FDI",
    "nume_prenume": "🔽 NUME SI PRENUME",
    "status_personal": "🔽 STATUS PERSONAL",
    "valuta": "🔽 VALUTA",
    "acronim_functie_upt": "🔽 ABREVIERE FUNCTIE UPT",
    "acronim_departament": "🔽 ACRONIM DEPARTAMENT",
    "persoana_contact": "PERSOANA DE CONTACT",
    "functie_upt": "Abreviere functie UPT (auto)",
    "data_contract": "📅 DATA CONTRACTULUI",
    "data_inceput": "📅 DATA DE INCEPUT",
    "data_sfarsit": "📅 DATA DE SFARSIT",
    "data_semnare": "📅 DATA SEMNARE",
    "data_depunere": "📅 DATA DEPUNERE",
    "data_apel": "📅 DATA APELULUI",
    "program": "PROGRAM",
    "subprogram": "SUBPROGRAM",
    "instrument_finantare": "INSTRUMENT DE FINANTARE",
    "apel": "APEL",
    "sursa_finantare": "SURSA DE FINANTARE",
    "programul_tematic": "PROGRAMUL TEMATIC",
    "componenta_axa": "COMPONENTA / AXA",
    "obiectiv_specific": "OBIECTIV SPECIFIC",
    "acronim_tip_contract": "ACRONIM TIP CONTRACT",
    "acronim_proiect": "ACRONIM PROIECT",
    "acronim_tip_proiect": "ACRONIM TIP PROIECT",
    "activitati_proiect": "ACTIVITATI",
    "an_referinta": "ANUL DE REFERINTA",
    "apel_pentru_propuneri": "APELUL PENTRU PROPUNERI",
    "cod_depunere": "COD DEPUNERE",
    "cod_identificare": "NR.CONTRACT/ID PROIECT",
    "cod_operatori": "COD OPERATORI",
    "cod_temporar": "COD DEPUNERE",
    "cofinantare_anuala_contract": "COFINANTARE ANUALA CONTRACT",
    "cofinantare_totala_contract": "COFINANTARE TOTALA CONTRACT",
    "cofinantare_upt_fdi": "COFINANTARE UPT",
    "total_buget": "TOTAL BUGET",
    "comentarii_diverse": "COMENTARII DIVERSE",
    "comentarii_document": "COMENTARII DOCUMENTE",
    "contributie_ue_proiect_upt": "CONTRIBUTIE UE PENTRU UPT",
    "contributie_ue_total_proiect": "CONTRIBUTIE UE PROIECT",
    "cost_proiect_upt": "COST UPT IN PROIECT",
    "cost_total_proiect": "COST TOTAL PROIECT",
    "denumire_beneficiar": "DENUMIREA BENEFICIARULUI",
    "denumire_completa": "DENUMIRE TIP CONTRACT",
    "denumire_domeniu_fdi": "DENUMIREA DOMENIULUI FDI",
    "denumire_institutie": "DENUMIREA INSTITUTIEI",
    "denumire_solicitant": "DENUMIRE SOLICITANT",
    "director_proiect": "DIRECTOR PROIECT",
    "director_contract": "DIRECTOR CONTRACT",
    "director": "DIRECTOR",
    "derulat_prin": "DERULAT PRIN",
    "document_oficial_original": "DOCUMENT OFICIAL ORIGINAL",
    "durata": "DURATA",
    "durata_luni": "DURATA",
    "email": "EMAIL",
    "email_upt": "EMAIL",
    "explicatii_satus_personal": "DESCRIERE STATUS PERSONAL",
    "explicatii_satus_proiect": "DESCRIERE STATUS CONTRACT/PROIECT",
    "facultate": "FACULTATEA",
    "filtru_categorie": "FILTRU CATEGORIE",
    "filtru_proiect": "FILTRU PROIECT",
    "functia_specifica": "ROLUL IN CONTRACT/PROIECT",
    "id_proiect_contract_sursa": "ID PROIECT (CONTRACT SURSA)",
    "institutii_organizare": "INSTITUTIILE ORGANIZATOARE",
    "interval_finantare": "TOTAL PROIECTE FINANTATE",
    "loc_desfasurare": "LOCUL DE DESFASURARE",
    "nr_crt": "NR.CRT.",
    "obiectiv_general": "OBIECTIV GENERAL",
    "obiective_specifice": "OBIECTIVE SPECIFICE",
    "parteneri": "PARTENERI",
    "programul_de_finantare": "PROGRAMUL DE FINANTARE",
    "rezultate_proiect": "REZULTATE",
    "rol": "ROL OPERATOR",
    "rol_upt": "ROL UPT",
    "schema_de_finantare": "SCHEMA DE FINANTARE",
    "status_activ": "STATUS ACTIV",
    "status_document": "STATUS DOCUMENT",
    "suma_aprobata": "SUMA APROBATA MEC",
    "suma_aprobata_mec": "SUMA APROBATA MINISTER",
    "suma_solicitata": "SUMA SOLICITATA",
    "suma_solicitata_fdi": "SUMA SOLICITATA",
    "telefon_mobil": "TELEFON MOBIL",
    "telefon_upt": "TELEFON UPT",
    "tema_specifica": "TEMA SPECIFICA",
    "titlul": "TITLUL",
    "titlul_proiect": "OBIECTUL/TITLUL CONTRACTULUI/PROIECTULUI",
    "valoare_anuala_contract": "VALOAREA ANUALA A CONTRACTULUI",
    "valoare_totala_contract": "VALOAREA TOTALA A CONTRACTULUI",
    "website": "WEBSITE",
    "abreviere_domeniu_fdi": "DOMENIUL FDI",
}


COL_LABELS_PER_TABLE_ADMIN = {
    "base_contracte_cep": {
        "cod_identificare": "NR. CONTRACT",
        "acronim_contracte_proiecte": "🔽 TIPUL DE CONTRACT",
        "status_contract_proiect": "🔽 STATUS CONTRACT",
        "titlul_proiect": "OBIECTUL CONTRACTULUI",
    },
    "base_contracte_terti": {
        "cod_identificare": "NR. CONTRACT",
        "acronim_contracte_proiecte": "🔽 TIPUL DE CONTRACT",
        "status_contract_proiect": "🔽 STATUS CONTRACT",
        "titlul_proiect": "OBIECTUL CONTRACTULUI",
    },
    "base_contracte_speciale": {
        "cod_identificare": "NR. CONTRACT",
        "acronim_contracte_proiecte": "🔽 TIPUL DE CONTRACT",
        "status_contract_proiect": "🔽 STATUS CONTRACT",
        "titlul_proiect": "OBIECTUL CONTRACTULUI",
    },
    "base_proiecte_fdi": {
        "cod_identificare": "ID PROIECT FDI",
        "acronim_contracte_proiecte": "🔽 TIPUL DE PROIECT",
        "cod_domeniu_fdi": "🔽 COD DOMENIU FDI",
        "abreviere_domeniu_fdi": "DOMENIUL FDI",
        "denumire_domeniu_fdi": "DENUMIREA DOMENIULUI FDI",
        "status_contract_proiect": "🔽 STATUS PROIECT",
        "titlul_proiect": "TITLUL PROIECTULUI",
    },
    "base_proiecte_internationale": {
        "cod_identificare": "COD / NR. PROIECT",
        "status_contract_proiect": "🔽 STATUS PROIECT",
        "titlul_proiect": "TITLUL PROIECTULUI",
        "rol_upt": "ROL UPT IN PROIECT",
    },
    "base_proiecte_interreg": {
        "cod_identificare": "COD PROIECT INTERREG",
        "status_contract_proiect": "🔽 STATUS PROIECT",
        "titlul_proiect": "TITLUL PROIECTULUI",
        "rol_upt": "ROL UPT IN PROIECT",
    },
    "base_proiecte_noneu": {
        "cod_identificare": "COD / NR. PROIECT",
        "status_contract_proiect": "🔽 STATUS PROIECT",
        "titlul_proiect": "TITLUL PROIECTULUI",
        "rol_upt": "ROL UPT IN PROIECT",
    },
    "base_proiecte_see": {
        "cod_identificare": "COD / NR. PROIECT",
        "status_contract_proiect": "🔽 STATUS PROIECT",
        "titlul_proiect": "TITLUL PROIECTULUI",
        "rol_upt": "ROL UPT IN PROIECT",
    },
}


def is_contract_context(tabela_baza_ctx: str | None) -> bool:
    return (tabela_baza_ctx or "").strip() in TABELE_CONTRACTE


def get_generic_admin_label(col: str) -> str:
    return COL_LABELS_ADMIN.get(col, col.replace("_", " ").capitalize())


def get_table_override_label(col: str, tabela: str | None) -> str | None:
    if tabela and tabela in COL_LABELS_PER_TABLE_ADMIN:
        return COL_LABELS_PER_TABLE_ADMIN[tabela].get(col)
    return None


def resolve_contract_proiect_like_label(
    *,
    col: str,
    table_name: str,
    tabela_baza_ctx: str | None = None,
) -> str:
    """
    Ordinea de rezolvare:
      1. override per tabelă de bază;
      2. override contextual pentru tabele auxiliare;
      3. label generic.
    """
    specific = get_table_override_label(col, table_name)
    if specific:
        return specific

    contract_ctx = is_contract_context(tabela_baza_ctx)

    if contract_ctx and table_name not in COL_LABELS_PER_TABLE_ADMIN:
        if col == "cod_identificare":
            return "NR. CONTRACT"
        if col == "functia_specifica":
            return "ROLUL IN CONTRACT"

    if not contract_ctx and table_name not in COL_LABELS_PER_TABLE_ADMIN:
        if col == "functia_specifica":
            return "ROLUL IN PROIECT"

    return get_generic_admin_label(col)


def get_contract_proiect_like_table_labels() -> dict[str, dict[str, str]]:
    return {
        table_name: labels.copy()
        for table_name, labels in COL_LABELS_PER_TABLE_ADMIN.items()
    }


def get_contract_proiect_like_generic_labels() -> dict[str, str]:
    return COL_LABELS_ADMIN.copy()
