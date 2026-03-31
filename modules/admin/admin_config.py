from __future__ import annotations

"""
Config comun pentru noua arhitectură admin.

În Etapa 2 păstrăm doar constante și mapări stabile,
fără logică de business.
"""

# ============================================================================
# Familii principale de entități
# ============================================================================

FAMILY_CONTRACT_PROIECT_LIKE = "contract_proiect_like"
FAMILY_CONTRACT_PN = "contract_pn"
FAMILY_EVENIMENTE = "evenimente"
FAMILY_PROPRIETATE_INDUSTRIALA = "proprietate_industriala"


# ============================================================================
# Tipuri de entități
# ============================================================================

TIP_CONTRACT = "contract"
TIP_FDI = "fdi"
TIP_INTERNATIONALE = "internationale"
TIP_INTERREG = "interreg"
TIP_NONEU = "noneu"
TIP_SEE = "see"
TIP_PNCDI = "pncdi"
TIP_PNRR = "pnrr"
TIP_EVENIMENT = "eveniment"
TIP_PROPRIETATE_INDUSTRIALA = "proprietate_industriala"


ALL_ENTITY_TYPES = [
    TIP_CONTRACT,
    TIP_FDI,
    TIP_INTERNATIONALE,
    TIP_INTERREG,
    TIP_NONEU,
    TIP_SEE,
    TIP_PNCDI,
    TIP_PNRR,
    TIP_EVENIMENT,
    TIP_PROPRIETATE_INDUSTRIALA,
]


# ============================================================================
# Grupări pe familii
# ============================================================================

CONTRACT_PROIECT_LIKE_TYPES = [
    TIP_CONTRACT,
    TIP_FDI,
    TIP_INTERNATIONALE,
    TIP_INTERREG,
    TIP_NONEU,
    TIP_SEE,
]

CONTRACT_PN_TYPES = [
    TIP_PNCDI,
    TIP_PNRR,
]

EVENIMENTE_TYPES = [
    TIP_EVENIMENT,
]

PROPRIETATE_INDUSTRIALA_TYPES = [
    TIP_PROPRIETATE_INDUSTRIALA,
]


# ============================================================================
# Mapare tip -> familie
# ============================================================================

ENTITY_TYPE_TO_FAMILY = {
    TIP_CONTRACT: FAMILY_CONTRACT_PROIECT_LIKE,
    TIP_FDI: FAMILY_CONTRACT_PROIECT_LIKE,
    TIP_INTERNATIONALE: FAMILY_CONTRACT_PROIECT_LIKE,
    TIP_INTERREG: FAMILY_CONTRACT_PROIECT_LIKE,
    TIP_NONEU: FAMILY_CONTRACT_PROIECT_LIKE,
    TIP_SEE: FAMILY_CONTRACT_PROIECT_LIKE,
    TIP_PNCDI: FAMILY_CONTRACT_PN,
    TIP_PNRR: FAMILY_CONTRACT_PN,
    TIP_EVENIMENT: FAMILY_EVENIMENTE,
    TIP_PROPRIETATE_INDUSTRIALA: FAMILY_PROPRIETATE_INDUSTRIALA,
}


# ============================================================================
# Secțiuni / taburi standard
# ============================================================================

TAB_DATE_GENERALE = "date_generale"
TAB_ASPECTE_TEHNICE = "aspecte_tehnice"
TAB_DATE_FINANCIARE = "date_financiare"
TAB_REZULTATE = "rezultate"
TAB_DOCUMENTE = "documente"
TAB_OBSERVATII = "observatii"
TAB_ECHIPA = "echipa"
TAB_PARTENERI = "parteneri"
TAB_ORGANIZARE = "organizare"
TAB_PROPRIETATE = "proprietate"

