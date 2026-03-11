# grant_navigator/engine/ai_analytics.py
"""
Secțiunea 1 — Chat AI cu baza IDBDC
Utilizatorul pune întrebări în limbaj natural despre datele din IDBDC.
Claude primește datele relevante ca context și generează un răspuns real.

FIX vers.2:
- Istoricul conversației se trimite la Claude (multi-turn real)
- Bug HTML streaming rezolvat — nu mai folosim st.markdown pentru div-uri deschise
- Detectare tabele îmbunătățită cu fallback inteligent

FIX vers.3:
- Calcul automat durata din data_inceput + data_sfarsit
- Context temporal: proiecte active azi, care se termină în anul curent,
  care continuă în anul viitor, durata maximă
"""

import streamlit as st
import datetime as _dt
from supabase import Client

from grant_navigator.engine.ai_core import (
    _call_claude_stream,
    safe_fetch,
    df_to_context,
    MODEL_FAST,
)


# =========================================================
# CONFIG
# =========================================================

SYSTEM_PROMPT = """Ești un asistent AI specializat în analiza bazei de date de cercetare IDBDC
a Universității Politehnica Timișoara (UPT).

Răspunzi EXCLUSIV în limba română, concis și precis.
Baza de date conține: contracte (CEP, TERTI), proiecte (FDI, PNCDI, PNRR, internaționale,
INTERREG, NONEU), evenimente științifice și proprietate intelectuală.

Când ți se oferă date din baza de date ca context, analizează-le și răspunde pe baza lor.
Dacă datele nu conțin informația cerută, spune-o clar.
Nu inventa date. Nu adăuga informații care nu sunt în context.
Fii direct și util pentru un cercetător universitar.
Menții contextul conversației — dacă utilizatorul face referire la ceva spus anterior, ții cont.

Când primești statistici temporale pre-calculate (STATISTICI TEMPORALE), folosește-le direct
pentru a răspunde la întrebări despre proiecte active, durate, termene. Nu recalcula manual."""

