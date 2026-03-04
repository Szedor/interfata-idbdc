import streamlit as st
import pandas as pd
from supabase import Client


def _safe_select_all(supabase: Client, table: str, limit: int = 800):
    try:
        res = supabase.table(table).select("*").limit(limit).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Eroare la citirea din baza de date ({table}): {e}")
        return []


def _filter_anywhere(df: pd.DataFrame, keyword: str) -> pd.DataFrame:
    """
    Filtrare robusta: cauta keyword-ul in ORICE coloana (convertit la text).
    """
    k = (keyword or "").strip().lower()
    if not k:
        return df

    # Construim un text per rand, concatenand toate coloanele
    try:
        row_text = df.astype(str).fillna("").agg(" | ".join, axis=1).str.lower()
        return df[row_text.str.contains(k, na=False)]
    except Exception:
        # fallback: daca ceva nu merge, nu filtram
        return df


def render(supabase: Client):
    st.subheader("📊 Analiza interna IDBDC")
    st.caption("Selectezi categoria si rulezi analiza (tabel + export).")

    col1, col2, col3 = st.columns([1.3, 1.3, 1.6])

    with col1:
        categorie = st.selectbox(
            "Categorie",
            ["Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"],
            index=0,
        )

    tip = ""
    with col2:
        if categorie == "Contracte & Proiecte":
            tip = st.selectbox(
                "Tip",
                ["CEP", "TERTI", "PNCDI", "PNRR", "FDI", "INTERNATIONALE", "INTERREG", "NONEU"],
                index=0,
            )
        else:
            st.write("")

    with col3:
        keyword = st.text_input("Cuvant cheie (optional)", value="").strip()

    map_baze = {
        "CEP": "base_contracte_cep",
        "TERTI": "base_contracte_terti",
        "PNCDI": "base_proiecte_pncdi",
        "PNRR": "base_proiecte_pnrr",
        "FDI": "base_proiecte_fdi",
        "INTERNATIONALE": "base_proiecte_internationale",
        "INTERREG": "base_proiecte_interreg",
        "NONEU": "base_proiecte_noneu",
    }

    if categorie == "Contracte & Proiecte":
        table = map_baze.get(tip, "")
    elif categorie == "Evenimente stiintifice":
        table = "base_evenimente_stiintifice"
    else:
        table = "base_prop_intelect"

    st.divider()

    if not st.button("Ruleaza analiza"):
        st.info("Apasa «Ruleaza analiza».")
        return

    rows = _safe_select_all(supabase, table, limit=800)
    if not rows:
        st.info("Nu exista rezultate.")
        return

    df = pd.DataFrame(rows)

    # Filtrare keyword robusta
    if keyword:
        df2 = _filter_anywhere(df, keyword)
        if df2.empty:
            st.warning("Nu am gasit potriviri pentru cuvantul cheie introdus.")
            return
        df = df2

    st.success(f"Total rezultate: {len(df)}")

    st.subheader("Tabel (primele 200 randuri)")
    st.dataframe(df.head(200), use_container_width=True, height=560)

    st.divider()
    st.subheader("Export")

    c1, c2 = st.columns(2)

    with c1:
        st.download_button(
            "⬇️ Download CSV",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"analiza_{table}.csv",
            mime="text/csv",
        )

    with c2:
        import io
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Rezultate")
        buf.seek(0)
        st.download_button(
            "⬇️ Download Excel",
            data=buf,
            file_name=f"analiza_{table}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
