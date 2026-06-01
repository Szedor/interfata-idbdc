# =========================================================
# IDBDC/domenii/proiecte_internationale/financiar.py
# VERSIUNE: 1.1
# STATUS: CORECTAT - etichete vizuale și ordine exacte din mapare
# DATA: 2026.06.01
# =========================================================
# DATE FINANCIARE — ordinea și etichetele exacte din mapare:
#  1. VALUTA                                       ← 🔖
#  2. VALOARE TOTALA COSTURI PROIECT               → costuri_totale_proiect
#  3. CONTRIBUTIE UE TOTAL PROIECT                 → contributie_totala_finantator
#  4. COSTURI TOTALE UPT                           → costuri_totale_upt
#  5. VALOARE CONTRIBUTIE UE PENTRU UPT            → contributie_finantator
#  6. VALOARE TOTALA ESTIMATA COSTURI ELIGIBILE    → costuri_eligibile_estimate_total
#  7. VALOARE TOTALA GRANT SOLICITAT               → valoare_grant_solicitat_total
#  8. VALOARE COSTURI ESTIMATE UPT                 → costuri_eligibile_estimate_upt
#  9. VALOARE CONTRIBUTIE ESTIMATA PENTRU UPT      → valoare_grant_solicitat_upt
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
        "🔖 VALUTA":                                    valuta_ex,
        "VALOARE TOTALA COSTURI PROIECT":               _sf(row_ex.get("costuri_totale_proiect")),
        "CONTRIBUTIE UE TOTAL PROIECT":                 _sf(row_ex.get("contributie_totala_finantator")),
        "COSTURI TOTALE UPT":                           _sf(row_ex.get("costuri_totale_upt")),
        "VALOARE CONTRIBUTIE UE PENTRU UPT":            _sf(row_ex.get("contributie_finantator")),
        "VALOARE TOTALA ESTIMATA COSTURI ELIGIBILE":    _sf(row_ex.get("costuri_eligibile_estimate_total")),
        "VALOARE TOTALA GRANT SOLICITAT":               _sf(row_ex.get("valoare_grant_solicitat_total")),
        "VALOARE COSTURI ESTIMATE UPT":                 _sf(row_ex.get("costuri_eligibile_estimate_upt")),
        "VALOARE CONTRIBUTIE ESTIMATA PENTRU UPT":      _sf(row_ex.get("valoare_grant_solicitat_upt")),
    }])

    col_cfg = {
        "🔖 VALUTA": st.column_config.SelectboxColumn(
            "🔖 VALUTA", options=VALUTE, required=True
        ),
        "VALOARE TOTALA COSTURI PROIECT": st.column_config.NumberColumn(
            "VALOARE TOTALA COSTURI PROIECT", format="%,.2f", min_value=0.0
        ),
        "CONTRIBUTIE UE TOTAL PROIECT": st.column_config.NumberColumn(
            "CONTRIBUTIE UE TOTAL PROIECT", format="%,.2f", min_value=0.0
        ),
        "COSTURI TOTALE UPT": st.column_config.NumberColumn(
            "COSTURI TOTALE UPT", format="%,.2f", min_value=0.0
        ),
        "VALOARE CONTRIBUTIE UE PENTRU UPT": st.column_config.NumberColumn(
            "VALOARE CONTRIBUTIE UE PENTRU UPT", format="%,.2f", min_value=0.0
        ),
        "VALOARE TOTALA ESTIMATA COSTURI ELIGIBILE": st.column_config.NumberColumn(
            "VALOARE TOTALA ESTIMATA COSTURI ELIGIBILE", format="%,.2f", min_value=0.0
        ),
        "VALOARE TOTALA GRANT SOLICITAT": st.column_config.NumberColumn(
            "VALOARE TOTALA GRANT SOLICITAT", format="%,.2f", min_value=0.0
        ),
        "VALOARE COSTURI ESTIMATE UPT": st.column_config.NumberColumn(
            "VALOARE COSTURI ESTIMATE UPT", format="%,.2f", min_value=0.0
        ),
        "VALOARE CONTRIBUTIE ESTIMATA PENTRU UPT": st.column_config.NumberColumn(
            "VALOARE CONTRIBUTIE ESTIMATA PENTRU UPT", format="%,.2f", min_value=0.0
        ),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"fin_int_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    return [{
        "cod_identificare":                 cod_introdus,
        "valuta":                           row["🔖 VALUTA"],
        "costuri_totale_proiect":           float(row["VALOARE TOTALA COSTURI PROIECT"] or 0),
        "contributie_totala_finantator":    float(row["CONTRIBUTIE UE TOTAL PROIECT"] or 0),
        "costuri_totale_upt":               float(row["COSTURI TOTALE UPT"] or 0),
        "contributie_finantator":           float(row["VALOARE CONTRIBUTIE UE PENTRU UPT"] or 0),
        "costuri_eligibile_estimate_total": float(row["VALOARE TOTALA ESTIMATA COSTURI ELIGIBILE"] or 0),
        "valoare_grant_solicitat_total":    float(row["VALOARE TOTALA GRANT SOLICITAT"] or 0),
        "costuri_eligibile_estimate_upt":   float(row["VALOARE COSTURI ESTIMATE UPT"] or 0),
        "valoare_grant_solicitat_upt":      float(row["VALOARE CONTRIBUTIE ESTIMATA PENTRU UPT"] or 0),
    }]
