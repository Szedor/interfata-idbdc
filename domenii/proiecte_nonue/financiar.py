# =========================================================
# IDBDC/domenii/proiecte_nonue/financiar.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.06.02
# =========================================================
# DATE FINANCIARE — ordinea și etichetele exacte din mapare:
#  1. VALUTA                  ← 🔖
#  2. BUGET TOTAL PROIECT     → costuri_totale_proiect
#  3. COSTURI ELIGIBILE       → cheltuieli_eligibile
#  4. FINANTARE EXTERNA       → contributie_finantator
#  5. COFINANTARE UPT         → cofinantare_upt
#  6. GRANT SOLICITAT         → grant_solicitat
#  7. GRANT APROBAT           → grant_aprobat
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
        "🔖 VALUTA":           valuta_ex,
        "BUGET TOTAL PROIECT": _sf(row_ex.get("costuri_totale_proiect")),
        "COSTURI ELIGIBILE":   _sf(row_ex.get("cheltuieli_eligibile")),
        "FINANTARE EXTERNA":   _sf(row_ex.get("contributie_finantator")),
        "COFINANTARE UPT":     _sf(row_ex.get("cofinantare_upt")),
        "GRANT SOLICITAT":     _sf(row_ex.get("grant_solicitat")),
        "GRANT APROBAT":       _sf(row_ex.get("grant_aprobat")),
    }])

    col_cfg = {
        "🔖 VALUTA": st.column_config.SelectboxColumn(
            "🔖 VALUTA", options=VALUTE, required=True
        ),
        "BUGET TOTAL PROIECT": st.column_config.NumberColumn(
            "BUGET TOTAL PROIECT", format="%,.2f", min_value=0.0
        ),
        "COSTURI ELIGIBILE": st.column_config.NumberColumn(
            "COSTURI ELIGIBILE", format="%,.2f", min_value=0.0
        ),
        "FINANTARE EXTERNA": st.column_config.NumberColumn(
            "FINANTARE EXTERNA", format="%,.2f", min_value=0.0
        ),
        "COFINANTARE UPT": st.column_config.NumberColumn(
            "COFINANTARE UPT", format="%,.2f", min_value=0.0
        ),
        "GRANT SOLICITAT": st.column_config.NumberColumn(
            "GRANT SOLICITAT", format="%,.2f", min_value=0.0
        ),
        "GRANT APROBAT": st.column_config.NumberColumn(
            "GRANT APROBAT", format="%,.2f", min_value=0.0
        ),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"fin_nonue_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    return [{
        "cod_identificare":       cod_introdus,
        "valuta":                 row["🔖 VALUTA"],
        "costuri_totale_proiect": float(row["BUGET TOTAL PROIECT"] or 0),
        "cheltuieli_eligibile":   float(row["COSTURI ELIGIBILE"] or 0),
        "contributie_finantator": float(row["FINANTARE EXTERNA"] or 0),
        "cofinantare_upt":        float(row["COFINANTARE UPT"] or 0),
        "grant_solicitat":        float(row["GRANT SOLICITAT"] or 0),
        "grant_aprobat":          float(row["GRANT APROBAT"] or 0),
    }]
