# grant_navigator/engine/ai_documents.py
"""
Secțiunea 4 — Generare Documente AI
Claude generează drafturi profesionale de documente pentru proiecte de cercetare:
idei de proiecte, scrisori de intenție, rezumate executive, fișe de proiect.
"""

import streamlit as st
import io
from supabase import Client

from grant_navigator.engine.ai_core import (
    _call_claude_stream,
    _call_claude,
    safe_fetch,
    df_to_context,
    MODEL_SMART,
    MODEL_FAST,
)


SYSTEM_PROMPT = """Ești un expert în scrierea de propuneri de proiecte de cercetare pentru
universități tehnice europene, cu experiență vastă în Horizon Europe, UEFISCDI, PNRR și
programe de cooperare internațională.

Generezi documente profesionale, clare și convingătoare, adaptate specificului
Universității Politehnica Timișoara (UPT) și contextului academic românesc.

Răspunzi EXCLUSIV în română (dacă nu se cere altfel explicit).
Documentele tale sunt concrete, bazate pe date reale când sunt disponibile,
și respectă structura standard a propunerilor de proiecte europene."""


DOC_TYPES = {
    "💡 Idee de proiect (draft complet)": "idea",
    "📋 Fișă sintetică de proiect":       "fisa",
    "✉️ Scrisoare de intenție":           "letter",
    "📝 Rezumat executiv":                "summary",
    "🤝 Propunere de parteneriat":        "partnership",
    "📊 Plan de diseminare":              "dissemination",
}


def _get_existing_projects_context(supabase: Client, tip_finantare: str) -> str:
    """Aduce proiecte similare din IDBDC ca referință."""
    table_map = {
        "Horizon Europe / European":  "base_proiecte_internationale",
        "PNCDI / Național":           "base_proiecte_pncdi",
        "PNRR":                       "base_proiecte_pnrr",
        "FDI":                        "base_proiecte_fdi",
        "INTERREG":                   "base_proiecte_interreg",
        "Contract cu industria":      "base_contracte_terti",
        "Altul / General":            "base_proiecte_internationale",
    }
    table = table_map.get(tip_finantare, "base_proiecte_internationale")
    rows  = safe_fetch(supabase, table, limit=50)
    if not rows:
        return ""
    return f"Proiecte similare existente în IDBDC ({tip_finantare}):\n" + df_to_context(rows, max_rows=10)


