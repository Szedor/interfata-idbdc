import streamlit as st
import pandas as pd
from datetime import datetime


def porneste_motorul(supabase):

    # ============================
    # CONFIG
    # ============================

    def _fmt_numeric(val) -> str:
        """Formatează valorile numerice cu separator de mii și 2 zecimale (format românesc)."""
        if val is None:
            return ""
        try:
            f = float(str(val).replace(",", ".").strip())
            return f"{f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            return str(val)
    ADMIN_ONLY_COLS = {
        "responsabil_idbdc", "observatii_idbdc",
        "status_confirmare", "data_ultimei_modificari", "validat_idbdc",
        "creat_de", "creat_la", "modificat_de", "modificat_la",
    }

    is_admin = st.session_state.get("operator_rol") == "ADMIN"

    CONTROL_COLS = [
        "responsabil_idbdc",
        "observatii_idbdc",
        "status_confirmare",
        "data_ultimei_modificari",
        "validat_idbdc",
    ]

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

    STATIC_OPTIONS = {"VALUTA_3": ["LEI", "EUR", "USD"]}

    # Tabele baza pentru contracte — folosit pentru override etichete
    TABELE_CONTRACTE = {"base_contracte_cep", "base_contracte_terti", "base_contracte_speciale"}

    # ============================
    # HELPERS
    # ============================

    def now_iso():
        return datetime.now().isoformat()

    def current_year():
        return datetime.now().year

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
        """Detectează coloane numerice reale, fără a trata codurile de identificare ca valori numerice."""
        c = (col or "").lower()
        if c == "cod_identificare":
            return False
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

    def normalize_identifier_column(df: pd.DataFrame) -> pd.DataFrame:
        """Forțează cod_identificare să fie text simplu, fără zecimale sau separatori numerici."""
        if "cod_identificare" not in df.columns:
            return df

        def _normalize_code(v):
            if v is None:
                return None
            if isinstance(v, float):
                if pd.isna(v):
                    return None
                if v.is_integer():
                    return str(int(v))
                return str(v)
            if isinstance(v, int):
                return str(v)
            s = str(v).strip()
            if s == "" or s.lower() in ("none", "nan"):
                return None
            return s

        out = df.copy()
        out["cod_identificare"] = out["cod_identificare"].apply(_normalize_code).astype("object")
        return out

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

        df = normalize_identifier_column(df)
        return df, cols, True

    def prepare_empty_single_row(cols: list, cod: str):
        if not cols:
            return pd.DataFrame()
        r = empty_row(cols)
        if "cod_identificare" in r:
            r["cod_identificare"] = cod
        import datetime as _dt
        df = pd.DataFrame([r], columns=cols)
        for c in df.columns:
            if is_date_col(c):
                df[c] = df[c].apply(lambda v: None if v is None else (v if isinstance(v, _dt.date) else None))
        df = normalize_identifier_column(df)
        return df

    def append_observatii(existing: str, msg: str) -> str:
        base = (existing or "").strip()
        if not base:
            return msg
        return base + "\n" + msg

    def hide_control_cols(df: pd.DataFrame) -> pd.DataFrame:
        df = normalize_identifier_column(df)
        if is_admin:
            return df
        cols = [c for c in df.columns if c not in ADMIN_ONLY_COLS]
        out = df[cols] if cols else df
        return normalize_identifier_column(out)

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
        return normalize_identifier_column(out)

    def fmt_bool(v):
        return "DA" if bool(v) else "NU"

    def is_row_effectively_empty(d: dict) -> bool:
        cod = d.get("cod_identificare")
        if cod is None or (isinstance(cod, str) and cod.strip() == ""):
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

    def direct_upsert_single_row(table_name: str, payload: dict, cod: str):
        try:
            check = supabase.table(table_name).select("cod_identificare").eq("cod_identificare", cod).limit(1).execute()
            exists = bool(check.data)
        except Exception:
            exists = False

        if exists:
            try:
                supabase.table(table_name).update(payload).eq("cod_identificare", cod).execute()
                return
            except Exception as e:
                raise Exception(f"Update eșuat pe {table_name}: {e}")
        else:
            try:
                supabase.table(table_name).insert(payload).execute()
                return
            except Exception as e:
                raise Exception(f"Insert eșuat pe {table_name}: {e}")

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
            res = supabase.table("det_resurse_umane") \
                .select("nume_prenume,acronim_functie_upt,acronim_departament") \
                .execute()
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

    def build_column_config_for_table(table_name: str, df: pd.DataFrame, tabela_baza_ctx: str = None):
        """
        tabela_baza_ctx: tabela de baza activa (ex: 'base_contracte_cep') — pentru override etichete
        in tabelele auxiliare (com_echipe_proiect, com_date_financiare, etc.)
        """
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

        COL_LABELS_ADMIN = {
            "denumire_categorie":         "🔽 CATEGORIE",
            "acronim_contracte_proiecte": "🔽 TIPUL DE CONTRACT",
            "status_contract_proiect":    "🔽 STATUS CONTRACT/PROIECT",
            "cod_domeniu_fdi":            "🔽 COD DOMENIU FDI",
            "natura_eveniment":           "🔽 NATURA EVENIMENTULUI STIINTIFIC",
            "format_eveniment":           "🔽 FORMATUL EVENIMENTULUI STIINTIFIC",
            "acronim_prop_intelect":      "🔽 FORME DE PROTECTIE",
            "nume_prenume":               "🔽 NUME SI PRENUME",
            "status_personal":            "🔽 STATUS PERSONAL",
            "valuta":                     "🔽 VALUTA",
            "acronim_functie_upt":        "🔽 ABREVIERE FUNCTIE UPT",
            "acronim_departament":        "🔽 ACRONIM DEPARTAMENT",
            "cod_universitate":           "🔽 COD UNIVERSITATE",
            "persoana_contact":           "PERSOANA DE CONTACT",
            "functie_upt":                "Abreviere functie UPT (auto)",
            "data_contract":              "📅 DATA CONTRACTULUI",
            "data_inceput":               "📅 DATA DE INCEPUT",
            "data_sfarsit":               "📅 DATA DE SFARSIT",
            "data_semnare":               "📅 DATA SEMNARE",
            "data_depunere":              "📅 DATA DEPUNERE",
            "data_acordare":              "📅 DATA ACORDARE",
            "data_eveniment":             "📅 DATA EVENIMENT",
            "data_inceput_rol":           "📅 DATA DE INCEPUT ROL",
            "data_sfarsit_rol":           "📅 DATA DE SFARSIT ROL",
            "data_depozit_cerere":        "📅 DATA DEPUNERE CERERE LA OSIM",
            "data_oficiala_acordare":     "📅 DATA OFICIALA DE ACORDARE",
            "data_inceput_valabilitate":  "📅 DATA DE INCEPUT VALABILITATE",
            "data_sfarsit_valabilitate":  "📅 DATA DE SFARSIT VALABILITATE",
            "data_apel":                  "📅 DATA APELULUI",
            "abreviere_domeniu_fdi": "DOMENIUL FDI",
            "program":               "PROGRAM",
            "subprogram":            "SUBPROGRAM",
            "instrument_finantare":  "INSTRUMENT DE FINANTARE",
            "apel":                  "APEL",
            "pilon":                 "PILON",
            "componenta":            "COMPONENTA",
            "reforma":               "REFORMA",
            "investitie":            "INVESTITIE",
            "sursa_finantare":       "SURSA DE FINANTARE",
            "programul_tematic":     "PROGRAMUL TEMATIC",
            "componenta_axa":        "COMPONENTA / AXA",
            "obiectiv_specific":     "OBIECTIV SPECIFIC",
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

        # Override etichete pentru tabela de baza
        COL_LABELS_PER_TABLE_ADMIN = {
            "base_contracte_cep": {
                "cod_identificare":           "NR. CONTRACT",
                "acronim_contracte_proiecte": "🔽 TIPUL DE CONTRACT",
                "status_
