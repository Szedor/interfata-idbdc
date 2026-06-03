# =========================================================
# IDBDC/domenii/proiecte_structurale/financiar.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.06.02
# =========================================================
# DATE FINANCIARE — ordinea și etichetele exacte din mapare:
#  1. VALUTA                    ← 🔖
#  2. VALOARE TOTALA PROIECT    → costuri_totale_proiect
#  3. CONTRIBUTIE UE TOTAL PROIECT → contributie_totala_finantator
#  4. VALOARE TOTALA ELIGIBILA  → cheltuieli_eligibile
#  5. VALOARE TOTALA NEELIGIBILA → cheltuieli_neeligibile
#  6. VALOARE TOTALA UPT        → costuri_totale_upt
#  7. VALOARE ELIGIBILA UPT     → buget_upt
#  8. CONTRIBUTIE UE            → contributie_finantator
#  9. COFINANTARE NATIONALA     → cofinantare_nationala
# 10. COFINANTARE UPT           → cofinantare_upt
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

    valuta_ex = row_ex.get("valuta") or "LEI"
    if valuta_ex not in VALUTE:
        valuta_ex = "LEI"

    df = pd.DataFrame([{
        "🔖 VALUTA":                      valuta_ex,
        "VALOARE TOTALA PROIECT":         _sf(row_ex.get("costuri_totale_proiect")),
        "CONTRIBUTIE UE TOTAL PROIECT":   _sf(row_ex.get("contributie_totala_finantator")),
        "VALOARE TOTALA ELIGIBILA":       _sf(row_ex.get("cheltuieli_eligibile")),
        "VALOARE TOTALA NEELIGIBILA":     _sf(row_ex.get("cheltuieli_neeligibile")),
        "VALOARE TOTALA UPT":             _sf(row_ex.get("costuri_totale_upt")),
        "VALOARE ELIGIBILA UPT":          _sf(row_ex.get("buget_upt")),
        "CONTRIBUTIE UE":                 _sf(row_ex.get("contributie_finantator")),
        "COFINANTARE NATIONALA":          _sf(row_ex.get("cofinantare_nationala")),
        "COFINANTARE UPT":                _sf(row_ex.get("cofinantare_upt")),
    }])

    col_cfg = {
        "🔖 VALUTA": st.column_config.SelectboxColumn(
            "🔖 VALUTA", options=VALUTE, required=True
        ),
        "VALOARE TOTALA PROIECT": st.column_config.NumberColumn(
            "VALOARE TOTALA PROIECT", format="%,.2f", min_value=0.0
        ),
        "CONTRIBUTIE UE TOTAL PROIECT": st.column_config.NumberColumn(
            "CONTRIBUTIE UE TOTAL PROIECT", format="%,.2f", min_value=0.0
        ),
        "VALOARE TOTALA ELIGIBILA": st.column_config.NumberColumn(
            "VALOARE TOTALA ELIGIBILA", format="%,.2f", min_value=0.0
        ),
        "VALOARE TOTALA NEELIGIBILA": st.column_config.NumberColumn(
            "VALOARE TOTALA NEELIGIBILA", format="%,.2f", min_value=0.0
        ),
        "VALOARE TOTALA UPT": st.column_config.NumberColumn(
            "VALOARE TOTALA UPT", format="%,.2f", min_value=0.0
        ),
        "VALOARE ELIGIBILA UPT": st.column_config.NumberColumn(
            "VALOARE ELIGIBILA UPT", format="%,.2f", min_value=0.0
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
        df, column_config=col_cfg, hide_index=True,
        use_container_width=True, num_rows="fixed",
        key=f"fin_structurale_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    return [{
        "cod_identificare":              cod_introdus,
        "valuta":                        row["🔖 VALUTA"],
        "costuri_totale_proiect":        float(row["VALOARE TOTALA PROIECT"] or 0),
        "contributie_totala_finantator": float(row["CONTRIBUTIE UE TOTAL PROIECT"] or 0),
        "cheltuieli_eligibile":          float(row["VALOARE TOTALA ELIGIBILA"] or 0),
        "cheltuieli_neeligibile":        float(row["VALOARE TOTALA NEELIGIBILA"] or 0),
        "costuri_totale_upt":            float(row["VALOARE TOTALA UPT"] or 0),
        "buget_upt":                     float(row["VALOARE ELIGIBILA UPT"] or 0),
        "contributie_finantator":        float(row["CONTRIBUTIE UE"] or 0),
        "cofinantare_nationala":         float(row["COFINANTARE NATIONALA"] or 0),
        "cofinantare_upt":               float(row["COFINANTARE UPT"] or 0),
    }]
