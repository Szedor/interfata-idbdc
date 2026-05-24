# =========================================================
# IDBDC/domenii/_baza/sectiune_financiar_structurale.py
# VERSIUNE: 1.0
# STATUS: NOU
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

    valuta_ex = row_ex.get("valuta") or "LEI"
    if valuta_ex not in VALUTE: valuta_ex = "LEI"

    df = pd.DataFrame([{
        "VALUTA":                      valuta_ex,
        "VALOARE TOTALA PROIECT":      _f(row_ex.get("costuri_totale_proiect")),
        "CONTRIBUTIE UE TOTAL PROIECT":_f(row_ex.get("contributie_totala_finantator")),
        "VALOARE TOTALA ELIGIBILA":    _f(row_ex.get("cheltuieli_eligibile")),
        "VALOARE TOTALA NEELIGIBILA":  _f(row_ex.get("cheltuieli_neeligibile")),
        "VALOARE TOTALA UPT":          _f(row_ex.get("costuri_totale_upt")),
        "VALOARE ELIGIBILA UPT":       _f(row_ex.get("buget_upt")),
        "CONTRIBUTIE UE":              _f(row_ex.get("contributie_finantator")),
        "COFINANTARE NATIONALA":       _f(row_ex.get("cofinantare_nationala")),
        "COFINANTARE UPT":             _f(row_ex.get("cofinantare_upt")),
    }])

    col_cfg = {
        "VALUTA":                       st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
        "VALOARE TOTALA PROIECT":       st.column_config.NumberColumn("💰 VALOARE TOTALA PROIECT",       format="%,.2f", min_value=0.0),
        "CONTRIBUTIE UE TOTAL PROIECT": st.column_config.NumberColumn("🇪🇺 CONTRIBUTIE UE TOTAL PROIECT", format="%,.2f", min_value=0.0),
        "VALOARE TOTALA ELIGIBILA":     st.column_config.NumberColumn("📋 VALOARE TOTALA ELIGIBILA",     format="%,.2f", min_value=0.0),
        "VALOARE TOTALA NEELIGIBILA":   st.column_config.NumberColumn("📋 VALOARE TOTALA NEELIGIBILA",   format="%,.2f", min_value=0.0),
        "VALOARE TOTALA UPT":           st.column_config.NumberColumn("🏛️ VALOARE TOTALA UPT",           format="%,.2f", min_value=0.0),
        "VALOARE ELIGIBILA UPT":        st.column_config.NumberColumn("🏛️ VALOARE ELIGIBILA UPT",        format="%,.2f", min_value=0.0),
        "CONTRIBUTIE UE":               st.column_config.NumberColumn("🎓 CONTRIBUTIE UE",               format="%,.2f", min_value=0.0),
        "COFINANTARE NATIONALA":        st.column_config.NumberColumn("🏦 COFINANTARE NATIONALA",        format="%,.2f", min_value=0.0),
        "COFINANTARE UPT":              st.column_config.NumberColumn("🎓 COFINANTARE UPT",              format="%,.2f", min_value=0.0),
    }

    df_edit = st.data_editor(df, column_config=col_cfg, hide_index=True,
                              use_container_width=True, num_rows="fixed",
                              key=f"fin_structurale_editor_{cod_introdus}")
    row = df_edit.iloc[0]

    return [{
        "cod_identificare":            cod_introdus,
        "valuta":                      row["VALUTA"],
        "costuri_totale_proiect":      _f(row["VALOARE TOTALA PROIECT"]),
        "contributie_totala_finantator": _f(row["CONTRIBUTIE UE TOTAL PROIECT"]),
        "cheltuieli_eligibile":        _f(row["VALOARE TOTALA ELIGIBILA"]),
        "cheltuieli_neeligibile":      _f(row["VALOARE TOTALA NEELIGIBILA"]),
        "costuri_totale_upt":          _f(row["VALOARE TOTALA UPT"]),
        "buget_upt":                   _f(row["VALOARE ELIGIBILA UPT"]),
        "contributie_finantator":      _f(row["CONTRIBUTIE UE"]),
        "cofinantare_nationala":       _f(row["COFINANTARE NATIONALA"]),
        "cofinantare_upt":             _f(row["COFINANTARE UPT"]),
    }]
