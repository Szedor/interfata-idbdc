# =========================================================
# IDBDC/domenii/proiecte_interreg/financiar.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.06.01
# =========================================================
# DATE FINANCIARE — ordinea și etichetele exacte din mapare:
#  1. VALUTA               ← 🔖
#  2. BUGET TOTAL PROIECT  → costuri_totale_proiect
#  3. BUGET_UPT            → buget_upt
#  4. CONTRIBUTIE UE       → contributie_finantator
#  5. COFINANTARE NATIONALA → cofinantare_nationala
#  6. COFINANTARE UPT      → cofinantare_upt
# Toate câmpurile introduse manual — fără calcul automat.
# =========================================================

import streamlit as st
import pandas as pd


def render(supabase, cod_introdus, is_new, date_existente):
    VALUTE = ["LEI", "EUR", "USD"]

    if is_new or not date_existente:
        row_ex = {}
    else:
        row_ex = date_existente[0] if isinstance(date_existente, list) else date_existente

    def _sf(val):
        if val is None or val == "":
            return 0.0
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    valuta_ex = row_ex.get("valuta") or "EUR"
    if valuta_ex not in VALUTE:
        valuta_ex = "EUR"

    df = pd.DataFrame([{
        "🔖 VALUTA":             valuta_ex,
        "BUGET TOTAL PROIECT":   _sf(row_ex.get("costuri_totale_proiect")),
        "BUGET_UPT":             _sf(row_ex.get("buget_upt")),
        "CONTRIBUTIE UE":        _sf(row_ex.get("contributie_finantator")),
        "COFINANTARE NATIONALA": _sf(row_ex.get("cofinantare_nationala")),
        "COFINANTARE UPT":       _sf(row_ex.get("cofinantare_upt")),
    }])

    col_cfg = {
        "🔖 VALUTA": st.column_config.SelectboxColumn(
            "🔖 VALUTA", options=VALUTE, required=True
        ),
        "BUGET TOTAL PROIECT": st.column_config.NumberColumn(
            "BUGET TOTAL PROIECT", format="%,.2f", min_value=0.0
        ),
        "BUGET_UPT": st.column_config.NumberColumn(
            "BUGET_UPT", format="%,.2f", min_value=0.0
        ),
        "CONTRIBUTIE UE": st.column_config.NumberColumn(
            "CONTRIBUTIE UE", format="%,.2f", min_value=0.0
        ),
        "COFINANTARE NATIONALA": st.column_config.NumberColumn(
            "COFINANTARE NATIONALA", format="%,.2f", min_value=0.0
        ),
        "COFINANTARE UPT": st.column_config.NumberColumn(
            "COFINANTARE UPT", format="%,.2f", min_value=0.0
        ),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"fin_interreg_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    return [{
        "cod_identificare":      cod_introdus,
        "valuta":                row["🔖 VALUTA"],
        "costuri_totale_proiect": float(row["BUGET TOTAL PROIECT"] or 0),
        "buget_upt":             float(row["BUGET_UPT"] or 0),
        "contributie_finantator": float(row["CONTRIBUTIE UE"] or 0),
        "cofinantare_nationala": float(row["COFINANTARE NATIONALA"] or 0),
        "cofinantare_upt":       float(row["COFINANTARE UPT"] or 0),
    }]
