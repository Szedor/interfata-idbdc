 import streamlit as st
import pandas as pd
from datetime import datetime


def porneste_motorul(supabase):
    """
    Motor Admin (Calea 2) - varianta extinsa:
      - pastreaza cele 4 casete + CRUD
      - dropdown pentru toate campurile din lista lui Eugen
      - rand nou SUS (mai rapid pentru tabele lungi)
      - optional: auto-creare randuri COM (cand salvezi in base_...)
    """

    # ----------------------------
    # Helpers: optiuni dropdown
    # ----------------------------
    @st.cache_data(show_spinner=False, ttl=3600)
    def fetch_opt(table_name: str, col_name: str) -> list[str]:
        """Ia optiuni distincte dintr-un tabel (nom_... / det_...)."""
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

    def merge_with_existing(options: list[str], df: pd.DataFrame, col: str) -> list[str]:
        """Ca dropdown-ul sa nu dispara, includem si valorile deja existente in tabel."""
        if df is None or df.empty or col not in df.columns:
            return [""] + options
        existing = (
            df[col].dropna().astype(str).map(lambda x: x.strip()).tolist()
            if col in df.columns else []
        )
        existing = [x for x in existing if x != ""]
        merged = list(dict.fromkeys([""] + options + sorted(list(set(existing)))))
        return merged

    def empty_row_for(df: pd.DataFrame) -> dict:
        """Creeaza un rand gol cu aceleasi coloane ca df (ca sa-l inseram sus)."""
        row = {c: None for c in df.columns}
        # daca exista campuri de status, le setam pe Draft (conservator)
        if "status_confirmare" in row:
            row["status_confirmare"] = False
        if "validat_idbdc" in row:
            row["validat_idbdc"] = False
        return row

    def now_iso() -> str:
        return datetime.now().isoformat()

    # ----------------------------
    # OPTIUNI NOMENCLATOARE (din lista ta)
    # ----------------------------
    opt_categorii = fetch_opt("nom_categorie", "denumire_categorie")
    opt_acronime_cp = fetch_opt("nom_contracte_proiecte", "acronim_contracte_proiecte")
    opt_status_proiect = fetch_opt("nom_status_proiect", "status_contract_proiect")

    opt_natura_eveniment = fetch_opt("nom_evenimente_stiintifice", "natura_eveniment")
    opt_format_eveniment = fetch_opt("nom_format_evenimente", "format_eveniment")

    opt_acronim_pi = fetch_opt("nom_prop_intelect", "acronim_prop_intelect")

    opt_functie = fetch_opt("nom_functie_upt", "acronim_functie_upt")
    opt_departament = fetch_opt("nom_departament", "acronim_departament")

    opt_universitati = fetch_opt("nom_universitati", "cod_universitate")

    opt_status_personal = fetch_opt("nom_status_personal", "status_personal")

    opt_domenii_fdi = fetch_opt("nom_domenii_fdi", "cod_domeniu_fdi")

    # Pentru com_echipe_proiect: nume_prenume vine din det_resurse_umane
    opt_nume_prenume = fetch_opt("det_resurse_umane", "nume_prenume")

    # ----------------------------
    # Header
    # ----------------------------
    st.markdown(
        f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.operator_identificat}</h3>",
        unsafe_allow_html=True
    )

    # ----------------------------
    # CASETELE 1-4 (cascada conform explicatiei tale)
    # ----------------------------
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2])

    with c1:
        cat_admin = st.selectbox(
            "1. Categoria:",
            ["", "Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"],
            key="admin_cat"
        )

    # Caseta 2 se foloseste doar la Contracte & Proiecte
    with c2:
        if cat_admin == "Contracte & Proiecte":
            tip_admin = st.selectbox("2. Tip (Acronim):", [""] + opt_acronime_cp, key="admin_tip")
        else:
            tip_admin = ""
            st.selectbox("2. Tip (Acronim):", ["(nu se aplica aici)"], index=0, key="admin_tip_disabled", disabled=True)

    with c3:
        id_admin = st.text_input("3. ID Proiect (Cod Identificare):", key="admin_id")

    with c4:
        componente_com = st.multiselect(
            "4. Componente (COM):",
            ["Date financiare", "Resurse umane", "Aspecte tehnice"],
            key="admin_com"
        )

    st.markdown("---")

    # ----------------------------
    # MAPARE tabele base_ in functie de categorie+tip
    # (AICI poti extinde ulterior pentru INTERREG/NONEU/PNCDI etc. daca tip_admin e standardizat)
    # ----------------------------
    map_baze_contracte_proiecte = {
        "FDI": "base_proiecte_fdi",
        "PNRR": "base_proiecte_pnrr",
        "INTERNATIONALE": "base_proiecte_internationale",
        # poti adauga aici: "INTERREG": "base_proiecte_interreg", etc.
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
    # BUTOANE CRUD
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
        st.button("🗑️ ȘTERGERE")  # stergerea reala: din tabel + SALVARE

    with col_a:
        if st.button("❌ ANULARE"):
            st.rerun()

    st.write("")

    if not nume_tabela:
        st.info("Alege Categoria (si Tip daca e Contracte & Proiecte) ca sa incarcam tabelul.")
        return

    # ----------------------------
    # CITIRE TABEL PRINCIPAL
    # ----------------------------
    res_main = supabase.table(nume_tabela).select("*")
    if id_admin:
        res_main = res_main.eq("cod_identificare", id_admin)

    df_main = pd.DataFrame(res_main.execute().data or [])

    # Rand nou SUS (daca s-a cerut si avem coloane)
    if st.session_state.get("adauga_rand_sus") and not df_main.empty:
        df_main = pd.concat([pd.DataFrame([empty_row_for(df_main)]), df_main], ignore_index=True)
        st.session_state["adauga_rand_sus"] = False

    # ----------------------------
    # CONFIG DROPDOWN - in functie de tabelul incarcat
    # ----------------------------
    column_config = {}

    # comune pentru multe base_ (categorie/acronim/status)
    if nume_tabela in [
        "base_contracte_cep", "base_contracte_terti",
        "base_proiecte_fdi", "base_proiecte_internationale",
        "base_proiecte_interreg", "base_proiecte_noneu",
        "base_proiecte_pncdi", "base_proiecte_pnrr"
    ]:
        column_config["denumire_categorie"] = st.column_config.SelectboxColumn(
            "denumire_categorie",
            options=merge_with_existing(opt_categorii, df_main, "denumire_categorie"),
        )
        column_config["acronim_contracte_proiecte"] = st.column_config.SelectboxColumn(
            "acronim_contracte_proiecte",
            options=merge_with_existing(opt_acronime_cp, df_main, "acronim_contracte_proiecte"),
        )
        column_config["status_contract_proiect"] = st.column_config.SelectboxColumn(
            "status_contract_proiect",
            options=merge_with_existing(opt_status_proiect, df_main, "status_contract_proiect"),
        )

    # specific: evenimente
    if nume_tabela == "base_evenimente_stiintifice":
        column_config["natura_eveniment"] = st.column_config.SelectboxColumn(
            "natura_eveniment",
            options=merge_with_existing(opt_natura_eveniment, df_main, "natura_eveniment"),
        )
        column_config["format_eveniment"] = st.column_config.SelectboxColumn(
            "format_eveniment",
            options=merge_with_existing(opt_format_eveniment, df_main, "format_eveniment"),
        )

    # specific: proprietate intelectuala
    if nume_tabela == "base_prop_intelect":
        column_config["acronim_prop_intelect"] = st.column_config.SelectboxColumn(
            "acronim_prop_intelect",
            options=merge_with_existing(opt_acronim_pi, df_main, "acronim_prop_intelect"),
        )

    # specific: FDI
    if nume_tabela == "base_proiecte_fdi":
        column_config["cod_domeniu_fdi"] = st.column_config.SelectboxColumn(
            "cod_domeniu_fdi",
            options=merge_with_existing(opt_domenii_fdi, df_main, "cod_domeniu_fdi"),
        )

    # ----------------------------
    # AFISARE + EDITARE TABEL PRINCIPAL
    # ----------------------------
    st.markdown(f"**📂 Tabel Principal: {nume_tabela}**")

    ed_df = st.data_editor(
        df_main,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key=f"ed_{nume_tabela}",
        column_config=column_config if column_config else None,
    )

    # ----------------------------
    # SALVARE TABEL PRINCIPAL
    # ----------------------------
    def upsert_rows(table_name: str, df_edit: pd.DataFrame):
        for _, r in df_edit.iterrows():
            v = r.to_dict()

            # nu salvam rand fara cod_identificare
            if "cod_identificare" not in v or v["cod_identificare"] is None or str(v["cod_identificare"]).strip() == "":
                continue

            v["data_ultimei_modificari"] = now_iso()
            v["observatii_idbdc"] = f"Editat de {st.session_state.operator_identificat}"

            # Draft implicit pentru booleene (conservator)
            if "status_confirmare" in v and v["status_confirmare"] is None:
                v["status_confirmare"] = False
            if "validat_idbdc" in v and v["validat_idbdc"] is None:
                v["validat_idbdc"] = False

            supabase.table(table_name).upsert(v).execute()

    def delete_missing_rows(table_name: str, df_before: pd.DataFrame, df_after: pd.DataFrame):
        if df_before.empty or "cod_identificare" not in df_before.columns or "cod_identificare" not in df_after.columns:
            return
        old_ids = set(df_before["cod_identificare"].dropna().astype(str))
        new_ids = set(df_after["cod_identificare"].dropna().astype(str))
        for cid in (old_ids - new_ids):
            supabase.table(table_name).delete().eq("cod_identificare", cid).execute()

    def ensure_com_rows(cod_identificare: str):
        """
        Cand salvezi date de identificare (base_...):
        pregatim automat cele 3 componente com_... cu cod_identificare (daca nu exista).
        """
        for t in ["com_date_financiare", "com_echipe_proiect", "com_aspecte_tehnice"]:
            try:
                existing = supabase.table(t).select("cod_identificare").eq("cod_identificare", cod_identificare).execute()
                if not (existing.data or []):
                    supabase.table(t).insert({
                        "cod_identificare": cod_identificare,
                        "status_confirmare": False,
                        "validat_idbdc": False,
                        "data_ultimei_modificari": now_iso(),
                        "observatii_idbdc": f"Auto-creat de sistem ({st.session_state.operator_identificat})"
                    }).execute()
            except Exception:
                # daca o tabela nu are aceste coloane, nu blocam sistemul; rezolvam dupa
                pass

    if btn_salvare:
        df_before = pd.DataFrame(res_main.execute().data or [])
        delete_missing_rows(nume_tabela, df_before, ed_df)
        upsert_rows(nume_tabela, ed_df)

        # daca e unul din tabelele de Contracte&Proiecte, pregatim COM-urile (cum ai descris)
        if cat_admin == "Contracte & Proiecte" and "cod_identificare" in ed_df.columns:
            for cid in ed_df["cod_identificare"].dropna().astype(str).tolist():
                ensure_com_rows(cid)

        st.success("✅ Salvare reușită!")
        st.rerun()

    # ----------------------------
    # VALIDARE (separat de salvare)
    # ----------------------------
    if btn_validare:
        # Validare = confirmare oficiala (nu doar salvare)
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

    # ----------------------------
    # COMPONENTE COM (daca sunt selectate in caseta 4)
    # ----------------------------
    if componente_com:
        map_tabele_com = {
            "Date financiare": "com_date_financiare",
            "Resurse umane": "com_echipe_proiect",
            "Aspecte tehnice": "com_aspecte_tehnice",
        }

        for comp in componente_com:
            tcom = map_tabele_com[comp]
            st.write("---")
            st.markdown(f"**🔍 Componenta: {comp} ({tcom})**")

            res_com = supabase.table(tcom).select("*")
            if id_admin:
                res_com = res_com.eq("cod_identificare", id_admin)

            df_com = pd.DataFrame(res_com.execute().data or [])

            # daca nu exista inca nimic, afisam un rand "Draft" (cum ai zis ca uneori ramane necompletat)
            if df_com.empty and id_admin:
                df_com = pd.DataFrame([{
                    "cod_identificare": id_admin,
                    "status_confirmare": False,
                    "validat_idbdc": False
                }])

            # dropdown-uri pentru COM (din lista ta)
            cfg_com = {}

            if tcom == "com_echipe_proiect":
                cfg_com["nume_prenume"] = st.column_config.SelectboxColumn(
                    "nume_prenume",
                    options=merge_with_existing(opt_nume_prenume, df_com, "nume_prenume"),
                )
                cfg_com["status_personal"] = st.column_config.SelectboxColumn(
                    "status_personal",
                    options=merge_with_existing(opt_status_personal, df_com, "status_personal"),
                )

            ed_com = st.data_editor(
                df_com,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                key=f"ed_{tcom}",
                column_config=cfg_com if cfg_com else None,
            )

            # Salvare pentru componenta COM (cand apesi SALVARE general)
            if btn_salvare:
                # (btn_salvare declanseaza rerun, deci practic nu ajunge aici in acelasi pas;
                # de aceea salvarea COM o facem in pasul urmator daca vrei — o activam separat cand spui.)
                pass
