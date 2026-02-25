import streamlit as st
import pandas as pd
from datetime import datetime


def porneste_motorul(supabase):
    # ----------------------------
    # Helpers
    # ----------------------------
    def norm_text(x) -> str:
        if x is None:
            return ""
        s = str(x).strip()
        s = " ".join(s.split())
        return s.casefold()

    def to_int_or_none(x):
        if x is None:
            return None
        try:
            if isinstance(x, bool):
                return None
            if isinstance(x, (int, float)) and not pd.isna(x):
                return int(x)
            s = str(x).strip()
            if s == "":
                return None
            return int(float(s))
        except Exception:
            return None

    def now_iso() -> str:
        return datetime.now().isoformat()

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
    def fetch_map_norm(table_name: str, key_col: str, val_col: str) -> dict:
        try:
            res = supabase.table(table_name).select(f"{key_col},{val_col}").execute()
            m = {}
            for r in (res.data or []):
                k = r.get(key_col)
                v = r.get(val_col)
                nk = norm_text(k)
                if nk == "":
                    continue
                m[nk] = v
            return m
        except Exception:
            return {}

    def merge_with_existing(options: list[str], df: pd.DataFrame, col: str) -> list[str]:
        if df is None or df.empty or col not in df.columns:
            return [""] + options
        existing = df[col].dropna().astype(str).map(lambda x: x.strip()).tolist()
        existing = [x for x in existing if x != ""]
        return list(dict.fromkeys([""] + options + sorted(list(set(existing)))))

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

    # ----------------------------
    # Dropdown options
    # ----------------------------
    opt_categorii = fetch_opt("nom_categorie", "denumire_categorie")
    opt_status_proiect = fetch_opt("nom_status_proiect", "status_contract_proiect")

    opt_natura_eveniment = fetch_opt("nom_evenimente_stiintifice", "natura_eveniment")
    opt_format_eveniment = fetch_opt("nom_format_evenimente", "format_eveniment")

    opt_acronim_pi = fetch_opt("nom_prop_intelect", "acronim_prop_intelect")
    opt_domenii_fdi = fetch_opt("nom_domenii_fdi", "cod_domeniu_fdi")

    # ----------------------------
    # Mapari auto-completare
    # ----------------------------
    map_natura_to_clasificare = fetch_map_norm(
        "nom_evenimente_stiintifice",
        "natura_eveniment",
        "clasificare_eveniment"
    )
    map_pi_to_perioada_ani = fetch_map_norm(
        "nom_prop_intelect",
        "acronim_prop_intelect",
        "perioada_valabilitate_ani"
    )

    # ----------------------------
    # Header
    # ----------------------------
    st.markdown(
        f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.operator_identificat}</h3>",
        unsafe_allow_html=True
    )

    # ----------------------------
    # Casete 1-4
    # ----------------------------
    c1, c2, c3, c4 = st.columns([1, 1.25, 1.25, 1.25])

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
        id_admin = st.text_input("3. ID Proiect / Numar contract:", key="admin_id")

    with c4:
        st.multiselect(
            "4. Componente:",
            ["Date financiare", "Resurse umane", "Aspecte tehnice"],
            key="admin_com"
        )

    st.markdown("---")

    # ----------------------------
    # Mapare tabele base_
    # ----------------------------
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

    # ----------------------------
    # CRUD
    # ----------------------------
    col_n, col_s, col_v, col_d, col_a = st.columns(5)

    with col_n:
        if st.button("➕ RAND NOU"):
            st.session_state["adauga_rand_sus"] = True

    with col_s:
        btn_salvare = st.button("💾 SALVARE")

    with col_v:
        btn_validare = st.button("✅ VALIDARE")

    with col_d:
        st.button("🗑️ ȘTERGERE")

    with col_a:
        if st.button("❌ ANULARE"):
            st.rerun()

    st.caption("Notă: completările ES/PI se aplică la SALVARE. (v12: dropdown stabil din prima selecție)")

    if not nume_tabela:
        st.info("Alege Categoria si Tipul de Contracte sau Proiecte pentru incarcare tabel.")
        return

    # ----------------------------
    # Coloane reale (safe-write)
    # ----------------------------
    cols_real = get_table_columns(nume_tabela)
    cols_set = set(cols_real)

    # ----------------------------
    # Incarcare DF (doar la schimbare de tabel / prima intrare)
    # ----------------------------
    res_main = supabase.table(nume_tabela).select("*")
    if id_admin:
        res_main = res_main.eq("cod_identificare", id_admin)

    df_main = pd.DataFrame(res_main.execute().data or [])
    if df_main.empty:
        df_main = pd.DataFrame(columns=cols_real)

    df_key = f"df_{nume_tabela}"
    if st.session_state.get("current_table") != nume_tabela or df_key not in st.session_state:
        st.session_state["current_table"] = nume_tabela
        st.session_state[df_key] = df_main.copy()

    # Rand nou SUS (modificam doar session_state aici)
    if st.session_state.get("adauga_rand_sus"):
        if cols_real:
            st.session_state[df_key] = pd.concat(
                [pd.DataFrame([empty_row_from_columns(cols_real)]), st.session_state[df_key]],
                ignore_index=True
            )
        st.session_state["adauga_rand_sus"] = False

    df_work = st.session_state[df_key].copy()

    # ----------------------------
    # Dropdown config
    # ----------------------------
    column_config = {}

    if nume_tabela in [
        "base_contracte_cep", "base_contracte_terti",
        "base_proiecte_fdi", "base_proiecte_internationale",
        "base_proiecte_interreg", "base_proiecte_noneu",
        "base_proiecte_pncdi", "base_proiecte_pnrr"
    ]:
        if "denumire_categorie" in df_work.columns:
            column_config["denumire_categorie"] = st.column_config.SelectboxColumn(
                "denumire_categorie",
                options=merge_with_existing(opt_categorii, df_work, "denumire_categorie")
            )
        if "status_contract_proiect" in df_work.columns:
            column_config["status_contract_proiect"] = st.column_config.SelectboxColumn(
                "status_contract_proiect",
                options=merge_with_existing(opt_status_proiect, df_work, "status_contract_proiect")
            )

    if nume_tabela == "base_evenimente_stiintifice":
        if "denumire_categorie" in df_work.columns:
            column_config["denumire_categorie"] = st.column_config.SelectboxColumn(
                "denumire_categorie",
                options=merge_with_existing(opt_categorii, df_work, "denumire_categorie")
            )
        if "natura_eveniment" in df_work.columns:
            column_config["natura_eveniment"] = st.column_config.SelectboxColumn(
                "natura_eveniment",
                options=merge_with_existing(opt_natura_eveniment, df_work, "natura_eveniment")
            )
        if "format_eveniment" in df_work.columns:
            column_config["format_eveniment"] = st.column_config.SelectboxColumn(
                "format_eveniment",
                options=merge_with_existing(opt_format_eveniment, df_work, "format_eveniment")
            )

    if nume_tabela == "base_prop_intelect":
        if "denumire_categorie" in df_work.columns:
            column_config["denumire_categorie"] = st.column_config.SelectboxColumn(
                "denumire_categorie",
                options=merge_with_existing(opt_categorii, df_work, "denumire_categorie")
            )
        if "acronim_prop_intelect" in df_work.columns:
            column_config["acronim_prop_intelect"] = st.column_config.SelectboxColumn(
                "acronim_prop_intelect",
                options=merge_with_existing(opt_acronim_pi, df_work, "acronim_prop_intelect")
            )

    if nume_tabela == "base_proiecte_fdi":
        if "cod_domeniu_fdi" in df_work.columns:
            column_config["cod_domeniu_fdi"] = st.column_config.SelectboxColumn(
                "cod_domeniu_fdi",
                options=merge_with_existing(opt_domenii_fdi, df_work, "cod_domeniu_fdi")
            )

    # ----------------------------
    # Editor (SINGURA sursa de adevar in timpul editarii)
    # ----------------------------
    st.markdown(f"**📂 Tabel Principal: {nume_tabela}**")

    ed_df = st.data_editor(
        df_work,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key=f"ed_{nume_tabela}",
        column_config=column_config if column_config else None,
    )

    # ----------------------------
    # Completari ES/PI (aplicate doar la butoane)
    # ----------------------------
    def aplica_completari(df_in: pd.DataFrame) -> pd.DataFrame:
        df_out = df_in.copy()

        if nume_tabela == "base_evenimente_stiintifice":
            if "natura_eveniment" in df_out.columns and "clasificare_eveniment" in df_out.columns:
                for i in range(len(df_out)):
                    nat = df_out.at[i, "natura_eveniment"]
                    nk = norm_text(nat)
                    if nk == "":
                        continue
                    val = map_natura_to_clasificare.get(nk)
                    if val is None:
                        continue
                    val_i = to_int_or_none(val)
                    df_out.at[i, "clasificare_eveniment"] = val_i if val_i is not None else val

        if nume_tabela == "base_prop_intelect":
            if "acronim_prop_intelect" in df_out.columns and "perioada_valabilitate" in df_out.columns:
                for i in range(len(df_out)):
                    ac = df_out.at[i, "acronim_prop_intelect"]
                    nk = norm_text(ac)
                    if nk == "":
                        continue
                    val = map_pi_to_perioada_ani.get(nk)
                    if val is None:
                        continue
                    val_i = to_int_or_none(val)
                    df_out.at[i, "perioada_valabilitate"] = val_i if val_i is not None else val

        return df_out

    # SALVARE
    if btn_salvare:
        df_to_save = aplica_completari(ed_df)

        # ca sa ramana in grila dupa rerun
        st.session_state[df_key] = df_to_save.copy()

        saved = 0
        for _, r in df_to_save.iterrows():
            v = r.to_dict()
            cod = v.get("cod_identificare")
            if cod is None or str(cod).strip() == "":
                continue

            if "data_ultimei_modificari" in cols_set:
                v["data_ultimei_modificari"] = now_iso()
            if "observatii_idbdc" in cols_set:
                v["observatii_idbdc"] = f"Editat de {st.session_state.operator_identificat}"

            if "status_confirmare" in cols_set and v.get("status_confirmare") is None:
                v["status_confirmare"] = False
            if "validat_idbdc" in cols_set and v.get("validat_idbdc") is None:
                v["validat_idbdc"] = False

            supabase.table(nume_tabela).upsert(v).execute()
            saved += 1

        st.success(f"✅ Salvare reușită. Rânduri salvate: {saved}.")
        st.rerun()

    # VALIDARE (rând cu rând, cu WHERE)
    if btn_validare:
        df_to_val = aplica_completari(ed_df)

        payload_base = {}
        if "status_confirmare" in cols_set:
            payload_base["status_confirmare"] = True
        if "validat_idbdc" in cols_set:
            payload_base["validat_idbdc"] = True
        if "data_ultimei_modificari" in cols_set:
            payload_base["data_ultimei_modificari"] = now_iso()
        if "observatii_idbdc" in cols_set:
            payload_base["observatii_idbdc"] = f"Validat de {st.session_state.operator_identificat}"

        count = 0
        for _, r in df_to_val.iterrows():
            cod = r.get("cod_identificare")
            if cod is None or str(cod).strip() == "":
                continue
            supabase.table(nume_tabela).update(payload_base).eq("cod_identificare", cod).execute()
            count += 1

        # pastram ce e in grila
        st.session_state[df_key] = df_to_val.copy()

        st.success(f"✅ Validare efectuată pentru {count} rând(uri).")
        st.rerun()
