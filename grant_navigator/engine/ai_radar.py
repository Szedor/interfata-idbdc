# grant_navigator/engine/ai_radar.py
"""
Sectiunea 2 — Radar Finantari vers.3

- 10 surse fixe definitive
- Web search live la activarea tab-ului — ultimele apeluri active per sursa
- Cache in session_state pe durata sesiunii
- Carduri colapsabile: click pe sursa — 4-5 apeluri cu deadline, buget, link
- Camp custom: cauta orice program necunoscut
- AI Matching cu profilul real UPT
- Afisare in limba originala a sursei
"""

import streamlit as st
import json
import requests
from supabase import Client

from grant_navigator.engine.ai_core import (
    _call_claude,
    _get_api_key,
    safe_fetch,
    df_to_context,
    MODEL_FAST,
    CLAUDE_API_URL,
)


# =========================================================
# CELE 10 SURSE FIXE
# =========================================================

SURSE_FIXE = [
    {
        "id":    "mec",
        "nume":  "Ministerul Educatiei si Cercetarii",
        "desc":  "UEFISCDI — PNCDI, PNRR, FDI, CNFIS si alte programe nationale",
        "url":   "https://uefiscdi.gov.ro",
        "query": "UEFISCDI apeluri active finantare cercetare PNCDI FDI 2025",
    },
    {
        "id":    "mipe",
        "nume":  "Ministerul Investitiilor si Proiectelor Europene",
        "desc":  "Fonduri europene structurale si de coeziune — apeluri active",
        "url":   "https://mfe.gov.ro",
        "query": "Ministerul Investitiilor Proiecte Europene apeluri active fonduri europene 2025",
    },
    {
        "id":    "mdlpa",
        "nume":  "Ministerul Dezvoltarii, Lucrarilor Publice si Administratiei",
        "desc":  "Programe de dezvoltare regionala si infrastructura",
        "url":   "https://www.mdlpa.ro",
        "query": "Ministerul Dezvoltarii apeluri finantare proiecte 2025",
    },
    {
        "id":    "eu_funding",
        "nume":  "EU Funding & Tenders Portal",
        "desc":  "Portalul oficial al Comisiei Europene — toate apelurile UE deschise",
        "url":   "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/home",
        "query": "EU Funding Tenders Portal open calls research innovation 2025",
    },
    {
        "id":    "eu_calls",
        "nume":  "EU Calls",
        "desc":  "Agregator apeluri europene — Horizon Europe, ERC, MSCA, EIC",
        "url":   "https://eucalls.net",
        "query": "Horizon Europe ERC MSCA EIC open calls deadline 2025",
    },
    {
        "id":    "interreg",
        "nume":  "Interreg EU",
        "desc":  "Cooperare teritoriala europeana — programe transnationale si transfrontaliere",
        "url":   "https://www.interreg.eu",
        "query": "Interreg EU open calls cooperation programme 2025",
    },
    {
        "id":    "esa",
        "nume":  "European Space Agency",
        "desc":  "ESA — apeluri pentru cercetare spatiala, ESA BIC Romania",
        "url":   "https://www.esa.int",
        "query": "ESA European Space Agency open calls tenders funding 2025",
    },
    {
        "id":    "eureka",
        "nume":  "Eureka",
        "desc":  "Retea europeana de inovare — proiecte colaborative industrie-cercetare",
        "url":   "https://www.eurekanetwork.org",
        "query": "Eureka network open calls funding innovation projects 2025",
    },
    {
        "id":    "nato",
        "nume":  "Funding NATO & Security Action for Europe (SAFE)",
        "desc":  "NATO Science for Peace, SAFE — finantari securitate si cercetare",
        "url":   "https://www.nato.int/cps/en/natohq/topics_85373.htm",
        "query": "NATO Science Peace Security funding calls grants 2025",
    },
    {
        "id":    "eea",
        "nume":  "EEA Grants",
        "desc":  "Granturi SEE si Norvegia — cercetare, inovare, mediu, educatie",
        "url":   "https://eeagrants.org",
        "query": "EEA Norway Grants open calls research Romania 2025",
    },
]


# =========================================================
# WEB SEARCH + CLAUDE — extragere apeluri per sursa
# =========================================================

