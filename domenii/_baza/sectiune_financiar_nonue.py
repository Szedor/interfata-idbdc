# =========================================================
# IDBDC/domenii/_baza/sectiune_financiar_nonue.py
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
        "VALUTA":              valuta_ex,
        "BUGET TOTAL PROIECT": _f(row_ex.get("costuri_totale_proiect")),
        "COSTURI ELIGIBILE":   _f(row_ex.get("cheltuieli_eligibile")),
        "FINANTARE EXTERNA":   _f(row_ex.get("contributie_finantator")),
        "COFINANTARE UPT":     _f(row_ex.get("cofinantare_upt")),
        "GRANT SOLICITAT":     _f(row_ex.get("grant_solicitat")),
        "GRANT APROBAT":       _f(row_ex.get("grant_aprobat")),
    }])

    col_cfg = {
        "VALUTA":              st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
        "BUGET TOTAL PROIECT": st.column_config.NumberColumn("💰 BUGET TOTAL PROIECT", format="%,.2f", min_value=0.0),
        "COSTURI ELIGIBILE":   st.column_config.NumberColumn("📋 COSTURI ELIGIBILE",   format="%,.2f", min_value=0.0),
        "FINANTARE EXTERNA":   st.column_config.NumberColumn("🌐 FINANTARE EXTERNA",   format="%,.2f", min_value=0.0),
        "COFINANTARE UPT":     st.column_config.NumberColumn("🎓 COFINANTARE UPT",     format="%,.2f", min_value=0.0),
        "GRANT SOLICITAT":     st.column_config.NumberColumn("📩 GRANT SOLICITAT",     format="%,.2f", min_value=0.0),
        "GRANT APROBAT":       st.column_config.NumberColumn("✅ GRANT APROBAT",       format="%,.2f", min_value=0.0),
    }

    df_edit = st.data_editor(df, column_config=col_cfg, hide_index=True,
                              use_container_width=True, num_rows="fixed",
                              key=f"fin_nonue_editor_{cod_introdus}")
    row = df_edit.iloc[0]

    return [{
        "cod_identificare":       cod_introdus,
        "valuta":                 row["VALUTA"],
        "costuri_totale_proiect": _f(row["BUGET TOTAL PROIECT"]),
        "cheltuieli_eligibile":   _f(row["COSTURI ELIGIBILE"]),
        "contributie_finantator": _f(row["FINANTARE EXTERNA"]),
        "cofinantare_upt":        _f(row["COFINANTARE UPT"]),
        "grant_solicitat":        _f(row["GRANT SOLICITAT"]),
        "grant_aprobat":          _f(row["GRANT APROBAT"]),
    }]
