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
        """
        Intoarce un dictionar: key_col -> val_col
        Ex: natura_eveniment -> clasificare_eveniment
        """
        try:
            res = supabase.table(table_name).select(f"{key_col},{val_col}").execute()
            m = {}
            for r in (res.data or []):
                k = r.get(key_col)
                v = r.get(val_col)
                if k is None or str(k).strip() == "":
                    continue
                m[str(k).strip()] = v
            return m
        except Exception:
            return {}

    def merge_with_existing(options: list[str], df: pd.DataFrame, col: str) -> list[str]:
        if df is None or df.empty or col not in df.columns:
            return [""] + options
        existing = df[col].dropna().astype(str).map(lambda x: x.strip()).tolist()
        existing = [x for x in existing if x != ""]
        merged = list(dict.fromkeys([""] + options + sorted(list(set(existing)))))
        return merged

    def now_iso() -> str:
        return datetime.now().isoformat()

    def get_table_columns(table_name: str) -> list[str]:
        try:
            res = supabase.rpc("idbdc_get_columns", {"p_table": table_name}).execute()
            return [r["column_name"] for r in (res.data or []) if r.get("column_name")]
        except Exception:
            return []

    def empty_row_from_columns(columns: list[str]) -> dict:
        row = {c: None for c in columns}
        if "status_confirmare" in row:
            row["status_confirmare"] = False
        if "validat_idbdc" in row:
            row["validat_idbdc"] = False
        return row

    # -------- options
    opt_categorii = fetch_opt("nom_categorie", "denumire_categorie")
    opt_status_proiect = fetch_opt("nom_status_proiect", "status_contract_proiect")

    opt_natura_eveniment = fetch_opt("nom_evenimente_stiintifice", "natura_eveniment")
    opt_format_eveniment = fetch_opt("nom_format_evenimente", "format_eveniment")

    opt_acronim_pi = fetch_opt("nom_prop_intelect", "acronim_prop_intelect")

    opt_domenii_fdi = fetch_opt("nom_domenii_fdi", "cod_domeniu_fdi")

    # -------- mape (automatizari)
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

    # -------- header
    st.markdown(
        f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.operator_identificat}</h3>",
        unsafe_allow_html=True
    )

    # -------- casete 1-4 (cu denumiri cerute de tine)
    c1, c2, c3, c4 = st.columns([1, 1.2, 1.2, 1.2])

    with c1:
        cat_admin = st.selectbox(
            "1. Categoria:",
            ["", "Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"],
            key="admin_cat"
        )

    with c2:
        if cat_admin == "Contracte & Proiecte":
            tip_admin = st.selectbox(
                "2. Tipul de Contracte sau Proiecte:",
                ["", "CEP", "TERTI", "FDI", "PNRR", "INTERNATIONALE", "INTERREG", "NONEU", "PNCDI"],
                key="admin_tip"
            )
        else:
            tip_admin = ""
            st.selectbox(
                "2. Tipul de Contracte sau Proiecte:",
                ["(nu se aplica aici)"],
                index=0,
                key="admin_tip_disabled",
                disabled=True
            )

    with c3:
        id_admin = st.text_input(
            "3. ID Proiect / Numar contract:",
            key="admin_id"
        )

    with c4:
        componente_com = st.multiselect(
            "4. Componente:",
            ["Date financiare", "Resurse umane", "Aspecte tehnice"],
            key="admin_com"
        )

    st.markdown("---")

    # -------- mapare base_
    map_baze_contracte_proiecte = {
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
        nume_tabela = map_baze_contracte_proiecte.get(tip_admin)
    elif cat_admin == "Evenimente stiintifice":
        nume_tabela = "base_evenimente_stiintifice"
    elif cat_admin == "Proprietate intelectuala":
        nume_tabela = "base_prop_intelect"
    else:
        nume_tabela = None

    # -------- CRUD
    col_n, col_s, col_v, col_d, col_a = st.columns(5)

    with col_n:
        if st.button("➕ RAND NOU"):
            st.session_state["adauga_rand_sus"] = True
            st.rerun()

    with col_s:
        btn_salvare = st.button("💾 SALVARE")

    with col_v:
        btn_validare = st.button("✅ VALIDARE")

    with col_d:
        st.button("🗑️ ȘTERGERE")

    with col_a:
        if st.button("❌ ANULARE"):
            st.rerun()

    st.write("")

    if not nume_tabela:
        st.info("Alege Categoria si Tipul de Contracte sau Proiecte pentru incarcare tabel.")
        return

    # -------- citire tabela
    res_main = supabase.table(nume_tabela).select("*")
    if id_admin:
        res_main = res_main.eq("cod_identificare", id_admin)

    data = res_main.execute().data or []
    df_main = pd.DataFrame(data)

    if df_main.empty:
        cols = get_table_columns(nume_tabela)
        df_main = pd.DataFrame(columns=cols)

    if st.session_state.get("adauga_rand_sus"):
        cols = list(df_main.columns)
        if cols:
            df_main = pd.concat([pd.DataFrame([empty_row_from_columns(cols)]), df_main], ignore_index=True)
        st.session_state["adauga_rand_sus"] = False

    # -------- dropdown config
    column_config = {}

    # contracte/proiecte
    if nume_tabela in [
        "base_contracte_cep", "base_contracte_terti",
        "base_proiecte_fdi", "base_proiecte_internationale",
        "base_proiecte_interreg", "base_proiecte_noneu",
        "base_proiecte_pncdi", "base_proiecte_pnrr"
    ]:
        if "denumire_categorie" in df_main.columns:
            column_config["denumire_categorie"] = st.column_config.SelectboxColumn(
                "denumire_categorie", options=merge_with_existing(opt_categorii, df_main, "denumire_categorie")
            )
        if "status_contract_proiect" in df_main.columns:
            column_config["status_contract_proiect"] = st.column_config.SelectboxColumn(
                "status_contract_proiect", options=merge_with_existing(opt_status_proiect, df_main, "status_contract_proiect")
            )

    # evenimente + auto-completare
    if nume_tabela == "base_evenimente_stiintifice":
        if "denumire_categorie" in df_main.columns:
            column_config["denumire_categorie"] = st.column_config.SelectboxColumn(
                "denumire_categorie", options=merge_with_existing(opt_categorii, df_main, "denumire_categorie")
            )
        if "natura_eveniment" in df_main.columns:
            column_config["natura_eveniment"] = st.column_config.SelectboxColumn(
                "natura_eveniment", options=merge_with_existing(opt_natura_eveniment, df_main, "natura_eveniment")
            )
        if "format_eveniment" in df_main.columns:
            column_config["format_eveniment"] = st.column_config.SelectboxColumn(
                "format_eveniment", options=merge_with_existing(opt_format_eveniment, df_main, "format_eveniment")
            )

    # PI + auto-completare
    if nume_tabela == "base_prop_intelect":
        if "denumire_categorie" in df_main.columns:
            column_config["denumire_categorie"] = st.column_config.SelectboxColumn(
                "denumire_categorie", options=merge_with_existing(opt_categorii, df_main, "denumire_categorie")
            )
        if "acronim_prop_intelect" in df_main.columns:
            column_config["acronim_prop_intelect"] = st.column_config.SelectboxColumn(
                "acronim_prop_intelect", options=merge_with_existing(opt_acronim_pi, df_main, "acronim_prop_intelect")
            )

    # FDI
    if nume_tabela == "base_proiecte_fdi":
        if "cod_domeniu_fdi" in df_main.columns:
            column_config["cod_domeniu_fdi"] = st.column_config.SelectboxColumn(
                "cod_domeniu_fdi", options=merge_with_existing(opt_domenii_fdi, df_main, "cod_domeniu_fdi")
            )

    # -------- editor
    st.markdown(f"**📂 Tabel Principal: {nume_tabela}**")

    ed_df = st.data_editor(
        df_main,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key=f"ed_{nume_tabela}",
        column_config=column_config if column_config else None,
    )

    # -------- AUTO-COMPLETARE (inainte de SALVARE)
    # Evenimente: natura_eveniment -> clasificare_eveniment
    if nume_tabela == "base_evenimente_stiintifice":
        if "natura_eveniment" in ed_df.columns and "clasificare_eveniment" in ed_df.columns:
            # completam pentru fiecare rand unde natura e aleasa
            for i in range(len(ed_df)):
                nat = ed_df.at[i, "natura_eveniment"]
                if pd.isna(nat) or str(nat).strip() == "":
                    continue
                nat_key = str(nat).strip()
                clas = map_natura_to_clasificare.get(nat_key)
                # completam doar daca e gol (nu suprascriem ce a scris operatorul)
                if (pd.isna(ed_df.at[i, "clasificare_eveniment"]) or str(ed_df.at[i, "clasificare_eveniment"]).strip() == "") and (clas is not None):
                    ed_df.at[i, "clasificare_eveniment"] = clas

    # PI: acronim_prop_intelect -> perioada_valabilitate_ani
    if nume_tabela == "base_prop_intelect":
        if "acronim_prop_intelect" in ed_df.columns and "perioada_valabilitate_ani" in ed_df.columns:
            for i in range(len(ed_df)):
                ac = ed_df.at[i, "acronim_prop_intelect"]
                if pd.isna(ac) or str(ac).strip() == "":
                    continue
                ac_key = str(ac).strip()
                per = map_pi_to_perioada.get(ac_key)
                if (pd.isna(ed_df.at[i, "perioada_valabilitate_ani"]) or str(ed_df.at[i, "perioada_valabilitate_ani"]).strip() == "") and (per is not None):
                    ed_df.at[i, "perioada_valabilitate_ani"] = per

    # -------- salvare
    if btn_salvare:
        saved = 0
        for _, r in ed_df.iterrows():
            v = r.to_dict()
            if "cod_identificare" not in v or v["cod_identificare"] is None or str(v["cod_identificare"]).strip() == "":
                continue
            v["data_ultimei_modificari"] = now_iso()
            v["observatii_idbdc"] = f"Editat de {st.session_state.operator_identificat}"

            if "status_confirmare" in v and v["status_confirmare"] is None:
                v["status_confirmare"] = False
            if "validat_idbdc" in v and v["validat_idbdc"] is None:
                v["validat_idbdc"] = False

            supabase.table(nume_tabela).upsert(v).execute()
            saved += 1

        st.success(f"✅ Salvare reușită. Rânduri salvate: {saved}.")
        st.rerun()

    # -------- validare
    if btn_validare:
        q = supabase.table(nume_tabela).update({
            "status_confirmare": True,
            "validat_idbdc": True,
            "data_ultimei_modificari": now_iso(),
            "observatii_idbdc": f"Validat de {st.session_state.operator_identificat}",
        })
        if id_admin:
            q = q.eq("cod_identificare", id_admin)
        q.execute()
        st.success("✅ Validare efectuată (pentru ce este afișat / filtrat).")
        st.rerun()
