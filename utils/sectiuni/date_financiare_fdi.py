# =========================================================
# utils/sectiuni/date_financiare_fdi.py
# VERSIUNE: 2.0
# STATUS: STABIL
# DATA: 2026.05.06
# =========================================================
# MODIFICĂRI VERSIUNEA 2.0:
#   - Cofinanțarea se păstrează după salvare: _safe_float
#     tratează corect valoarea 0.0 (nu o confundă cu None).
#   - Total valoare proiect: citit din BD dacă există,
#     recalculat și afișat explicit după editor.
#   - Nota subsol: "Total valoare proiect se calculează
#     automat după salvarea fișei."
# =========================================================

import streamlit as st
import pandas as pd


def render_date_financiare_fdi(supabase, cod_introdus, is_new, date_existente):
    VALUTE = ["LEI", "EUR", "USD"]

    if is_new or not date_existente:
        row_ex = {
            "valuta":                  "LEI",
            "suma_solicitata_fdi":     0.0,
            "suma_aprobata_mec":       0.0,
            "cofinantare_upt_fdi":     0.0,
            "total_buget_proiect_fdi": 0.0,
        }
    else:
        row_ex = date_existente[0] if isinstance(date_existente, list) else date_existente

    def _safe_float(val):
        # None și "" → 0.0 ; 0.0 rămâne 0.0 (nu e tratat ca lipsă)
        if val is None or val == "":
            return 0.0
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    valuta_ex = row_ex.get("valuta") or "LEI"
    if valuta_ex not in VALUTE:
        valuta_ex = "LEI"

    suma_sol = _safe_float(row_ex.get("suma_solicitata_fdi"))
    suma_apr = _safe_float(row_ex.get("suma_aprobata_mec"))
    cofin    = _safe_float(row_ex.get("cofinantare_upt_fdi"))
    total    = _safe_float(row_ex.get("total_buget_proiect_fdi"))
    if total == 0.0:
        total = suma_apr + cofin

    df = pd.DataFrame([{
        "VALUTA":                valuta_ex,
        "SUMA SOLICITATA":       suma_sol,
        "SUMA APROBATA":         suma_apr,
        "COFINANTARE":           cofin,
        "TOTAL VALOARE PROIECT": total,
    }])

    col_cfg = {
        "VALUTA": st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
        "SUMA SOLICITATA":       st.column_config.NumberColumn("💰 SUMA SOLICITATA",       format="%,.2f", min_value=0.0),
        "SUMA APROBATA":         st.column_config.NumberColumn("✅ SUMA APROBATA",         format="%,.2f", min_value=0.0),
        "COFINANTARE":           st.column_config.NumberColumn("🏛️ COFINANTARE",           format="%,.2f", min_value=0.0),
        "TOTAL VALOARE PROIECT": st.column_config.NumberColumn("📊 TOTAL VALOARE PROIECT", format="%,.2f", disabled=True),
    }

    df_edit = st.data_editor(
        df, column_config=col_cfg, hide_index=True,
        use_container_width=True, num_rows="fixed",
        key=f"fin_fdi_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    suma_apr_e = _safe_float(row["SUMA APROBATA"])
    cofin_e    = _safe_float(row["COFINANTARE"])
    total_e    = suma_apr_e + cofin_e

    st.caption("Total valoare proiect se calculează automat după salvarea fișei.")

    return [{
        "cod_identificare":        cod_introdus,
        "valuta":                  row["VALUTA"],
        "suma_solicitata_fdi":     _safe_float(row["SUMA SOLICITATA"]),
        "suma_aprobata_mec":       suma_apr_e,
        "cofinantare_upt_fdi":     cofin_e,
        "total_buget_proiect_fdi": total_e,
    }]
