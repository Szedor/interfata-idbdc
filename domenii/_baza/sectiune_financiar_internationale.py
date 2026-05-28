# =========================================================
# IDBDC/domenii/_baza/sectiune_financiar_internationale.py
# VERSIUNE: 1.3
# STATUS: CORECTAT - eliminat an_referinta din payload (nu e aplicabil)
# DATA: 2026.05.28
# =========================================================
# MODIFICARI VERSIUNEA 1.3:
#   - Eliminat an_referinta din dict-ul returnat
#     (proiectele INTERNATIONALE nu au structura financiara pe ani;
#      coloana an_referinta din com_date_financiare permite acum NULL
#      conform SQL_3_fix_com_date_financiare_internationale.sql)
#   - Logica de date si coloanele de afisare raman neschimbate
# =========================================================

import streamlit as st
import pandas as pd


def render(supabase, cod_introdus, is_new, date_existente):
    VALUTE = ["EUR", "LEI", "USD"]

    row_ex = {} if (is_new or not date_existente) else (
        date_existente[0] if isinstance(date_existente, list) else date_existente
    )

    def _f(v):
        try:
            return float(v) if v not in (None, "") else 0.0
        except (TypeError, ValueError):
            return 0.0

    valuta_ex = row_ex.get("valuta") or "EUR"
    if valuta_ex not in VALUTE:
        valuta_ex = "EUR"

    df = pd.DataFrame([{
        "VALUTA":                                    valuta_ex,
        "VALOARE TOTALA COSTURI PROIECT":            _f(row_ex.get("costuri_totale_proiect")),
        "CONTRIBUTIE UE TOTAL PROIECT":              _f(row_ex.get("contributie_totala_finantator")),
        "COSTURI TOTALE UPT":                        _f(row_ex.get("costuri_totale_upt")),
        "VALOARE CONTRIBUTIE UE PENTRU UPT":         _f(row_ex.get("contributie_finantator")),
        "VALOARE TOTALA ESTIMATA COSTURI ELIGIBILE": _f(row_ex.get("costuri_eligibile_estimate_total")),
        "VALOARE TOTALA GRANT SOLICITAT":            _f(row_ex.get("valoare_grant_solicitat_total")),
        "VALOARE COSTURI ESTIMATE UPT":              _f(row_ex.get("costuri_eligibile_estimate_upt")),
        "VALOARE CONTRIBUTIE ESTIMATA PENTRU UPT":  _f(row_ex.get("valoare_grant_solicitat_upt")),
    }])

    col_cfg = {
        "VALUTA": st.column_config.SelectboxColumn(
            "💱 VALUTA", options=VALUTE, required=True
        ),
        "VALOARE TOTALA COSTURI PROIECT":            st.column_config.NumberColumn(
            "💰 VALOARE TOTALA COSTURI PROIECT",            format="%,.2f", min_value=0.0),
        "CONTRIBUTIE UE TOTAL PROIECT":              st.column_config.NumberColumn(
            "🇪🇺 CONTRIBUTIE UE TOTAL PROIECT",              format="%,.2f", min_value=0.0),
        "COSTURI TOTALE UPT":                        st.column_config.NumberColumn(
            "🏛️ COSTURI TOTALE UPT",                        format="%,.2f", min_value=0.0),
        "VALOARE CONTRIBUTIE UE PENTRU UPT":         st.column_config.NumberColumn(
            "🎓 VALOARE CONTRIBUTIE UE PENTRU UPT",         format="%,.2f", min_value=0.0),
        "VALOARE TOTALA ESTIMATA COSTURI ELIGIBILE": st.column_config.NumberColumn(
            "📋 VALOARE TOTALA ESTIMATA COSTURI ELIGIBILE", format="%,.2f", min_value=0.0),
        "VALOARE TOTALA GRANT SOLICITAT":            st.column_config.NumberColumn(
            "📋 VALOARE TOTALA GRANT SOLICITAT",            format="%,.2f", min_value=0.0),
        "VALOARE COSTURI ESTIMATE UPT":              st.column_config.NumberColumn(
            "📋 VALOARE COSTURI ESTIMATE UPT",              format="%,.2f", min_value=0.0),
        "VALOARE CONTRIBUTIE ESTIMATA PENTRU UPT":  st.column_config.NumberColumn(
            "📋 VALOARE CONTRIBUTIE ESTIMATA PENTRU UPT",  format="%,.2f", min_value=0.0),
    }

    df_edit = st.data_editor(
        df, column_config=col_cfg, hide_index=True,
        use_container_width=True, num_rows="fixed",
        key=f"fin_internationale_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    # an_referinta este intentionat absent — proiectele INTERNATIONALE
    # nu au structura financiara pe ani de referinta
    return [{
        "cod_identificare":                  cod_introdus,
        "valuta":                            row["VALUTA"],
        "costuri_totale_proiect":            _f(row["VALOARE TOTALA COSTURI PROIECT"]),
        "contributie_totala_finantator":     _f(row["CONTRIBUTIE UE TOTAL PROIECT"]),
        "costuri_totale_upt":                _f(row["COSTURI TOTALE UPT"]),
        "contributie_finantator":            _f(row["VALOARE CONTRIBUTIE UE PENTRU UPT"]),
        "costuri_eligibile_estimate_total":  _f(row["VALOARE TOTALA ESTIMATA COSTURI ELIGIBILE"]),
        "valoare_grant_solicitat_total":     _f(row["VALOARE TOTALA GRANT SOLICITAT"]),
        "costuri_eligibile_estimate_upt":    _f(row["VALOARE COSTURI ESTIMATE UPT"]),
        "valoare_grant_solicitat_upt":       _f(row["VALOARE CONTRIBUTIE ESTIMATA PENTRU UPT"]),
    }]
