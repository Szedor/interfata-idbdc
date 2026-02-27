import streamlit as st
import pandas as pd
from supabase import create_client, Client

PASSWORD = "EverDream2SZ"

BASE_TABLES = {
    "CEP": "base_contracte_cep",
    "TERTI": "base_contracte_terti",
    "FDI": "base_proiecte_fdi",
    "PNRR": "base_proiecte_pnrr",
    "INTERNATIONALE": "base_proiecte_internationale",
    "INTERREG": "base_proiecte_interreg",
    "NONEU": "base_proiecte_noneu",
    "PNCDI": "base_proiecte_pncdi",
}

def gate():
    if "auth_explorator" not in st.session_state:
        st.session_state.auth_explorator = False
    if not st.session_state.auth_explorator:
        st.markdown("## 🛡️ Acces Securizat – Explorator IDBDC")
        p = st.text_input("Parola:", type="password")
        if st.button("Intră"):
            if p == PASSWORD:
                st.session_state.auth_explorator = True
                st.rerun()
        st.stop()

def run():
    st.set_page_config(page_title="IDBDC – Explorator (B)", layout="wide")
    gate()

    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.title("🧭 Explorator IDBDC — Varianta B (Wizard)")
    st.caption("3 pași: alegi tipul → introduci indicii → vezi rezultate + detalii.")
    st.divider()

    if "step" not in st.session_state:
        st.session_state.step = 1

    # STEP 1
    if st.session_state.step == 1:
        st.subheader("Pas 1/3 — Alege tipurile")
        tipuri = st.multiselect("Tipuri contract/proiect", list(BASE_TABLES.keys()), default=["CEP"])
        if st.button("Continuă"):
            st.session_state.tipuri = tipuri
            st.session_state.step = 2
            st.rerun()
        st.stop()

    # STEP 2
    if st.session_state.step == 2:
        st.subheader("Pas 2/3 — Indicii")
        col1, col2 = st.columns(2)
        with col1:
            q_text = st.text_input("Cuvinte cheie (ID / acronim / titlu)")
        with col2:
            an = st.number_input("An (opțional)", 2010, 2035, 2024)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Înapoi"):
                st.session_state.step = 1
                st.rerun()
        with c2:
            if st.button("Caută"):
                st.session_state.q_text = q_text
                st.session_state.an = an
                st.session_state.step = 3
                st.rerun()
        st.stop()

    # STEP 3
    st.subheader("Pas 3/3 — Rezultate")
    tipuri = st.session_state.get("tipuri", ["CEP"])
    q_text = (st.session_state.get("q_text") or "").strip()
    an = st.session_state.get("an")

    rows_all = []
    for tip in tipuri:
        table_name = BASE_TABLES.get(tip)
        if not table_name:
            continue
        try:
            res = supabase.table(table_name).select("*").execute()
            for r in (res.data or []):
                r["_tip"] = tip
                r["_table"] = table_name
            rows_all.extend(res.data or [])
        except Exception as e:
            st.warning(f"Nu pot citi {table_name}: {e}")

    df = pd.DataFrame(rows_all)
    if df.empty:
        st.warning("Niciun rezultat.")
        st.stop()

    if "cod_identificare" in df.columns:
        df["cod_identificare"] = df["cod_identificare"].astype(str)

    if q_text:
        t = q_text.casefold()
        masks = []
        for col in ["cod_identificare", "acronim_proiect", "titlu_proiect", "obiect_contract", "denumire_proiect"]:
            if col in df.columns:
                masks.append(df[col].astype(str).str.casefold().str.contains(t, na=False))
        if masks:
            m = masks[0]
            for x in masks[1:]:
                m = m | x
            df = df[m]

    # an (best effort)
    for an_col in ["an_implementare", "an", "an_derulare", "an_inceput"]:
        if an_col in df.columns and an:
            df = df[df[an_col].fillna(0).astype(int) == int(an)]
            break

    c1, c2 = st.columns([1.1, 1.2])
    with c1:
        show_cols = [c for c in ["cod_identificare", "_tip", "titlu_proiect", "obiect_contract", "acronim_proiect"] if c in df.columns]
        st.dataframe(df[show_cols], use_container_width=True, height=520)
        selected_id = st.text_input("ID pentru detalii:", value="")

        b1, b2 = st.columns(2)
        with b1:
            if st.button("Înapoi la indicii"):
                st.session_state.step = 2
                st.rerun()
        with b2:
            if st.button("Reia de la început"):
                st.session_state.step = 1
                st.rerun()

    with c2:
        st.subheader("Detalii")
        if not selected_id.strip():
            st.info("Introdu un ID din listă.")
            st.stop()
        if "cod_identificare" not in df.columns:
            st.error("Lipsește cod_identificare.")
            st.stop()
        match = df[df["cod_identificare"] == selected_id.strip()]
        if match.empty:
            st.warning("ID-ul nu există.")
            st.stop()
        r = match.iloc[0].to_dict()
        st.caption(f"Sursă: {r.get('_table','')} ({r.get('_tip','')})")
        for k, v in sorted(r.items()):
            if k.startswith("_"):
                continue
            if v is None or str(v).strip() == "":
                continue
            st.write(f"**{k}**: {v}")

if __name__ == "__main__":
    run()
