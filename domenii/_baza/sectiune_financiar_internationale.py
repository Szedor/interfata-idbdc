# =========================================================
# IDBDC/domenii/_baza/sectiune_financiar_internationale.py
# VERSIUNE: 1.1
# STATUS: CORECTAT - CONTRIBUTIE UE UPT → CONTRIBUTIE UE
# DATA: 2026.05.09
# =========================================================

import streamlit as st
import pandas as pd


def render(supabase, cod_introdus, is_new, date_existente):
    VALUTE = ["EUR", "LEI", "USD"]

    if is_new or not date_existente:
        row_ex = {
            "valuta":                       "EUR",
            "cost_total_proiect":           0.0,
            "contributie_ue_total_proiect": 0.0,
            "cost_proiect_upt":             0.0,
            "contributie_ue_proiect_upt":   0.0,
        }
    else:
        row_ex = date_existente[0] if isinstance(date_existente, list) else date_existente

    def _safe_float(val):
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
        "VALUTA":                  valuta_ex,
        "VALOARE TOTALA PROIECT":  _safe_float(row_ex.get("cost_total_proiect")),
        "CONTRIBUTIE UE TOTALA":   _safe_float(row_ex.get("contributie_ue_total_proiect")),
        "VALOARE PROIECT UPT":     _safe_float(row_ex.get("cost_proiect_upt")),
        "CONTRIBUTIE UE":          _safe_float(row_ex.get("contributie_ue_proiect_upt")),
    }])

    col_cfg = {
        "VALUTA":                 st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
        "VALOARE TOTALA PROIECT": st.column_config.NumberColumn("💰 VALOARE TOTALA PROIECT", format="%,.2f", min_value=0.0),
        "CONTRIBUTIE UE TOTALA":  st.column_config.NumberColumn("🇪🇺 CONTRIBUTIE UE TOTALA",  format="%,.2f", min_value=0.0),
        "VALOARE PROIECT UPT":    st.column_config.NumberColumn("🏛️ VALOARE PROIECT UPT",    format="%,.2f", min_value=0.0),
        "CONTRIBUTIE UE":         st.column_config.NumberColumn("🎓 CONTRIBUTIE UE",         format="%,.2f", min_value=0.0),
    }

    df_edit = st.data_editor(
        df, column_config=col_cfg, hide_index=True,
        use_container_width=True, num_rows="fixed",
        key=f"fin_internationale_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    return [{
        "cod_identificare":             cod_introdus,
        "valuta":                       row["VALUTA"],
        "cost_total_proiect":           _safe_float(row["VALOARE TOTALA PROIECT"]),
        "contributie_ue_total_proiect": _safe_float(row["CONTRIBUTIE UE TOTALA"]),
        "cost_proiect_upt":             _safe_float(row["VALOARE PROIECT UPT"]),
        "contributie_ue_proiect_upt":   _safe_float(row["CONTRIBUTIE UE"]),
    }]
