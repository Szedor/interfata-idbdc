# =========================================================
# IDBDC/domenii/contracte_terti/financiar.py
# v.modul.1.0 - Date financiare pentru Contracte TERTI
# =========================================================

import streamlit as st
import pandas as pd


def render(supabase, cod_introdus, is_new, date_existente):
    VALUTE = ["LEI", "EUR", "USD"]
    
    if is_new or not date_existente:
        val_ex = 0.0
        valuta_ex = "LEI"
    else:
        row_ex = date_existente[0] if isinstance(date_existente, list) else date_existente
        try:
            val_ex = float(row_ex.get("valoare_contract") or 0)
        except:
            val_ex = 0.0
        valuta_ex = row_ex.get("valuta", "LEI")
        if valuta_ex not in VALUTE:
            valuta_ex = "LEI"

    df = pd.DataFrame([{
        "💱 VALUTA": valuta_ex,
        "💰 VALOARE CONTRACT": val_ex,
    }])

    col_cfg = {
        "💱 VALUTA": st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
        "💰 VALOARE CONTRACT": st.column_config.NumberColumn("💰 VALOARE CONTRACT", format="%.2f", min_value=0.0),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"fin_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]
    
    return [{
        "cod_identificare": cod_introdus,
        "valuta": row["💱 VALUTA"],
        "valoare_contract": float(row["💰 VALOARE CONTRACT"] or 0),
    }]