TABLE_KEYWORDS = {
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

# Tabele implicite când nu se detectează niciun keyword specific
FALLBACK_TABLES = [
    "base_proiecte_internationale",
    "base_proiecte_pncdi",
    "base_proiecte_fdi",
    "base_contracte_terti",
]

# Tabele care au data_inceput + data_sfarsit
TABLES_WITH_DATES = [
    "base_contracte_cep",
    "base_contracte_terti",
    "base_contracte_speciale",
    "base_proiecte_fdi",
    "base_proiecte_pncdi",
    "base_proiecte_pnrr",
    "base_proiecte_internationale",
    "base_proiecte_interreg",
    "base_proiecte_noneu",
]

# Cuvinte cheie care indică întrebări despre perioade/durate
DATE_KEYWORDS = [
    "activ", "active", "în derulare", "derulare", "implementare",
    "continuă", "continua", "anul curent", "anul viitor", "anul acesta",
    "se termină", "se finalizeaza", "finalizare", "încheie", "incheie",
    "durata", "durată", "cea mai mare", "cel mai lung", "perioadă",
    "început", "inceput", "sfarsit", "sfârșit", "când", "cand",
    "cate proiecte", "câte proiecte", "executie", "execuție",
]


# =========================================================
# CALCUL TEMPORAL
# =========================================================

def _build_temporal_context(supabase: Client) -> str:
    """
    Interoghează toate tabelele cu date și calculează statistici temporale:
    - proiecte/contracte active azi
    - care se termină în anul curent
    - care continuă în anul viitor
    - durata maximă (în luni) dintre cele active
    """
    azi = _dt.date.today()
    an_curent = azi.year
    an_viitor = azi.year + 1

    active_azi = []
    se_termina_an_curent = []
    continua_an_viitor = []
    durate = []  # (titlu, label, luni)

    for table in TABLES_WITH_DATES:
        try:
            res = supabase.table(table).select(
                "cod_identificare,titlu,titlul_proiect,titlu_proiect,"
                "denumire,obiect_contract,data_inceput,data_sfarsit"
            ).not_.is_("data_inceput", "null").not_.is_("data_sfarsit", "null").limit(500).execute()
            rows = res.data or []
        except Exception:
            continue

        label = table.replace("base_", "").replace("_", " ").upper()

        for r in rows:
            try:
                d_inc = _dt.date.fromisoformat(str(r["data_inceput"])[:10])
                d_sfa = _dt.date.fromisoformat(str(r["data_sfarsit"])[:10])
            except Exception:
                continue

            # Cel mai potrivit titlu disponibil
            titlu = (
                r.get("titlu") or r.get("titlul_proiect") or r.get("titlu_proiect")
                or r.get("denumire") or r.get("obiect_contract")
                or r.get("cod_identificare") or "—"
            )
            titlu = str(titlu)[:80]

            # Durata în luni
            luni = (d_sfa.year - d_inc.year) * 12 + (d_sfa.month - d_inc.month)

            # Activ azi
            if d_inc <= azi <= d_sfa:
                active_azi.append(f"[{label}] {titlu} ({d_inc} → {d_sfa}, {luni} luni)")
                durate.append((titlu, label, luni))

            # Se termină în anul curent și a început deja
            if d_sfa.year == an_curent and d_inc <= azi:
                se_termina_an_curent.append(f"[{label}] {titlu} (se termină: {d_sfa})")

            # Continuă în anul viitor (activ azi și data_sfarsit >= 1 ian anul viitor)
            if d_inc <= azi and d_sfa >= _dt.date(an_viitor, 1, 1):
                continua_an_viitor.append(f"[{label}] {titlu} (până la: {d_sfa})")

    # Durata maximă dintre proiectele active
    durata_max = ""
    if durate:
        titlu_max, label_max, luni_max = max(durate, key=lambda x: x[2])
        durata_max = (
            f"{titlu_max} [{label_max}] — {luni_max} luni "
            f"({luni_max // 12} ani și {luni_max % 12} luni)"
        )

    linii = [
        f"=== STATISTICI TEMPORALE (calculate la data de {azi}) ===",
        f"An curent: {an_curent} | An viitor: {an_viitor}",
        "",
        f"PROIECTE/CONTRACTE ACTIVE AZI: {len(active_azi)}",
    ]
    for x in active_azi[:30]:
        linii.append(f"  • {x}")
    if len(active_azi) > 30:
        linii.append(f"  ... și încă {len(active_azi) - 30} înregistrări")

    linii += ["", f"SE TERMINĂ ÎN {an_curent}: {len(se_termina_an_curent)}"]
    for x in se_termina_an_curent[:20]:
        linii.append(f"  • {x}")

    linii += ["", f"CONTINUĂ ÎN {an_viitor}: {len(continua_an_viitor)}"]
    for x in continua_an_viitor[:20]:
        linii.append(f"  • {x}")

    linii += ["", f"DURATA MAXIMĂ (dintre cele active): {durata_max or 'N/A'}"]

    return "\n".join(linii)


def _is_temporal_question(question: str) -> bool:
    """Detectează dacă întrebarea este despre perioade, durate sau status temporal."""
    q = question.lower()
    return any(kw in q for kw in DATE_KEYWORDS)


# =========================================================
# DETECT & CONTEXT
# =========================================================

def _detect_tables(question: str) -> list[str]:
    """Detectează ce tabele sunt relevante pentru întrebare."""
    q = question.lower()
    tables = []
    for table, kws in TABLE_KEYWORDS.items():
        if any(k in q for k in kws):
            tables.append(table)

    # Dacă întrebarea e generală — toate tabelele proiecte
    general_kws = ["total", "toate", "câte", "toate proiectele", "portofoliu", "situatie generala"]
    if not tables and any(k in q for k in general_kws):
        tables = list(TABLE_KEYWORDS.keys())

    return tables[:3] if tables else FALLBACK_TABLES[:3]


def _build_context(supabase: Client, tables: list[str]) -> str:
    """Construiește contextul din datele reale."""
    context_parts = []
    for table in tables:
        rows = safe_fetch(supabase, table, limit=200)
        if not rows:
            continue
        label = table.replace("base_", "").replace("_", " ").upper()
        context_parts.append(f"=== {label} ({len(rows)} înregistrări) ===")
        context_parts.append(df_to_context(rows, max_rows=40))
    return "\n\n".join(context_parts) if context_parts else "(nicio dată relevantă găsită)"


def _build_messages_for_claude(history: list[dict], new_user_msg: str) -> list[dict]:
    """
    Construiește lista de messages pentru API — include istoricul complet.
    Claude API necesită alternare strictă user/assistant.
    """
    messages = []
    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"],
        })
    messages.append({"role": "user", "content": new_user_msg})
    return messages


# =========================================================
# RENDER
# =========================================================

