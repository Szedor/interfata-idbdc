# =========================================================
# IDBDC/domenii/_baza/sectiune_financiar_see.py
# VERSIUNE: 1.0
# STATUS: NOU - Date financiare pentru Proiecte SEE
# DATA: 2026.05.09
# =========================================================

import streamlit as st
import pandas as pd


def render(supabase, cod_introdus, is_new, date_existente):
    VALUTE = ["EUR", "LEI", "USD"]

    if is_new or not date_existente:
        row_ex = {"valuta": "EUR", "cost_total_proiect": 0.0, "cost_proiect_upt": 0.0}
    else:
        row_ex = date_existente[0] if isinstance(date_existente, list) else date_existente

    def _safe_float(val):
        try:
            return float(val) if val else 0.0
        except (TypeError, ValueError):
            return 0.0

    valuta_ex = row_ex.get("valuta") or "EUR"
    if valuta_ex not in VALUTE:
        valuta_ex = "EUR"

    df = pd.DataFrame([{
        "VALUTA":       valuta_ex,
        "BUGET TOTAL":  _safe_float(row_ex.get("cost_total_proiect")),
        "BUGET UPT":    _safe_float(row_ex.get("cost_proiect_upt")),
    }])

    col_cfg = {
        "VALUTA":      st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
        "BUGET TOTAL": st.column_config.NumberColumn("💰 BUGET TOTAL", format="%,.2f", min_value=0.0),
        "BUGET UPT":   st.column_config.NumberColumn("🏛️ BUGET UPT",   format="%,.2f", min_value=0.0),
    }

    df_edit = st.data_editor(
        df, column_config=col_cfg, hide_index=True,
        use_container_width=True, num_rows="fixed",
        key=f"fin_see_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    return [{
        "cod_identificare":   cod_introdus,
        "valuta":             row["VALUTA"],
        "cost_total_proiect": _safe_float(row["BUGET TOTAL"]),
        "cost_proiect_upt":   _safe_float(row["BUGET UPT"]),
    }]
