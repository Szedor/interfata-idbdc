# =========================================================
# IDBDC/domenii/_baza/sectiune_financiar_pncdi.py
# VERSIUNE: 2.1
# STATUS: CORECTAT - eliminat placeholder neacceptat
# DATA: 2026.05.28
# =========================================================
# MODIFICĂRI VERSIUNEA 2.1:
#   - Eliminat parametrul placeholder de la TextColumn
# MODIFICĂRI VERSIUNEA 2.0:
#   - Păstrare toți anii la încărcare și salvare
# =========================================================

import streamlit as st
import pandas as pd


def render(supabase, cod_introdus, is_new, date_existente):
    VALUTE = ["LEI", "EUR", "USD"]

    # Pregatire date existente
    if is_new or not date_existente:
        rows_ex = []
    else:
        if isinstance(date_existente, dict):
            rows_ex = [date_existente]
        elif isinstance(date_existente, list):
            rows_ex = date_existente
        else:
            rows_ex = []

    def _f(v):
        try: 
            return float(v) if v not in (None, "") else 0.0
        except (ValueError, TypeError): 
            return 0.0

    # Valuta si totaluri din primul rand
    valuta_ex = rows_ex[0].get("valuta", "LEI") if rows_ex else "LEI"
    if valuta_ex not in VALUTE:
        valuta_ex = "LEI"
    val_totala = _f(rows_ex[0].get("valoare_totala_contract")) if rows_ex else 0.0
    cofin_totala = _f(rows_ex[0].get("cofinantare_totala_contract")) if rows_ex else 0.0

    st.markdown("#### 📅 Valori pe ani de referință")

    def _an_str(v):
        if v is None:
            return ""
        try:
            if isinstance(v, (int, float)):
                return str(int(v))
            s = str(v).strip()
            if s in ("", "None", "nan", "NaN"):
                return ""
            return str(int(float(s)))
        except (ValueError, TypeError):
            return str(v)

    # Construim DataFrame cu TOȚI anii existenți
    if rows_ex:
        date_ani = []
        ani_vazuti = set()
        for r in rows_ex:
            an = _an_str(r.get("an_referinta"))
            if an and an not in ani_vazuti:
                ani_vazuti.add(an)
                date_ani.append({
                    "ANUL DE REFERINTA": an,
                    "VALOARE AN REFERINTA": _f(r.get("valoare_contract_an_referinta")),
                    "COFINANTARE AN REFERINTA": _f(r.get("cofinantare_contract_an_referinta")),
                })
        if date_ani:
            df_ani = pd.DataFrame(date_ani)
        else:
            df_ani = pd.DataFrame([{"ANUL DE REFERINTA": "", "VALOARE AN REFERINTA": 0.0, "COFINANTARE AN REFERINTA": 0.0}])
    else:
        df_ani = pd.DataFrame([{"ANUL DE REFERINTA": "", "VALOARE AN REFERINTA": 0.0, "COFINANTARE AN REFERINTA": 0.0}])

    df_ani["ANUL DE REFERINTA"] = df_ani["ANUL DE REFERINTA"].astype(str).replace("nan", "").replace("None", "")

    col_cfg_ani = {
        "ANUL DE REFERINTA": st.column_config.TextColumn("📆 ANUL DE REFERINTA", width="small"),
        "VALOARE AN REFERINTA": st.column_config.NumberColumn("💰 VALOARE AN REFERINTA", format="%.2f", min_value=0.0, step=1000.0),
        "COFINANTARE AN REFERINTA": st.column_config.NumberColumn("🏛️ COFINANTARE AN REFERINTA", format="%.2f", min_value=0.0, step=1000.0),
    }

    df_ani_edit = st.data_editor(
        df_ani,
        column_config=col_cfg_ani,
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic",
        key=f"fin_pncdi_ani_editor_{cod_introdus}",
    )

    st.markdown("#### 💼 Totaluri contract")

    df_total = pd.DataFrame([{
        "VALUTA": valuta_ex,
        "VALOARE TOTALA": val_totala,
        "COFINANTARE TOTALA": cofin_totala,
    }])

    col_cfg_total = {
        "VALUTA": st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
        "VALOARE TOTALA": st.column_config.NumberColumn("💰 VALOARE TOTALA", format="%.2f", min_value=0.0, step=10000.0),
        "COFINANTARE TOTALA": st.column_config.NumberColumn("🏛️ COFINANTARE TOTALA", format="%.2f", min_value=0.0, step=10000.0),
    }

    df_total_edit = st.data_editor(
        df_total,
        column_config=col_cfg_total,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"fin_pncdi_total_editor_{cod_introdus}",
    )

    def _frow(r, col):
        try:
            val = r[col]
            return float(val) if val not in (None, "") else 0.0
        except (ValueError, TypeError):
            return 0.0

    suma_val_anuale = sum(_frow(r, "VALOARE AN REFERINTA") for _, r in df_ani_edit.iterrows())
    suma_cofin_anuale = sum(_frow(r, "COFINANTARE AN REFERINTA") for _, r in df_ani_edit.iterrows())

    row_total = df_total_edit.iloc[0]
    valuta_sel = row_total["VALUTA"]
    val_tot_sel = _frow(row_total, "VALOARE TOTALA")
    cof_tot_sel = _frow(row_total, "COFINANTARE TOTALA")

    st.markdown("#### 🔍 Verificare concordanță")

    TOL = 0.01
    ok_val = abs(suma_val_anuale - val_tot_sel) <= TOL
    ok_cofin = abs(suma_cofin_anuale - cof_tot_sel) <= TOL

    col1, col2 = st.columns(2)

    with col1:
        if ok_val:
            st.success(f"✅ **VALOARE** — concordanță OK\n\nSuma anuală: **{suma_val_anuale:,.2f}** {valuta_sel}\n\nValoare totală: **{val_tot_sel:,.2f}** {valuta_sel}")
        else:
            diferenta_val = suma_val_anuale - val_tot_sel
            st.warning(f"⚠️ **VALOARE** — discordanță!\n\nSuma anuală: **{suma_val_anuale:,.2f}** {valuta_sel}\n\nValoare totală: **{val_tot_sel:,.2f}** {valuta_sel}\n\nDiferență: **{diferenta_val:+,.2f}** {valuta_sel}")

    with col2:
        if ok_cofin:
            st.success(f"✅ **COFINANTARE** — concordanță OK\n\nSuma anuală: **{suma_cofin_anuale:,.2f}** {valuta_sel}\n\nCofinantare totală: **{cof_tot_sel:,.2f}** {valuta_sel}")
        else:
            diferenta_cofin = suma_cofin_anuale - cof_tot_sel
            st.warning(f"⚠️ **COFINANTARE** — discordanță!\n\nSuma anuală: **{suma_cofin_anuale:,.2f}** {valuta_sel}\n\nCofinantare totală: **{cof_tot_sel:,.2f}** {valuta_sel}\n\nDiferență: **{diferenta_cofin:+,.2f}** {valuta_sel}")

    # Pregatire date de salvat - TOȚI ANII
    rezultat = []
    ani_vazuti = set()

    for _, r in df_ani_edit.iterrows():
        an_raw = r["ANUL DE REFERINTA"]
        if an_raw is None or str(an_raw).strip() in ("", "None", "nan", "NaN"):
            continue

        try:
            an_int = int(float(str(an_raw).strip()))
            an = str(an_int)
        except (ValueError, TypeError):
            an = str(an_raw).strip()

        if not an:
            continue

        if an in ani_vazuti:
            continue
        ani_vazuti.add(an)

        rezultat.append({
            "cod_identificare": cod_introdus,
            "valuta": valuta_sel,
            "an_referinta": an,
            "valoare_contract_an_referinta": _frow(r, "VALOARE AN REFERINTA"),
            "cofinantare_contract_an_referinta": _frow(r, "COFINANTARE AN REFERINTA"),
            "valoare_totala_contract": val_tot_sel,
            "cofinantare_totala_contract": cof_tot_sel,
        })

    return rezultat
