import streamlit as st
import pandas as pd
from datetime import datetime


def porneste_motorul(supabase):

    # ============================
    # CONFIG
    # ============================

    def _fmt_numeric(val, col_name: str = "") -> str:
        if val is None:
            return ""
        raw = str(val).strip()
        if raw == "":
            return ""
        try:
            f = float(raw.replace(",", "."))
        except (ValueError, TypeError):
            return raw

        col_name = (col_name or "").lower().strip()
        no_decimal_fields = {
            "cod_identificare",
            "numar_contract",
            "nr_contract",
            "nr_contract_achizitie",
            "nr_contract_subsecvent",
            "numar_oficial_acordare",
            "numar_publicare_cerere",
            "numar_data_notificare_intern",
            "telefon_mobil",
            "telefon_upt",
            "cod_depunere",
            "cod_temporar",
        }

        if col_name in no_decimal_fields:
            return str(int(round(f)))

        if f.is_integer():
            return str(int(f))

        return f"{f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    ADMIN_ONLY_COLS = {
        "responsabil_idbdc", "observatii_idbdc",
        "status_confirmare", "data_ultimei_modificari", "validat_idbdc",
        "creat_de", "creat_la", "modificat_de", "modificat_la",
    }

    CONTROL_COLS = [
        "responsabil_idbdc",
        "observatii_idbdc",
        "status_confirmare",
        "data_ultimei_modificari",
        "validat_idbdc",
    ]

    STATIC_OPTIONS = {"VALUTA_3": ["LEI", "EUR", "USD"]}

    TABELE_CONTRACTE = {"base_contracte_cep", "base_contracte_terti", "base_contracte_speciale"}
    TABELE_PROIECTE_CONTRACT_LIKE = {
        "base_proiecte_fdi",
        "base_proiecte_internationale",
        "base_proiecte_interreg",
        "base_proiecte_noneu",
        "base_proiecte_see",
    }

    FDI_BASE_ORDER = [
        "nr_crt",
        "denumire_categorie",
        "acronim_contracte_proiecte",
        "cod_identificare",
        "cod_temporar",
        "titlul_proiect",
        "acronim_proiect",
        "data_inceput",
        "data_sfarsit",
        "status_contract_proiect",
        "program",
        "cod_domeniu_fdi",
        "validat_idbdc",
        "observatii_idbdc",
    ]

    FDI_BASE_EXCLUDE = {
        "an_referinta",
        "responsabil_idbdc",
    }

    FDI_FIN_ORDER = [
        "suma_solicitata_fdi",
        "suma_aprobata_mec",
        "cofinantare_upt_fdi",
    ]

    TECHNIC_ORDER = [
        "cod_identificare",
        "obiectiv_general",
        "obiective_specifice",
        "activitati_proiect",
        "rezultate_proiect",
    ]

    is_admin = st.session_state.get("operator_rol") == "ADMIN"

    # ============================
    # HELPERS
    # ============================

    def now_iso():
        return datetime.now().isoformat()

    def current_year():
        return datetime.now().year

    def state_key(table_name: str) -> str:
        return f"admin_df_{table_name}_{cod}"

    def state_key_raw(table_name: str) -> str:
        return f"admin_raw_{table_name}_{cod}"

    def get_table_columns(table_name: str):
        try:
            res = supabase.rpc("idbdc_get_columns", {"p_table": table_name}).execute()
            return [r["column_name"] for r in (res.data or []) if r.get("column_name")]
        except Exception:
            return []

    def is_date_col(col: str) -> bool:
        c = (col or "").lower()
        if c in ("data_ultimei_modificari",):
            return False
        return c.startswith("data_") or c.endswith("_data") or c.startswith("dt_")

    def is_year_col(col: str) -> bool:
        c = (col or "").lower()
        return c == "an" or c.startswith("an_")

    def is_numeric_col(col: str, df: pd.DataFrame) -> bool:
        c = (col or "").lower()
        numeric_keywords = (
            "valoare_", "suma_", "cost_", "buget_", "cofinantare_",
            "contributie_", "numar_", "nr_", "punctaj", "scor_",
            "interval_", "total_", "pozitie_", "perioada_valabilitate_ani",
        )
        if any(c.startswith(k) or c == k for k in numeric_keywords):
            return True
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            return True
        return False

    def empty_row(columns):
        row = {c: None for c in columns}
        if "status_confirmare" in row:
            row["status_confirmare"] = False
        if "validat_idbdc" in row:
            row["validat_idbdc"] = False
        if "persoana_contact" in row:
            row["persoana_contact"] = False
        y = current_year()
        for c in columns:
            if c == "an" or c.startswith("an_"):
                row[c] = y
        return row

    def load_single_row(table_name: str, cod_local: str):
        cols = get_table_columns(table_name)
        if not cols:
            return pd.DataFrame(), [], False

        try:
            res = supabase.table(table_name).select("*").eq("cod_identificare", cod_local).execute()
            data = res.data or []
        except Exception:
            data = []

        df = pd.DataFrame(data)

        if df.empty:
            df = pd.DataFrame(columns=cols)
            return df, cols, False

        for c in cols:
            if c not in df.columns:
                df[c] = None
        df = df[cols]

        import datetime as _dt
        for c in df.columns:
            if is_date_col(c):
                def _to_date(v):
                    if v is None or (isinstance(v, float) and pd.isna(v)):
                        return None
                    if isinstance(v, _dt.date):
                        return v
                    try:
                        return pd.to_datetime(str(v)).date()
                    except Exception:
                        return None
                df[c] = df[c].apply(_to_date)

        return df, cols, True

    def prepare_empty_single_row(cols: list, cod_local: str):
        if not cols:
            return pd.DataFrame()
        r = empty_row(cols)
        if "cod_identificare" in r:
            r["cod_identificare"] = cod_local
        import datetime as _dt
        df = pd.DataFrame([r], columns=cols)
        for c in df.columns:
            if is_date_col(c):
                df[c] = df[c].apply(lambda v: None if v is None else (v if isinstance(v, _dt.date) else None))
        return df

    def append_observatii(existing: str, msg: str) -> str:
        base = (existing or "").strip()
        if not base:
            return msg
        return base + "\n" + msg

    def hide_control_cols(df: pd.DataFrame) -> pd.DataFrame:
        if is_admin:
            return df
        cols = [c for c in df.columns if c not in ADMIN_ONLY_COLS]
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

    def is_row_effectively_empty(d: dict) -> bool:
        cod_local = d.get("cod_identificare")
        if cod_local is None or (isinstance(cod_local, str) and cod_local.strip() == ""):
            return True
        return False

    def cleanup_payload(payload: dict) -> dict:
        out = {}
        for k, v in (payload or {}).items():
            if k == "nr_crt":
                if v is None:
                    continue
                if isinstance(v, str) and v.strip() == "":
                    continue
                out[k] = v
                continue
            if k == "cod_identificare":
                if v is not None and str(v).strip():
                    out[k] = str(v).strip()
                continue
            if v is None:
                continue
            if isinstance(v, str) and v.strip() == "":
                continue
            out[k] = v
        return out

    def direct_upsert_single_row(table_name: str, payload: dict, cod_local: str):
        try:
            check = supabase.table(table_name).select("cod_identificare").eq("cod_identificare", cod_local).limit(1).execute()
            exists = bool(check.data)
        except Exception:
            exists = False

        if exists:
            supabase.table(table_name).update(payload).eq("cod_identificare", cod_local).execute()
        else:
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
                    cod_local = str(p.get("cod_identificare", "")).strip()
                    if not cod_local:
                        continue

                    cp = {k: p.get(k) for k in cols_real if k in p}
                    cp["cod_identificare"] = cod_local

                    if "data_ultimei_modificari" in cols_real:
                        cp["data_ultimei_modificari"] = now_iso()

                    if "observatii_idbdc" in cols_real:
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
        return True, "Salvarea realizată cu succes!"

    def direct_validate_all_tables(cod_local: str, table_names: list[str], operator: str) -> tuple[bool, str]:
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
                            .eq("cod_identificare", cod_local)
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

                supabase.table(t).update(payload).eq("cod_identificare", cod_local).execute()
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

    def direct_delete_all_tables(cod_local: str, table_names: list[str]) -> tuple[bool, str]:
        ok_any = False
        errors = []
        for t in table_names:
            try:
                cols = set(get_table_columns(t))
                if "cod_identificare" not in cols:
                    continue
                supabase.table(t).delete().eq("cod_identificare", cod_local).execute()
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

    @st.cache_data(show_spinner=False, ttl=600)
    def load_functie_map() -> dict:
        try:
            res = (
                supabase.table("det_resurse_umane")
                .select("nume_prenume,acronim_functie_upt,acronim_departament")
                .execute()
            )
            result = {}
            for r in (res.data or []):
                if r.get("nume_prenume"):
                    result[r["nume_prenume"]] = {
                        "functie_upt": r.get("acronim_functie_upt", "") or "",
                        "acronim_departament": r.get("acronim_departament", "") or "",
                    }
            return result
        except Exception:
            return {}

    def autofill_functie_upt(df: pd.DataFrame) -> pd.DataFrame:
        if "nume_prenume" not in df.columns:
            return df
        functie_map = load_functie_map()
        if not functie_map:
            return df
        has_functie = "functie_upt" in df.columns
        has_dept = "acronim_departament" in df.columns
        for idx, row in df.iterrows():
            nume = row.get("nume_prenume")
            if nume and str(nume).strip():
                info = functie_map.get(str(nume).strip(), {})
                if has_functie:
                    functie = info.get("functie_upt", "")
                    if functie:
                        df.at[idx, "functie_upt"] = functie
                if has_dept:
                    dept = info.get("acronim_departament", "")
                    if dept:
                        df.at[idx, "acronim_departament"] = dept
        return df

    def _base_ctx_is_contract_like(ctx: str) -> bool:
        return ctx in TABELE_CONTRACTE

    def _col_label_admin(col: str, tbl: str = None, tabela_baza_ctx: str = None) -> str:
        ctx = tabela_baza_ctx or tbl
        is_contract_ctx = _base_ctx_is_contract_like(ctx)

        COL_LABELS_ADMIN = {
            "denumire_categorie": "🔽 CATEGORIE",
            "acronim_contracte_proiecte": "🔽 TIPUL DE CONTRACT",
            "status_contract_proiect": "🔽 STATUS CONTRACT/PROIECT",
            "cod_domeniu_fdi": "🔽 COD DOMENIU FDI",
            "natura_eveniment": "🔽 NATURA EVENIMENTULUI STIINTIFIC",
            "format_eveniment": "🔽 FORMATUL EVENIMENTULUI STIINTIFIC",
            "acronim_prop_intelect": "🔽 FORME DE PROTECTIE",
            "nume_prenume": "🔽 NUME SI PRENUME",
            "status_personal": "🔽 STATUS PERSONAL",
            "valuta": "🔽 VALUTA",
            "acronim_functie_upt": "🔽 ABREVIERE FUNCTIE UPT",
            "acronim_departament": "🔽 ACRONIM DEPARTAMENT",
            "cod_universitate": "🔽 COD UNIVERSITATE",
            "persoana_contact": "PERSOANA DE CONTACT",
            "functie_upt": "Abreviere functie UPT (auto)",
            "data_contract": "📅 DATA CONTRACTULUI",
            "data_inceput": "📅 DATA DE INCEPUT",
            "data_sfarsit": "📅 DATA DE SFARSIT",
            "data_semnare": "📅 DATA SEMNARE",
            "data_depunere": "📅 DATA DEPUNERE",
            "data_acordare": "📅 DATA ACORDARE",
            "data_eveniment": "📅 DATA EVENIMENT",
            "data_inceput_rol": "📅 DATA DE INCEPUT ROL",
            "data_sfarsit_rol": "📅 DATA DE SFARSIT ROL",
            "data_depozit_cerere": "📅 DATA DEPUNERE CERERE LA OSIM",
            "data_oficiala_acordare": "📅 DATA OFICIALA DE ACORDARE",
            "data_inceput_valabilitate": "📅 DATA DE INCEPUT VALABILITATE",
            "data_sfarsit_valabilitate": "📅 DATA DE SFARSIT VALABILITATE",
            "data_apel": "📅 DATA APELULUI",
            "abreviere_domeniu_fdi": "DOMENIUL FDI",
            "program": "PROGRAM",
            "subprogram": "SUBPROGRAM",
            "instrument_finantare": "INSTRUMENT DE FINANTARE",
            "apel": "APEL",
            "pilon": "PILON",
            "componenta": "COMPONENTA",
            "reforma": "REFORMA",
            "investitie": "INVESTITIE",
            "sursa_finantare": "SURSA DE FINANTARE",
            "programul_tematic": "PROGRAMUL TEMATIC",
            "componenta_axa": "COMPONENTA / AXA",
            "obiectiv_specific": "OBIECTIV SPECIFIC",
            "acronim_tip_contract": "ACRONIM TIP CONTRACT",
            "acronim_proiect": "ACRONIM PROIECT",
            "acronim_tip_proiect": "ACRONIM TIP PROIECT",
            "activitati_proiect": "ACTIVITATI",
            "an_referinta": "ANUL DE REFERINTA",
            "apel_pentru_propuneri": "APELUL PENTRU PROPUNERI",
            "autori": "AUTORI",
            "clasificare_eveniment": "CLASIFICAREA EVENIMENTULUI",
            "cod_depunere": "COD DEPUNERE",
            "cod_identificare": "NR.CONTRACT/ID PROIECT",
            "cod_operatori": "COD OPERATORI",
            "cod_temporar": "COD DEPUNERE",
            "cofinantare_anuala_contract": "COFINANTARE ANUALA CONTRACT",
            "cofinantare_totala_contract": "COFINANTARE TOTALA CONTRACT",
            "cofinantare_upt_fdi": "COFINANTARE UPT PROIECTE FDI",
            "comentarii_diverse": "COMENTARII DIVERSE",
            "comentarii_document": "COMENTARII DOCUMENTE",
            "contract_cesiune_inventatori_externi": "CONTRACT CESIUNE / INVENTATORI EXTERNI UPT",
            "contributie_ue_proiect_upt": "CONTRIBUTIE UE PENTRU UPT",
            "contributie_ue_total_proiect": "CONTRIBUTIE UE PROIECT",
            "cost_proiect_upt": "COST UPT IN PROIECT",
            "cost_total_proiect": "COST TOTAL PROIECT",
            "denumire_beneficiar": "DENUMIREA BENEFICIARULUI",
            "denumire_completa": "DENUMIRE TIP CONTRACT",
            "denumire_departament": "DENUMIRE DEPARTAMENT",
            "denumire_domeniu_fdi": "DENUMIREA DOMENIULUI FDI",
            "denumire_functie_upt": "DENUMIRE FUNCTIE UPT",
            "denumire_institutie": "DENUMIREA INSTITUTIEI",
            "denumire_participanti": "DENUMIRE PARTICIPANTI",
            "denumire_prop_intelect": "DENUMIREA FORMEI DE PROTECTIE",
            "denumire_solicitant": "DENUMIRE SOLICITANT",
            "denumire_titular": "DENUMIRE TITULAR",
            "derulat_prin": "DERULAT PRIN",
            "document_oficial_original": "DOCUMENT OFICIAL ORIGINAL",
            "domenii_studii": "DOMENIILE DE STUDII SUPERIOARE",
            "domeniu_aplicare": "DOMENIUL DE APLICARE",
            "domeniu_cercetare": "DOMENIUL DE CERCETARE",
            "durata": "DURATA",
            "durata_luni": "DURATA",
            "email": "EMAIL",
            "email_upt": "EMAIL",
            "explicatii_format_evenimente": "DESCRIERE FORMAT EVENIMENT",
            "explicatii_satus_personal": "DESCRIERE STATUS PERSONAL",
            "explicatii_satus_proiect": "DESCRIERE STATUS CONTRACT/PROIECT",
            "facultate": "FACULTATEA",
            "filtru_categorie": "FILTRU CATEGORIE",
            "filtru_proiect": "FILTRU PROIECT",
            "functia_specifica": "ROLUL IN CONTRACT/PROIECT",
            "id_proiect_contract_sursa": "ID PROIECT (CONTRACT SURSA)",
            "institutii_organizare": "INSTITUTIILE ORGANIZATOARE",
            "interval_finantare": "TOTAL PROIECTE FINANTATE",
            "link_espacenet": "LINK ESPACENET",
            "loc_desfasurare": "LOCUL DE DESFASURARE",
            "nr_crt": "NR.CRT.",
            "numar_autori_total": "NUMAR AUTORI TOTAL",
            "numar_autori_upt": "NUMAR AUTORI UPT",
            "numar_data_notificare_intern": "NR. SI DATA NOTIFICARE INTERNA UPT",
            "numar_oficial_acordare": "NUMAR OFICIAL DE ACORDARE",
            "numar_participanti": "NUMAR DE PARTICIPANTI",
            "numar_publicare_cerere": "NUMAR PUBLICARE CERERE",
            "obiectiv_general": "OBIECTIV GENERAL",
            "obiective_specifice": "OBIECTIVE SPECIFICE",
            "parteneri": "PARTENERI",
            "perioada_valabilitate": "PERIOADA DE VALABILITATE A TITLULUI DE PROTECTIE",
            "perioada_valabilitate_ani": "PERIOADA DE VALABILITATE A FORMEI DE PROTECTIE",
            "pozitie_clasament": "POZITIE IN CLASAMENT",
            "programul_de_finantare": "PROGRAMUL DE FINANTARE",
            "punctaj": "PUNCTAJ",
            "rezultate_proiect": "REZULTATE",
            "rol": "ROL OPERATOR",
            "rol_upt": "ROL UPT",
            "schema_de_finantare": "SCHEMA DE FINANTARE",
            "scor_evaluare": "SCORUL EVALUARII",
            "spin_off": "SPIN OFF",
            "status_activ": "STATUS ACTIV",
            "status_document": "STATUS DOCUMENT",
            "suma_aprobata": "SUMA APROBATA MEC",
            "suma_aprobata_mec": "SUMA APROBATA MEC",
            "suma_solicitata": "SUMA SOLICITATA",
            "suma_solicitata_fdi": "SUMA SOLICITATA",
            "telefon_mobil": "TELEFON MOBIL",
            "telefon_upt": "TELEFON UPT",
            "tema_specifica": "TEMA SPECIFICA",
            "titlu_engleza_diploma": "TITLUL IN ENGLEZA CONF. DIPLOMA",
            "titlu_engleza_epo": "TITLUL IN ENGLEZA CONF. EPO",
            "titlu_engleza_fisa_inventiei": "TITLUL IN ENGLEZA CONF. FISA INVENTIEI",
            "titlu_engleza_google_translate": "TITLUL IN ENGLEZA CONF. GOOGLE TRANSLATE",
            "titlul": "TITLUL",
            "titlul_eveniment": "TITLUL EVENIMENTULUI STIINTIFIC",
            "titlul_proiect": "OBIECTUL/TITLUL CONTRACTULUI/PROIECTULUI",
            "total_proiecte": "TOTAL PROIECTE DEPUSE",
            "username_sistem": "USERNAME",
            "valoare_anuala_contract": "VALOAREA ANUALA A CONTRACTULUI",
            "valoare_totala_contract": "VALOAREA TOTALA A CONTRACTULUI",
            "website": "WEBSITE",
        }

        COL_LABELS_PER_TABLE_ADMIN = {
            "base_contracte_cep": {
                "cod_identificare": "NR. CONTRACT",
                "acronim_contracte_proiecte": "🔽 TIPUL DE CONTRACT",
                "status_contract_proiect": "🔽 STATUS CONTRACT",
                "titlul_proiect": "OBIECTUL CONTRACTULUI",
            },
            "base_contracte_terti": {
                "cod_identificare": "NR. CONTRACT",
                "acronim_contracte_proiecte": "🔽 TIPUL DE CONTRACT",
                "status_contract_proiect": "🔽 STATUS CONTRACT",
                "titlul_proiect": "OBIECTUL CONTRACTULUI",
            },
            "base_contracte_speciale": {
                "cod_identificare": "NR. CONTRACT",
                "acronim_contracte_proiecte": "🔽 TIPUL DE CONTRACT",
                "status_contract_proiect": "🔽 STATUS CONTRACT",
                "titlul_proiect": "OBIECTUL CONTRACTULUI",
            },
            "base_proiecte_fdi": {
                "nr_crt": "NR.CRT.",
                "denumire_categorie": "CATEGORIE",
                "acronim_contracte_proiecte": "TIPUL DE PROIECT",
                "cod_identificare": "ID PROIECT",
                "cod_temporar": "COD DEPUNERE",
                "titlul_proiect": "TITLUL PROIECTULUI",
                "acronim_proiect": "ACRONIMUL PROIECTULUI",
                "data_inceput": "DATA DE INCEPUT",
                "data_sfarsit": "DATA DE SFARSIT",
                "status_contract_proiect": "STATUS PROIECT",
                "program": "PROGRAM",
                "cod_domeniu_fdi": "COD DOMENIU FDI",
                "validat_idbdc": "VALIDAT IDBDC",
                "observatii_idbdc": "OBSERVATII IDBDC",
            },
            "base_proiecte_pncdi": {
                "cod_identificare": "NR.CONTRACT / COD PROIECT",
                "program": "PROGRAM",
                "subprogram": "SUBPROGRAM",
                "instrument_finantare": "INSTRUMENT DE FINANTARE",
                "apel": "APEL",
                "status_contract_proiect": "🔽 STATUS PROIECT",
                "titlul_proiect": "TITLUL PROIECTULUI",
            },
            "base_proiecte_pnrr": {
                "cod_identificare": "COD PROIECT PNRR",
                "pilon": "PILON",
                "componenta": "COMPONENTA",
                "reforma": "REFORMA",
                "investitie": "INVESTITIE",
                "apel": "APEL",
                "status_contract_proiect": "🔽 STATUS PROIECT",
                "titlul_proiect": "TITLUL PROIECTULUI",
            },
            "base_proiecte_internationale": {
                "cod_identificare": "COD / NR. PROIECT",
                "status_contract_proiect": "🔽 STATUS PROIECT",
                "titlul_proiect": "TITLUL PROIECTULUI",
                "rol_upt": "ROL UPT IN PROIECT",
            },
            "base_proiecte_interreg": {
                "cod_identificare": "COD PROIECT INTERREG",
                "status_contract_proiect": "🔽 STATUS PROIECT",
                "titlul_proiect": "TITLUL PROIECTULUI",
                "rol_upt": "ROL UPT IN PROIECT",
            },
            "base_proiecte_noneu": {
                "cod_identificare": "COD / NR. PROIECT",
                "status_contract_proiect": "🔽 STATUS PROIECT",
                "titlul_proiect": "TITLUL PROIECTULUI",
                "rol_upt": "ROL UPT IN PROIECT",
            },
            "base_proiecte_see": {
                "cod_identificare": "COD / NR. PROIECT",
                "status_contract_proiect": "🔽 STATUS PROIECT",
                "titlul_proiect": "TITLUL PROIECTULUI",
                "rol_upt": "ROL UPT IN PROIECT",
            },
            "base_evenimente_stiintifice": {
                "cod_identificare": "COD EVENIMENT",
                "titlul_eveniment": "TITLUL EVENIMENTULUI",
                "natura_eveniment": "NATURA EVENIMENTULUI",
                "format_eveniment": "FORMATUL EVENIMENTULUI",
                "loc_desfasurare": "LOCUL DE DESFASURARE",
            },
            "base_prop_intelect": {
                "cod_identificare": "NR. CERERE / BREVET",
                "acronim_prop_intelect": "FORMA DE PROTECTIE",
                "titlul_proiect": "TITLUL INVENTIEI / LUCRARII",
                "data_depozit_cerere": "DATA DEPUNERE LA OSIM",
                "data_oficiala_acordare": "DATA ACORDARE",
                "numar_oficial_acordare": "NR. OFICIAL ACORDARE",
            },
        }

        if tbl and tbl in COL_LABELS_PER_TABLE_ADMIN and col in COL_LABELS_PER_TABLE_ADMIN[tbl]:
            return COL_LABELS_PER_TABLE_ADMIN[tbl][col]

        if is_contract_ctx and tbl not in COL_LABELS_PER_TABLE_ADMIN:
            if col == "cod_identificare":
                return "NR. CONTRACT"
            if col == "functia_specifica":
                return "ROLUL IN CONTRACT"

        return COL_LABELS_ADMIN.get(col, col.replace("_", " ").capitalize())

    def build_column_config_for_table(table_name: str, df: pd.DataFrame, tabela_baza_ctx: str = None):
        DROPDOWN_MAP = {
            "base_contracte_cep": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_contracte", "acronim_tip_contract"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            },
            "base_contracte_terti": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_contracte", "acronim_tip_contract"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            },
            "base_contracte_speciale": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_contracte", "acronim_tip_contract"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            },
            "base_proiecte_fdi": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
                "cod_domeniu_fdi": ("nom_domenii_fdi", "cod_domeniu_fdi"),
            },
            "base_proiecte_internationale": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            },
            "base_proiecte_interreg": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            },
            "base_proiecte_noneu": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            },
            "base_proiecte_see": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            },
            "base_proiecte_pncdi": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            },
            "base_proiecte_pnrr": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
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

        rel = DROPDOWN_MAP.get(table_name, {})
        cfg = {}
        AUTO_FILLED_COLS = {"denumire_categorie", "acronim_contracte_proiecte"}

        for target_col, (src_table, src_col) in rel.items():
            if target_col not in df.columns:
                continue

            if target_col in AUTO_FILLED_COLS:
                cfg[target_col] = st.column_config.TextColumn(
                    label=_col_label_admin(target_col, table_name, tabela_baza_ctx),
                    disabled=True,
                    help="Completat automat din selectoarele de sus",
                )
                continue

            if src_table == "__STATIC__":
                options = STATIC_OPTIONS.get(src_col, [])
            else:
                options = load_dropdown_options(src_table, src_col)

            if not options:
                continue

            cfg[target_col] = st.column_config.SelectboxColumn(
                label=_col_label_admin(target_col, table_name, tabela_baza_ctx),
                options=options,
                required=False,
                help="🔽 Selectează din listă",
            )

        if table_name == "com_echipe_proiect" and "persoana_contact" in df.columns:
            df["persoana_contact"] = df["persoana_contact"].apply(
                lambda v: True if v is True or str(v).strip().upper() in ("TRUE", "DA", "1") else False
            )
            cfg["persoana_contact"] = st.column_config.CheckboxColumn(
                label="PERSOANA DE CONTACT",
                help="Bifeaza daca persoana este persoana de contact pentru acest contract/proiect",
                default=False,
            )

        if table_name == "com_echipe_proiect" and "functie_upt" in df.columns:
            cfg["functie_upt"] = st.column_config.TextColumn(
                label=_col_label_admin("functie_upt", table_name, tabela_baza_ctx),
                help="Completat automat din det_resurse_umane",
                disabled=True,
            )

        for c in df.columns:
            if c in CONTROL_COLS:
                continue
            if is_date_col(c):
                cfg[c] = st.column_config.DateColumn(
                    label=_col_label_admin(c, table_name, tabela_baza_ctx),
                    format="YYYY-MM-DD",
                    step=1,
                    help="📅 Click pentru a selecta data din calendar",
                )

        for c in df.columns:
            if c in CONTROL_COLS:
                continue
            if is_year_col(c):
                cfg[c] = st.column_config.NumberColumn(
                    label=_col_label_admin(c, table_name, tabela_baza_ctx),
                    min_value=1900,
                    max_value=2100,
                    step=1,
                    format="%d",
                )

        if "nr_crt" in df.columns and "nr_crt" not in cfg:
            cfg["nr_crt"] = st.column_config.NumberColumn(
                label=_col_label_admin("nr_crt", table_name, tabela_baza_ctx),
                disabled=True,
                format="%d",
            )

        VALUE_COLS_KEYWORDS = (
            "valoare_", "suma_", "cost_", "buget_", "cofinantare_",
            "contributie_", "total_",
        )
        for c in df.columns:
            if c in cfg or c in CONTROL_COLS:
                continue
            if is_numeric_col(c, df):
                c_lower = c.lower()
                is_value_col = any(c_lower.startswith(k) or c_lower == k for k in VALUE_COLS_KEYWORDS)
                cfg[c] = st.column_config.NumberColumn(
                    label=_col_label_admin(c, table_name, tabela_baza_ctx),
                    step=0.01 if is_value_col else 1,
                    format="%.2f" if is_value_col else "%d",
                )

        for c in df.columns:
            if c in cfg or c in CONTROL_COLS:
                continue
            cfg[c] = st.column_config.TextColumn(
                label=_col_label_admin(c, table_name, tabela_baza_ctx),
            )

        return cfg

    def _nomdet_detect_pk(cols: list[str]) -> str:
        if "nr_crt" in cols:
            return "nr_crt"
        return cols[0] if cols else ""

    def _nomdet_clean_payload(d: dict):
        out = {}
        for k, v in (d or {}).items():
            if k == "__STERGE__":
                continue
            if v is None:
                continue
            if isinstance(v, str) and v.strip() == "":
                continue
            out[k] = v
        return out

    def _nomdet_build_column_config(table_name: str, df: pd.DataFrame):
        NOMDET_WHITELIST = [
            "nom_categorie",
            "nom_status_proiect",
            "nom_contracte",
            "nom_proiecte",
            "nom_departament",
            "nom_functie_upt",
            "nom_domenii_fdi",
            "nom_universitati",
            "det_resurse_umane",
        ]

        NOMDET_DROPDOWN_MAP = {
            "det_resurse_umane": {
                "acronim_functie_upt": ("nom_functie_upt", "acronim_functie_upt"),
                "acronim_departament": ("nom_departament", "acronim_departament"),
            }
        }

        cfg = {}
        rel = NOMDET_DROPDOWN_MAP.get(table_name, {})
        for target_col, (src_table, src_col) in rel.items():
            if target_col not in df.columns:
                continue
            options = load_dropdown_options(src_table, src_col)
            if not options:
                continue
            cfg[target_col] = st.column_config.SelectboxColumn(
                label=target_col,
                options=options,
                required=False,
            )
        if "__STERGE__" in df.columns:
            cfg["__STERGE__"] = st.column_config.CheckboxColumn(label="Șterge", default=False)
        for c in df.columns:
            if c == "__STERGE__":
                continue
            if is_date_col(c):
                cfg[c] = st.column_config.DateColumn(label=c, format="YYYY-MM-DD", step=1)
        for c in df.columns:
            if c == "__STERGE__":
                continue
            if is_year_col(c):
                cfg[c] = st.column_config.NumberColumn(label=c, min_value=1900, max_value=2100, step=1, format="%d")
        return cfg

    def render_nomenclatoare_admin_box():
        NOMDET_WHITELIST = [
            "nom_categorie",
            "nom_status_proiect",
            "nom_contracte",
            "nom_proiecte",
            "nom_departament",
            "nom_functie_upt",
            "nom_domenii_fdi",
            "nom_universitati",
            "det_resurse_umane",
        ]

        rol = (st.session_state.get("operator_rol") or "").strip().upper()
        if rol != "ADMIN":
            return

        if st.session_state.get("nomdet_saved_ok", False):
            st.success("Salvarea realizată cu succes!")
            st.session_state.nomdet_saved_ok = False

        with st.expander("🧩 Nomenclatoare & Detalii", expanded=False):
            st.caption("Alege tabela, editează în grid și apasă SALVARE.")
            tabela = st.selectbox("Tabelă", NOMDET_WHITELIST, index=0, key="nomdet_table")
            cols = get_table_columns(tabela)
            if not cols:
                st.error("Nu pot citi coloanele tablei (idbdc_get_columns nu a returnat nimic).")
                return

            pk = _nomdet_detect_pk(cols)

            try:
                res = supabase.table(tabela).select("*").execute()
                data = res.data or []
                df = pd.DataFrame(data)
            except Exception as e:
                st.error(f"Eroare la încărcare: {e}")
                return

            if df.empty:
                df = pd.DataFrame(columns=cols)

            for c in cols:
                if c not in df.columns:
                    df[c] = None

            df = df[cols].copy()
            if "__STERGE__" not in df.columns:
                df["__STERGE__"] = False

            cfg = _nomdet_build_column_config(tabela, df)
            edited = st.data_editor(
                df,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                column_config=cfg,
                key="nomdet_editor",
            )

            if st.button("💾 SALVARE", key="nomdet_save"):
                try:
                    to_delete = edited[edited["__STERGE__"] == True]
                    for _, row in to_delete.iterrows():
                        key_val = row.get(pk)
                        if key_val is None or str(key_val).strip() == "":
                            continue
                        supabase.table(tabela).delete().eq(pk, key_val).execute()

                    to_upsert = edited[edited["__STERGE__"] != True].copy()
                    payloads = []
                    for _, row in to_upsert.iterrows():
                        d = _nomdet_clean_payload(row.to_dict())
                        key_val = d.get(pk)
                        if key_val is None or str(key_val).strip() == "":
                            continue
                        payloads.append(d)

                    if payloads:
                        supabase.table(tabela).upsert(payloads, on_conflict=pk).execute()

                    st.session_state.nomdet_saved_ok = True
                    st.rerun()

                except Exception as e:
                    st.error(f"Eroare la salvare: {e}")

    def _safe_float(v):
        if v is None:
            return 0.0
        try:
            return float(str(v).replace(",", ".").strip())
        except Exception:
            return 0.0

    def _apply_auto_values(df: pd.DataFrame) -> pd.DataFrame:
        if "denumire_categorie" in df.columns:
            df["denumire_categorie"] = map_categorie_label.get(cat_admin, cat_admin)
        if "acronim_contracte_proiecte" in df.columns:
            df["acronim_contracte_proiecte"] = map_tip_label.get(tip_admin, tip_admin)
        if "cod_identificare" in df.columns:
            df["cod_identificare"] = cod
        return df

    def _reorder_df(df: pd.DataFrame, first_cols: list[str]) -> pd.DataFrame:
        ordered = [c for c in first_cols if c in df.columns]
        rest = [c for c in df.columns if c not in ordered]
        return df[ordered + rest]

    def _prepare_display_df(table_name: str, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()

        if table_name == "base_proiecte_fdi":
            out = out.drop(columns=[c for c in FDI_BASE_EXCLUDE if c in out.columns], errors="ignore")
            out = _reorder_df(out, FDI_BASE_ORDER)

        if table_name == "com_aspecte_tehnice":
            out = _reorder_df(out, TECHNIC_ORDER)

        if table_name == "com_date_financiare" and tabela_baza == "base_proiecte_fdi":
            keep = [c for c in FDI_FIN_ORDER if c in out.columns]
            extras = [c for c in out.columns if c in CONTROL_COLS or c == "cod_identificare"]
            out = out[[c for c in ["cod_identificare"] + keep + extras if c in out.columns]]
            total_values = []
            for _, r in out.iterrows():
                total_values.append(_safe_float(r.get("suma_aprobata_mec")) + _safe_float(r.get("cofinantare_upt_fdi")))
            out["total_buget_calc"] = total_values

        return out

    def _render_editor_standard(table_name: str, df_show: pd.DataFrame, editing_blocked: bool):
        col_cfg = build_column_config_for_table(table_name, df_show, tabela_baza)
        key_editor = f"editor_{table_name}_{cod}"
        return st.data_editor(
            df_show,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config=col_cfg,
            disabled=editing_blocked,
            key=key_editor,
            height=420,
        )

    def _render_editor_echipa(table_name: str, df_show: pd.DataFrame, editing_blocked: bool):
        col_cfg_echipa = build_column_config_for_table(table_name, df_show, tabela_baza)

        cols_echipa_show = [c for c in df_show.columns if c != "cod_identificare"]
        df_show_edit = df_show[cols_echipa_show].copy()
        col_cfg_echipa.pop("cod_identificare", None)

        if "persoana_contact" in df_show_edit.columns:
            df_show_edit["persoana_contact"] = df_show_edit["persoana_contact"].apply(
                lambda v: True if v is True or str(v).strip().upper() in ("TRUE", "DA", "1") else False
            )

        nr_membri = len(df_show_edit)
        st.markdown(
            f"<div style='background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.18);"
            f"border-radius:10px;padding:8px 14px;margin-bottom:6px;'>"
            f"<span style='color:#ffffff;font-weight:800;font-size:0.92rem;'>👥 Echipa</span> "
            f"<span style='color:rgba(255,255,255,0.55);font-size:0.80rem;'>{nr_membri} persoane</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        key_editor = f"editor_echipa_{cod}"
        edited_echipa = st.data_editor(
            df_show_edit,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config=col_cfg_echipa,
            disabled=editing_blocked,
            key=key_editor,
            height=420,
        )

        edited_echipa = edited_echipa.copy()
        edited_echipa["cod_identificare"] = cod

        if "persoana_contact" not in edited_echipa.columns:
            edited_echipa["persoana_contact"] = False

        if "nume_prenume" in edited_echipa.columns:
            edited_echipa = edited_echipa[
                edited_echipa["nume_prenume"].notna() &
                (edited_echipa["nume_prenume"].astype(str).str.strip() != "")
            ].reset_index(drop=True)

        st.session_state[f"echipa_reunited_{cod}"] = edited_echipa
        return edited_echipa

    def _render_fdi_financial_preview(df_show: pd.DataFrame):
        if tabela_baza != "base_proiecte_fdi":
            return
        if "total_buget_calc" not in df_show.columns:
            return

        vals = df_show.iloc[0].to_dict() if len(df_show) else {}
        suma_sol = _fmt_numeric(vals.get("suma_solicitata_fdi"), "suma_solicitata_fdi")
        suma_apr = _fmt_numeric(vals.get("suma_aprobata_mec"), "suma_aprobata_mec")
        cofin = _fmt_numeric(vals.get("cofinantare_upt_fdi"), "cofinantare_upt_fdi")
        total = _fmt_numeric(vals.get("total_buget_calc"), "total_buget_calc")

        st.markdown(
            f"""
            <div style='background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.18);
                        border-radius:10px;padding:10px 14px;margin-bottom:8px;'>
                <div style='color:#ffffff;font-weight:800;font-size:0.92rem;margin-bottom:6px;'>💰 Date financiare FDI</div>
                <div style='color:rgba(255,255,255,0.90);font-size:0.90rem;line-height:1.8;'>
                    <b>SUMA SOLICITATA:</b> {suma_sol or "-"}<br/>
                    <b>SUMA APROBATA MINISTER:</b> {suma_apr or "-"}<br/>
                    <b>COFINANTARE UPT:</b> {cofin or "-"}<br/>
                    <b>TOTAL BUGET:</b> {total or "-"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ============================
    # STYLE
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
          div.block-container { padding-top: 1.0rem; padding-bottom: 1.0rem; }
          .stRadio, .stToggle { margin-bottom: 0.2rem; }
          .stButton { margin-top: 0.2rem; margin-bottom: 0.2rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ============================
    # HEADER
    # ============================

    st.markdown(
        f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.operator_identificat}</h3>",
        unsafe_allow_html=True,
    )

    render_nomenclatoare_admin_box()
    st.divider()

    # ============================
    # SELECTOARE
    # ============================

    _filtru_categorii = st.session_state.get("operator_filtru_categorie") or []
    _filtru_tipuri = st.session_state.get("operator_filtru_tipuri") or []

    _toate_cat = ["Contracte", "Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"]
    _cat_disponibile = [""] + [c for c in _toate_cat if not _filtru_categorii or c in _filtru_categorii]

    c1, c2, c3 = st.columns(3)
    with c1:
        cat_admin = st.selectbox("Categoria de date", _cat_disponibile)
    with c2:
        if cat_admin == "Contracte":
            _toate_contracte = ["CEP", "TERTI", "SPECIALE"]
            _tip_disponibile = [""] + [t for t in _toate_contracte if not _filtru_tipuri or t in _filtru_tipuri]
            tip_admin = st.selectbox("Tipul de contract", _tip_disponibile)
        elif cat_admin == "Proiecte":
            _toate_proiecte = ["FDI", "PNRR", "PNCDI", "INTERNATIONALE", "INTERREG", "NONEU", "SEE"]
            _tip_disponibile = [""] + [t for t in _toate_proiecte if not _filtru_tipuri or t in _filtru_tipuri]
            tip_admin = st.selectbox("Tipul de proiect", _tip_disponibile)
        else:
            tip_admin = ""
    with c3:
        if cat_admin == "Contracte":
            id_admin = st.text_input("Filtru număr contract")
        else:
            id_admin = st.text_input("Filtru număr contract sau ID proiect")

    # ── Buton Listă contracte SPECIALE ───────────────────────────────────────
    if cat_admin == "Contracte" and tip_admin == "SPECIALE" and (not id_admin or not id_admin.strip()):
        st.markdown("---")
        st.markdown("**📋 Listă contracte SPECIALE**")
        _fc1, _fc2, _fc3 = st.columns(3)
        with _fc1:
            _filtru_an = st.text_input("Filtru an (ex: 2024)", key="spec_filtru_an")
        with _fc2:
            try:
                _responsabili_spec = [""] + sorted(set(
                    r.get("responsabil_idbdc", "") for r in
                    (supabase.table("base_contracte_speciale").select("responsabil_idbdc").execute().data or [])
                    if r.get("responsabil_idbdc")
                ))
            except Exception:
                _responsabili_spec = [""]
            _filtru_responsabil = st.selectbox("Filtru responsabil", _responsabili_spec, key="spec_filtru_responsabil")
        with _fc3:
            _filtru_beneficiar = st.text_input("Filtru beneficiar", key="spec_filtru_beneficiar")

        if st.button("🔍 Afișează lista", key="spec_btn_lista"):
            try:
                q = supabase.table("base_contracte_speciale").select(
                    "cod_identificare, titlul_proiect, denumire_beneficiar, "
                    "derulat_prin, responsabil_idbdc, data_contract, "
                    "data_inceput, data_sfarsit, status_contract_proiect"
                )
                if _filtru_an and _filtru_an.strip():
                    try:
                        _an = int(_filtru_an.strip())
                        q = q.lte("data_inceput", f"{_an}-12-31").gte("data_sfarsit", f"{_an}-01-01")
                    except ValueError:
                        st.warning("Anul introdus nu este valid.")
                if _filtru_responsabil:
                    q = q.eq("responsabil_idbdc", _filtru_responsabil)
                if _filtru_beneficiar and _filtru_beneficiar.strip():
                    q = q.ilike("denumire_beneficiar", f"%{_filtru_beneficiar.strip()}%")
                _res_base = q.order("data_inceput", desc=True).limit(500).execute()
                _df_base = pd.DataFrame(_res_base.data or [])

                if _df_base.empty:
                    st.info("Niciun contract SPECIAL găsit pentru filtrele selectate.")
                else:
                    _coduri = _df_base["cod_identificare"].tolist()
                    try:
                        _res_fin = (
                            supabase.table("com_date_financiare")
                            .select("cod_identificare, valoare_totala_contract, cofinantare_totala_contract, valuta")
                            .in_("cod_identificare", _coduri)
                            .execute()
                        )
                        _df_fin = pd.DataFrame(_res_fin.data or [])
                        if not _df_fin.empty:
                            _df_fin = _df_fin.dropna(axis=1, how="all")
                            _df_fin = _df_fin.groupby("cod_identificare", as_index=False).first()
                    except Exception:
                        _df_fin = pd.DataFrame()

                    try:
                        _res_ech = (
                            supabase.table("com_echipe_proiect")
                            .select("cod_identificare, nume_prenume, functia_specifica, persoana_contact")
                            .in_("cod_identificare", _coduri)
                            .execute()
                        )
                        _df_ech = pd.DataFrame(_res_ech.data or [])
                        if not _df_ech.empty:
                            _df_ech = _df_ech.sort_values(["cod_identificare", "persoana_contact"], ascending=[True, False])
                            _df_ech_grp = (
                                _df_ech.groupby("cod_identificare", as_index=False)
                                .agg(membri_echipa=("nume_prenume", lambda x: ", ".join(x.dropna())))
                            )
                        else:
                            _df_ech_grp = pd.DataFrame()
                    except Exception:
                        _df_ech_grp = pd.DataFrame()

                    _df_final = _df_base.copy()
                    if not _df_fin.empty and "cod_identificare" in _df_fin.columns:
                        _df_final = _df_final.merge(_df_fin, on="cod_identificare", how="left")
                    if not _df_ech_grp.empty and "cod_identificare" in _df_ech_grp.columns:
                        _df_final = _df_final.merge(_df_ech_grp, on="cod_identificare", how="left")

                    _df_final = _df_final.dropna(axis=1, how="all")
                    _df_final = _df_final.loc[:, (_df_final != "").any(axis=0)]

                    _rename_spec = {
                        "cod_identificare": "NR. CONTRACT",
                        "titlul_proiect": "OBIECTUL CONTRACTULUI",
                        "denumire_beneficiar": "BENEFICIAR",
                        "derulat_prin": "DERULAT PRIN",
                        "responsabil_idbdc": "RESPONSABIL",
                        "data_contract": "DATA CONTRACT",
                        "data_inceput": "DATA ÎNCEPUT",
                        "data_sfarsit": "DATA SFÂRȘIT",
                        "status_contract_proiect": "STATUS",
                        "valoare_totala_contract": "VALOARE TOTALĂ",
                        "cofinantare_totala_contract": "COFINANȚARE",
                        "valuta": "VALUTĂ",
                        "membri_echipa": "MEMBRI ECHIPĂ",
                    }
                    _df_final = _df_final.rename(columns={k: v for k, v in _rename_spec.items() if k in _df_final.columns})

                    for _val_col in ["VALOARE TOTALĂ", "COFINANȚARE"]:
                        if _val_col in _df_final.columns:
                            _df_final[_val_col] = _df_final[_val_col].apply(
                                lambda v: _fmt_numeric(v, _val_col) if v is not None and str(v).strip() not in ("", "None", "nan") else ""
                            )

                    st.dataframe(_df_final, use_container_width=True, height=400)
                    st.caption(f"Total: {len(_df_final)} contracte SPECIALE")

            except Exception as e:
                st.error(f"Eroare la încărcarea listei: {e}")
        st.markdown("---")

    if id_admin and str(id_admin).strip():
        if not cat_admin:
            st.warning("Nu ati selectat categoria de date.")
        elif cat_admin in ("Contracte", "Proiecte") and not tip_admin:
            if cat_admin == "Contracte":
                st.warning("Nu ati selectat tipul de contract.")
            else:
                st.warning("Nu ati selectat tipul de proiect.")

    st.divider()

    map_baze = {
        "CEP": "base_contracte_cep",
        "TERTI": "base_contracte_terti",
        "SPECIALE": "base_contracte_speciale",
        "FDI": "base_proiecte_fdi",
        "PNRR": "base_proiecte_pnrr",
        "INTERNATIONALE": "base_proiecte_internationale",
        "INTERREG": "base_proiecte_interreg",
        "NONEU": "base_proiecte_noneu",
        "SEE": "base_proiecte_see",
        "PNCDI": "base_proiecte_pncdi",
    }

    map_categorie_label = {
        "Contracte": "Contracte",
        "Proiecte": "Proiecte",
        "Evenimente stiintifice": "Evenimente stiintifice",
        "Proprietate intelectuala": "Proprietate intelectuala",
    }
    map_tip_label = {
        "CEP": "CEP", "TERTI": "TERTI", "SPECIALE": "SPECIALE",
        "FDI": "FDI", "PNRR": "PNRR", "PNCDI": "PNCDI",
        "INTERNATIONALE": "INTERNATIONALE", "INTERREG": "INTERREG", "NONEU": "NONEU", "SEE": "SEE",
    }

    if cat_admin in ("Contracte", "Proiecte"):
        tabela_baza = map_baze.get(tip_admin)
    elif cat_admin == "Evenimente stiintifice":
        tabela_baza = "base_evenimente_stiintifice"
    elif cat_admin == "Proprietate intelectuala":
        tabela_baza = "base_prop_intelect"
    else:
        tabela_baza = None

    if not tabela_baza:
        st.info("Selecteaza categoria si (daca este cazul) tipul.")
        return

    if not id_admin or str(id_admin).strip() == "":
        st.info("Introdu filtrul pentru a deschide fisa.")
        return

    cod = str(id_admin).strip()

    # ============================
    # ACȚIUNE
    # ============================

    st.markdown("**Acțiune**")
    actiune = st.radio(
        label="",
        options=["Modificare / completare fișă existentă", "Fișă nouă"],
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ============================
    # STRUCTURĂ TAB-URI
    # ============================

    if cat_admin in ("Contracte", "Proiecte"):
        tabele = [
            ("Date de baza", tabela_baza),
            ("Date financiare", "com_date_financiare"),
            ("Echipa", "com_echipe_proiect"),
            ("Aspecte tehnice", "com_aspecte_tehnice"),
        ]
    elif cat_admin == "Evenimente stiintifice":
        tabele = [
            ("Date de baza", tabela_baza),
            ("Aspecte tehnice", "com_aspecte_tehnice"),
        ]
    else:
        tabele = [
            ("Date de baza", tabela_baza),
            ("Aspecte tehnice", "com_aspecte_tehnice"),
        ]

    # ============================
    # LOAD / INIT STATE
    # ============================

    loaded = {}
    any_existing = False

    for _, table_name in tabele:
        df_loaded, cols_real, exists = load_single_row(table_name, cod)

        if actiune == "Fișă nouă" and not exists:
            if cols_real:
                df_work = prepare_empty_single_row(cols_real, cod)
            else:
                df_work = pd.DataFrame()
        else:
            if exists:
                df_work = df_loaded.copy()
                any_existing = True
            else:
                if cols_real:
                    df_work = prepare_empty_single_row(cols_real, cod)
                else:
                    df_work = pd.DataFrame()

        if table_name == tabela_baza and not df_work.empty:
            df_work = _apply_auto_values(df_work)

        st.session_state[state_key(table_name)] = df_work.copy()
        st.session_state[state_key_raw(table_name)] = df_work.copy()
        loaded[table_name] = (df_work.copy(), cols_real)

    validated_any = False
    detaliu_err = ""

    for _, table_name in tabele:
        df_raw = st.session_state.get(state_key_raw(table_name), pd.DataFrame())
        if "validat_idbdc" in df_raw.columns and len(df_raw):
            try:
                if bool(df_raw["validat_idbdc"].iloc[0]):
                    validated_any = True
                    break
            except Exception:
                pass

    editing_blocked = bool(validated_any and not is_admin)

    if any_existing:
        st.markdown(
            """
            <div style='background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.45);
                        border-radius:10px;padding:7px 14px;margin-bottom:4px;display:inline-block;'>
                <span style='color:#4ade80;font-weight:700;font-size:0.92rem;'>
                    ✅ Fișa a fost identificată și este pregătită pentru administrare.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if editing_blocked:
        st.markdown(
            f"""
            <div style='background:rgba(255,90,90,0.10);border:1px solid rgba(255,90,90,0.45);
                        border-radius:10px;padding:10px 14px;margin-bottom:8px;'>
                <span style='color:#ffb4b4;font-weight:800;font-size:0.96rem;'>⛔ Fișa este validată și blocată pentru modificare.</span>
                {("<span style='color:rgba(255,255,255,0.85);font-size:0.95rem;font-weight:600;margin-top:6px;display:block;'>Motiv: " + detaliu_err + "</span>") if detaliu_err else ""}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ============================
    # TAB-URI + EDITOR
    # ============================

    tabs = st.tabs([label for label, _ in tabele])
    edited_data = {}

    for i, (label, table_name) in enumerate(tabele):
        with tabs[i]:
            df_show = st.session_state[state_key(table_name)].copy()
            df_show = hide_control_cols(df_show)
            df_show = _prepare_display_df(table_name, df_show)

            if table_name == "com_echipe_proiect":
                edited_data[table_name] = _render_editor_echipa(table_name, df_show, editing_blocked)
                continue

            if table_name == "com_date_financiare" and tabela_baza == "base_proiecte_fdi":
                _render_fdi_financial_preview(df_show)

            if table_name == "base_proiecte_fdi":
                df_show = _reorder_df(df_show, FDI_BASE_ORDER)

            if table_name == "com_aspecte_tehnice":
                df_show = _reorder_df(df_show, TECHNIC_ORDER)

            edited_data[table_name] = _render_editor_standard(table_name, df_show, editing_blocked)

    # ============================
    # BUTOANE
    # ============================

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3)
    with b1:
        btn_save = st.button("💾 SALVARE FIȘĂ", disabled=editing_blocked)
    with b2:
        btn_validate = st.button("✅ VALIDARE FIȘĂ")
    with b3:
        btn_delete = st.button("🗑️ ȘTERGE FIȘA")

    # ============================
    # SALVARE
    # ============================

    if btn_save:
        operator = st.session_state.operator_identificat
        try:
            items = []
            for _, table_name in tabele:
                _, cols_real = loaded[table_name]
                if not cols_real:
                    continue

                df_base = st.session_state[state_key(table_name)].copy()

                if table_name == "com_echipe_proiect":
                    df_edit_visible = st.session_state.get(
                        f"echipa_reunited_{cod}",
                        edited_data.get(table_name, df_base)
                    )
                else:
                    editor_key = f"editor_{table_name}_{cod}"
                    editor_state = st.session_state.get(editor_key)

                    if editor_state is not None and isinstance(editor_state, dict):
                        edited_rows = editor_state.get("edited_rows", {})
                        added_rows = editor_state.get("added_rows", [])
                        deleted_rows = editor_state.get("deleted_rows", [])

                        for idx_str, changes in edited_rows.items():
                            idx = int(idx_str)
                            if idx < len(df_base):
                                for col, val in changes.items():
                                    df_base.at[df_base.index[idx], col] = val

                        for new_row in added_rows:
                            new_r = {c: None for c in df_base.columns}
                            new_r.update(new_row)
                            df_base = pd.concat([df_base, pd.DataFrame([new_r])], ignore_index=True)

                        if deleted_rows:
                            df_base = df_base.drop(index=[i for i in deleted_rows if i < len(df_base)]).reset_index(drop=True)

                        df_edit_visible = df_base
                    else:
                        df_edit_visible = edited_data.get(table_name, df_base)

                df_raw_original = st.session_state[state_key_raw(table_name)]

                if df_edit_visible is None or len(df_edit_visible) == 0:
                    continue

                if table_name == "com_echipe_proiect":
                    df_for_save = df_edit_visible.copy()
                    df_for_save["cod_identificare"] = cod
                    df_for_save = autofill_functie_upt(df_for_save)
                else:
                    if table_name == "com_date_financiare" and "total_buget_calc" in df_edit_visible.columns:
                        df_edit_visible = df_edit_visible.drop(columns=["total_buget_calc"], errors="ignore")

                    df_for_save = merge_back_control_cols(df_edit_visible, df_raw_original)
                    if "cod_identificare" in df_for_save.columns:
                        df_for_save["cod_identificare"] = df_for_save["cod_identificare"].fillna(cod)
                        df_for_save["cod_identificare"] = df_for_save["cod_identificare"].astype(str).replace("nan", cod)

                    if table_name == tabela_baza:
                        df_for_save = _apply_auto_values(df_for_save)

                for _, row in df_for_save.iterrows():
                    items.append({
                        "table": table_name,
                        "payload": row.to_dict(),
                    })

            ok, msg = direct_save_all_tables(items, operator)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

        except Exception as e:
            st.error(f"Eroare la salvare: {e}")

    # ============================
    # VALIDARE
    # ============================

    if btn_validate:
        operator = st.session_state.operator_identificat
        ok, msg = direct_validate_all_tables(cod, [t for _, t in tabele], operator)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

    # ============================
    # ȘTERGERE
    # ============================

    if btn_delete:
        ok, msg = direct_delete_all_tables(cod, [t for _, t in tabele])
        if ok:
            st.success(msg)
        else:
            st.error(msg)
