# grant_navigator/engine/strategy_recommendations.py

import streamlit as st
import pandas as pd
from supabase import Client

from grant_navigator.sources import fetch_calls_from_sources


def _safe_select_all(supabase: Client, table: str, limit: int = 400):
    try:
        res = supabase.table(table).select("*").limit(limit).execute()
        return res.data or []
    except Exception:
        return []


def _best_text_col(df: pd.DataFrame):
    for c in [
        "cuvinte_cheie",
        "descriere",
        "observatii",
        "titlu_proiect",
        "titlu",
        "denumire_proiect",
        "denumire",
        "titlu_eveniment",
        "denumire_eveniment",
    ]:
        if c in df.columns:
            return c
    return None


def render(supabase: Client):
    st.subheader("🎯 Recomandari strategice")

    st.caption(
        "Coreleaza ce avem in IDBDC cu oportunitati externe (matching simplu pe cuvinte cheie)."
    )

    col1, col2 = st.columns([1.2, 1.8])

    with col1:
        semnal = st.selectbox(
            "Semnal intern (IDBDC)",
            ["Proiecte PNRR", "Proiecte PNCDI", "Proiecte FDI", "Contracte CEP", "Contracte TERTI"],
            index=0,
        )

    with col2:
        keywords = st.text_input(
            "Cuvinte cheie pentru potrivire (separate prin virgula)",
            value="AI, energie, digitalizare",
        ).strip()

    limit = st.slider("Numar recomandari", min_value=10, max_value=60, value=25, step=5)

    st.divider()

    if not st.button("Genereaza recomandari"):
        st.info("Apasa «Genereaza recomandari».")
        return

    # 1) Date interne (sample)
    table_map = {
        "Proiecte PNRR": "base_proiecte_pnrr",
        "Proiecte PNCDI": "base_proiecte_pncdi",
        "Proiecte FDI": "base_proiecte_fdi",
        "Contracte CEP": "base_contracte_cep",
        "Contracte TERTI": "base_contracte_terti",
    }
    table = table_map.get(semnal)

    internal_rows = _safe_select_all(supabase, table, limit=400)
    df_int = pd.DataFrame(internal_rows) if internal_rows else pd.DataFrame()

    if df_int.empty:
        st.warning("Nu am gasit date interne pentru semnalul ales.")
    else:
        st.write("### Semnal intern (primele 30 randuri)")
        st.dataframe(df_int.head(30), use_container_width=True, height=360)

    # 2) Oportunitati externe (din radar)
    kws = [k.strip() for k in keywords.split(",") if k.strip()]
    query = " ".join(kws[:6]) if kws else ""

    calls = fetch_calls_from_sources(query=query, limit=120)
    df_calls = pd.DataFrame(calls) if calls else pd.DataFrame()

    if df_calls.empty:
        st.warning("Nu am gasit oportunitati externe.")
        return

    # 3) Scoring simplu: cate keyword-uri apar in titlu
    def score_title(t: str):
        t = (t or "").lower()
        s = 0
        for k in kws:
            if k.lower() in t:
                s += 1
        return s

    if "title" not in df_calls.columns:
        df_calls["title"] = ""

    df_calls["score"] = df_calls["title"].astype(str).apply(score_title)

    # 4) bonus mic daca in intern exista un text col care contine acele keyword-uri
    bonus = 0
    if not df_int.empty and kws:
        text_col = _best_text_col(df_int)
        if text_col:
            all_text = " ".join(df_int[text_col].astype(str).tolist()).lower()
            for k in kws:
                if k.lower() in all_text:
                    bonus += 1

    df_calls["score"] = df_calls["score"] + (0.2 * bonus)

    df_calls = df_calls.sort_values("score", ascending=False).head(int(limit))

    st.write("### Recomandari (top potrivire)")
    st.dataframe(df_calls, use_container_width=True, height=560)

    st.download_button(
        "⬇️ Download CSV",
        data=df_calls.to_csv(index=False).encode("utf-8-sig"),
        file_name="recomandari_strategice.csv",
        mime="text/csv",
    )
