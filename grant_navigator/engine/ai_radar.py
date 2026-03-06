# grant_navigator/engine/ai_radar.py
"""
Secțiunea 2 — Radar Finanțări
Versiunea curentă: date demonstrative + prezentare elegantă.
Conectorii live (Horizon Europe, UEFISCDI etc.) vor fi adăugați în versiunea următoare.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta


SURSE_DEMO = [
    {
        "sursa":    "Horizon Europe",
        "program":  "ERC Starting Grant",
        "tip":      "Grant individual",
        "tara":     "UE",
        "deadline": (datetime.today() + timedelta(days=45)).strftime("%Y-%m-%d"),
        "buget":    "până la 1.5M EUR",
        "link":     "https://erc.europa.eu",
        "status":   "🟢 Deschis",
    },
    {
        "sursa":    "Horizon Europe",
        "program":  "MSCA Postdoctoral Fellowships",
        "tip":      "Mobilitate cercetători",
        "tara":     "UE",
        "deadline": (datetime.today() + timedelta(days=60)).strftime("%Y-%m-%d"),
        "buget":    "variabil",
        "link":     "https://marie-sklodowska-curie-actions.ec.europa.eu",
        "status":   "🟢 Deschis",
    },
    {
        "sursa":    "UEFISCDI",
        "program":  "Proiecte de Cercetare Exploratorie (PCE)",
        "tip":      "Proiect național",
        "tara":     "România",
        "deadline": (datetime.today() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "buget":    "până la 1.2M RON",
        "link":     "https://uefiscdi.gov.ro",
        "status":   "🟢 Deschis",
    },
    {
        "sursa":    "UEFISCDI",
        "program":  "Proiecte de Transfer de Cunoaștere (PTC)",
        "tip":      "Transfer tehnologic",
        "tara":     "România",
        "deadline": (datetime.today() + timedelta(days=90)).strftime("%Y-%m-%d"),
        "buget":    "până la 800K RON",
        "link":     "https://uefiscdi.gov.ro",
        "status":   "🟡 În curând",
    },
    {
        "sursa":    "EEA / Norway Grants",
        "program":  "Research Collaborative Programme",
        "tip":      "Colaborare bilaterală",
        "tara":     "SEE",
        "deadline": (datetime.today() + timedelta(days=75)).strftime("%Y-%m-%d"),
        "buget":    "variabil",
        "link":     "https://eeagrants.org",
        "status":   "🟢 Deschis",
    },
    {
        "sursa":    "Horizon Europe",
        "program":  "INTERREG Danube Transnational",
        "tip":      "Cooperare teritorială",
        "tara":     "UE / Regional",
        "deadline": (datetime.today() + timedelta(days=120)).strftime("%Y-%m-%d"),
        "buget":    "variabil per partener",
        "link":     "https://www.interreg-danube.eu",
        "status":   "🟡 În pregătire",
    },
    {
        "sursa":    "PNRR",
        "program":  "Investiții în infrastructura de CDI",
        "tip":      "Infrastructură",
        "tara":     "România",
        "deadline": (datetime.today() + timedelta(days=15)).strftime("%Y-%m-%d"),
        "buget":    "variabil",
        "link":     "https://mfe.gov.ro",
        "status":   "🔴 Deadline apropiat",
    },
    {
        "sursa":    "ESA (Agenția Spațială Europeană)",
        "program":  "ESA BIC Romania — Space Startup",
        "tip":      "Incubator / startup",
        "tara":     "International",
        "deadline": (datetime.today() + timedelta(days=180)).strftime("%Y-%m-%d"),
        "buget":    "până la 50K EUR + mentoring",
        "link":     "https://esabic.ro",
        "status":   "🟢 Deschis",
    },
]


def render():
    st.subheader("🛰️ Radar Finanțări")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.85);font-size:0.95rem;margin-bottom:1rem;'>"
        "Oportunități de finanțare pentru cercetare — surse naționale și internaționale. "
        "<span style='background:rgba(255,200,0,0.2);border-radius:4px;padding:2px 8px;"
        "font-size:0.80rem;'>⚙️ Conectori live în dezvoltare</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Filtre
    c1, c2, c3 = st.columns([1.5, 1.5, 2])
    with c1:
        surse_disponibile = sorted(list({s["sursa"] for s in SURSE_DEMO}))
        sursa_sel = st.selectbox("Sursă finanțare", ["Toate"] + surse_disponibile)
    with c2:
        status_sel = st.selectbox("Status", ["Toate", "🟢 Deschis", "🟡 În curând", "🔴 Deadline apropiat"])
    with c3:
        keyword = st.text_input("Cuvânt cheie", placeholder="Ex: mobilitate, infrastructură, startup...").strip()

    # Filtrare
    items = SURSE_DEMO.copy()
    if sursa_sel != "Toate":
        items = [i for i in items if i["sursa"] == sursa_sel]
    if status_sel != "Toate":
        items = [i for i in items if i["status"] == status_sel]
    if keyword:
        k = keyword.lower()
        items = [i for i in items if k in (i["program"] + i["tip"] + i["sursa"]).lower()]

    # Sortare după deadline
    items = sorted(items, key=lambda x: x["deadline"])

    st.divider()

    if not items:
        st.info("Niciun rezultat pentru filtrele selectate.")
        return

    st.markdown(f"**{len(items)} oportunități găsite:**")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Afișare carduri
    for item in items:
        deadline_dt = datetime.strptime(item["deadline"], "%Y-%m-%d")
        days_left   = (deadline_dt - datetime.today()).days
        urgency_color = (
            "rgba(255,80,80,0.15)"   if days_left <= 20 else
            "rgba(255,200,0,0.12)"   if days_left <= 60 else
            "rgba(255,255,255,0.08)"
        )

        st.markdown(
            f"""
            <div style='background:{urgency_color};border:1px solid rgba(255,255,255,0.20);
            border-radius:12px;padding:14px 18px;margin-bottom:10px;'>
                <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <div>
                        <span style='font-weight:900;font-size:1.05rem;color:#ffffff;'>
                            {item['program']}
                        </span>
                        <span style='margin-left:10px;font-size:0.82rem;
                        color:rgba(255,255,255,0.70);'>{item['sursa']}</span>
                    </div>
                    <div style='text-align:right;'>
                        <span style='font-size:0.88rem;color:rgba(255,255,255,0.85);'>
                            {item['status']}
                        </span>
                    </div>
                </div>
                <div style='margin-top:6px;color:rgba(255,255,255,0.80);font-size:0.88rem;'>
                    📋 {item['tip']} &nbsp;|&nbsp;
                    🌍 {item['tara']} &nbsp;|&nbsp;
                    💰 {item['buget']} &nbsp;|&nbsp;
                    📅 Deadline: <b>{item['deadline']}</b>
                    ({days_left} zile) &nbsp;|&nbsp;
                    <a href='{item['link']}' target='_blank'
                    style='color:rgba(150,210,255,0.90);'>🔗 Link</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # Export
    df = pd.DataFrame(items)
    st.download_button(
        "⬇️ Export CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="radar_finantari.csv",
        mime="text/csv",
    )

    st.markdown(
        "<div style='color:rgba(255,255,255,0.50);font-size:0.78rem;margin-top:12px;'>"
        "ℹ️ Datele sunt orientative. Verificați întotdeauna termenele oficiale pe site-urile finanțatorilor. "
        "Conectori live pentru actualizare automată sunt în dezvoltare."
        "</div>",
        unsafe_allow_html=True,
    )
