# =========================================================
# utils/display_config.py
# VERSIUNE: 3.1
# STATUS: ACTUALIZAT - derulat_prin adăugat pentru TERȚI și SPECIALE
# DATA: 2026.05.09
# =========================================================
# MODIFICĂRI VERSIUNEA 3.1:
#   - Adăugat derulat_prin → "DERULAT PRIN" în COL_LABELS.
#   - Adăugat derulat_prin în COL_LABELS_PER_TABLE pentru
#     base_contracte_terti și base_contracte_speciale.
#
# MODIFICĂRI VERSIUNEA 3.0:
#   - Mapare contracte_cep conform definitie.py.
# =========================================================

# ── Etichete globale (fallback) ────────────────────────────────────────
COL_LABELS = {
    "acronim_proiect":              "ACRONIMUL PROIECTULUI",
    "acronim_proiecte":             "ACRONIMUL PROIECTULUI",
    "acronim_tip_proiecte":         "TIPUL DE PROIECT",
    "acronim_tip_contract":         "TIPUL DE CONTRACT",
    "apel_pentru_propuneri":        "APEL PENTRU PROPUNERI",
    "an_inceput":                   "AN INCEPUT",
    "an_referinta":                 "AN REFERINTA",
    "an_sfarsit":                   "AN SFARSIT",
    "cod_domeniu_fdi":              "DOMENIU",
    "cod_identificare":             "NR.CONTRACT",
    "cod_temporar":                 "COD DEPUNERE",
    "contributie_ue_proiect_upt":   "CONTRIBUTIE UE (UPT)",
    "contributie_ue_total_proiect": "CONTRIBUTIE UE (TOTAL PROIECT)",
    "coordonator":                  "COORDONATOR",
    "cost_proiect_upt":             "COST PROIECT UPT",
    "cost_total_proiect":           "COST TOTAL PROIECT",
    "cuvinte_cheie":                "CUVINTE CHEIE",
    "data_acordare":                "DATA ACORDARE",
    "data_apel":                    "DATA APEL",
    "data_contract":                "DATA CONTRACTULUI",
    "data_depozit_cerere":          "DATA DEPUNERE LA OSIM",
    "data_depunere":                "DATA DEPUNERE",
    "data_inceput":                 "DATA DE INCEPUT",
    "data_officiala_acordare":      "DATA OFICIALA ACORDARE",
    "data_sfarsit":                 "DATA DE SFARSIT",
    "denumire_beneficiar":          "BENEFICIAR",
    "denumire_categorie":           "CATEGORIE",
    "derulat_prin":                 "DERULAT PRIN",
    "descriere":                    "DESCRIERE",
    "director_proiect":             "DIRECTOR PROIECT",
    "durata":                       "DURATA (luni)",
    "durata_luni":                  "DURATA",
    "email":                        "EMAIL",
    "format_eveniment":             "FORMATUL EVENIMENTULUI",
    "functia_specifica":            "FUNCTIA IN CONTRACT",
    "institutii_organizare":        "INSTITUTII ORGANIZARE",
    "inventatori":                  "INVENTATORI",
    "loc_desfasurare":              "LOCUL DE DESFASURARE",
    "natura_eveniment":             "NATURA EVENIMENTULUI",
    "nr_brevet":                    "NR. BREVET",
    "nr_cerere":                    "NR. CERERE",
    "nr_contract":                  "NR. CONTRACT",
    "numar_oficial_acordare":       "NR. OFICIAL ACORDARE",
    "numar_participanti":           "NR. PARTICIPANTI",
    "obiectul_contractului":        "OBIECTUL CONTRACTULUI",
    "observatii":                   "OBSERVATII",
    "parteneri":                    "PARTENERI",
    "program":                      "PROGRAM DE FINANTARE",
    "programul_de_finantare":       "PROGRAMUL DE FINANTARE",
    "rol":                          "ROLUL IN CONTRACT",
    "rol_upt":                      "ROL UPT IN PROIECT",
    "schema_de_finantare":          "SCHEMA DE FINANTARE",
    "status_contract_proiect":      "STATUS CONTRACT/PROIECT",
    "suma_aprobata_mec":            "SUMA APROBATA",
    "suma_solicitata_fdi":          "SUMA SOLICITATA",
    "cofinantare_upt_fdi":          "COFINANTARE",
    "total_buget_proiect_fdi":      "TOTAL VALOARE PROIECT",
    "titlul_proiect":               "TITLUL PROIECTULUI",
    "valoare_contract_cep_terti_speciale": "VALOARE CONTRACT",
    "valoare_anuala_contract":      "VALOARE ANUALA CONTRACT",
    "valoare_totala_contract":      "VALOARE TOTALA CONTRACT",
    "cofinantare_anuala_contract":  "COFINANTARE ANUALA",
    "cofinantare_totala_contract":  "COFINANTARE TOTALA",
    "valuta":                       "VALUTA",
    "costuri_totale_proiect":       "VALOARE TOTALA COSTURI PROIECT",
    "contributie_totala_finantator":"CONTRIBUTIE UE TOTAL PROIECT",
    "costuri_totale_upt":           "COSTURI TOTALE UPT",
    "contributie_finantator":       "VALOARE CONTRIBUTIE UE PENTRU UPT",
    "costuri_eligibile_estimate_total": "VALOARE TOTALA ESTIMATA COSTURI ELIGIBILE",
    "valoare_grant_solicitat_total":"VALOARE TOTALA GRANT SOLICITAT",
    "costuri_eligibile_estimate_upt":"VALOARE COSTURI ESTIMATE UPT",
    "valoare_grant_solicitat_upt":  "VALOARE CONTRIBUTIE ESTIMATA PENTRU UPT",
    "nume_prenume":                 "NUME SI PRENUME",
    "departament":                  "DEPARTAMENT",
    "telefon":                      "TELEFON",
}

