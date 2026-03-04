# grant_navigator/engine/external_radar.py

import streamlit as st
import pandas as pd

from grant_navigator.sources import get_available_sources, fetch_calls_from_sources


def render():
    st.subheader("🛰️ Radar finantari (surse deschise)")

    st.caption("Cauti oportunitati in surse open (UE/RO/SEE/agentii/administratii).")

    sources = get_available_sources()

    # afisare surse in UI
    source_labels = {s["name"]: s["id"] for s in sources}
    default_names = [s["name"] for s in sources]

    col1, col2 = st.columns([1.6, 1.4])

    with col1:
        selected_names = st.multiselect(
            "Surse selectate",
            options=list(source_labels.keys()),
            default=default_names,
        )

    with col2:
        keyword = st.text_input("Cuvant cheie (optional)", value="").strip()

    limit = st.slider("Numar maxim rezultate", min_value=10, max_value=200, value=50, step=10)

    st.divider()

    if not st.button("Cauta oportunitati"):
        st.info("Apasa «Cauta oportunitati».")
        return

    # in versiunea actuala, filtrarea pe surse e simpla (demonstrativ)
    selected_ids = [source_labels[n] for n in selected_names if n in source_labels]

    items = fetch_calls_from_sources(query=keyword, limit=int(limit))

    # filtreaza dupa sursele selectate
    if selected_ids:
        items = [it for it in items if (it.get("source") in selected_ids)]

    if not items:
        st.info("Nu exista rezultate pentru criteriile selectate.")
        return

    df = pd.DataFrame(items)

    # ordonare rapida dupa deadline (daca exista)
    if "deadline" in df.columns:
        try:
            df = df.sort_values("deadline", ascending=True)
        except Exception:
            pass

    st.success(f"Total oportunitati: {len(df)}")

    st.dataframe(df, use_container_width=True, height=560)

    st.divider()
    st.subheader("Export")

    st.download_button(
        "⬇️ Download CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="radar_finantari.csv",
        mime="text/csv",
    )
