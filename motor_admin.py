import streamlit as st
import pandas as pd
from datetime import datetime


def porneste_motorul(supabase):

    # ============================
    # CONFIG
    # ============================
    CONTROL_COLS = [
        "responsabil_idbdc",
        "observatii_idbdc",
        "status_confirmare",
        "data_ultimei_modificari",
        "validat_idbdc",
    ]

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
        cols = get_table_columns(table_name)
        if not cols:
            return pd.DataFrame(), [], False

        res = supabase.table(table_name).select("*").eq("cod_identificare", cod).execute()
        data = res.data or []
        df = pd.DataFrame(data)

        if df.empty:
            df = pd.DataFrame(columns=cols)
            return df, cols, False

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

    def append_observatii(existing: str, msg: str) -> str:
        base = (existing or "").strip()
        if not base:
            return msg
        return base + "\n" + msg

    def hide_control_cols(df: pd.DataFrame) -> pd.DataFrame:
        cols = [c for c in df.columns if c not in CONTROL_COLS]
        return df[cols] if cols else df

    def merge_back_control_cols(df_edited: pd.DataFrame, df_original: pd.DataFrame) -> pd.DataFrame:
        out = df_edited.copy()

        for c in CONTROL_COLS:
            if c in df_original.columns:
                if c not in out.columns:
                    out[c] = None
                try:
                    out[c] = list(df_original[c]) + [None] * max(0, (len(out) - len(df_original)))
                except Exception:
                    out[c] = df_original[c].iloc[0] if len(df_original) else None

        for c in df_original.columns:
            if c not in out.columns:
                out[c] = df_original[c]

        try:
            out = out[df_original.columns]
        except Exception:
            pass

        return out

    def fmt_bool(v):
        return "DA" if bool(v) else "NU"

    def is_row_effectively_empty(d: dict) -> bool:
        for k, v in d.items():
            if k in ("cod_identificare", "id_tehnic"):
                continue
            if v is None:
                continue
            if isinstance(v, str) and v.strip() == "":
                continue
            return False
        return True

    def cleanup_payload(payload: dict) -> dict:
        out = {}
        for k, v in (payload or {}).items():
            if k == "id_tehnic":
                if v is None:
                    continue
                if isinstance(v, str) and v.strip() == "":
                    continue
                out[k] = v
                continue

            if v is None:
                continue
            if isinstance(v, str) and v.strip() == "":
                continue

            out[k] = v
        return out

    def direct_upsert_single_row(table_name: str, payload: dict, cod: str):
        try:
            supabase.table(table_name).upsert(payload, on_conflict="cod_identificare").execute()
            return
        except Exception:
            pass

        try:
            upd = supabase.table(table_name).update(payload).eq("cod_identificare", cod).execute()
            if upd.data:
                return
        except Exception:
            pass

        supabase.table(table_name).insert(payload).execute()

    def direct_save_all_tables(items: list, operator: str) -> tuple[bool, str]:
        if not items:
            return False, "Nu există date de salvat."

        by_table: dict[str, list[dict]] = {}
        for it in items:
            t = it.get("table")
            p = it.get("payload") or {}
            if not t or not isinstance(p, dict):
                continue
            by_table.setdefault(t, [])
            by_table[t].append(p)

        errors = []
        ok_any = False
        edit_msg = f"Editat de {operator} @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        for table_name, payloads in by_table.items():
            try:
                cols_real = set(get_table_columns(table_name))
                if "cod_identificare" not in cols_real:
                    continue

                clean_payloads = []
                for p in payloads:
                    cod = str(p.get("cod_identificare", "")).strip()
                    if not cod:
                        continue

                    cp = {k: p.get(k) for k in cols_real if k in p}
                    cp["cod_identificare"] = cod

                    if "data_ultimei_modificari" in cols_real:
                        cp["data_ultimei_modificari"] = now_iso()

                    if "observatii_idbdc" in cols_real:
                        # adăugăm o singură dată, aici (nu și în build items)
                        cp["observatii_idbdc"] = append_observatii(cp.get("observatii_idbdc"), edit_msg)

                    cp = cleanup_payload(cp)

                    if is_row_effectively_empty(cp):
                        continue

                    clean_payloads.append(cp)

                if not clean_payloads:
                    continue

                cod0 = str(clean_payloads[0].get("cod_identificare", "")).strip()

                if len(clean_payloads) > 1:
                    try:
                        supabase.table(table_name).delete().eq("cod_identificare", cod0).execute()
                    except Exception:
                        pass
                    supabase.table(table_name).insert(clean_payloads).execute()
                    ok_any = True
                    continue

                direct_upsert_single_row(table_name, clean_payloads[0], cod0)
                ok_any = True

            except Exception as e:
                errors.append(f"{table_name}: {e}")

        if not ok_any and errors:
            return False, " | ".join(errors)
        if not ok_any:
            return False, "Nu s-a putut salva (nicio operație aplicată)."
        if errors:
            return True, "Salvare parțială (cu unele avertismente)."
        return True, "Salvare completă."

    def direct_validate_all_tables(cod: str, table_names: list[str], operator: str) -> tuple[bool, str]:
        ok_any = False
        errors = []
        msg = f"Validat de {operator} @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        for t in table_names:
            try:
                cols = set(get_table_columns(t))
                if "cod_identificare" not in cols:
                    continue

                payload = {}

                if "validat_idbdc" in cols:
                    payload["validat_idbdc"] = True

                if "data_ultimei_modificari" in cols:
                    payload["data_ultimei_modificari"] = now_iso()

                if "observatii_idbdc" in cols:
                    try:
                        cur = (
                            supabase.table(t)
                            .select("observatii_idbdc")
                            .eq("cod_identificare", cod)
                            .limit(1)
                            .execute()
                        )
                        existing = ""
                        if cur.data and isinstance(cur.data, list) and len(cur.data) > 0:
                            existing = cur.data[0].get("observatii_idbdc") or ""
                        payload["observatii_idbdc"] = append_observatii(existing, msg)
                    except Exception:
                        payload["observatii_idbdc"] = msg

                payload = cleanup_payload(payload)

                if not payload:
                    continue

                supabase.table(t).update(payload).eq("cod_identificare", cod).execute()
                ok_any = True

            except Exception as e:
                errors.append(f"{t}: {e}")

        if not ok_any and errors:
            return False, " | ".join(errors)
        if not ok_any:
            return False, "Nu s-a putut valida (nu există coloane compatibile în tabelele selectate)."
        if errors:
            return True, "Validare parțială (cu unele avertismente)."
        return True, "Validare realizată."

    def direct_delete_all_tables(cod: str, table_names: list[str]) -> tuple[bool, str]:
        ok_any = False
        errors = []

        for t in table_names:
            try:
                cols = set(get_table_columns(t))
                if "cod_identificare" not in cols:
                    continue
                supabase.table(t).delete().eq("cod_identificare", cod).execute()
                ok_any = True
            except Exception as e:
                errors.append(f"{t}: {e}")

        if not ok_any and errors:
            return False, " | ".join(errors)
        if not ok_any:
            return False, "Nu s-a șters nimic."
        if errors:
            return True, "Ștergere parțială (cu unele avertismente)."
        return True, "Fișa a fost ștearsă."

    # ============================
    # STYLE (spațieri)
    # ============================

    st.markdown(
        """
        <style>
          [data-testid="stSidebar"] {
            background: #0b2a52 !important;
            border-right: 2px solid rgba(255,255,255,0.20);
          }
          [data-testid="stSidebar"] .stMarkdown,
          [data-testid="stSidebar"] label,
          [data-testid="stSidebar"] p,
          [data-testid="stSidebar"] h1,
          [data-testid="stSidebar"] h2,
          [data-testid="stSidebar"] h3 {
            color: #ffffff !important;
          }

          /* micșorare spații între blocuri */
          div.block-container { padding-top: 1.0rem; padding-bottom: 1.0rem; }
          .stRadio, .stToggle { margin-bottom: 0.2rem; }
          .stButton { margin-top: 0.2rem; margin-bottom: 0.2rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ============================
    # DROPDOWN MAP
    # ============================

    DROPDOWN_MAP = {
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
        "base_evenimente_stiintifice": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "natura_eveniment": ("nom_evenimente_stiintifice", "natura_eveniment"),
            "format_eveniment": ("nom_format_evenimente", "format_eveniment"),
        },
        "base_prop_intelect": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_prop_intelect": ("nom_prop_intelect", "acronim_prop_intelect"),
        },
        "com_echipe_proiect": {
            "nume_prenume": ("det_resurse_umane", "nume_prenume"),
            "status_personal": ("nom_status_personal", "status_personal"),
        },
        "com_date_financiare": {
            "valuta": ("__STATIC__", "VALUTA_3"),
        },
        "det_resurse_umane": {
            "acronim_functie_upt": ("nom_functie_upt", "acronim_functie_upt"),
            "acronim_departament": ("nom_departament", "acronim_departament"),
        },
        "det_evaluare_fdi": {
            "cod_universitate": ("nom_universitati", "cod_universitate"),
        },
    }

    STATIC_OPTIONS = {"VALUTA_3": ["LEI", "EUR", "USD"]}

    @st.cache_data(show_spinner=False, ttl=600)
    def load_dropdown_options(source_table: str, source_col: str):
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
                required=False,
            )
        return cfg

    # ============================
    # HEADER
    # ============================

    st.markdown(
        f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.operator_identificat}</h3>",
        unsafe_allow_html=True,
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
    # ACȚIUNE
    # ============================

    st.markdown("**Acțiune**")
    actiune = st.radio(
        label="",
        options=["Modificare date existente", "Introducere noutate"],
        horizontal=True,
        label_visibility="collapsed",
    )

    # micșorăm spațiul până la toggle
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ============================
    # STRUCTURĂ TAB-URI
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

    table_names = [t for _, t in tabele]

    # ============================
    # ÎNCĂRCARE
    # ============================

    state_key = lambda t: f"df_admin__{t}"
    state_key_raw = lambda t: f"df_admin_raw__{t}"

    loaded = {}
    exists_map = {}

    for _, table_name in tabele:
        df, cols, exista = load_single_row(table_name, cod)
        loaded[table_name] = (df, cols)
        exists_map[table_name] = exista

    base_exists = exists_map.get(tabela_baza, False)
    if actiune == "Modificare date existente" and not base_exists:
        st.warning("Nu există fișă pentru acest cod în baza de date. Alege «Introducere noutate» dacă vrei să creezi.")
        return

    for _, table_name in tabele:
        df, cols = loaded[table_name]
        if df.empty and cols:
            df_full = prepare_empty_single_row(cols, cod)
        else:
            df_full = df.copy()

        st.session_state[state_key_raw(table_name)] = df_full.copy()
        st.session_state[state_key(table_name)] = hide_control_cols(df_full)

    base_full = st.session_state[state_key_raw(tabela_baza)]

    # ============================
    # BLOCARE DUPĂ VALIDARE
    # ============================

    lock_after_validate = st.toggle("🔒 Blochează editarea după validare", value=True)

    already_valid = False
    if len(base_full) > 0 and "validat_idbdc" in base_full.columns:
        try:
            already_valid = bool(base_full.loc[0, "validat_idbdc"])
        except Exception:
            already_valid = False

    if lock_after_validate and already_valid:
        st.warning("Fișa este deja validată iar editarea este blocată. Deblochează dacă vrei modificare.")

    # ============================
    # BUTOANE
    # ============================

    b1, b2, b3 = st.columns(3)
    with b1:
        btn_save = st.button("💾 SALVARE (toată fișa)", disabled=(lock_after_validate and already_valid))
    with b2:
        btn_validate = st.button("✅ VALIDARE (toată fișa)")
    with b3:
        btn_delete = st.button("🗑️ ȘTERGE FIȘA")

    # micșorăm spațiul până la tab-uri
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ============================
    # TAB-URI + EDITOR
    # ============================

    tabs = st.tabs([label for label, _ in tabele])
    edited_data = {}

    for i, (label, table_name) in enumerate(tabele):
        with tabs[i]:
            df_show = st.session_state[state_key(table_name)]
            col_cfg = build_column_config_for_table(table_name, df_show)
            num_rows_mode = "dynamic" if table_name == "com_echipe_proiect" else "fixed"

            edited = st.data_editor(
                df_show,
                use_container_width=True,
                hide_index=True,
                num_rows=num_rows_mode,
                column_config=col_cfg,
                disabled=(lock_after_validate and already_valid and table_name != tabela_baza),
            )
            edited_data[table_name] = edited

    # ============================
    # STATUS FIȘĂ (în expander)
    # ============================

    if len(base_full) > 0:
        with st.expander("Status fișă (Responsabil / Observații / Confirmare / Ultima modificare / Validat)", expanded=False):
            r = base_full.iloc[0].to_dict()

            s1, s2, s3, s4, s5 = st.columns([1.2, 2.2, 1.0, 1.6, 1.0])
            with s1:
                st.caption("Responsabil")
                st.write(r.get("responsabil_idbdc", "") or "")
            with s2:
                st.caption("Observații")
                obs = (r.get("observatii_idbdc", "") or "").strip()
                st.write(obs if obs else "-")
            with s3:
                st.caption("Confirmare")
                st.write(fmt_bool(r.get("status_confirmare", False)))
            with s4:
                st.caption("Ultima modificare")
                st.write(r.get("data_ultimei_modificari", "") or "-")
            with s5:
                st.caption("Validat")
                st.write(fmt_bool(r.get("validat_idbdc", False)))

    # ============================
    # SALVARE (DIRECT)
    # ============================

    if btn_save:
        operator = st.session_state.operator_identificat
        try:
            items = []

            for _, table_name in tabele:
                df_edit_visible = edited_data[table_name]
                df_raw_original = st.session_state[state_key_raw(table_name)]
                _, cols_real = loaded[table_name]
                if not cols_real:
                    continue
                if df_edit_visible is None or len(df_edit_visible) == 0:
                    continue

                df_for_save = merge_back_control_cols(df_edit_visible, df_raw_original)

                if "cod_identificare" in df_for_save.columns:
                    df_for_save["cod_identificare"] = df_for_save["cod_identificare"].fillna(cod)
                    df_for_save["cod_identificare"] = df_for_save["cod_identificare"].astype(str).replace("nan", cod)

                for _, row in df_for_save.iterrows():
                    data = row.to_dict()
                    cod_row = data.get("cod_identificare")
                    if cod_row is None or str(cod_row).strip() == "":
                        continue

                    payload = {k: data.get(k) for k in cols_real if k in data}
                    payload["cod_identificare"] = str(cod_row).strip()

                    # IMPORTANT: nu mai adăugăm aici observatii/data_ultimei_modificari
                    # ca să nu se dubleze; se face o singură dată în direct_save_all_tables().

                    items.append({"table": table_name, "payload": payload})

            ok, msg = direct_save_all_tables(items, operator)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(f"Eroare la salvare: {msg}")

        except Exception as e:
            st.error(f"Eroare la salvare: {e}")

    # ============================
    # VALIDARE (DIRECT)
    # ============================

    if btn_validate:
        operator = st.session_state.operator_identificat
        try:
            ok, msg = direct_validate_all_tables(cod, table_names, operator)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(f"Eroare la validare: {msg}")
        except Exception as e:
            st.error(f"Eroare la validare: {e}")

    # ============================
    # ȘTERGERE (DIRECT) + CONFIRMARE
    # ============================

    if btn_delete:
        st.warning("Ștergerea este definitivă.")
        confirm = st.checkbox("Confirm că vreau să șterg definitiv fișa (din toate tabelele).")
        typed = st.text_input("Reintrodu cod_identificare pentru confirmare:", value="")
        if confirm and typed.strip() == cod:
            try:
                ok, msg = direct_delete_all_tables(cod, table_names)
                if ok:
                    for _, table_name in tabele:
                        for k in (state_key(table_name), state_key_raw(table_name)):
                            if k in st.session_state:
                                del st.session_state[k]
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(f"Eroare la ștergere: {msg}")
            except Exception as e:
                st.error(f"Eroare la ștergere: {e}")
        else:
            st.info("Bifează confirmarea și tastează exact codul pentru a executa ștergerea.")