# ── Câmpuri niciodată afișate în Calea1 ────────────────────────────────
COLS_HIDDEN_FISA = {
    "id", "created_at", "updated_at", "deleted_at", "is_deleted",
    "responsabil_idbdc", "observatii_idbdc", "status_confirmare",
    "data_ultimei_modificari", "validat_idbdc",
    "observatii",
    "nr_crt",
    "creat_de", "creat_la", "modificat_de", "modificat_la",
    "acronim_departament", "denumire_departament",
    "telefon_mobil", "telefon_fix",
    "persoana_contact",
}

# ── Câmpuri prioritare în card ─────────────────────────────────────────
CARD_PRIORITY = [
    "titlul_proiect", "titlu_proiect", "titlu", "titlu_eveniment", "titlu_lucrare",
    "obiectul_contractului",
    "acronim", "acronim_proiect", "acronim_contracte_proiecte",
    "denumire_categorie", "status_contract_proiect",
]

# ── Tabelele de tip CONTRACT ────────────────────────────────────────────
_TABELE_CONTRACTE = {
    "base_contracte_cep",
    "base_contracte_terti",
    "base_contracte_speciale",
}
_COLS_EXCLUDE_CONTRACTE = set()

# ── Ordinea coloanelor pentru Aspecte tehnice ──────────────────────────
TEHNIC_COL_ORDER = [
    "cod_identificare", "tip_rezultat", "titlu_rezultat",
    "descriere_rezultat", "stadiu", "observatii_tehnice",
]

