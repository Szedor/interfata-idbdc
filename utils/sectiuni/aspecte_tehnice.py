# =========================================================
# utils/sectiuni/aspecte_tehnice.py
# VERSIUNE: 1.0
# STATUS: STABIL - Secțiunea ASPECTE TEHNICE pentru proiecte
# DATA: 2026.05.04
# =========================================================
# CONȚINUT:
#   Secțiunea ASPECTE TEHNICE comună pentru toate tipurile
#   de proiecte. Randează tabelul editabil cu 4 câmpuri
#   text de mari dimensiuni și returnează datele pentru
#   salvare în PostgreSQL (tabela com_aspecte_tehnice).
#
#   Câmpuri (mapare coloană tehnică → etichetă vizuală):
#       obiectiv_general     → OBIECTIV GENERAL
#       obiective_specifice  → OBIECTIVE SPECIFICE
#       activitati_proiect   → ACTIVITATI
#       rezultate_proiect    → REZULTATE
#
#   Nu există reguli speciale pentru această secțiune
#   (conform documentului de cerințe).
#
# MODIFICĂRI VERSIUNEA 1.0:
#   - Înlocuire placeholder cu implementare completă.
#   - Toate cele 4 câmpuri sunt editabile cu TextArea.
#   - Returnează list[dict] consistent cu celelalte secțiuni.
# =========================================================

import streamlit as st
import pandas as pd


def render_aspecte_tehnice(supabase, cod_introdus, is_new, date_existente):
    """
    Randare și colectare aspecte tehnice pentru orice tip de proiect.

    Parametri:
        supabase       : clientul Supabase (nefolosit direct, pentru consistență)
        cod_introdus   : codul identificator al proiectului
        is_new         : True dacă este înregistrare nouă
        date_existente : list[dict] cu datele din com_aspecte_tehnice,
                         sau dict dacă vine din date_existente directe

    Returnează:
        list[dict] cu valorile pentru salvare în com_aspecte_tehnice
    """
    # ── Citire date existente ──────────────────────────────────
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

    # ── Construire DataFrame ───────────────────────────────────
    # Folosim data_editor cu TextColumn de tip large pentru
    # câmpuri cu conținut extins (obiective, activități, rezultate)
    df = pd.DataFrame([{
        "OBIECTIV GENERAL":    _str(row_ex.get("obiectiv_general")),
        "OBIECTIVE SPECIFICE": _str(row_ex.get("obiective_specifice")),
        "ACTIVITATI":          _str(row_ex.get("activitati_proiect")),
        "REZULTATE":           _str(row_ex.get("rezultate_proiect")),
    }])

    col_cfg = {
        "OBIECTIV GENERAL": st.column_config.TextColumn(
            "🎯 OBIECTIV GENERAL", width="large"
        ),
        "OBIECTIVE SPECIFICE": st.column_config.TextColumn(
            "📌 OBIECTIVE SPECIFICE", width="large"
        ),
        "ACTIVITATI": st.column_config.TextColumn(
            "⚙️ ACTIVITATI", width="large"
        ),
        "REZULTATE": st.column_config.TextColumn(
            "📈 REZULTATE", width="large"
        ),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"aspecte_tehnice_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    # ── Returnare dict pentru salvare PostgreSQL ───────────────
    return [{
        "cod_identificare":    cod_introdus,
        "obiectiv_general":    _str(row["OBIECTIV GENERAL"])    or None,
        "obiective_specifice": _str(row["OBIECTIVE SPECIFICE"]) or None,
        "activitati_proiect":  _str(row["ACTIVITATI"])          or None,
        "rezultate_proiect":   _str(row["REZULTATE"])           or None,
    }]
