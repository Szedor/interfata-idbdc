# =========================================================
# IDBDC/domenii/proiecte_fdi/financiar.py
# v.modul.1.0 - Date financiare pentru Proiecte FDI
# =========================================================

import streamlit as st
import pandas as pd


def render(supabase, cod_introdus, is_new, date_existente):
    VALUTE = ["LEI", "EUR", "USD"]
    
    if is_new or not date_existente:
        row_ex = {
            "valuta": "LEI",
            "suma_solicitata": 0.0,
            "suma_aprobata": 0.0,
            "cofinantare": 0.0,
        }
    else:
        row_ex = date_existente[0] if isinstance(date_existente, list) else date_existente
        try:
            suma_solicitata = float(row_ex.get("suma_solicitata_fdi") or 0)
        except:
            suma_solicitata = 0.0
        try:
            suma_aprobata = float(row_ex.get("suma_aprobata_mec") or 0)
        except:
            suma_aprobata = 0.0
        try:
            cofinantare = float(row_ex.get("cofinantare_upt_fdi") or 0)
        except:
            cofinantare = 0.0
        valuta_ex = row_ex.get("valuta", "LEI")
        if valuta_ex not in VALUTE:
            valuta_ex = "LEI"

    df = pd.DataFrame([{
        "💱 VALUTA": valuta_ex,
        "💰 SUMA SOLICITATA": suma_solicitata,
        "✅ SUMA APROBATA": suma_aprobata,
        "🏛️ COFINANTARE": cofinantare,
    }])

    col_cfg = {
        "💱 VALUTA": st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
        "💰 SUMA SOLICITATA": st.column_config.NumberColumn("💰 SUMA SOLICITATA", format="%.2f", min_value=0.0),
        "✅ SUMA APROBATA": st.column_config.NumberColumn("✅ SUMA APROBATA", format="%.2f", min_value=0.0),
        "🏛️ COFINANTARE": st.column_config.NumberColumn("🏛️ COFINANTARE", format="%.2f", min_value=0.0),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"fin_fdi_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    suma_aprobata = float(row["✅ SUMA APROBATA"] or 0)
    cofinantare = float(row["🏛️ COFINANTARE"] or 0)
    total = suma_aprobata + cofinantare

    st.caption(f"📊 **TOTAL VALOARE CONTRACT: {total:,.2f} {row['💱 VALUTA']}** (Suma aprobată + Cofinanțare)")

    return [{
        "cod_identificare": cod_introdus,
        "valuta": row["💱 VALUTA"],
        "suma_solicitata_fdi": float(row["💰 SUMA SOLICITATA"] or 0),
        "suma_aprobata_mec": suma_aprobata,
        "cofinantare_upt_fdi": cofinantare,
        "total_buget_proiect_fdi": total,
    }]
