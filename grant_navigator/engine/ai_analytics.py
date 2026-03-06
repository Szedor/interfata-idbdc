# grant_navigator/engine/ai_analytics.py
"""
Secțiunea 1 — Chat AI cu baza IDBDC
Utilizatorul pune întrebări în limbaj natural despre datele din IDBDC.
Claude primește datele relevante ca context și generează un răspuns real.
"""

import streamlit as st
import pandas as pd
from supabase import Client

from grant_navigator.engine.ai_core import (
    _call_claude_stream,
    _call_claude,
    safe_fetch,
    df_to_context,
    MODEL_FAST,
)


# =========================================================
# MAP TABELE
# =========================================================

TABLE_MAP = {
    "contracte CEP":            "base_contracte_cep",
    "contracte TERTI":          "base_contracte_terti",
    "proiecte FDI":             "base_proiecte_fdi",
    "proiecte PNCDI":           "base_proiecte_pncdi",
    "proiecte PNRR":            "base_proiecte_pnrr",
    "proiecte internaționale":  "base_proiecte_internationale",
    "proiecte INTERREG":        "base_proiecte_interreg",
    "proiecte NONEU":           "base_proiecte_noneu",
    "evenimente științifice":   "base_evenimente_stiintifice",
    "proprietate intelectuală": "base_prop_intelect",
}

SYSTEM_PROMPT = """Ești un asistent AI specializat în analiza bazei de date de cercetare IDBDC 
a Universității Politehnica Timișoara (UPT). 

Răspunzi EXCLUSIV în limba română, concis și precis.
Baza de date conține: contracte (CEP, TERTI), proiecte (FDI, PNCDI, PNRR, internaționale, 
INTERREG, NONEU), evenimente științifice și proprietate intelectuală.

Când ți se oferă date din baza de date ca context, analizează-le și răspunde pe baza lor.
Dacă datele nu conțin informația cerută, spune-o clar.
Nu inventa date. Nu adăuga informații care nu sunt în context.
Fii direct și util pentru un cercetător universitar."""


def _detect_tables(question: str) -> list[str]:
    """Detectează ce tabele sunt relevante pentru întrebare."""
    q = question.lower()
    tables = []

    keywords = {
        "base_contracte_cep":           ["cep", "educatie permanenta", "formare"],
        "base_contracte_terti":         ["terti", "contract", "companie", "firma", "industrie"],
        "base_proiecte_fdi":            ["fdi", "fond dezvoltare", "institutionala"],
        "base_proiecte_pncdi":          ["pncdi", "plan national", "uefiscdi"],
        "base_proiecte_pnrr":           ["pnrr", "redresare", "rezilienta"],
        "base_proiecte_internationale": ["international", "horizon", "european", "ue ", "h2020",
                                         "erasmus", "cost ", "marie curie"],
        "base_proiecte_interreg":       ["interreg", "cooperare teritoriala"],
        "base_proiecte_noneu":          ["noneu", "non-eu", "extra-european", "bilateral"],
        "base_evenimente_stiintifice":  ["eveniment", "conferinta", "workshop", "simpozion",
                                         "manifestare", "congres"],
        "base_prop_intelect":           ["brevet", "patent", "marca", "inventie",
                                         "proprietate intelectuala", "osim"],
    }

    for table, kws in keywords.items():
        if any(k in q for k in kws):
            tables.append(table)

    # Dacă nu s-a detectat nimic specific, returnăm principalele tabele
    if not tables:
        tables = [
            "base_proiecte_internationale",
            "base_proiecte_pncdi",
            "base_proiecte_fdi",
            "base_contracte_terti",
        ]

    return tables[:3]  # maxim 3 tabele per interogare


def _build_context(supabase: Client, tables: list[str], keyword: str = "") -> str:
    """Construiește contextul din datele reale."""
    context_parts = []

    for table in tables:
        rows = safe_fetch(supabase, table, limit=200)
        if not rows:
            continue

        # Filtrare după keyword dacă există
        if keyword:
            k = keyword.lower()
            filtered = []
            for r in rows:
                row_text = " ".join(str(v) for v in r.values() if v).lower()
                if k in row_text:
                    filtered.append(r)
            rows = filtered if filtered else rows[:30]

        label = table.replace("base_", "").replace("_", " ").upper()
        context_parts.append(f"=== {label} ({len(rows)} înregistrări) ===")
        context_parts.append(df_to_context(rows, max_rows=40))

    return "\n\n".join(context_parts) if context_parts else "(nicio dată relevantă găsită)"


# =========================================================
# RENDER
# =========================================================

def render(supabase: Client):
    st.subheader("🧠 Chat AI cu baza IDBDC")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.85);font-size:0.95rem;margin-bottom:1rem;'>"
        "Pune întrebări în limbaj natural despre proiectele, contractele și activitatea "
        "de cercetare din IDBDC. AI-ul analizează datele reale și îți răspunde instant."
        "</div>",
        unsafe_allow_html=True,
    )

    # Istoric conversație
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Afișare istoric
    for msg in st.session_state.chat_history:
        role  = msg["role"]
        icon  = "👤" if role == "user" else "🤖"
        color = "rgba(255,255,255,0.08)" if role == "user" else "rgba(255,255,255,0.14)"
        st.markdown(
            f"<div style='background:{color};border-radius:10px;padding:10px 14px;"
            f"margin-bottom:8px;'><b>{icon}</b> {msg['content']}</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    # Input
    col_q, col_btn = st.columns([4, 1])
    with col_q:
        question = st.text_input(
            "Întreabă ceva despre baza IDBDC:",
            placeholder="Ex: Câte proiecte internaționale active avem? / Care sunt contractele TERTI din 2023?",
            key="chat_input",
            label_visibility="collapsed",
        )
    with col_btn:
        send = st.button("▶ Trimite", key="chat_send", use_container_width=True)

    # Exemple rapide
    st.markdown(
        "<div style='color:rgba(255,255,255,0.60);font-size:0.82rem;margin-top:4px;'>"
        "Exemple: «Câte proiecte FDI avem?» · «Arată proiectele Horizon Europe» · "
        "«Care sunt brevetele înregistrate?» · «Câte contracte TERTI sunt active?»"
        "</div>",
        unsafe_allow_html=True,
    )

    if st.button("🗑️ Șterge conversația", key="chat_clear"):
        st.session_state.chat_history = []
        st.rerun()

    if not send or not (question or "").strip():
        return

    q = question.strip()

    # Adaugă întrebarea în istoric
    st.session_state.chat_history.append({"role": "user", "content": q})

    # Detectează tabele relevante
    tables  = _detect_tables(q)
    context = _build_context(supabase, tables, keyword="")

    user_msg = f"""Întrebare: {q}

Date din baza IDBDC (context):
{context}

Răspunde la întrebare pe baza datelor de mai sus. Fii concis și precis."""

    # Răspuns cu streaming
    st.markdown(
        "<div style='background:rgba(255,255,255,0.14);border-radius:10px;"
        "padding:10px 14px;margin-top:8px;'><b>🤖</b> ",
        unsafe_allow_html=True,
    )
    placeholder = st.empty()

    answer = _call_claude_stream(
        system_prompt=SYSTEM_PROMPT,
        user_message=user_msg,
        model=MODEL_FAST,
        max_tokens=1200,
        placeholder=placeholder,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Adaugă răspunsul în istoric
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    st.rerun()
