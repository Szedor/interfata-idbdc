import streamlit as st
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

def pick_title(r: dict) -> str:
    for k in ["titlu_proiect", "titlu", "obiect_contract", "denumire_proiect"]:
        if r.get(k):
            return str(r.get(k)).strip()
    return "—"

def run():
    st.set_page_config(page_title="IDBDC – Explorator (C)", layout="wide")
    gate()

    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.title("🧾 Explorator IDBDC — Varianta C (Carduri)")
    st.caption("Căutare + rezultate ca listă de carduri cu expandere.")
    st.divider()

    tipuri = st.multiselect("Tipuri", list(BASE_TABLES.keys()), default=["CEP"])
    q_text = st.text_input("Căutare text (ID/acronim/titlu)")

    if not st.button("🔎 Caută", use_container_width=True):
        st.stop()

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

    if not rows_all:
        st.info("Niciun rezultat.")
        return

    # filtrare locală
    t = q_text.strip().casefold()
    if t:
        filtered = []
        for r in rows_all:
            blob = " ".join([str(r.get(k, "")) for k in ["cod_identificare","acronim_proiect","titlu_proiect","obiect_contract","denumire_proiect"]]).casefold()
            if t in blob:
                filtered.append(r)
        rows_all = filtered

    st.subheader(f"Rezultate ({len(rows_all)})")

    for r in rows_all:
        cod = str(r.get("cod_identificare", "")).strip() or "(fără cod)"
        tip = r.get("_tip", "")
        title = pick_title(r)
        header = f"🆔 {cod} | {title} ({tip})"

        with st.expander(header, expanded=False):
            st.caption(f"Sursă: {r.get('_table','')}")
            for k, v in sorted(r.items()):
                if k.startswith("_"):
                    continue
                if v is None or str(v).strip() == "":
                    continue
                st.write(f"**{k}**: {v}")

            st.divider()
            st.info("Atașamentele le conectăm după ce confirmi tabelele exacte ale componentelor.")

if __name__ == "__main__":
    run()
