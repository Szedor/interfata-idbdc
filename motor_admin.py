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
            # pregătim doar structura, fără a crea rând
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
    # MAPARE RAND 1
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
    # DROPDOWN ACȚIUNE (MODIFICARE / NOUTATE)
    # ============================

    actiune = st.selectbox(
        "Acțiune",
        ["Modificare date existente", "Introducere noutate"],
    )

    st.divider()

    # ============================
    # STRUCTURĂ FIȘĂ (TAB-URI FĂRĂ i), ii) etc.)
    # ============================

    if cat_admin == "Contracte & Proiecte":
        tabele = [
            ("Date de bază", tabela_baza),
            ("Date financiare", "com_date_financiare"),
            ("Echipa", "com_echipe_proiect"),
            ("Aspecte tehnice", "com_aspecte_tehnice"),
        ]
    else:
        # Evenimente + PI: doar Bază + Echipa
        tabele = [
            ("Date de bază", tabela_baza),
            ("Echipa", "com_echipe_proiect"),
        ]

    # ============================
    # ÎNCĂRCARE DATE (fără auto-creare implicită)
    # ============================

    state_key = lambda t: f"df_admin__{t}"
    loaded = {}       # table -> (df, cols)
    exists_map = {}   # table -> bool

    for label, table_name in tabele:
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

        # încărcăm exact ce există; pentru tabele lipsă, afișăm rând gol (doar pentru completare),
        # dar NU îl băgăm automat în DB decât când apasă SALVARE.
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
    # TAB-URI + EDITOR
    # ============================

    tabs = st.tabs([label for label, _ in tabele])
    edited_data = {}

    for i, (label, table_name) in enumerate(tabele):
        with tabs[i]:
            edited = st.data_editor(
                st.session_state[state_key(table_name)],
                use_container_width=True,
                hide_index=True,
                num_rows="fixed"
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
