# =========================================================
# IDBDC/domenii/_baza/sectiune_financiar_fdi.py
# VERSIUNE: 1.0
# STATUS: NOU - Date financiare pentru Proiecte FDI
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Randează secțiunea Date financiare pentru Proiecte FDI.
#   Conținut preluat din utils/sectiuni/date_financiare_fdi.py
#   v2.0, neatins.
# =========================================================

import streamlit as st
import pandas as pd


def render(supabase, cod_introdus, is_new, date_existente):
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
        "TOTAL VALOARE CONTRACT": total,
    }])

    col_cfg = {
        "VALUTA":                 st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
        "SUMA SOLICITATA":        st.column_config.NumberColumn("💰 SUMA SOLICITATA",        format="%,.2f", min_value=0.0),
        "SUMA APROBATA":          st.column_config.NumberColumn("✅ SUMA APROBATA",          format="%,.2f", min_value=0.0),
        "COFINANTARE":            st.column_config.NumberColumn("🏛️ COFINANTARE",            format="%,.2f", min_value=0.0),
        "TOTAL VALOARE CONTRACT":  st.column_config.NumberColumn("📊 TOTAL VALOARE CONTRACT", format="%,.2f", disabled=True),
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

    st.caption("ℹ️ Total valoare contract se calculează automat după salvarea fișei.")

    return [{
        "cod_identificare":        cod_introdus,
        "valuta":                  row["VALUTA"],
        "suma_solicitata_fdi":     _safe_float(row["SUMA SOLICITATA"]),
        "suma_aprobata_mec":       suma_apr_e,
        "cofinantare_upt_fdi":     cofin_e,
        "total_buget_proiect_fdi": total_e,
    }]