def _extract_calls_for_source(sursa: dict) -> list[dict]:
    """
    Face web search si extrage apelurile active pentru o sursa,
    returnand o lista structurata JSON.
    """
    api_key = _get_api_key()
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    system = (
        "You are a research funding specialist. "
        "Search the web for active/open funding calls from a specific source "
        "and return ONLY a valid JSON array. No explanations, no markdown, just JSON.\n\n"
        "Each item must have exactly these fields:\n"
        "- title: exact name of the call/programme in original language\n"
        "- deadline: deadline date as found (e.g. '15 March 2025', 'Rolling', 'TBD')\n"
        "- budget: funding amount as found (e.g. 'up to 1.5M EUR', 'variabil')\n"
        "- link: direct URL to the call page\n"
        "- status: 'Open', 'Forthcoming', or 'Closed'\n\n"
        "Return maximum 5 calls. If none found return [].\n"
        "CRITICAL: Return ONLY valid JSON array, nothing else."
    )

    user_msg = (
        f"Find active/open funding calls from: {sursa['nume']}\n"
        f"Official URL: {sursa['url']}\n"
        f"Search hint: {sursa['query']}\n\n"
        f"Return JSON array only, in original language of the source."
    )

    payload = {
        "model": MODEL_FAST,
        "max_tokens": 1200,
        "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 4}],
        "system": system,
        "messages": [{"role": "user", "content": user_msg}],
    }

    try:
        resp = requests.post(CLAUDE_API_URL, headers=headers, json=payload, timeout=50)
        resp.raise_for_status()
        data = resp.json()

        full_text = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                full_text += block.get("text", "")

        full_text = full_text.strip()
        if "```" in full_text:
            parts = full_text.split("```")
            for part in parts:
                if "[" in part and "{" in part:
                    full_text = part.replace("json", "").strip()
                    break

        # Gasim primul [ si ultimul ] din text
        start = full_text.find("[")
        end   = full_text.rfind("]")
        if start != -1 and end != -1:
            full_text = full_text[start:end+1]

        calls = json.loads(full_text)
        if isinstance(calls, list):
            return calls[:5]
        return []

    except json.JSONDecodeError:
        return [{
            "title":    "Nu s-au putut extrage apelurile automat",
            "deadline": "—",
            "budget":   "—",
            "link":     sursa.get("url", "#"),
            "status":   "Unknown",
        }]
    except Exception as e:
        return [{
            "title":    f"Eroare cautare: {str(e)[:80]}",
            "deadline": "—",
            "budget":   "—",
            "link":     sursa.get("url", "#"),
            "status":   "Unknown",
        }]


def _load_all_sources_progressive() -> dict:
    """
    Incarca apelurile pentru toate cele 10 surse, una dupa alta,
    afisand progresul live. Returneaza dict {sursa_id: [calls]}.
    """
    results = {}
    progress_box = st.empty()

    for i, sursa in enumerate(SURSE_FIXE):
        progress_box.markdown(
            f"<div style='background:rgba(255,255,255,0.07);border:1px solid "
            f"rgba(255,255,255,0.18);border-radius:10px;padding:12px 18px;'>"
            f"<span style='color:rgba(255,255,255,0.70);font-size:0.88rem;'>"
            f"🔍 {i+1}/{len(SURSE_FIXE)} — Caut apeluri: "
            f"<b style='color:#ffffff;'>{sursa['nume']}</b>"
            f"</span></div>",
            unsafe_allow_html=True,
        )
        results[sursa["id"]] = _extract_calls_for_source(sursa)

    progress_box.empty()
    return results


# =========================================================
# UI HELPERS
# =========================================================

def _status_badge(status: str) -> str:
    s = (status or "").lower()
    if "open" in s or "deschis" in s:
        return "🟢"
    if "forthcoming" in s or "upcoming" in s or "viitor" in s:
        return "🟡"
    if "closed" in s or "inchis" in s:
        return "🔴"
    return "⚪"


def _render_calls(sursa_url: str, calls: list[dict]):
    if not calls:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.45);font-size:0.85rem;"
            "padding:6px 0;'>Niciun apel activ gasit.</div>",
            unsafe_allow_html=True,
        )
        return

    for call in calls:
        title    = call.get("title", "—")
        deadline = call.get("deadline", "—")
        budget   = call.get("budget", "—")
        link     = call.get("link") or sursa_url or "#"
        status   = call.get("status", "")
        badge    = _status_badge(status)

        st.markdown(
            f"<div style='background:rgba(255,255,255,0.06);border-left:3px solid "
            f"rgba(255,255,255,0.28);border-radius:8px;padding:10px 14px;"
            f"margin-bottom:7px;'>"
            f"<div style='font-weight:700;color:#ffffff;font-size:0.95rem;'>"
            f"{badge} {title}</div>"
            f"<div style='color:rgba(255,255,255,0.65);font-size:0.82rem;margin-top:5px;'>"
            f"📅 <b>{deadline}</b> &nbsp;|&nbsp; "
            f"💰 {budget} &nbsp;|&nbsp; "
            f"<a href='{link}' target='_blank' "
            f"style='color:rgba(150,210,255,0.90);'>🔗 Link</a>"
            f"</div></div>",
            unsafe_allow_html=True,
        )