ALL_STANDARD_TABS = [
    TAB_DATE_GENERALE,
    TAB_ASPECTE_TEHNICE,
    TAB_DATE_FINANCIARE,
    TAB_REZULTATE,
    TAB_DOCUMENTE,
    TAB_OBSERVATII,
    TAB_ECHIPA,
    TAB_PARTENERI,
    TAB_ORGANIZARE,
    TAB_PROPRIETATE,
]


# ============================================================================
# Taburi active pe familie
# ============================================================================

FAMILY_DEFAULT_TABS = {
    FAMILY_CONTRACT_PROIECT_LIKE: [
        TAB_DATE_GENERALE,
        TAB_ASPECTE_TEHNICE,
        TAB_DATE_FINANCIARE,
        TAB_REZULTATE,
        TAB_DOCUMENTE,
        TAB_OBSERVATII,
    ],
    FAMILY_CONTRACT_PN: [
        TAB_DATE_GENERALE,
        TAB_ASPECTE_TEHNICE,
        TAB_DATE_FINANCIARE,
        TAB_REZULTATE,
        TAB_DOCUMENTE,
        TAB_OBSERVATII,
    ],
    FAMILY_EVENIMENTE: [
        TAB_DATE_GENERALE,
        TAB_ORGANIZARE,
        TAB_REZULTATE,
        TAB_DOCUMENTE,
        TAB_OBSERVATII,
    ],
    FAMILY_PROPRIETATE_INDUSTRIALA: [
        TAB_DATE_GENERALE,
        TAB_PROPRIETATE,
        TAB_DOCUMENTE,
        TAB_OBSERVATII,
    ],
}


# ============================================================================
# Câmpuri de bază comune
# ============================================================================

COMMON_BASE_FIELDS = [
    "id",
    "cod_identificare",
    "tip_entitate",
    "titlu",
    "acronim",
    "status",
    "data_inceput",
    "data_sfarsit",
    "an",
    "observatii",
]


AUDIT_FIELDS = [
    "creat_la",
    "creat_de",
    "modificat_la",
    "modificat_de",
    "data_ultimei_modificari",
]


COMMON_FLAG_FIELDS = [
    "status_confirmare",
    "validat_idbdc",
    "persoana_contact",
]


# ============================================================================
# Coloane rezervate / speciale
# ============================================================================

RESERVED_COLUMNS = [
    "id",
    "nr_crt",
]

IDENTITY_COLUMNS = [
    "id",
    "cod_identificare",
]

SYSTEM_COLUMNS = AUDIT_FIELDS + COMMON_FLAG_FIELDS + RESERVED_COLUMNS


# ============================================================================
# Câmpuri financiare standard
# ============================================================================

STANDARD_FINANCIAL_FIELDS = [
    "valoare_totala",
    "buget_total",
    "buget_upt",
    "cofinantare",
    "contributie_proprie",
]

FDI_FINANCIAL_FIELDS = [
    "suma_aprobata_mec",
    "cofinantare_upt_fdi",
]


# ============================================================================
# Câmpuri tehnice standard
# ============================================================================

STANDARD_TECHNICAL_FIELDS = [
    "obiective",
    "rezumat_tehnic",
    "stadiu_realizare",
    "indicatori",
    "rezultate_tehnice",
]


# ============================================================================
# Etichete standard pentru afișare
# ============================================================================

TAB_LABELS = {
    TAB_DATE_GENERALE: "Date generale",
    TAB_ASPECTE_TEHNICE: "Aspecte tehnice",
    TAB_DATE_FINANCIARE: "Date financiare",
    TAB_REZULTATE: "Rezultate",
    TAB_DOCUMENTE: "Documente",
    TAB_OBSERVATII: "Observații",
    TAB_ECHIPA: "Echipă",
    TAB_PARTENERI: "Parteneri",
    TAB_ORGANIZARE: "Organizare",
    TAB_PROPRIETATE: "Proprietate industrială",
}