def render(supabase: Client):
    st.subheader("🧠 Chat AI cu baza IDBDC")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.85);font-size:0.95rem;margin-bottom:1rem;'>"
        "Pune întrebări în limbaj natural despre proiectele, contractele și activitatea "
        "de cercetare din IDBDC. AI-ul analizează datele reale și îți răspunde instant. "
        "Conversația este continuă — poți întreba în continuare pe aceeași temă."
        "</div>",
        unsafe_allow_html=True,
    )

    # Inițializare istoric
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ── Afișare istoric conversație ────────────────────────────────────────
    for msg in st.session_state.chat_history:
        role  = msg["role"]
        icon  = "👤" if role == "user" else "🤖"
        color = "rgba(255,255,255,0.08)" if role == "user" else "rgba(255,255,255,0.14)"
        with st.container():
            st.markdown(
                f"<div style='background:{color};border-radius:10px;padding:10px 14px;"
                f"margin-bottom:8px;'><b>{icon}</b>&nbsp; {msg['content']}</div>",
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Input ──────────────────────────────────────────────────────────────
    col_q, col_btn = st.columns([4, 1])
    with col_q:
        question = st.text_input(
            "Întreabă ceva despre baza IDBDC:",
            placeholder="Ex: Câte proiecte sunt active azi? / Care se termină în acest an?",
            key="chat_input",
            label_visibility="collapsed",
        )
    with col_btn:
        send = st.button("▶ Trimite", key="chat_send", use_container_width=True)

    st.markdown(
        "<div style='color:rgba(255,255,255,0.60);font-size:0.82rem;margin-top:4px;'>"
        "Exemple: «Câte proiecte sunt active azi?» · «Care se termină în acest an?» · "
        "«Câte continuă și anul viitor?» · «Care este durata maximă a unui proiect activ?»"
        "</div>",
        unsafe_allow_html=True,
    )

    if st.button("🗑️ Șterge conversația", key="chat_clear"):
        st.session_state.chat_history = []
        st.rerun()

    if not send or not (question or "").strip():
        return

    q = question.strip()

    # ── Construiește contextul — temporal sau tematic ──────────────────────
    if _is_temporal_question(q):
        with st.spinner("Calculez statistici temporale din baza de date..."):
            context = _build_temporal_context(supabase)
    else:
        tables  = _detect_tables(q)
        context = _build_context(supabase, tables)

    # Mesajul curent include datele din DB ca context
    user_msg_with_context = (
        f"Întrebare: {q}\n\n"
        f"Date din baza IDBDC (context):\n{context}\n\n"
        f"Răspunde la întrebare pe baza datelor de mai sus. Fii concis și precis."
    )

    # ── Construiește lista de messages cu tot istoricul ───────────────────
    messages_for_api = _build_messages_for_claude(
        st.session_state.chat_history,
        user_msg_with_context,
    )

    # ── Afișare răspuns streaming ──────────────────────────────────────────
    st.markdown(
        "<div style='background:rgba(255,255,255,0.14);border-radius:10px;"
        "padding:10px 14px;margin-top:8px;'><b>🤖</b>&nbsp;",
        unsafe_allow_html=True,
    )
    placeholder = st.empty()

    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.error("ANTHROPIC_API_KEY lipsă în Streamlit Secrets.")
        return

    import requests, json as _json
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": MODEL_FAST,
        "max_tokens": 1200,
        "stream": True,
        "system": SYSTEM_PROMPT,
        "messages": messages_for_api,
    }

    full_text = ""
    try:
        with requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers, json=payload, stream=True, timeout=90
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                decoded = line.decode("utf-8")
                if decoded.startswith("data:"):
                    raw = decoded[5:].strip()
                    if raw == "[DONE]":
                        break
                    try:
                        event = _json.loads(raw)
                        if event.get("type") == "content_block_delta":
                            delta = event.get("delta", {})
                            if delta.get("type") == "text_delta":
                                chunk = delta.get("text", "")
                                full_text += chunk
                                placeholder.markdown(full_text + "▌")
                    except _json.JSONDecodeError:
                        continue
        placeholder.markdown(full_text)
    except Exception as e:
        full_text = f"⚠️ Eroare: {e}"
        placeholder.markdown(full_text)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Salvează în istoric: user (fără context DB) + assistant ──────────
    st.session_state.chat_history.append({"role": "user",      "content": q})
    st.session_state.chat_history.append({"role": "assistant", "content": full_text})
    st.rerun()
