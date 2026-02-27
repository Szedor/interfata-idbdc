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

@st.cache_data(show_spinner=False, ttl=600)
def fetch_categories(_url: str, _key: str) -> list[str]:
    supabase = create_client(_url, _key)
    try:
        res = supabase.table("nom_categorie").select("denumire_categorie").execute()
        return sorted({r["denumire_categorie"] for r in (res.data or []) if r.get("denumire_categorie")})
    except Exception:
        return ["Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"]

def run():
    st.set_page_config(page_title="IDBDC – Explorator (A)", layout="wide")
    gate()

    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.title("🔎 Explorator IDBDC — Varianta A")
    st.caption("Căutare rapidă + selecție rezultat + detalii în dreapta.")
    st.divider()

    left, right = st.columns([1.1, 1.2], gap="large")

    with left:
        st.subheader("Filtre rapide")
        categorii = fetch_categories(url, key)
        cat = st.selectbox("Categoria", ["Contracte & Proiecte"] + [c for c in categorii if c != "Contracte & Proiecte"])
        tipuri = st.multiselect("Tip (Contracte & Proiecte)", list(BASE_TABLES.keys()), default=["CEP"])

        q_text = st.text_input("Căutare text (ID / acronim / titlu)")

        col1, col2 = st.columns(2)
        with col1:
            an_min = st.number_input("An minim", 2010, 2035, 2010)
        with col2:
            an_max = st.number_input("An maxim", 2010, 2035, 2035)

        do_search = st.button("🔎 Caută", use_container_width=True)

    if not do_search:
        st.info("Setează filtrele și apasă Caută.")
        st.stop()

    # 1) Căutare în tabelele selectate
    rows_all = []
    for tip in tipuri:
        table_name = BASE_TABLES.get(tip)
        if not table_name:
            continue
        q = supabase.table(table_name).select("*")

        # filtre simple (best-effort)
        if q_text.strip():
            # încercăm pe câteva câmpuri uzuale
            # Supabase nu suportă OR ușor fără view/rpc; facem fallback: luăm mai multe și filtrăm local
            pass

        try:
            res = q.execute()
            for r in (res.data or []):
                r["_tip"] = tip
                r["_table"] = table_name
            rows_all.extend(res.data or [])
        except Exception as e:
            st.warning(f"Nu pot citi {table_name}: {e}")

    if not rows_all:
        st.warning("Niciun rezultat.")
        st.stop()

    df = pd.DataFrame(rows_all)

    # 2) Filtrare locală pe text + an
    if "cod_identificare" in df.columns:
        df["cod_identificare"] = df["cod_identificare"].astype(str)

    if q_text.strip():
        t = q_text.strip().casefold()
        candidates = []
        for col in ["cod_identificare", "acronim_proiect", "titlu_proiect", "obiect_contract", "denumire_proiect"]:
            if col in df.columns:
                candidates.append(df[col].astype(str).str.casefold().str.contains(t, na=False))
        if candidates:
            mask = candidates[0]
            for m in candidates[1:]:
                mask = mask | m
            df = df[mask]

    for an_col in ["an_implementare", "an", "an_derulare", "an_inceput"]:
        if an_col in df.columns:
            df = df[(df[an_col].fillna(0).astype(int) >= int(an_min)) & (df[an_col].fillna(9999).astype(int) <= int(an_max))]
            break

    if df.empty:
        st.warning("Niciun rezultat după filtre.")
        st.stop()

    # 3) Tabel rezultate + selecție
    show_cols = [c for c in ["cod_identificare", "_tip", "titlu_proiect", "obiect_contract", "denumire_proiect", "acronim_proiect"] if c in df.columns]
    if "_tip" in df.columns and "_tip" not in show_cols:
        show_cols.insert(1, "_tip")

    with left:
        st.subheader(f"Rezultate ({len(df)})")
        st.dataframe(df[show_cols], use_container_width=True, height=520)

        selected_id = st.text_input("Deschide detalii pentru ID (copie din tabel):", value="")

    with right:
        st.subheader("Detalii")
        if not selected_id.strip():
            st.info("Copiază un ID din tabel și pune-l aici.")
            st.stop()

        # găsește primul rând cu cod_identificare
        if "cod_identificare" not in df.columns:
            st.error("Lipsește coloana cod_identificare în rezultate.")
            st.stop()

        match = df[df["cod_identificare"].astype(str) == selected_id.strip()]
        if match.empty:
            st.warning("ID-ul nu există în rezultate.")
            st.stop()

        r = match.iloc[0].to_dict()
        st.caption(f"Sursă: {r.get('_table','')} ({r.get('_tip','')})")

        for k, v in sorted(r.items()):
            if k.startswith("_"):
                continue
            if v is None or str(v).strip() == "":
                continue
            st.write(f"**{k}**: {v}")

        st.divider()
        st.subheader("Atașamente (placeholder)")
        st.info("Atașamentele le conectăm după ce confirmi numele tabelelor de componente. (nu schimbăm acum baza).")

if __name__ == "__main__":
    run()
