# =========================================================
# IDBDC/domenii/proiecte_fdi/financiar.py
# VERSIUNE: 1.0
# STATUS: NOU — Date financiare Proiecte FDI
# DATA: 2026.05.31
# =========================================================
# CONȚINUT:
#   render() pentru Date financiare FDI.
#   4 coloane editabile + 1 coloană calculată automat:
#     💱 VALUTA               → valuta
#     💰 SUMA SOLICITATĂ      → suma_solicitata_fdi
#     ✅ SUMA APROBATĂ MEC    → suma_aprobata_mec
#     🏛️ COFINANȚARE UPT      → cofinantare_upt_fdi
#     📊 TOTAL VALOARE PROIECT → suma_aprobata_mec + cofinantare_upt_fdi  (readonly)
#
#   TOTAL este calculat automat și afișat ca:
#     (a) coloana readonly în editor
#     (b) nota de subsol cu valoarea exactă după editare
#
#   Principiu emoji: aceeași convenție ca definitie.py
# =========================================================

import streamlit as st
import pandas as pd


def render(supabase, cod_introdus, is_new, date_existente):
    """
    Randează și colectează Date financiare pentru Proiecte FDI.

    Returnează:
        list[dict] cu valorile pentru salvare în com_date_financiare
    """
    VALUTE = ["LEI", "EUR", "USD"]

    # ── Citire date existente ──────────────────────────────────────────
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

    def _sf(val):
        """Safe float: None/'' → 0.0, orice altceva → float."""
        if val is None or val == "":
            return 0.0
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    valuta_ex  = row_ex.get("valuta") or "LEI"
    if valuta_ex not in VALUTE:
        valuta_ex = "LEI"

    suma_sol  = _sf(row_ex.get("suma_solicitata_fdi"))
    suma_apr  = _sf(row_ex.get("suma_aprobata_mec"))
    cofin     = _sf(row_ex.get("cofinantare_upt_fdi"))
    total     = _sf(row_ex.get("total_buget_proiect_fdi"))
    if total == 0.0:
        total = suma_apr + cofin

    # ── Construire DataFrame ───────────────────────────────────────────
    df = pd.DataFrame([{
        "💱 VALUTA":                valuta_ex,
        "💰 SUMA SOLICITATĂ":       suma_sol,
        "✅ SUMA APROBATĂ MEC":     suma_apr,
        "🏛️ COFINANȚARE UPT":       cofin,
        "📊 TOTAL VALOARE PROIECT": total,
    }])

    col_cfg = {
        "💱 VALUTA": st.column_config.SelectboxColumn(
            "💱 VALUTA", options=VALUTE, required=True
        ),
        "💰 SUMA SOLICITATĂ": st.column_config.NumberColumn(
            "💰 SUMA SOLICITATĂ", format="%,.2f", min_value=0.0
        ),
        "✅ SUMA APROBATĂ MEC": st.column_config.NumberColumn(
            "✅ SUMA APROBATĂ MEC", format="%,.2f", min_value=0.0
        ),
        "🏛️ COFINANȚARE UPT": st.column_config.NumberColumn(
            "🏛️ COFINANȚARE UPT", format="%,.2f", min_value=0.0
        ),
        # Readonly — calculat automat
        "📊 TOTAL VALOARE PROIECT": st.column_config.NumberColumn(
            "📊 TOTAL VALOARE PROIECT", format="%,.2f", disabled=True
        ),
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

    # ── Calcul automat TOTAL după editare ─────────────────────────────
    suma_apr_e = _sf(row["✅ SUMA APROBATĂ MEC"])
    cofin_e    = _sf(row["🏛️ COFINANȚARE UPT"])
    total_e    = suma_apr_e + cofin_e
    valuta_e   = row["💱 VALUTA"] or "LEI"

    st.caption(
        f"📊 Total valoare proiect calculat automat: "
        f"{total_e:,.2f} {valuta_e}  "
        f"(Sumă aprobată {suma_apr_e:,.2f} + Cofinanțare {cofin_e:,.2f})"
    )

    # ── Returnare dict pentru salvare ─────────────────────────────────
    return [{
        "cod_identificare":        cod_introdus,
        "valuta":                  valuta_e,
        "suma_solicitata_fdi":     _sf(row["💰 SUMA SOLICITATĂ"]),
        "suma_aprobata_mec":       suma_apr_e,
        "cofinantare_upt_fdi":     cofin_e,
        "total_buget_proiect_fdi": total_e,
    }]
