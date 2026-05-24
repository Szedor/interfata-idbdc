# =========================================================
# IDBDC/domenii/_baza/sectiune_financiar_see.py
# VERSIUNE: 1.1
# STATUS: ACTUALIZAT - completat cu toate campurile din mapare finala
# DATA: 2026.05.23
# =========================================================

import streamlit as st
import pandas as pd


def render(supabase, cod_introdus, is_new, date_existente):
    VALUTE = ["EUR", "LEI", "USD"]
    row_ex = {} if (is_new or not date_existente) else (date_existente[0] if isinstance(date_existente, list) else date_existente)

    def _f(v):
        try: return float(v) if v else 0.0
        except: return 0.0

    valuta_ex = row_ex.get("valuta") or "EUR"
    if valuta_ex not in VALUTE: valuta_ex = "EUR"

    df = pd.DataFrame([{
        "VALUTA":                    valuta_ex,
        "CHELTUIELI ELIGIBILE TOTALE": _f(row_ex.get("costuri_totale_proiect")),
        "BUGET UPT":                 _f(row_ex.get("buget_upt")),
        "CONTRIBUTIE MECANISM":      _f(row_ex.get("contributie_finantator")),
        "COFINANTARE NATIONALA":     _f(row_ex.get("cofinantare_nationala")),
        "COFINANTARE UPT":           _f(row_ex.get("cofinantare_upt")),
    }])

    col_cfg = {
        "VALUTA":                    st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
        "CHELTUIELI ELIGIBILE TOTALE": st.column_config.NumberColumn("💰 CHELTUIELI ELIGIBILE TOTALE", format="%,.2f", min_value=0.0),
        "BUGET UPT":                 st.column_config.NumberColumn("🏛️ BUGET UPT",                  format="%,.2f", min_value=0.0),
        "CONTRIBUTIE MECANISM":      st.column_config.NumberColumn("🌐 CONTRIBUTIE MECANISM",        format="%,.2f", min_value=0.0),
        "COFINANTARE NATIONALA":     st.column_config.NumberColumn("🏦 COFINANTARE NATIONALA",       format="%,.2f", min_value=0.0),
        "COFINANTARE UPT":           st.column_config.NumberColumn("🎓 COFINANTARE UPT",             format="%,.2f", min_value=0.0),
    }

    df_edit = st.data_editor(df, column_config=col_cfg, hide_index=True,
                              use_container_width=True, num_rows="fixed",
                              key=f"fin_see_editor_{cod_introdus}")
    row = df_edit.iloc[0]

    return [{
        "cod_identificare":       cod_introdus,
        "valuta":                 row["VALUTA"],
        "costuri_totale_proiect": _f(row["CHELTUIELI ELIGIBILE TOTALE"]),
        "buget_upt":              _f(row["BUGET UPT"]),
        "contributie_finantator": _f(row["CONTRIBUTIE MECANISM"]),
        "cofinantare_nationala":  _f(row["COFINANTARE NATIONALA"]),
        "cofinantare_upt":        _f(row["COFINANTARE UPT"]),
    }]