FAMILY_LABELS = {
    FAMILY_CONTRACT_PROIECT_LIKE: "Contracte și proiecte de tip contract-like",
    FAMILY_CONTRACT_PN: "Contracte PN",
    FAMILY_EVENIMENTE: "Evenimente",
    FAMILY_PROPRIETATE_INDUSTRIALA: "Proprietate industrială",
}


ENTITY_TYPE_LABELS = {
    TIP_CONTRACT: "Contract",
    TIP_FDI: "FDI",
    TIP_INTERNATIONALE: "Internaționale",
    TIP_INTERREG: "Interreg",
    TIP_NONEU: "NonEU",
    TIP_SEE: "SEE",
    TIP_PNCDI: "PNCDI",
    TIP_PNRR: "PNRR",
    TIP_EVENIMENT: "Eveniment",
    TIP_PROPRIETATE_INDUSTRIALA: "Proprietate industrială",
}


# ============================================================================
# Config declarativ pe tip
# ============================================================================

ENTITY_TYPE_CONFIG = {
    TIP_CONTRACT: {
        "family": FAMILY_CONTRACT_PROIECT_LIKE,
        "tabs": FAMILY_DEFAULT_TABS[FAMILY_CONTRACT_PROIECT_LIKE],
        "has_financial": True,
        "has_technical": True,
        "is_multianual": False,
    },
    TIP_FDI: {
        "family": FAMILY_CONTRACT_PROIECT_LIKE,
        "tabs": FAMILY_DEFAULT_TABS[FAMILY_CONTRACT_PROIECT_LIKE],
        "has_financial": True,
        "has_technical": True,
        "is_multianual": False,
    },
    TIP_INTERNATIONALE: {
        "family": FAMILY_CONTRACT_PROIECT_LIKE,
        "tabs": FAMILY_DEFAULT_TABS[FAMILY_CONTRACT_PROIECT_LIKE],
        "has_financial": True,
        "has_technical": True,
        "is_multianual": False,
    },
    TIP_INTERREG: {
        "family": FAMILY_CONTRACT_PROIECT_LIKE,
        "tabs": FAMILY_DEFAULT_TABS[FAMILY_CONTRACT_PROIECT_LIKE],
        "has_financial": True,
        "has_technical": True,
        "is_multianual": False,
    },
    TIP_NONEU: {
        "family": FAMILY_CONTRACT_PROIECT_LIKE,
        "tabs": FAMILY_DEFAULT_TABS[FAMILY_CONTRACT_PROIECT_LIKE],
        "has_financial": True,
        "has_technical": True,
        "is_multianual": False,
    },
    TIP_SEE: {
        "family": FAMILY_CONTRACT_PROIECT_LIKE,
        "tabs": FAMILY_DEFAULT_TABS[FAMILY_CONTRACT_PROIECT_LIKE],
        "has_financial": True,
        "has_technical": True,
        "is_multianual": False,
    },
    TIP_PNCDI: {
        "family": FAMILY_CONTRACT_PN,
        "tabs": FAMILY_DEFAULT_TABS[FAMILY_CONTRACT_PN],
        "has_financial": True,
        "has_technical": True,
        "is_multianual": True,
    },
    TIP_PNRR: {
        "family": FAMILY_CONTRACT_PN,
        "tabs": FAMILY_DEFAULT_TABS[FAMILY_CONTRACT_PN],
        "has_financial": True,
        "has_technical": True,
        "is_multianual": True,
    },
    TIP_EVENIMENT: {
        "family": FAMILY_EVENIMENTE,
        "tabs": FAMILY_DEFAULT_TABS[FAMILY_EVENIMENTE],
        "has_financial": False,
        "has_technical": False,
        "is_multianual": False,
    },
    TIP_PROPRIETATE_INDUSTRIALA: {
        "family": FAMILY_PROPRIETATE_INDUSTRIALA,
        "tabs": FAMILY_DEFAULT_TABS[FAMILY_PROPRIETATE_INDUSTRIALA],
        "has_financial": False,
        "has_technical": False,
        "is_multianual": False,
    },
}
