# =========================================================
# IDBDC/domenii/contracte_cep/financiar.py
# VERSIUNE: 2.0 | DATA: 2026.06.02
# =========================================================
# DATE FINANCIARE — ordinea și etichetele exacte din mapare:
#  1. VALUTA            ← 🔖
#  2. VALOARE CONTRACT  → valoare_contract_cep_terti_speciale
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

    valuta_ex = row_ex.get("valuta") or "LEI"
    if valuta_ex not in VALUTE:
        valuta_ex = "LEI"

    df = pd.DataFrame([{
        "🔖 VALUTA":        valuta_ex,
        "VALOARE CONTRACT": _sf(row_ex.get("valoare_contract_cep_terti_speciale")),
    }])

    col_cfg = {
        "🔖 VALUTA": st.column_config.SelectboxColumn(
            "🔖 VALUTA", options=VALUTE, required=True
        ),
        "VALOARE CONTRACT": st.column_config.NumberColumn(
            "VALOARE CONTRACT", format="%,.2f", min_value=0.0
        ),
    }

    df_edit = st.data_editor(
        df, column_config=col_cfg, hide_index=True,
        use_container_width=True, num_rows="fixed",
        key=f"fin_cep_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    return [{
        "cod_identificare":                    cod_introdus,
        "valuta":                              row["🔖 VALUTA"],
        "valoare_contract_cep_terti_speciale": float(row["VALOARE CONTRACT"] or 0),
    }]