# ── Etichete per tabelă (suprascriu COL_LABELS global) ────────────────
COL_LABELS_PER_TABLE = {
    "base_contracte_cep": {
        "denumire_categorie":                  "CATEGORIE",
        "acronim_tip_contract":                "TIPUL DE CONTRACT",
        "cod_identificare":                    "NR.CONTRACT",
        "data_contract":                       "DATA CONTRACTULUI",
        "obiectul_contractului":               "OBIECTUL CONTRACTULUI",
        "denumire_beneficiar":                 "BENEFICIAR",
        "data_inceput":                        "DATA DE INCEPUT",
        "data_sfarsit":                        "DATA DE SFARSIT",
        "durata":                              "DURATA (luni)",
        "status_contract_proiect":             "STATUS CONTRACT",
    },
    "base_contracte_terti": {
        "cod_identificare":        "NR.CONTRACT",
        "status_contract_proiect": "STATUS CONTRACT",
        "obiectul_contractului":   "OBIECTUL CONTRACTULUI",
        "derulat_prin":            "DERULAT PRIN",
    },
    "base_contracte_speciale": {
        "cod_identificare":        "NR.CONTRACT",
        "status_contract_proiect": "STATUS CONTRACT",
        "obiectul_contractului":   "OBIECTUL CONTRACTULUI",
        "derulat_prin":            "DERULAT PRIN",
    },
    "base_proiecte_fdi": {
        "cod_identificare":        "COD FINAL ÎNREGISTRARE",
        "denumire_categorie":      "CATEGORIE",
        "acronim_tip_proiecte":    "TIPUL DE PROIECT",
        "titlul_proiect":          "TITLUL PROIECTULUI",
        "acronim_proiect":         "ACRONIMUL PROIECTULUI",
        "data_inceput":            "DATA DE INCEPUT",
        "data_sfarsit":            "DATA DE SFARSIT",
        "durata":                  "DURATA (nr.luni)",
        "status_contract_proiect": "STATUS PROIECT",
        "program":                 "PROGRAM DE FINANTARE",
        "cod_domeniu_fdi":         "DOMENIU",
        "cod_temporar":            "COD DEPUNERE",
        "suma_solicitata_fdi":     "SUMA SOLICITATA",
        "suma_aprobata_mec":       "SUMA APROBATA",
        "cofinantare_upt_fdi":     "COFINANTARE",
        "total_buget_proiect_fdi": "TOTAL VALOARE PROIECT",
    },
    "base_proiecte_pncdi": {
        "cod_identificare":        "NR.CONTRACT / COD PROIECT",
        "status_contract_proiect": "STATUS PROIECT",
        "titlul_proiect":          "TITLUL PROIECTULUI",
    },
    "base_proiecte_pnrr": {
        "cod_identificare":        "COD PROIECT PNRR",
        "status_contract_proiect": "STATUS PROIECT",
        "titlul_proiect":          "TITLUL PROIECTULUI",
    },
    "base_proiecte_internationale": {
        "denumire_categorie":      "CATEGORIE",
        "acronim_tip_proiecte":    "TIPUL DE PROIECT",
        "cod_identificare":        "ID PROIECT",
        "titlul_proiect":          "TITLUL PROIECTULUI",
        "acronim_proiect":         "ACRONIMUL PROIECTULUI",
        "data_inceput":            "DATA DE INCEPUT",
        "data_sfarsit":            "DATA DE SFARSIT",
        "durata":                  "DURATA (luni)",
        "status_contract_proiect": "STATUS PROIECT",
        "scor_evaluare":           "SCOR EVALUARE",
        "numar_participanti":      "NR.PARTICIPANTI",
        "denumire_participanti":   "DENUMIRE PARTICIPANTI",
        "rol_upt":                 "ROL UPT",
        "identificare_apel":       "APELUL",
        "data_inchidere_apel":     "DATA LIMITA DEPUNERE",
        "program_finantare":       "PROGRAM DE FINANTARE",
        "tema_topic":              "TEMA / TOPIC",
        "schema_de_finantare":     "SCHEMA DE FINANTARE",
        "website":                 "WEBSITE",
    },
    "base_proiecte_interreg": {
        "cod_identificare":        "COD PROIECT INTERREG",
        "status_contract_proiect": "STATUS PROIECT",
        "titlul_proiect":          "TITLUL PROIECTULUI",
        "rol_upt":                 "ROL UPT IN PROIECT",
    },
    "base_proiecte_noneu": {
        "cod_identificare":        "COD / NR. PROIECT",
        "status_contract_proiect": "STATUS PROIECT",
        "titlul_proiect":          "TITLUL PROIECTULUI",
        "rol_upt":                 "ROL UPT IN PROIECT",
    },
    "base_proiecte_see": {
        "cod_identificare":        "COD / NR. PROIECT",
        "status_contract_proiect": "STATUS PROIECT",
        "titlul_proiect":          "TITLUL PROIECTULUI",
        "rol_upt":                 "ROL UPT IN PROIECT",
    },
    "base_proiecte_structurale": {
        "cod_identificare":        "COD / NR. PROIECT",
        "status_contract_proiect": "STATUS PROIECT",
        "titlul_proiect":          "TITLUL PROIECTULUI",
        "rol_upt":                 "ROL UPT IN PROIECT",
    },
    "base_evenimente_stiintifice": {
        "cod_identificare": "COD EVENIMENT",
        "titlul_eveniment": "TITLUL EVENIMENTULUI",
        "natura_eveniment": "NATURA EVENIMENTULUI",
        "format_eveniment": "FORMATUL EVENIMENTULUI",
        "loc_desfasurare":  "LOCUL DE DESFASURARE",
    },
    "base_prop_intelect": {
        "cod_identificare":       "NR. CERERE / BREVET",
        "acronim_prop_intelect":  "FORMA DE PROTECTIE",
        "titlul_proiect":         "TITLUL INVENTIEI / LUCRARII",
        "data_depozit_cerere":    "DATA DEPUNERE LA OSIM",
        "data_oficiala_acordare": "DATA ACORDARE",
        "numar_oficial_acordare": "NR. OFICIAL ACORDARE",
    },
    "com_date_financiare": {
        "cod_identificare":                    "NR.CONTRACT",
        "valuta":                              "VALUTA",
        "valoare_contract_cep_terti_speciale": "VALOARE CONTRACT",
        "suma_solicitata_fdi":                 "SUMA SOLICITATA",
        "suma_aprobata_mec":                   "SUMA APROBATA",
        "cofinantare_upt_fdi":                 "COFINANTARE",
        "total_buget_proiect_fdi":             "TOTAL VALOARE PROIECT",
    },
    "com_echipe_proiect": {
        "cod_identificare": "NR.CONTRACT",
        "nume_prenume":     "NUME SI PRENUME",
        "rol":              "ROLUL IN CONTRACT",
        "departament":      "DEPARTAMENT",
        "email":            "EMAIL",
        "telefon":          "TELEFON",
    },
    "com_aspecte_tehnice": {
        "cod_identificare": "NR.CONTRACT",
    },
}

