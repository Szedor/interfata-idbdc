# =========================================================
# IDBDC/domenii/_baza/sectiune_financiar_interreg_see.py
# VERSIUNE: 1.0
# STATUS: NOU - comun INTERREG si SEE
# DATA: 2026.05.09
# =========================================================

import streamlit as st
import pandas as pd


def render(supabase, cod_introdus, is_new, date_existente,
           label_total="BUGET TOTAL PROIECT",
           label_buget_upt="BUGET UPT",
           label_contributie="CONTRIBUTIE UE",
           editor_key_suffix="interreg_see"):

    VALUTE = ["EUR", "LEI", "USD"]
    row_ex = {} if (is_new or not date_existente) else (date_existente[0] if isinstance(date_existente, list) else date_existente)

    def _f(v):
        try: return float(v) if v else 0.0
        except: return 0.0

    valuta_ex = row_ex.get("valuta") or "EUR"
    if valuta_ex not in VALUTE: valuta_ex = "EUR"

    df = pd.DataFrame([{
        "VALUTA":                valuta_ex,
        label_total:             _f(row_ex.get("costuri_totale_proiect")),
        label_buget_upt:         _f(row_ex.get("buget_upt")),
        label_contributie:       _f(row_ex.get("contributie_finantator")),
        "COFINANTARE NATIONALA": _f(row_ex.get("cofinantare_nationala")),
        "COFINANTARE UPT":       _f(row_ex.get("cofinantare_upt")),
    }])

    col_cfg = {
        "VALUTA":                st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
        label_total:             st.column_config.NumberColumn(f"💰 {label_total}",       format="%,.2f", min_value=0.0),
        label_buget_upt:         st.column_config.NumberColumn(f"🏛️ {label_buget_upt}",   format="%,.2f", min_value=0.0),
        label_contributie:       st.column_config.NumberColumn(f"🇪🇺 {label_contributie}", format="%,.2f", min_value=0.0),
        "COFINANTARE NATIONALA": st.column_config.NumberColumn("🏦 COFINANTARE NATIONALA", format="%,.2f", min_value=0.0),
        "COFINANTARE UPT":       st.column_config.NumberColumn("🎓 COFINANTARE UPT",       format="%,.2f", min_value=0.0),
    }

    df_edit = st.data_editor(df, column_config=col_cfg, hide_index=True,
                              use_container_width=True, num_rows="fixed",
                              key=f"fin_{editor_key_suffix}_editor_{cod_introdus}")
    row = df_edit.iloc[0]

    return [{
        "cod_identificare":       cod_introdus,
        "valuta":                 row["VALUTA"],
        "costuri_totale_proiect": _f(row[label_total]),
        "buget_upt":              _f(row[label_buget_upt]),
        "contributie_finantator": _f(row[label_contributie]),
        "cofinantare_nationala":  _f(row["COFINANTARE NATIONALA"]),
        "cofinantare_upt":        _f(row["COFINANTARE UPT"]),
    }]
