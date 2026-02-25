import streamlit as st
import pandas as pd
from datetime import datetime


def porneste_motorul(supabase):
    # ----------------------------
    # Helpers (simple + robuste)
    # ----------------------------
    def norm_text(x) -> str:
        """Normalizeaza text: strip, spatii multiple -> 1 spatiu, case-insensitive."""
        if x is None:
            return ""
        s = str(x).strip()
        s = " ".join(s.split())
        return s.casefold()

    def to_int_or_none(x):
        """Conversie toleranta la int (pentru comparatii), altfel None."""
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
        """Lista distincta de valori pentru dropdown."""
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
        """
        Mapare robusta: normalizeaza cheia.
        Exemplu: natura_eveniment -> clasificare_eveniment
        """
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
        """
        Dropdown robust: include si valorile deja existente in tabel,
        ca sa nu dispara daca nu sunt in nomenclator.
        """
        if df is None or df.empty or col not in df.columns:
            return [""] + options
        existing = df[col].dropna().astype(str).map(lambda x: x.strip()).tolist()
        existing = [x for x in existing if x != ""]
        return list(dict.fromkeys([""] + options + sorted(list(set(existing)))))

    def get_table_columns(table_name: str) -> list[str]:
        """Ia coloanele tabelului chiar daca nu are randuri (folosind functia SQL deja creata)."""
        try:
            res = supabase.rpc("idbdc_get_columns", {"p_table": table_name}).execute()
            return [r["column_name"] for r in (res.data or []) if r.get("column_name")]
        except Exception:
            return []

    def empty_row_from_columns(columns: list[str]) -> dict:
        """Rand gol (cu booleene implicit False daca exista)."""
        row = {c: None for c in columns}
        if "status_confirmare" in row:
            row["status_confirmare"] = False
        if "validat_idbdc" in row:
            row["validat_idbdc"] = False
        return row

    # ----------------------------
    # Dropdown options (nomenclatoare)
    # ----------------------------
    opt_categorii = fetch_opt("nom_categorie", "denumire_categorie")
    opt_status_proiect = fetch_opt("nom_status_proiect", "status_contract_proiect")

    opt_natura_eveniment = fetch_opt("nom_evenimente_stiintifice", "natura_eveniment")
    opt_format_eveniment = fetch_opt("nom_format_evenimente", "format_eveniment")

    opt_acronim_pi = fetch_opt("nom_prop_intelect", "acronim_prop_intelect")

    opt_domenii_fdi = fetch_opt("nom_domenii_fdi", "cod_domeniu_fdi")

    # ----------------------------
    # Mapari pentru auto-completare
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
    # CASETE 1-4 (denumiri finale)
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
    # CRUD (Rand nou sus)
    # ----------------------------
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
        st.button("🗑️ ȘTERGERE")  # se sterge din tabelul editat + SALVARE

    with col_a:
        if st.button("❌ ANULARE"):
            st.rerun()

    st.write("")

    if not nume_tabela:
        st.info("Alege Categoria si Tipul de Contracte sau Proiecte pentru incarcare tabel.")
        return

    # ----------------------------
    # Incarcare DF (si coloane daca tabela e goala)
    # ----------------------------
    res_main = supabase.table(nume_tabela).select("*")
    if id_admin:
        res_main = res_main.eq("cod_identificare", id_admin)

    df_main = pd.DataFrame(res_main.execute().data or [])
    if df_main.empty:
        cols = get_table_columns(nume_tabela)
        df_main = pd.DataFrame(columns=cols)

    # Session-state DF (ca auto-completarea sa fie vizibila imediat)
    df_key = f"df_{nume_tabela}"
    if st.session_state.get("current_table") != nume_tabela or df_key not in st.session_state:
        st.session_state["current_table"] = nume_tabela
        st.session_state[df_key] = df_main.copy()

    # Rand nou SUS (nu mai derulezi pana la final)
    if st.session_state.get("adauga_rand_sus"):
        cols = list(st.session_state[df_key].columns)
        if cols:
            st.session_state[df_key] = pd.concat(
                [pd.DataFrame([empty_row_from_columns(cols)]), st.session_state[df_key]],
                ignore_index=True
            )
        st.session_state["adauga_rand_sus"] = False

    df_work = st.session_state[df_key].copy()

    # ----------------------------
    # Dropdown config
    # ----------------------------
    column_config = {}

    # 1) Contracte / Proiecte
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

    # 2) Evenimente stiintifice
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

    # 3) Proprietate intelectuala
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

    # 4) FDI
    if nume_tabela == "base_proiecte_fdi":
        if "cod_domeniu_fdi" in df_work.columns:
            column_config["cod_domeniu_fdi"] = st.column_config.SelectboxColumn(
                "cod_domeniu_fdi",
                options=merge_with_existing(opt_domenii_fdi, df_work, "cod_domeniu_fdi")
            )

    # ----------------------------
    # Editor
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
    # Auto-completare REACTIVA (cu suprascriere a default-ului 1)
    # ----------------------------
    changed = False
    df_auto = ed_df.copy()

    # A) Evenimente: natura_eveniment -> clasificare_eveniment
    if nume_tabela == "base_evenimente_stiintifice":
        if "natura_eveniment" in df_auto.columns and "clasificare_eveniment" in df_auto.columns:
            for i in range(len(df_auto)):
                nat = df_auto.at[i, "natura_eveniment"]
                nk = norm_text(nat)
                if nk == "":
                    continue

                val = map_natura_to_clasificare.get(nk)
                if val is None:
                    continue

                cur = df_auto.at[i, "clasificare_eveniment"]

                # daca sunt numerice, comparam numeric
                cur_i = to_int_or_none(cur)
                val_i = to_int_or_none(val)

                if val_i is not None:
                    # IMPORTANT: suprascriem si daca era 1 default
                    if cur_i != val_i:
                        df_auto.at[i, "clasificare_eveniment"] = val_i
                        changed = True
                else:
                    # fallback text
                    if norm_text(cur) != norm_text(val):
                        df_auto.at[i, "clasificare_eveniment"] = val
                        changed = True

    # B) PI: acronim_prop_intelect -> perioada_valabilitate (in base)
    if nume_tabela == "base_prop_intelect":
        if "acronim_prop_intelect" in df_auto.columns and "perioada_valabilitate" in df_auto.columns:
            for i in range(len(df_auto)):
                ac = df_auto.at[i, "acronim_prop_intelect"]
                nk = norm_text(ac)
                if nk == "":
                    continue

                val = map_pi_to_perioada_ani.get(nk)
                if val is None:
                    continue

                cur = df_auto.at[i, "perioada_valabilitate"]

                cur_i = to_int_or_none(cur)
                val_i = to_int_or_none(val)

                if val_i is not None:
                    if cur_i != val_i:
                        df_auto.at[i, "perioada_valabilitate"] = val_i
                        changed = True
                else:
                    if norm_text(cur) != norm_text(val):
                        df_auto.at[i, "perioada_valabilitate"] = val
                        changed = True

    # Persistam DF in session_state si rerun daca am auto-completari noi
    if changed:
        st.session_state[df_key] = df_auto
        st.rerun()
    else:
        st.session_state[df_key] = df_auto

    # ----------------------------
    # SALVARE
    # ----------------------------
    if btn_salvare:
        saved = 0
        for _, r in st.session_state[df_key].iterrows():
            v = r.to_dict()

            # Nu salvam rand fara cheie
            if "cod_identificare" not in v or v["cod_identificare"] is None or str(v["cod_identificare"]).strip() == "":
                continue

            v["data_ultimei_modificari"] = now_iso()
            v["observatii_idbdc"] = f"Editat de {st.session_state.operator_identificat}"

            # booleene implicite
            if "status_confirmare" in v and v["status_confirmare"] is None:
                v["status_confirmare"] = False
            if "validat_idbdc" in v and v["validat_idbdc"] is None:
                v["validat_idbdc"] = False

            supabase.table(nume_tabela).upsert(v).execute()
            saved += 1

        st.success(f"✅ Salvare reușită. Rânduri salvate: {saved}.")
        st.rerun()

    # ----------------------------
    # VALIDARE (marcheaza validate ce este filtrat/afisat)
    # ----------------------------
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