# ── Etichete tabele (pentru titluri secțiuni) ─────────────────────────
TABLE_LABELS = {
    "base_contracte_cep":           "📋 Contract CEP",
    "base_contracte_terti":         "📋 Contract Terți",
    "base_contracte_speciale":      "📋 Contract Special",
    "base_proiecte_fdi":            "🔬 Proiect FDI",
    "base_proiecte_pncdi":          "🔬 Proiect PNCDI",
    "base_proiecte_pnrr":           "🔬 Proiect PNRR",
    "base_proiecte_internationale": "🔬 Proiect Internațional",
    "base_proiecte_interreg":       "🔬 Proiect INTERREG",
    "base_proiecte_noneu":          "🔬 Proiect Non-EU",
    "base_proiecte_see":            "🔬 Proiect SEE",
    "base_proiecte_structurale":    "🔬 Proiect Structural",
    "base_evenimente_stiintifice":  "🎓 Eveniment Științific",
    "base_prop_intelect":           "💡 Proprietate Intelectuală",
    "com_date_financiare":          "💰 Date Financiare",
    "com_echipe_proiect":           "👥 Echipă",
    "com_aspecte_tehnice":          "🧪 Aspecte Tehnice",
}

ALL_BASE_TABLES = [
    "base_contracte_terti",
    "base_contracte_cep",
    "base_contracte_speciale",
    "base_proiecte_fdi",
    "base_proiecte_pncdi",
    "base_proiecte_pnrr",
    "base_proiecte_internationale",
    "base_proiecte_interreg",
    "base_proiecte_noneu",
    "base_proiecte_see",
    "base_proiecte_structurale",
    "base_evenimente_stiintifice",
    "base_prop_intelect",
]