def _get_upt_profile_summary(supabase: Client) -> str:
    parts = []
    tables = {
        "Internationale": "base_proiecte_internationale",
        "PNCDI":          "base_proiecte_pncdi",
        "FDI":            "base_proiecte_fdi",
        "TERTI":          "base_contracte_terti",
        "PI":             "base_prop_intelect",
    }
    for label, table in tables.items():
        rows = safe_fetch(supabase, table, limit=50)
        if rows:
            parts.append(f"{label} ({len(rows)} inregistrari): {df_to_context(rows, max_rows=8)}")
    return "\n\n".join(parts) if parts else "(profil indisponibil)"


# =========================================================
# RENDER PRINCIPAL
# =========================================================

def render(supabase: Client = None):
    st.subheader("🛰️ Radar Finantari")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.85);font-size:0.95rem;margin-bottom:1rem;'>"
        "Apeluri active din cele 10 surse de finantare — actualizate la fiecare deschidere a tab-ului. "
        "Informatiile sunt afisate in limba originala a sursei."
        "</div>",
        unsafe_allow_html=True,
    )

    # ── Incarcare progresiva la prima deschidere ──────────────────────────
    if "radar_calls" not in st.session_state:
        st.info("Se cauta apelurile active pentru cele 10 surse... (~30 secunde)", icon="🔍")
        st.session_state["radar_calls"] = _load_all_sources_progressive()
        st.rerun()

    calls_data = st.session_state["radar_calls"]

    # Buton refresh
    col_r, col_info, _ = st.columns([1, 3, 2])
    with col_r:
        if st.button("🔄 Actualizeaza", key="radar_refresh"):
            for k in ("radar_calls", "radar_match_result", "radar_custom_result"):
                st.session_state.pop(k, None)
            st.rerun()
    with col_info:
        st.markdown(
            "<span style='color:rgba(255,255,255,0.45);font-size:0.80rem;'>"
            "Rezultatele sunt valabile pentru intreaga sesiune.</span>",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Cele 10 surse — colapsabile ───────────────────────────────────────
    st.markdown(
        "<div style='color:rgba(255,255,255,0.55);font-size:0.80rem;"
        "font-weight:700;text-transform:uppercase;letter-spacing:0.06em;"
        "margin-bottom:10px;'>Surse monitorizate</div>",
        unsafe_allow_html=True,
    )

    for sursa in SURSE_FIXE:
        calls = calls_data.get(sursa["id"], [])
        nr_open = sum(
            1 for c in calls
            if "open" in (c.get("status") or "").lower()
        )
        nr_total = len(calls)

        if nr_open > 0:
            badge_txt = f"🟢 {nr_open} deschis"
            badge_col = "rgba(50,220,100,0.90)"
        elif nr_total > 0:
            badge_txt = f"🟡 {nr_total} in curand"
            badge_col = "rgba(255,200,50,0.90)"
        else:
            badge_txt = "⚪ niciun apel"
            badge_col = "rgba(255,255,255,0.35)"

        with st.expander(f"{sursa['nume']}  —  {badge_txt}", expanded=False):
            st.markdown(
                f"<div style='color:rgba(255,255,255,0.55);font-size:0.82rem;"
                f"margin-bottom:8px;'>{sursa['desc']}</div>",
                unsafe_allow_html=True,
            )
            _render_calls(sursa["url"], calls)
            st.markdown(
                f"<div style='margin-top:8px;'>"
                f"<a href='{sursa['url']}' target='_blank' "
                f"style='color:rgba(150,210,255,0.75);font-size:0.80rem;'>"
                f"🌐 Site oficial</a></div>",
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Cautare sursa custom ──────────────────────────────────────────────
    st.markdown(
        "<div style='color:rgba(255,255,255,0.88);font-size:0.97rem;font-weight:700;"
        "margin-bottom:4px;'>🔎 Alta sursa de finantare</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='color:rgba(255,255,255,0.55);font-size:0.82rem;margin-bottom:8px;'>"
        "Scrie denumirea unui program sau finantator si primesti apelurile active.</div>",
        unsafe_allow_html=True,
    )

    col_inp, col_btn = st.columns([3, 1])
    with col_inp:
        sursa_custom = st.text_input(
            "Sursa",
            value="",
            placeholder="Ex: Marie Curie, COST Actions, Erasmus+, Fond Bilateral...",
            label_visibility="collapsed",
            key="radar_custom_input",
        ).strip()
    with col_btn:
        btn_custom = st.button("🔍 Cauta", key="radar_custom_go", use_container_width=True)

    if btn_custom and sursa_custom:
        with st.spinner(f"Caut apeluri pentru: {sursa_custom}..."):
            sursa_temp = {
                "id":    "custom",
                "nume":  sursa_custom,
                "desc":  "",
                "url":   "",
                "query": f"{sursa_custom} open calls funding deadline 2025",
            }
            st.session_state["radar_custom_result"] = {
                "sursa": sursa_custom,
                "calls": _extract_calls_for_source(sursa_temp),
            }

    if "radar_custom_result" in st.session_state:
        res = st.session_state["radar_custom_result"]
        st.markdown(
            f"<div style='background:rgba(255,255,255,0.07);border:1px solid "
            f"rgba(255,255,255,0.22);border-radius:10px;padding:12px 16px;margin-top:8px;'>"
            f"<b style='color:#ffffff;'>Rezultate: {res['sursa']}</b>"
            f"</div>",
            unsafe_allow_html=True,
        )
        _render_calls("", res["calls"])

    st.divider()

    # ── AI Matching cu profilul UPT ───────────────────────────────────────
    if supabase is not None:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.88);font-size:0.97rem;font-weight:700;"
            "margin-bottom:4px;'>🤖 Potrivire cu profilul UPT</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='color:rgba(255,255,255,0.55);font-size:0.82rem;margin-bottom:8px;'>"
            "AI analizeaza portofoliul real IDBDC si recomanda top 3 apeluri potrivite.</div>",
            unsafe_allow_html=True,
        )

        if st.button("🤖 Analizeaza potrivirea", key="radar_match"):
            with st.spinner("Analizez portofoliul UPT..."):
                profile   = _get_upt_profile_summary(supabase)
                opps_lines = []
                for sursa in SURSE_FIXE:
                    for c in calls_data.get(sursa["id"], []):
                        opps_lines.append(
                            f"[{sursa['nume']}] {c.get('title','?')} | "
                            f"deadline: {c.get('deadline','?')} | status: {c.get('status','?')}"
                        )
                opps_text = "\n".join(opps_lines) or "(niciun apel gasit)"
                msg = (
                    f"Profilul de cercetare UPT (date reale IDBDC):\n{profile}\n\n"
                    f"Apeluri active gasite:\n{opps_text}\n\n"
                    f"Identifica TOP 3 apeluri cele mai potrivite pentru UPT, "
                    f"cu justificare scurta bazata pe profilul real. Fii concis."
                )
                result = _call_claude(
                    system_prompt=(
                        "Esti expert in finantari de cercetare universitara. "
                        "Raspunzi exclusiv in romana, concis si direct."
                    ),
                    user_message=msg,
                    model=MODEL_FAST,
                    max_tokens=700,
                )
            st.session_state["radar_match_result"] = result

        if "radar_match_result" in st.session_state:
            st.markdown(
                "<div style='background:rgba(255,255,255,0.12);border:1px solid "
                "rgba(255,255,255,0.25);border-radius:12px;padding:14px 18px;margin-top:8px;'>"
                "<b style='color:#ffffff;'>🤖 Recomandari AI pentru UPT:</b><br><br>"
                f"<span style='color:rgba(255,255,255,0.90);'>"
                f"{st.session_state['radar_match_result']}</span></div>",
                unsafe_allow_html=True,
            )

    st.markdown(
        "<div style='color:rgba(255,255,255,0.35);font-size:0.76rem;margin-top:16px;'>"
        "Informatiile sunt extrase automat de pe site-urile oficiale. "
        "Verificati intotdeauna termenele si conditiile pe site-ul oficial inainte de depunere."
        "</div>",
        unsafe_allow_html=True,
    )
