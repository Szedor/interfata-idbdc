# =========================================================
# IDBDC/domenii/_baza/sectiune_financiar_pnrr.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.05.23
# =========================================================
# LOGICA SPECIALA (identica cu PNCDI):
#   - Financiarul PNRR are mai multe randuri per proiect (cate unul per an).
#   - VALOARE TOTALA si COFINANTARE TOTALA sunt aceleasi pe toate randurile.
#   - Sistemul verifica automat daca suma valorilor anuale = VALOARE TOTALA
#     si daca suma cofinantarilor anuale = COFINANTARE TOTALA.
#   - Operatorul este avertizat vizual (warning) daca nu exista egalitate.
# =========================================================

import streamlit as st
import pandas as pd


def render(supabase, cod_introdus, is_new, date_existente):
    VALUTE = ["LEI", "EUR", "USD"]

    # ── Pregatire date existente ──────────────────────────────────────────────
    if is_new or not date_existente:
        rows_ex = []
    else:
        rows_ex = date_existente if isinstance(date_existente, list) else [date_existente]

    def _f(v):
        try: return float(v) if v else 0.0
        except: return 0.0

    valuta_ex    = rows_ex[0].get("valuta", "LEI") if rows_ex else "LEI"
    if valuta_ex not in VALUTE: valuta_ex = "LEI"
    val_totala   = _f(rows_ex[0].get("valoare_totala_contract"))      if rows_ex else 0.0
    cofin_totala = _f(rows_ex[0].get("cofinantare_totala_contract"))  if rows_ex else 0.0

    # ── Tabel randuri anuale ──────────────────────────────────────────────────
    st.markdown("#### 📅 Valori pe ani de referință")

    if rows_ex:
        df_ani = pd.DataFrame([{
            "ANUL DE REFERINTA":        r.get("an_referinta", ""),
            "VALOARE AN REFERINTA":     _f(r.get("valoare_contract_an_referinta")),
            "COFINANTARE AN REFERINTA": _f(r.get("cofinantare_contract_an_referinta")),
        } for r in rows_ex])
    else:
        df_ani = pd.DataFrame([{
            "ANUL DE REFERINTA":        "",
            "VALOARE AN REFERINTA":     0.0,
            "COFINANTARE AN REFERINTA": 0.0,
        }])

    col_cfg_ani = {
        "ANUL DE REFERINTA":        st.column_config.TextColumn("📆 ANUL DE REFERINTA", width="small"),
        "VALOARE AN REFERINTA":     st.column_config.NumberColumn("💰 VALOARE AN REFERINTA",     format="%,.2f", min_value=0.0),
        "COFINANTARE AN REFERINTA": st.column_config.NumberColumn("🏛️ COFINANTARE AN REFERINTA", format="%,.2f", min_value=0.0),
    }

    df_ani_edit = st.data_editor(
        df_ani,
        column_config=col_cfg_ani,
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic",
        key=f"fin_pnrr_ani_editor_{cod_introdus}",
    )

    # ── Totaluri contract ─────────────────────────────────────────────────────
    st.markdown("#### 💼 Totaluri contract")

    df_total = pd.DataFrame([{
        "VALUTA":             valuta_ex,
        "VALOARE TOTALA":     val_totala,
        "COFINANTARE TOTALA": cofin_totala,
    }])

    col_cfg_total = {
        "VALUTA":             st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
        "VALOARE TOTALA":     st.column_config.NumberColumn("💰 VALOARE TOTALA",     format="%,.2f", min_value=0.0),
        "COFINANTARE TOTALA": st.column_config.NumberColumn("🏛️ COFINANTARE TOTALA", format="%,.2f", min_value=0.0),
    }

    df_total_edit = st.data_editor(
        df_total,
        column_config=col_cfg_total,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"fin_pnrr_total_editor_{cod_introdus}",
    )

    # ── Calcul sume anuale ────────────────────────────────────────────────────
    def _frow(r, col):
        try: return float(r[col]) if r[col] else 0.0
        except: return 0.0

    suma_val_anuale   = sum(_frow(r, "VALOARE AN REFERINTA")     for _, r in df_ani_edit.iterrows())
    suma_cofin_anuale = sum(_frow(r, "COFINANTARE AN REFERINTA") for _, r in df_ani_edit.iterrows())

    row_total   = df_total_edit.iloc[0]
    valuta_sel  = row_total["VALUTA"]
    val_tot_sel = _f(row_total["VALOARE TOTALA"])
    cof_tot_sel = _f(row_total["COFINANTARE TOTALA"])

    # ── Verificare si avertizare ──────────────────────────────────────────────
    st.markdown("#### 🔍 Verificare concordanță")

    TOL = 0.01  # toleranta rotunjire (1 ban)

    ok_val   = abs(suma_val_anuale   - val_tot_sel) <= TOL
    ok_cofin = abs(suma_cofin_anuale - cof_tot_sel) <= TOL

    col1, col2 = st.columns(2)

    with col1:
        if ok_val:
            st.success(
                f"✅ **VALOARE** — concordanță OK\n\n"
                f"Suma anuală: **{suma_val_anuale:,.2f}** {valuta_sel}\n\n"
                f"Valoare totală: **{val_tot_sel:,.2f}** {valuta_sel}"
            )
        else:
            diferenta_val = suma_val_anuale - val_tot_sel
            st.warning(
                f"⚠️ **VALOARE** — discordanță!\n\n"
                f"Suma anuală: **{suma_val_anuale:,.2f}** {valuta_sel}\n\n"
                f"Valoare totală: **{val_tot_sel:,.2f}** {valuta_sel}\n\n"
                f"Diferență: **{diferenta_val:+,.2f}** {valuta_sel}"
            )

    with col2:
        if ok_cofin:
            st.success(
                f"✅ **COFINANTARE** — concordanță OK\n\n"
                f"Suma anuală: **{suma_cofin_anuale:,.2f}** {valuta_sel}\n\n"
                f"Cofinantare totală: **{cof_tot_sel:,.2f}** {valuta_sel}"
            )
        else:
            diferenta_cofin = suma_cofin_anuale - cof_tot_sel
            st.warning(
                f"⚠️ **COFINANTARE** — discordanță!\n\n"
                f"Suma anuală: **{suma_cofin_anuale:,.2f}** {valuta_sel}\n\n"
                f"Cofinantare totală: **{cof_tot_sel:,.2f}** {valuta_sel}\n\n"
                f"Diferență: **{diferenta_cofin:+,.2f}** {valuta_sel}"
            )

    # ── Pregatire date de salvat ──────────────────────────────────────────────
    rezultat = []
    for _, r in df_ani_edit.iterrows():
        an = str(r["ANUL DE REFERINTA"]).strip() if r["ANUL DE REFERINTA"] else None
        if not an:
            continue
        rezultat.append({
            "cod_identificare":                  cod_introdus,
            "valuta":                            valuta_sel,
            "an_referinta":                      an,
            "valoare_contract_an_referinta":     _frow(r, "VALOARE AN REFERINTA"),
            "cofinantare_contract_an_referinta": _frow(r, "COFINANTARE AN REFERINTA"),
            "valoare_totala_contract":           val_tot_sel,
            "cofinantare_totala_contract":       cof_tot_sel,
        })

    return rezultat
