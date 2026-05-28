# =========================================================
# domenii/_baza/sectiune_financiar/proiecte_pncdi.py
# v.modul.1.0 - Date financiare pentru Proiecte PNCDI (multi-an)
# =========================================================

import streamlit as st
import pandas as pd

def render(supabase, cod_introdus, is_new, date_existente):
    VALUTE = ["LEI", "EUR", "USD"]
    
    # Exemplu: pentru multi-an, se poate afișa un tabel cu mai multe rânduri
    # Momentan, placeholder simplu
    if is_new or not date_existente:
        rows = [{"an_referinta": 2024, "valuta": "LEI", "valoare": 0.0}]
    else:
        rows = []
        for r in date_existente:
            rows.append({
                "an_referinta": r.get("an_referinta", 2024),
                "valuta": r.get("valuta", "LEI"),
                "valoare": float(r.get("valoare_contract_cep_terti_speciale") or 0),
            })
    
    df = pd.DataFrame(rows)
    df = df.rename(columns={
        "an_referinta": "📅 AN",
        "valuta": "💱 VALUTA",
        "valoare": "💰 VALOARE",
    })

    col_cfg = {
        "📅 AN": st.column_config.NumberColumn("📅 AN", format="%d", min_value=2000, max_value=2030),
        "💱 VALUTA": st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
        "💰 VALOARE": st.column_config.NumberColumn("💰 VALOARE", format="%.2f", min_value=0.0),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic",
        key=f"fin_editor_pncdi_{cod_introdus}",
    )
    
    rezultat = []
    for _, row in df_edit.iterrows():
        rezultat.append({
            "cod_identificare": cod_introdus,
            "an_referinta": int(row["📅 AN"]),
            "valuta": row["💱 VALUTA"],
            "valoare_contract_cep_terti_speciale": float(row["💰 VALOARE"] or 0),
        })
    return rezultat
