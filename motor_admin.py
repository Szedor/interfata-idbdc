import streamlit as st
import pandas as pd
from datetime import datetime


def porneste_motorul(supabase):

    @st.cache_data(show_spinner=False, ttl=3600)
    def fetch_opt(table_name: str, col_name: str) -> list[str]:
        try:
            res = supabase.table(table_name).select(col_name).execute()
            vals = []
            for r in (res.data or []):
                v = r.get(col_name)
                if v is None:
                    continue
                v = str(v).strip()
                if v:
                    vals.append(v)
            return sorted(list(set(vals)))
        except Exception:
            return []

    @st.cache_data(show_spinner=False, ttl=3600)
    def fetch_map(table_name: str, key_col: str, val_col: str) -> dict:
        try:
            res = supabase.table(table_name).select(f"{key_col},{val_col}").execute()
            m = {}
            for r in (res.data or []):
                k = r.get(key_col)
                v = r.get(val_col)
                if k is None:
                    continue
                m[str(k).strip()] = v
            return m
        except Exception:
            return {}

    def now_iso():
        return datetime.now().isoformat()

    def get_table_columns(table_name: str):
        try:
            res = supabase.rpc("idbdc_get_columns", {"p_table": table_name}).execute()
            return [r["column_name"] for r in (res.data or [])]
        except Exception:
            return []

    # -----------------------------
    # MAPARI PENTRU AUTO-COMPLETARE
    # -----------------------------
    map_natura_to_clasificare = fetch_map(
        "nom_evenimente_stiintifice",
        "natura_eveniment",
        "clasificare_eveniment"
    )

    map_pi_to_perioada = fetch_map(
        "nom_prop_intelect",
        "acronim_prop_intelect",
        "perioada_valabilitate_ani"
    )

    # -----------------------------
    # SELECTII CASETE
    # -----------------------------
    st.markdown(
        f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.operator_identificat}</h3>",
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns([1, 1.2, 1.2, 1.2])

    with c1:
        cat_admin = st.selectbox(
            "1. Categoria:",
            ["", "Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"]
        )

    with c2:
        if cat_admin == "Contracte & Proiecte":
            tip_admin = st.selectbox(
                "2. Tipul de Contracte sau Proiecte:",
                ["", "CEP", "TERTI", "FDI", "PNRR", "INTERNATIONALE", "INTERREG", "NONEU", "PNCDI"]
            )
        else:
            tip_admin = ""

    with c3:
        id_admin = st.text_input("3. ID Proiect / Numar contract:")

    with c4:
        componente_com = st.multiselect(
            "4. Componente:",
            ["Date financiare", "Resurse umane", "Aspecte tehnice"]
        )

    st.markdown("---")

    # -----------------------------
    # MAPARE TABELE
    # -----------------------------
    map_baze = {
        "CEP": "base_contracte_cep",
        "TERTI": "base_contracte_terti",
        "FDI": "base_proiecte_fdi",
        "PNRR": "base_proiecte_pnrr",
        "INTERNATIONALE": "base_proiecte_internationale",
        "INTERREG": "base_proiecte_interreg",
        "NONEU": "base_proiecte_noneu",
        "PNCDI": "base_proiecte_pncdi",
    }

    if cat_admin == "Contracte & Proiecte":
        nume_tabela = map_baze.get(tip_admin)
    elif cat_admin == "Evenimente stiintifice":
        nume_tabela = "base_evenimente_stiintifice"
    elif cat_admin == "Proprietate intelectuala":
        nume_tabela = "base_prop_intelect"
    else:
        nume_tabela = None

    if not nume_tabela:
        st.info("Alege Categoria si Tipul de Contracte sau Proiecte pentru incarcare tabel.")
        return

    # -----------------------------
    # CITIRE TABEL
    # -----------------------------
    res = supabase.table(nume_tabela).select("*")
    if id_admin:
        res = res.eq("cod_identificare", id_admin)

    df = pd.DataFrame(res.execute().data or [])

    if df.empty:
        cols = get_table_columns(nume_tabela)
        df = pd.DataFrame(columns=cols)

    # -----------------------------
    # AUTO-COMPLETARE INAINTE DE EDITOR
    # -----------------------------
    if nume_tabela == "base_evenimente_stiintifice":
        if "natura_eveniment" in df.columns and "clasificare_eveniment" in df.columns:
            for i in range(len(df)):
                nat = df.at[i, "natura_eveniment"]
                if pd.notna(nat):
                    df.at[i, "clasificare_eveniment"] = map_natura_to_clasificare.get(str(nat).strip())

    if nume_tabela == "base_prop_intelect":
        if "acronim_prop_intelect" in df.columns and "perioada_valabilitate" in df.columns:
            for i in range(len(df)):
                ac = df.at[i, "acronim_prop_intelect"]
                if pd.notna(ac):
                    df.at[i, "perioada_valabilitate"] = map_pi_to_perioada.get(str(ac).strip())

    # -----------------------------
    # EDITOR
    # -----------------------------
    ed_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic"
    )

    # -----------------------------
    # SALVARE
    # -----------------------------
    if st.button("💾 SALVARE"):
        for _, r in ed_df.iterrows():
            v = r.to_dict()
            if "cod_identificare" not in v or not v["cod_identificare"]:
                continue
            v["data_ultimei_modificari"] = now_iso()
            supabase.table(nume_tabela).upsert(v).execute()

        st.success("Salvare reușită.")
        st.rerun()
