# modules/admin/contract_proiect_like/contract_proiect_like_column_config.py

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from modules.admin.admin_helpers import (
    is_date_col,
    is_numeric_col,
    is_year_col,
)
from modules.admin.contract_proiect_like.contract_proiect_like_dropdowns import (
    build_dropdown_options_for_table,
    is_auto_filled_column,
)
from modules.admin.contract_proiect_like.contract_proiect_like_labels import (
    resolve_contract_proiect_like_label,
)


VALUE_COLS_KEYWORDS = (
    "valoare_",
    "suma_",
    "cost_",
    "buget_",
    "cofinantare_",
    "contributie_",
    "total_",
)

CONTROL_COLS = {
    "responsabil_idbdc",
    "observatii_idbdc",
    "status_confirmare",
    "data_ultimei_modificari",
    "validat_idbdc",
}


def build_contract_proiect_like_column_config(
    *,
    table_name: str,
    df: pd.DataFrame,
    tabela_baza_ctx: str | None = None,
    load_dropdown_options_callable,
) -> dict[str, Any]:
    """
    Construiește column_config pentru familia contract_proiect_like.

    Consumă:
      - labels din contract_proiect_like_labels.py
      - dropdown map din contract_proiect_like_dropdowns.py

    Păstrează regulile existente din motor_admin.py:
      - denumire_categorie / acronim_contracte_proiecte = readonly auto-filled
      - persoana_contact = checkbox (doar în context proiect)
      - functie_upt = readonly
      - total_buget = readonly pe FDI
      - DateColumn pentru date
      - NumberColumn pentru ani / numerice
      - TextColumn fallback
    """
    cfg: dict[str, Any] = {}

    dropdown_options_map = build_dropdown_options_for_table(
        table_name=table_name,
        available_columns=list(df.columns),
        load_dropdown_options_callable=load_dropdown_options_callable,
    )

    # ---------------------------------------------------------
    # 1. Dropdown / auto-filled
    # ---------------------------------------------------------
    for col in df.columns:
        if col in CONTROL_COLS:
            continue

        label = resolve_contract_proiect_like_label(
            col=col,
            table_name=table_name,
            tabela_baza_ctx=tabela_baza_ctx,
        )

        if is_auto_filled_column(col):
            cfg[col] = st.column_config.TextColumn(
                label=label,
                disabled=True,
                help="Completat automat din selectoarele de sus",
            )
            continue

        if col in dropdown_options_map:
            cfg[col] = st.column_config.SelectboxColumn(
                label=label,
                options=dropdown_options_map[col],
                required=False,
                help="🔽 Selectează din listă",
            )

    # ---------------------------------------------------------
    # 2. Cazuri speciale
    # ---------------------------------------------------------
    if table_name == "com_echipe_proiect" and "persoana_contact" in df.columns:
        if tabela_baza_ctx != "base_contracte_cep" and tabela_baza_ctx != "base_contracte_terti" and tabela_baza_ctx != "base_contracte_speciale":
            cfg["persoana_contact"] = st.column_config.CheckboxColumn(
                label=resolve_contract_proiect_like_label(
                    col="persoana_contact",
                    table_name=table_name,
                    tabela_baza_ctx=tabela_baza_ctx,
                ),
                help="Bifează dacă persoana reprezintă IDBDC în proiect",
                default=False,
            )

    if table_name == "com_echipe_proiect" and "functie_upt" in df.columns:
        cfg["functie_upt"] = st.column_config.TextColumn(
            label=resolve_contract_proiect_like_label(
                col="functie_upt",
                table_name=table_name,
                tabela_baza_ctx=tabela_baza_ctx,
            ),
            help="Completat automat din det_resurse_umane",
            disabled=True,
        )

    if (
        table_name == "com_date_financiare"
        and tabela_baza_ctx == "base_proiecte_fdi"
        and "total_buget" in df.columns
    ):
        cfg["total_buget"] = st.column_config.NumberColumn(
            label=resolve_contract_proiect_like_label(
                col="total_buget",
                table_name=table_name,
                tabela_baza_ctx=tabela_baza_ctx,
            ),
            format="%.2f",
            disabled=True,
        )

    if "nr_crt" in df.columns and "nr_crt" not in cfg:
        cfg["nr_crt"] = st.column_config.NumberColumn(
            label="NR.CRT.",
            disabled=True,
            format="%d",
        )

    # ---------------------------------------------------------
    # 3. Date
    # ---------------------------------------------------------
    for col in df.columns:
        if col in cfg or col in CONTROL_COLS:
            continue

        if is_date_col(col):
            cfg[col] = st.column_config.DateColumn(
                label=resolve_contract_proiect_like_label(
                    col=col,
                    table_name=table_name,
                    tabela_baza_ctx=tabela_baza_ctx,
                ),
                format="YYYY-MM-DD",
                step=1,
                help="📅 Click pentru a selecta data din calendar",
            )

    # ---------------------------------------------------------
    # 4. Ani
    # ---------------------------------------------------------
    for col in df.columns:
        if col in cfg or col in CONTROL_COLS:
            continue

        if is_year_col(col):
            cfg[col] = st.column_config.NumberColumn(
                label=resolve_contract_proiect_like_label(
                    col=col,
                    table_name=table_name,
                    tabela_baza_ctx=tabela_baza_ctx,
                ),
                min_value=1900,
                max_value=2100,
                step=1,
                format="%d",
            )

    # ---------------------------------------------------------
    # 5. Numerice
    # ---------------------------------------------------------
    for col in df.columns:
        if col in cfg or col in CONTROL_COLS:
            continue

        if is_numeric_col(col, df):
            col_lower = col.lower()
            is_value_col = any(
                col_lower.startswith(prefix) or col_lower == prefix
                for prefix in VALUE_COLS_KEYWORDS
            )

            cfg[col] = st.column_config.NumberColumn(
                label=resolve_contract_proiect_like_label(
                    col=col,
                    table_name=table_name,
                    tabela_baza_ctx=tabela_baza_ctx,
                ),
                step=0.01 if is_value_col else 1,
                format="%.2f" if is_value_col else "%d",
            )

    # ---------------------------------------------------------
    # 6. Fallback text
    # ---------------------------------------------------------
    for col in df.columns:
        if col in cfg or col in CONTROL_COLS:
            continue

        cfg[col] = st.column_config.TextColumn(
            label=resolve_contract_proiect_like_label(
                col=col,
                table_name=table_name,
                tabela_baza_ctx=tabela_baza_ctx,
            ),
        )

    return cfg


def normalize_contract_proiect_like_team_df(
    *,
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normalizează câmpuri speciale pentru grid-ul de echipă.
    Păstrează comportamentul existent pentru persoana_contact.
    """
    out = df.copy()

    if "persoana_contact" in out.columns:
        out["persoana_contact"] = out["persoana_contact"].apply(
            lambda v: True
            if v is True or str(v).strip().upper() in ("TRUE", "DA", "1")
            else False
        )

    return out


def prepare_contract_proiect_like_df_for_editor(
    *,
    table_name: str,
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Pre-procesare minimă înainte de data_editor.
    """
    out = df.copy()

    if table_name == "com_echipe_proiect":
        out = normalize_contract_proiect_like_team_df(df=out)

    return out
