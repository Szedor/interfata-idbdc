# =========================================================
# IDBDC/domenii/proiecte_pnrr/financiar.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.06.02
# =========================================================
# DATE FINANCIARE — tabelă dedicată: com_date_financiare_pn
# Structură identică cu PNCDI — pe ani de referință:
#  - VALUTA              ← 🔖
#  - ANUL DE REFERINTA   ← 🔢
#  - VALOARE AN REFERINTA
#  - COFINANTARE AN REFERINTA
# Totaluri calculate automat: VALOARE TOTALA + COFINANTARE TOTALA
# =========================================================

import streamlit as st
import pandas as pd


VALUTE = ["LEI", "EUR", "USD"]
NR_RANDURI_INIT = 4


def render(supabase, cod_introdus, is_new, date_existente):
    if is_new or not date_existente:
        rows_ex = []
    else:
        rows_ex = date_existente if isinstance(date_existente, list) else [date_existente]

    def _sf(val):
        if val is None or val == "":
            return 0.0
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    valuta_ex = "LEI"
    if rows_ex:
        valuta_ex = rows_ex[0].get("valuta") or "LEI"
        if valuta_ex not in VALUTE:
            valuta_ex = "LEI"

    valuta = st.selectbox("🔖 VALUTA", options=VALUTE,
                          index=VALUTE.index(valuta_ex),
                          key=f"pnrr_valuta_{cod_introdus}")

    st.markdown(
        "<div style='color:rgba(255,255,255,0.65);font-size:0.85rem;margin-bottom:6px;'>"
        "Introduceți valorile pentru fiecare an de referință. "
        "Totalurile se calculează automat.</div>",
        unsafe_allow_html=True,
    )

    if rows_ex:
        data_init = [{
            "ANUL DE REFERINTA":        int(r.get("an_referinta") or 0),
            "VALOARE AN REFERINTA":     _sf(r.get("valoare_contract_an_referinta")),
            "COFINANTARE AN REFERINTA": _sf(r.get("cofinantare_contract_an_referinta")),
        } for r in rows_ex]
    else:
        data_init = [
            {"ANUL DE REFERINTA": 0, "VALOARE AN REFERINTA": 0.0, "COFINANTARE AN REFERINTA": 0.0}
            for _ in range(NR_RANDURI_INIT)
        ]

    df = pd.DataFrame(data_init)

    col_cfg = {
        "ANUL DE REFERINTA": st.column_config.NumberColumn(
            "🔢 ANUL DE REFERINTA", format="%d", min_value=1990, max_value=2100, required=False
        ),
        "VALOARE AN REFERINTA": st.column_config.NumberColumn(
            "VALOARE AN REFERINTA", format="%,.2f", min_value=0.0
        ),
        "COFINANTARE AN REFERINTA": st.column_config.NumberColumn(
            "COFINANTARE AN REFERINTA", format="%,.2f", min_value=0.0
        ),
    }

    df_edit = st.data_editor(
        df, column_config=col_cfg, hide_index=True,
        use_container_width=True, num_rows="dynamic",
        key=f"fin_pnrr_editor_{cod_introdus}",
    )

    total_valoare = float(df_edit["VALOARE AN REFERINTA"].fillna(0).sum())
    total_cofin   = float(df_edit["COFINANTARE AN REFERINTA"].fillna(0).sum())

    st.markdown(
        f"<div style='background:rgba(255,255,255,0.07);border-radius:8px;"
        f"padding:8px 14px;margin-top:6px;font-size:0.90rem;'>"
        f"<b style='color:rgba(255,255,255,0.70);'>VALOARE TOTALA:</b> "
        f"<span style='color:#ffffff;font-weight:700;'>{total_valoare:,.2f} {valuta}</span>"
        f"&nbsp;&nbsp;&nbsp;"
        f"<b style='color:rgba(255,255,255,0.70);'>COFINANTARE TOTALA:</b> "
        f"<span style='color:#ffffff;font-weight:700;'>{total_cofin:,.2f} {valuta}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    rezultat = []
    for _, row in df_edit.iterrows():
        an = row.get("ANUL DE REFERINTA")
        try:
            an_int = int(an) if an and not pd.isna(an) else 0
        except (TypeError, ValueError):
            an_int = 0
        if an_int == 0:
            continue
        rezultat.append({
            "cod_identificare":                  cod_introdus,
            "valuta":                            valuta,
            "an_referinta":                      an_int,
            "valoare_contract_an_referinta":     float(row["VALOARE AN REFERINTA"] or 0),
            "cofinantare_contract_an_referinta": float(row["COFINANTARE AN REFERINTA"] or 0),
            "valoare_totala_contract":           total_valoare,
            "cofinantare_totala_contract":       total_cofin,
        })

    return rezultat