def render(supabase: Client):
    st.subheader("📝 Generare Documente AI")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.85);font-size:0.95rem;margin-bottom:1rem;'>"
        "Generează drafturi profesionale pentru propuneri de proiecte, scrisori de intenție "
        "și alte documente de cercetare. AI-ul folosește contextul real din IDBDC."
        "</div>",
        unsafe_allow_html=True,
    )

    # Tip document
    doc_type_label = st.selectbox("Tip document", list(DOC_TYPES.keys()))
    doc_type       = DOC_TYPES[doc_type_label]

    st.divider()

    # Formular comun
    c1, c2 = st.columns(2)
    with c1:
        titlu = st.text_input(
            "Titlu propus / Subiect",
            placeholder="Ex: Platformă AI pentru diagnosticare medicală non-invazivă",
        )
        tip_finantare = st.selectbox(
            "Program de finanțare vizat",
            ["Horizon Europe / European", "PNCDI / Național", "PNRR",
             "FDI", "INTERREG", "Contract cu industria", "Altul / General"],
        )
    with c2:
        domeniu = st.text_input(
            "Domeniu / Cuvinte cheie",
            placeholder="Ex: inteligență artificială, sănătate, digitalizare",
        )
        limba = st.selectbox("Limba documentului", ["Română", "Engleză"])

    context_user = st.text_area(
        "Descriere / Context (cu cât mai detaliat, cu atât mai bun documentul)",
        placeholder="Descrie pe scurt ideea, problema pe care o rezolvă, "
                    "echipa disponibilă, infrastructura existentă la UPT...",
        height=120,
    )

    # Opțiuni specifice per tip document
    extra_options = {}

    if doc_type == "idea":
        extra_options["nr_obiective"] = st.slider("Număr obiective specifice", 2, 6, 3)
        extra_options["durata"]       = st.selectbox("Durata proiectului", ["12 luni", "24 luni", "36 luni", "48 luni"])
        extra_options["buget"]        = st.text_input("Buget estimat (opțional)", placeholder="Ex: 500.000 EUR")

    elif doc_type == "letter":
        extra_options["destinatar"] = st.text_input("Destinatar / Finanțator", placeholder="Ex: Comisia Europeană / UEFISCDI")
        extra_options["coordonator"] = st.text_input("Coordonator proiect (nume)", placeholder="Ex: Prof. Dr. Ion Popescu")

    elif doc_type == "partnership":
        extra_options["tip_partener"] = st.selectbox(
            "Tip partener căutat",
            ["Universitate europeană", "Companie privată (SME)", "Autoritate publică",
             "Institut de cercetare", "ONG / Asociație profesională"],
        )
        extra_options["rol_upt"] = st.selectbox("Rolul UPT", ["Coordonator", "Partener principal", "Partener"])

    st.info("AI-ul va genera documentul pe baza informațiilor completate + datele din IDBDC.", icon="🤖")

    if not st.button("✨ Generează documentul", key="doc_go"):
        return

    if not titlu.strip():
        st.warning("Completează cel puțin titlul / subiectul.")
        return

    # Context din IDBDC
    idbdc_context = _get_existing_projects_context(supabase, tip_finantare)

    # Construiesc prompt-ul specific tipului
    if doc_type == "idea":
        task = f"""Generează o idee de proiect completă și profesională cu structura:

1. **Titlu** (în {limba})
2. **Rezumat executiv** (max 150 cuvinte)
3. **Context și necesitate** (problema adresată, relevanța)
4. **Obiectiv general**
5. **Obiective specifice** ({extra_options.get('nr_obiective', 3)} obiective, SMART)
6. **Metodologie și activități principale** (WP-uri)
7. **Rezultate așteptate și indicatori**
8. **Consorțiu propus** (roluri)
9. **Buget estimat**: {extra_options.get('buget', 'de estimat') or 'de estimat'}
10. **Durata**: {extra_options.get('durata', '36 luni')}
11. **Impact și sustenabilitate**"""

    elif doc_type == "fisa":
        task = """Generează o fișă sintetică de proiect (1-2 pagini) cu:
1. Date de identificare (titlu, acronim propus, program, durată, buget)
2. Rezumat (max 200 cuvinte)
3. Obiective (3-4 puncte)
4. Activități principale
5. Rezultate cheie
6. Echipa / Consorțiu
7. Relevanță și impact"""

    elif doc_type == "letter":
        task = f"""Generează o scrisoare de intenție profesională adresată: {extra_options.get('destinatar', 'finanțatorului')}.
Semnată de: {extra_options.get('coordonator', 'coordonatorul proiectului')}, UPT.
Structură: introducere, prezentarea proiectului, experiența UPT, solicitare, încheiere formală."""

    elif doc_type == "summary":
        task = """Generează un rezumat executiv de maximum 1 pagină (400-500 cuvinte) care să convingă
un evaluator în 2 minute. Include: problema, soluția, impactul, echipa, bugetul."""

    elif doc_type == "partnership":
        task = f"""Generează o propunere de parteneriat pentru:
- Tip partener căutat: {extra_options.get('tip_partener', 'universitate europeană')}
- Rolul UPT: {extra_options.get('rol_upt', 'Coordonator')}
Include: prezentarea UPT, motivația parteneriatului, contribuții reciproce, beneficii, next steps."""

    elif doc_type == "dissemination":
        task = """Generează un plan de diseminare și valorificare a rezultatelor cu:
1. Grupuri țintă
2. Canale de diseminare (articole, conferințe, social media, events)
3. Calendar activități diseminare
4. Indicatori de diseminare
5. Plan de exploatare comercială / transfer tehnologic"""

    user_msg = f"""TITLU / SUBIECT: {titlu}
DOMENIU / CUVINTE CHEIE: {domeniu}
PROGRAM FINANȚARE: {tip_finantare}
LIMBA: {limba}
CONTEXT FURNIZAT: {context_user if context_user.strip() else '(nefurnizat)'}

{idbdc_context}

TASK: {task}

Generează documentul complet, profesional, gata de utilizat ca draft de lucru."""

    st.divider()
    st.markdown(f"### {doc_type_label} — generat de AI:")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    response_placeholder = st.empty()

    generated_text = _call_claude_stream(
        system_prompt=SYSTEM_PROMPT,
        user_message=user_msg,
        model=MODEL_SMART,
        max_tokens=2500,
        placeholder=response_placeholder,
    )

    # Export
    if generated_text and not generated_text.startswith("⚠️"):
        st.divider()
        c1, c2 = st.columns(2)

        with c1:
            st.download_button(
                "⬇️ Download Markdown (.md)",
                data=generated_text.encode("utf-8"),
                file_name=f"idbdc_document_{doc_type}.md",
                mime="text/markdown",
                key="doc_dl_md",
            )

        with c2:
            # Export ca text simplu pentru Word
            txt_content = generated_text.replace("**", "").replace("*", "").replace("#", "")
            st.download_button(
                "⬇️ Download Text (.txt)",
                data=txt_content.encode("utf-8"),
                file_name=f"idbdc_document_{doc_type}.txt",
                mime="text/plain",
                key="doc_dl_txt",
            )

    st.caption(
        "Documentul generat este un draft de lucru. Revizuiți și adaptați "
        "înainte de depunere oficială."
    )
