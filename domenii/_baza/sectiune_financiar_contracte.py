# =========================================================
# IDBDC/domenii/_baza/sectiune_financiar_contracte.py
# VERSIUNE: 1.0
# STATUS: NOU - Date financiare comune pentru toate contractele
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Randează secțiunea Date financiare pentru contracte
#   (CEP, TERȚI, SPECIALE). Conținut preluat din
#   utils/contracte_common.py v7.0, neatins.
# =========================================================

import streamlit as st
import pandas as pd


def render(supabase, cod_introdus, is_new, date_existente):
    VALUTE = ["LEI", "EUR", "USD"]

    if is_new or not date_existente:
        row_ex = {"valuta": "LEI", "valoare_contract_cep_terti_speciale": 0.0}
    else:
        row_ex = date_existente[0] if isinstance(date_existente, list) else date_existente

    try:
        val_ex = float(row_ex.get("valoare_contract_cep_terti_speciale") or 0)
    except (TypeError, ValueError):
        val_ex = 0.0

    valuta_ex = row_ex.get("valuta", "LEI") or "LEI"
    if valuta_ex not in VALUTE:
        valuta_ex = "LEI"

    df = pd.DataFrame([{
        "VALUTA":           valuta_ex,
        "VALOARE CONTRACT": val_ex,
    }])

    col_cfg = {
        "VALUTA":           st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
        "VALOARE CONTRACT": st.column_config.NumberColumn("💰 VALOARE CONTRACT", format="%,.2f", min_value=0.0),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"fin_contracte_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    return [{
        "cod_identificare":                    cod_introdus,
        "valuta":                              row["VALUTA"],
        "valoare_contract_cep_terti_speciale": float(row["VALOARE CONTRACT"] or 0),
    }]
