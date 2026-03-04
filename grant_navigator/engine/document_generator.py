# grant_navigator/engine/document_generator.py

import streamlit as st
from supabase import Client


TEMPLATE_IDEA_PROIECT = """\
# Idee de proiect (draft)

## Titlu propus
{title}

## 1) Context / Necesitate
{context}

## 2) Obiective
1. {obj1}
2. {obj2}
3. {obj3}

## 3) Activitati principale (propuse)
- WP1: Analiza nevoi, design, planificare
- WP2: Implementare / dezvoltare / pilot
- WP3: Evaluare, raportare, diseminare

## 4) Rezultate asteptate
{results}

## 5) Consortiu propus
{consortium}

## 6) Impact estimat
{impact}

---
Generat in modulul: Oportunitati si Analiza Cercetare – DCDI
"""


def render(_supabase: Client):
    st.subheader("📝 Generare documente")

    st.caption("Generator simplu (determinist) – produce un draft de idee de proiect.")

    title = st.text_input("Titlu propus", value="Platforma pentru managementul si analiza activitatii de cercetare")
    context = st.text_area(
        "Context / Necesitate",
        value="Este necesara consolidarea datelor si raportarilor privind activitatea de cercetare si finantarile aferente.",
        height=120,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        obj1 = st.text_input("Obiectiv 1", value="Centralizarea datelor relevante")
    with col2:
        obj2 = st.text_input("Obiectiv 2", value="Indicatori si rapoarte pentru decizie")
    with col3:
        obj3 = st.text_input("Obiectiv 3", value="Pilotare si validare in UPT")

    results = st.text_area(
        "Rezultate asteptate",
        value="Dashboard-uri, rapoarte standardizate, proceduri interne, ghid de utilizare.",
        height=120,
    )

    consortium = st.text_area(
        "Consortiu propus",
        value="UPT + 1-2 universitati partenere + 1 SME tehnologic (optional) + autoritate publica (optional).",
        height=90,
    )

    impact = st.text_area(
        "Impact estimat",
        value="Decizii mai rapide, cresterea ratei de succes la finantare, transparenta si monitorizare imbunatatite.",
        height=90,
    )

    st.divider()

    if not st.button("Genereaza draft"):
        st.info("Apasa «Genereaza draft».")
        return

    doc = TEMPLATE_IDEA_PROIECT.format(
        title=title.strip(),
        context=context.strip(),
        obj1=obj1.strip(),
        obj2=obj2.strip(),
        obj3=obj3.strip(),
        results=results.strip(),
        consortium=consortium.strip(),
        impact=impact.strip(),
    )

    st.success("Draft generat.")

    st.download_button(
        "⬇️ Download (Markdown)",
        data=doc.encode("utf-8"),
        file_name="idee_proiect_draft.md",
        mime="text/markdown",
    )

    st.text_area("Previzualizare draft", value=doc, height=560)
