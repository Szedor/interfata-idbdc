# =========================================================
# IDBDC/domenii/proiecte_fdi/tehnic.py
# VERSIUNE: 1.0
# STATUS: NOU — Aspecte tehnice Proiecte FDI
# DATA: 2026.05.31
# =========================================================
# CONȚINUT:
#   render() pentru tab-ul Aspecte tehnice.
#   Prezent în TOATE tipurile de proiecte (FDI, PNCDI,
#   PNRR, Internaționale etc.) — acest fișier este
#   modelul/șablonul pentru toate celelalte domenii.
#
#   4 câmpuri text de mari dimensiuni:
#     🎯 OBIECTIV GENERAL     → obiectiv_general
#     📌 OBIECTIVE SPECIFICE  → obiective_specifice
#     ⚙️ ACTIVITATI           → activitati_proiect
#     📈 REZULTATE            → rezultate_proiect
#
#   Salvare în tabela com_aspecte_tehnice.
# =========================================================

import streamlit as st
import pandas as pd


def render(supabase, cod_introdus, is_new, date_existente):
    """
    Randează și colectează Aspecte tehnice pentru Proiecte FDI.

    Parametri:
        supabase       : clientul Supabase (nefolosit direct, pentru consistență)
        cod_introdus   : codul identificator
        is_new         : True dacă este înregistrare nouă
        date_existente : list[dict] din com_aspecte_tehnice sau dict

    Returnează:
        list[dict] cu valorile pentru salvare în com_aspecte_tehnice
    """
    # ── Citire date existente ──────────────────────────────────────────
    if is_new or not date_existente:
        row_ex = {
            "obiectiv_general":    "",
            "obiective_specifice": "",
            "activitati_proiect":  "",
            "rezultate_proiect":   "",
        }
    else:
        row_ex = date_existente[0] if isinstance(date_existente, list) else date_existente

    def _str(val):
        return str(val).strip() if val else ""

    # ── Construire DataFrame ───────────────────────────────────────────
    df = pd.DataFrame([{
        "🎯 OBIECTIV GENERAL":    _str(row_ex.get("obiectiv_general")),
        "📌 OBIECTIVE SPECIFICE": _str(row_ex.get("obiective_specifice")),
        "⚙️ ACTIVITATI":          _str(row_ex.get("activitati_proiect")),
        "📈 REZULTATE":           _str(row_ex.get("rezultate_proiect")),
    }])

    col_cfg = {
        "🎯 OBIECTIV GENERAL": st.column_config.TextColumn(
            "🎯 OBIECTIV GENERAL", width="large"
        ),
        "📌 OBIECTIVE SPECIFICE": st.column_config.TextColumn(
            "📌 OBIECTIVE SPECIFICE", width="large"
        ),
        "⚙️ ACTIVITATI": st.column_config.TextColumn(
            "⚙️ ACTIVITATI", width="large"
        ),
        "📈 REZULTATE": st.column_config.TextColumn(
            "📈 REZULTATE", width="large"
        ),
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

    # ── Returnare dict pentru salvare ─────────────────────────────────
    return [{
        "cod_identificare":    cod_introdus,
        "obiectiv_general":    _str(row["🎯 OBIECTIV GENERAL"])    or None,
        "obiective_specifice": _str(row["📌 OBIECTIVE SPECIFICE"]) or None,
        "activitati_proiect":  _str(row["⚙️ ACTIVITATI"])          or None,
        "rezultate_proiect":   _str(row["📈 REZULTATE"])           or None,
    }]
