# =========================================================
# IDBDC/domenii/proiecte_fdi/tehnic.py
# v.modul.1.0 - Aspecte tehnice pentru Proiecte FDI
# =========================================================

import streamlit as st
import pandas as pd


def render(supabase, cod_introdus, is_new, date_existente):
    if is_new or not date_existente:
        row_ex = {
            "obiectiv_general": "",
            "obiective_specifice": "",
            "activitati": "",
            "rezultate": "",
        }
    else:
        row_ex = date_existente[0] if isinstance(date_existente, list) else date_existente

    df = pd.DataFrame([{
        "🎯 OBIECTIV GENERAL": row_ex.get("obiectiv_general", ""),
        "📌 OBIECTIVE SPECIFICE": row_ex.get("obiective_specifice", ""),
        "⚙️ ACTIVITATI": row_ex.get("activitati_proiect", ""),
        "📈 REZULTATE": row_ex.get("rezultate_proiect", ""),
    }])

    col_cfg = {
        "🎯 OBIECTIV GENERAL": st.column_config.TextColumn("🎯 OBIECTIV GENERAL", width="large"),
        "📌 OBIECTIVE SPECIFICE": st.column_config.TextColumn("📌 OBIECTIVE SPECIFICE", width="large"),
        "⚙️ ACTIVITATI": st.column_config.TextColumn("⚙️ ACTIVITATI", width="large"),
        "📈 REZULTATE": st.column_config.TextColumn("📈 REZULTATE", width="large"),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"tehnic_fdi_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    return [{
        "cod_identificare": cod_introdus,
        "obiectiv_general": row["🎯 OBIECTIV GENERAL"] or None,
        "obiective_specifice": row["📌 OBIECTIVE SPECIFICE"] or None,
        "activitati_proiect": row["⚙️ ACTIVITATI"] or None,
        "rezultate_proiect": row["📈 REZULTATE"] or None,
    }]
