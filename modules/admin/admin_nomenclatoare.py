from __future__ import annotations

"""
Nomenclatoare comune pentru modulul admin.

În această etapă păstrăm doar liste și mapări declarative
care sunt sigure și generale pentru arhitectura nouă.
Fără nomenclatoare speculative sau neconfirmate de sistemul existent.
"""

from modules.admin.admin_config import (
    TIP_CONTRACT,
    TIP_EVENIMENT,
    TIP_FDI,
    TIP_INTERREG,
    TIP_INTERNATIONALE,
    TIP_NONEU,
    TIP_PNCDI,
    TIP_PNRR,
    TIP_PROPRIETATE_INDUSTRIALA,
    TIP_SEE,
)


STATUSURI_GENERALE = [
    "În pregătire",
    "Depus",
    "În evaluare",
    "Aprobat",
    "Respins",
    "Contractat",
    "În derulare",
    "Suspendat",
    "Finalizat",
    "Închis",
]


OPT_DA_NU = [
    "Da",
    "Nu",
]


TIPURI_ENTITATI = [
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


TIPURI_ENTITATI_LABELS = {
    TIP_CONTRACT: "Contract",
    TIP_FDI: "FDI",
    TIP_INTERNATIONALE: "Internaționale",
    TIP_INTERREG: "Interreg",
    TIP_NONEU: "NonEU",
    TIP_SEE: "SEE",
    TIP_PNCDI: "PNCDI",
    TIP_PNRR: "PNRR",
    TIP_EVENIMENT: "Eveniment științific",
    TIP_PROPRIETATE_INDUSTRIALA: "Proprietate industrială",
}


STATUSURI_PROPRIETATE_INDUSTRIALA = [
    "În pregătire",
    "Depus",
    "În examinare",
    "Acordat",
    "Respins",
    "Expirat",
]


STATUS_BY_ENTITY_TYPE = {
    TIP_CONTRACT: STATUSURI_GENERALE,
    TIP_FDI: STATUSURI_GENERALE,
    TIP_INTERNATIONALE: STATUSURI_GENERALE,
    TIP_INTERREG: STATUSURI_GENERALE,
    TIP_NONEU: STATUSURI_GENERALE,
    TIP_SEE: STATUSURI_GENERALE,
    TIP_PNCDI: STATUSURI_GENERALE,
    TIP_PNRR: STATUSURI_GENERALE,
    TIP_EVENIMENT: [
        "Planificat",
        "În desfășurare",
        "Finalizat",
        "Anulat",
    ],
    TIP_PROPRIETATE_INDUSTRIALA: STATUSURI_PROPRIETATE_INDUSTRIALA,
}


EXTRA_OPTIONS_BY_ENTITY_TYPE = {
    TIP_CONTRACT: {},
    TIP_FDI: {},
    TIP_INTERNATIONALE: {},
    TIP_INTERREG: {},
    TIP_NONEU: {},
    TIP_SEE: {},
    TIP_PNCDI: {},
    TIP_PNRR: {},
    TIP_EVENIMENT: {},
    TIP_PROPRIETATE_INDUSTRIALA: {},
}
