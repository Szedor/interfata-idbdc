# =========================================================
# utils/sectiuni/date_financiare_fdi.py
# VERSIUNE: 1.0
# STATUS: STABIL - Secțiunea DATE FINANCIARE pentru FDI
# DATA: 2026.05.04
# =========================================================
# CONȚINUT:
#   Secțiunea DATE FINANCIARE specifică proiectelor FDI.
#   Randează tabelul editabil cu 4 coloane financiare și
#   returnează datele pentru salvare în PostgreSQL
#   (tabela com_date_financiare).
#
#   Diferențe față de date_financiare.py (contracte):
#   - 4 coloane în loc de 1:
#       SUMA SOLICITATA   → suma_solicitata_fdi
#       SUMA APROBATA     → suma_aprobata_mec
#       COFINANTARE       → cofinantare_upt_fdi
#       TOTAL VALOARE PROIECT → total_buget_proiect_fdi
#         (calculat automat: SUMA APROBATA + COFINANTARE)
#   - TOTAL este readonly, recalculat la fiecare render
#   - Formatare: 2 zecimale, punct mii, virgulă zecimale
#     (realizată prin format="%,.2f" în NumberColumn)
#
# MODIFICĂRI VERSIUNEA 1.0:
#   - Creare inițială, fișier independent de date_financiare.py.
# =========================================================

import streamlit as st
import pandas as pd


def render_date_financiare_fdi(supabase, cod_introdus, is_new, date_existente):
    """
    Randare și colectare date financiare pentru proiecte FDI.

    Parametri:
        supabase       : clientul Supabase (nefolosit direct, pentru consistență)
        cod_introdus   : codul identificator al proiectului
        is_new         : True dacă este înregistrare nouă
        date_existente : list[dict] cu datele din com_date_financiare,
                         sau dict dacă vine din date_existente directe

    Returnează:
        list[dict] cu valorile pentru salvare în com_date_financiare
    """
    VALUTE = ["LEI", "EUR", "USD"]

    # ── Citire date existente ──────────────────────────────────
    if is_new or not date_existente:
        row_ex = {
            "valuta": "LEI",
            "suma_solicitata_fdi": 0.0,
            "suma_aprobata_mec": 0.0,
            "cofinantare_upt_fdi": 0.0,
            "total_buget_proiect_fdi": 0.0,
        }
    else:
        # date_existente poate fi list (din safe_select_eq) sau dict
        row_ex = date_existente[0] if isinstance(date_existente, list) else date_existente

    def _safe_float(val):
        try:
            return float(val or 0)
        except (TypeError, ValueError):
            return 0.0

    valuta_ex       = row_ex.get("valuta", "LEI")
    if valuta_ex not in VALUTE:
        valuta_ex = "LEI"

    suma_sol   = _safe_float(row_ex.get("suma_solicitata_fdi"))
    suma_apr   = _safe_float(row_ex.get("suma_aprobata_mec"))
    cofin      = _safe_float(row_ex.get("cofinantare_upt_fdi"))
    # TOTAL = SUMA APROBATA + COFINANTARE (conform cerință)
    total      = suma_apr + cofin

    # ── Construire DataFrame ───────────────────────────────────
    df = pd.DataFrame([{
        "VALUTA":                 valuta_ex,
        "SUMA SOLICITATA":        suma_sol,
        "SUMA APROBATA":          suma_apr,
        "COFINANTARE":            cofin,
        "TOTAL VALOARE PROIECT":  total,
    }])

    # ── Configurare coloane editor ─────────────────────────────
    col_cfg = {
        "VALUTA": st.column_config.SelectboxColumn(
            "💱 VALUTA", options=VALUTE, required=True
        ),
        "SUMA SOLICITATA": st.column_config.NumberColumn(
            "💰 SUMA SOLICITATA", format="%,.2f", min_value=0.0
        ),
        "SUMA APROBATA": st.column_config.NumberColumn(
            "✅ SUMA APROBATA", format="%,.2f", min_value=0.0
        ),
        "COFINANTARE": st.column_config.NumberColumn(
            "🏛️ COFINANTARE", format="%,.2f", min_value=0.0
        ),
        # TOTAL este readonly — calculat automat
        "TOTAL VALOARE PROIECT": st.column_config.NumberColumn(
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

    # ── Recalcul TOTAL după editare ────────────────────────────
    suma_apr_e = float(row["SUMA APROBATA"]  or 0)
    cofin_e    = float(row["COFINANTARE"]    or 0)
    total_e    = suma_apr_e + cofin_e

    st.caption(
        f"📊 Total valoare proiect calculat automat: "
        f"{total_e:,.2f} {row['VALUTA']}  "
        f"(Suma aprobată {suma_apr_e:,.2f} + Cofinanțare {cofin_e:,.2f})"
    )

    # ── Returnare dict pentru salvare PostgreSQL ───────────────
    return [{
        "cod_identificare":       cod_introdus,
        "valuta":                 row["VALUTA"],
        "suma_solicitata_fdi":    float(row["SUMA SOLICITATA"] or 0),
        "suma_aprobata_mec":      suma_apr_e,
        "cofinantare_upt_fdi":    cofin_e,
        "total_buget_proiect_fdi": total_e,
    }]
