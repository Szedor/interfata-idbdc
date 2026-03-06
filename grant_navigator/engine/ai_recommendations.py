# grant_navigator/engine/ai_recommendations.py
"""
Secțiunea 3 — Recomandări Strategice AI
Claude analizează profilul de cercetare al UPT (din IDBDC) și generează
recomandări strategice reale pentru finanțări și direcții de dezvoltare.
"""

import streamlit as st
import pandas as pd
from supabase import Client

from grant_navigator.engine.ai_core import (
    _call_claude_stream,
    safe_fetch,
    df_to_context,
    MODEL_SMART,
)


SYSTEM_PROMPT = """Ești un expert în strategia de cercetare universitară și finanțări europene,
specializat în contextul universităților tehnice din România și Europa Centrală și de Est.

Ai acces la datele reale de cercetare ale Universității Politehnica Timișoara (UPT).
Analizezi datele și generezi recomandări strategice concrete, acționabile, bazate pe:
- portofoliul actual de proiecte și contracte
- tendințele în finanțarea europeană (Horizon Europe, PNRR, structurale)
- punctele forte și lacunele identificate

Răspunzi EXCLUSIV în română. Ești direct, specific și practic.
Nu dai sfaturi generice — fiecare recomandare trebuie să fie ancorată în datele reale."""


def _get_profile_context(supabase: Client) -> str:
    """Construiește profilul de cercetare din toate tabelele base_*."""
    context_parts = []

    tables = {
        "Proiecte internaționale": "base_proiecte_internationale",
        "Proiecte FDI":            "base_proiecte_fdi",
        "Proiecte PNCDI":          "base_proiecte_pncdi",
        "Proiecte PNRR":           "base_proiecte_pnrr",
        "Contracte TERTI":         "base_contracte_terti",
        "Contracte CEP":           "base_contracte_cep",
        "Proprietate intelectuală":"base_prop_intelect",
    }

    for label, table in tables.items():
        rows = safe_fetch(supabase, table, limit=100)
        if rows:
            context_parts.append(f"--- {label} ({len(rows)} înregistrări) ---")
            context_parts.append(df_to_context(rows, max_rows=20))

    return "\n\n".join(context_parts) if context_parts else "(baza de date este în curs de completare)"


def render(supabase: Client):
    st.subheader("🎯 Recomandări Strategice AI")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.85);font-size:0.95rem;margin-bottom:1rem;'>"
        "AI-ul analizează portofoliul real de cercetare al UPT și generează recomandări "
        "strategice personalizate pentru finanțări și direcții de dezvoltare."
        "</div>",
        unsafe_allow_html=True,
    )

    # Configurare analiză
    c1, c2 = st.columns(2)

    with c1:
        focus = st.selectbox(
            "Focalizare analiză",
            [
                "Strategia generală de finanțare",
                "Creșterea finanțărilor europene (Horizon Europe)",
                "Consolidarea parteneriatelor cu industria",
                "Dezvoltarea proiectelor PNCDI / naționale",
                "Proprietate intelectuală și transfer tehnologic",
                "Atragerea tinerilor cercetători (MSCA, FDI)",
            ],
        )

    with c2:
        orizont = st.selectbox(
            "Orizont de timp",
            ["1-2 ani (termen scurt)", "3-5 ani (termen mediu)", "5+ ani (viziune strategică)"],
        )

    context_extra = st.text_area(
        "Context suplimentar (opțional)",
        placeholder="Ex: dorim să dezvoltăm un centru de excelență în AI, avem un laborator nou de materiale avansate...",
        height=80,
    )

    st.info(
        "AI-ul va analiza datele reale din IDBDC și va genera recomandări specifice UPT.",
        icon="🤖",
    )

    if not st.button("🎯 Generează recomandări strategice", key="strat_go"):
        return

    with st.spinner("Analizez portofoliul de cercetare UPT..."):
        profile_context = _get_profile_context(supabase)

    user_msg = f"""Analizează portofoliul de cercetare al UPT și generează recomandări strategice.

FOCALIZARE: {focus}
ORIZONT DE TIMP: {orizont}
{f"CONTEXT SUPLIMENTAR: {context_extra}" if context_extra.strip() else ""}

DATE REALE DIN BAZA IDBDC:
{profile_context}

Generează:
1. **Analiza situației actuale** (3-4 rânduri bazate pe datele reale)
2. **Top 5 recomandări strategice** (concrete, cu justificare din date)
3. **Acțiuni imediate** (ce se poate face în următoarele 3 luni)
4. **Riscuri de evitat** (1-2 puncte)

Fii specific și bazat pe datele reale, nu generic."""

    st.divider()
    st.markdown("### 📊 Analiza și recomandările AI:")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    response_placeholder = st.empty()

    _call_claude_stream(
        system_prompt=SYSTEM_PROMPT,
        user_message=user_msg,
        model=MODEL_SMART,
        max_tokens=2000,
        placeholder=response_placeholder,
    )

    st.divider()
    st.caption("Recomandările sunt generate de AI pe baza datelor reale din IDBDC. "
               "Validați cu echipa de management înainte de implementare.")
