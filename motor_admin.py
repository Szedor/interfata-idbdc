import streamlit as st
import pandas as pd
from datetime import datetime


def porneste_motorul(supabase):

    # ============================
    # HELPERS
    # ============================

    def now_iso():
        return datetime.now().isoformat()

    def get_table_columns(table_name: str):
        try:
            res = supabase.rpc("idbdc_get_columns", {"p_table": table_name}).execute()
            return [r["column_name"] for r in (res.data or []) if r.get("column_name")]
        except Exception:
            return []

    def empty_row(columns):
        row = {c: None for c in columns}
        if "status_confirmare" in row:
            row["status_confirmare"] = False
        if "validat_idbdc" in row:
            row["validat_idbdc"] = False
        return row

    def load_single_row(table_name: str, cod: str):
        """
        Încarcă rândul pentru cod_identificare.
        Returnează (df, cols_real, exista_bool).
        """
        cols = get_table_columns(table_name)
        if not cols:
            return pd.DataFrame(), [], False

        res = supabase.table(table_name).select("*").eq("cod_identificare", cod).execute()
        data = res.data or []
        df = pd.DataFrame(data)

        if df.empty:
            df = pd.DataFrame(columns=cols)
            return df, cols, False

        # asigură toate coloanele și ordinea
        for c in cols:
            if c not in df.columns:
                df[c] = None
        df = df[cols]

        return df, cols, True

    def prepare_empty_single_row(cols: list, cod: str):
        if not cols:
            return pd.DataFrame()
        r = empty_row(cols)
        if "cod_identificare" in r:
            r["cod_identificare"] = cod
        return pd.DataFrame([r], columns=cols)

    def safe_upsert(table_name: str, df: pd.DataFrame, cols_real: list):
        saved = 0
        for _, row in df.iterrows():
            data = row.to_dict()
            cod = data.get("cod_identificare")

            if not cod or str(cod).strip() == "":
                continue

            payload = {k: v for k, v in data.items() if k in cols_real}

            if "data_ultimei_modificari" in cols_real:
                payload["data_ultimei_modificari"] = now_iso()
            if "observatii_idbdc" in cols_real:
                payload["observatii_idbdc"] = f"Editat de {st.session_state.operator_identificat}"

            supabase.table(table_name).upsert(payload).execute()
            saved += 1

        return saved

    def safe_validate(table_name: str, df: pd.DataFrame, cols_real: list):
        count = 0
        for _, row in df.iterrows():
            cod = row.get("cod_identificare")
            if not cod:
                continue

            payload = {}
            if "status_confirmare" in cols_real:
                payload["status_confirmare"] = True
            if "validat_idbdc" in cols_real:
                payload["validat_idbdc"] = True
            if "data_ultimei_modificari" in cols_real:
                payload["data_ultimei_modificari"] = now_iso()
            if "observatii_idbdc" in cols_real:
                payload["observatii_idbdc"] = f"Validat de {st.session_state.operator_identificat}"

            if payload:
                supabase.table(table_name).update(payload).eq("cod_identificare", cod).execute()
                count += 1

        return count

    # ============================
    # DROPDOWN RELATIONS (st.data_editor)
    # ============================

    # Relațiile conform documentului tău + o regulă STATIC pentru valuta din com_date_financiare.
    # Format: target_table -> { target_column: (source_table, source_column) }
    # Pentru opțiuni fixe: ("__STATIC__", "<key>")
    DROPDOWN_MAP = {
        # Contracte & Proiecte (base_*)
        "base_contracte_cep": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_contracte_proiecte", "acronim_contracte_proiecte"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
        },
        "base_contracte_terti": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_contracte_proiecte", "acronim_contracte_proiecte"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
        },
        "base_proiecte_fdi": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_contracte_proiecte", "acronim_contracte_proiecte"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            "cod_domeniu_fdi": ("nom_domenii_fdi", "cod_domeniu_fdi"),
        },
        "base_proiecte_internationale": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_contracte_proiecte", "acronim_contracte_proiecte"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
        },
        "base_proiecte_interreg": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_contracte_proiecte", "acronim_contracte_proiecte"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
        },
        "base_proiecte_noneu": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_contracte_proiecte", "acronim_contracte_proiecte"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
        },
        "base_proiecte_pncdi": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_contracte_proiecte", "acronim_contracte_proiecte"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
        },
        "base_proiecte_pnrr": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_contracte_proiecte", "acronim_contracte_proiecte"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
        },

        # Evenimente
        "base_evenimente_stiintifice": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "natura_eveniment": ("nom_evenimente_stiintifice", "natura_eveniment"),
            "format_eveniment": ("nom_format_evenimente", "format_eveniment"),
        },

        # Proprietate intelectuală
        "base_prop_intelect": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_prop_intelect": ("nom_prop_intelect", "acronim_prop_intelect"),
        },

        # Echipe proiect
        "com_echipe_proiect": {
            "nume_prenume": ("det_resurse_umane", "nume_prenume"),
            "status_personal": ("nom_status_personal", "status_personal"),
        },

        # Financiar: valuta dropdown fix (LEI/EUR/USD)
        "com_date_financiare": {
            "valuta": ("__STATIC__", "VALUTA_3"),
        },

        # Dacă vei edita vreodată aceste tabele în motor_admin:
        "det_resurse_umane": {
            "acronim_functie_upt": ("nom_functie_upt", "acronim_functie_upt"),
            "acronim_departament": ("nom_departament", "acronim_departament"),
        },
        "det_evaluare_fdi": {
            "cod_universitate": ("nom_universitati", "cod_universitate"),
        },
    }

    STATIC_OPTIONS = {
        "VALUTA_3": ["LEI", "EUR", "USD"],
    }

    @st.cache_data(show_spinner=False, ttl=600)
    def load_dropdown_options(source_table: str, source_col: str):
        """
        Încarcă opțiuni distincte pentru dropdown din tabela sursă.
        Cache 10 minute ca să nu bată DB la fiecare rerun.
        """
        try:
            res = supabase.table(source_table).select(source_col).execute()
            rows = res.data or []
            vals = []
            for r in rows:
                v = r.get(source_col)
                if v is None:
                    continue
                s = str(v).strip()
                if s:
                    vals.append(s)
            return sorted(list(set(vals)))
        except Exception:
            return []

    def build_column_config_for_table(table_name: str, df: pd.DataFrame):
        """
        Construiește column_config pentru st.data_editor, pe baza DROPDOWN_MAP,
        doar pentru coloanele existente în df și doar dacă există opțiuni.
        """
        rel = DROPDOWN_MAP.get(table_name, {})
        cfg = {}

        for target_col, (src_table, src_col) in rel.items():
            if target_col not in df.columns:
                continue

            if src_table == "__STATIC__":
                options = STATIC_OPTIONS.get(src_col, [])
            else:
                options = load_dropdown_options(src_table, src_col)

            if not options:
                continue

            cfg[target_col] = st.column_config.SelectboxColumn(
                label=target_col,
                options=options,
                required=False
            )

        return cfg

    # ============================
    # HEADER
    # ============================

    st.markdown(
        f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.operator_identificat}</h3>",
        unsafe_allow_html=True
    )

    # ============================
    # SELECTOARE
    # ============================

    c1, c2, c3 = st.columns(3)

    with c1:
        cat_admin = st.selectbox(
            "Categoria de date",
            ["", "Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"],
        )

    with c2:
        if cat_admin == "Contracte & Proiecte":
            tip_admin = st.selectbox(
                "Tipul de contracte sau proiecte",
                ["", "CEP", "TERTI", "FDI", "PNRR", "INTERNATIONALE", "INTERREG", "NONEU", "PNCDI"],
            )
        else:
            tip_admin = ""

    with c3:
        id_admin = st.text_input("Filtru numar contract sau id proiect")

    st.divider()

    # ============================
    # MAPARE TABELA BAZA
    # ============================

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
        tabela_baza = map_baze.get(tip_admin)
    elif cat_admin == "Evenimente stiintifice":
        tabela_baza = "base_evenimente_stiintifice"
    elif cat_admin == "Proprietate intelectuala":
        tabela_baza = "base_prop_intelect"
    else:
        tabela_baza = None

    if not tabela_baza:
        st.info("Selectează categoria și (dacă este cazul) tipul.")
        return

    if not id_admin or str(id_admin).strip() == "":
        st.info("Introdu «Filtru numar contract sau id proiect» pentru a deschide fișa.")
        return

    cod = str(id_admin).strip()

    # ============================
    # DROPDOWN ACȚIUNE
    # ============================

    actiune = st.selectbox(
        "Acțiune",
        ["Modificare date existente", "Introducere noutate"],
    )

    st.divider()

    # ============================
    # STRUCTURĂ FIȘĂ (TAB-URI CURATE)
    # ============================

    if cat_admin == "Contracte & Proiecte":
        tabele = [
            ("Date de bază", tabela_baza),
            ("Date financiare", "com_date_financiare"),
            ("Echipa", "com_echipe_proiect"),
            ("Aspecte tehnice", "com_aspecte_tehnice"),
        ]
    else:
        tabele = [
            ("Date de bază", tabela_baza),
            ("Echipa", "com_echipe_proiect"),
        ]

    # ============================
    # ÎNCĂRCARE DATE
    # ============================

    state_key = lambda t: f"df_admin__{t}"
    loaded = {}       # table -> (df, cols_real)
    exists_map = {}   # table -> bool

    for _, table_name in tabele:
        df, cols, exista = load_single_row(table_name, cod)
        loaded[table_name] = (df, cols)
        exists_map[table_name] = exista

    # Există fișa? (criteriu: rând existent în tabela de bază)
    base_exists = exists_map.get(tabela_baza, False)

    # ============================
    # REGULI PE ACȚIUNE
    # ============================

    if actiune == "Modificare date existente":
        if not base_exists:
            st.warning("Nu există fișă pentru acest cod în Date de bază. Alege «Introducere noutate» dacă vrei să creezi.")
            return

        for _, table_name in tabele:
            df, cols = loaded[table_name]
            if df.empty and cols:
                st.session_state[state_key(table_name)] = prepare_empty_single_row(cols, cod)
            else:
                st.session_state[state_key(table_name)] = df.copy()

    else:  # Introducere noutate
        if base_exists:
            st.warning("Fișa există deja pentru acest cod. Se încarcă datele existente (nu se creează dubluri).")

        for _, table_name in tabele:
            df, cols = loaded[table_name]
            if df.empty and cols:
                st.session_state[state_key(table_name)] = prepare_empty_single_row(cols, cod)
            else:
                st.session_state[state_key(table_name)] = df.copy()

    # ============================
    # BUTOANE FIȘĂ
    # ============================

    b1, b2, b3 = st.columns(3)

    with b1:
        btn_save = st.button("💾 SALVARE (toată fișa)")
    with b2:
        btn_validate = st.button("✅ VALIDARE (toată fișa)")
    with b3:
        btn_delete = st.button("🗑️ ȘTERGE FIȘA")

    st.divider()

    # ============================
    # TAB-URI + EDITOR (CU DROPDOWN PE COLOANE)
    # ============================

    tabs = st.tabs([label for label, _ in tabele])
    edited_data = {}

    for i, (label, table_name) in enumerate(tabele):
        with tabs[i]:
            df_show = st.session_state[state_key(table_name)]
            col_cfg = build_column_config_for_table(table_name, df_show)

            edited = st.data_editor(
                df_show,
                use_container_width=True,
                hide_index=True,
                num_rows="fixed",
                column_config=col_cfg
            )
            edited_data[table_name] = edited

    # ============================
    # SALVARE
    # ============================

    if btn_save:
        total = 0
        for _, table_name in tabele:
            df_edit = edited_data[table_name]
            _, cols_real = loaded[table_name]
            total += safe_upsert(table_name, df_edit, cols_real)
            st.session_state[state_key(table_name)] = df_edit.copy()

        st.success(f"Salvare completă ({total} rânduri procesate).")
        st.rerun()

    # ============================
    # VALIDARE
    # ============================

    if btn_validate:
        total = 0
        for _, table_name in tabele:
            df_edit = edited_data[table_name]
            _, cols_real = loaded[table_name]
            total += safe_validate(table_name, df_edit, cols_real)

        st.success(f"Validare realizată ({total} rânduri actualizate).")
        st.rerun()

    # ============================
    # ȘTERGERE FIȘĂ
    # ============================

    if btn_delete:
        for _, table_name in tabele:
            supabase.table(table_name).delete().eq("cod_identificare", cod).execute()
            if state_key(table_name) in st.session_state:
                del st.session_state[state_key(table_name)]

        st.success("Fișa a fost ștearsă din toate tabelele aferente.")
        st.rerun()
