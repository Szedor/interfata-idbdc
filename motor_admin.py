import streamlit as st
import pandas as pd
from datetime import datetime


def porneste_motorul(supabase):

    # ============================
    # CONFIG
    # ============================
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
        """Detectează coloane numerice (INTEGER/FLOAT) după dtype și nume."""
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
                .select("nume_prenume,acronim_functie_upt") \
                .execute()
            return {
                r["nume_prenume"]: r.get("acronim_functie_upt", "")
                for r in (res.data or [])
                if r.get("nume_prenume")
            }
        except Exception:
            return {}

    def autofill_functie_upt(df: pd.DataFrame) -> pd.DataFrame:
        if "nume_prenume" not in df.columns or "functie_upt" not in df.columns:
            return df
        functie_map = load_functie_map()
        if not functie_map:
            return df
        for idx, row in df.iterrows():
            nume = row.get("nume_prenume")
            if nume and str(nume).strip():
                functie = functie_map.get(str(nume).strip(), "")
                if functie:
                    df.at[idx, "functie_upt"] = functie
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
                "status_contract_proiect":    "🔽 STATUS CONTRACT",
                "titlul_proiect":             "OBIECTUL CONTRACTULUI",
            },
            "base_contracte_terti": {
                "cod_identificare":           "NR. CONTRACT",
                "acronim_contracte_proiecte": "🔽 TIPUL DE CONTRACT",
                "status_contract_proiect":    "🔽 STATUS CONTRACT",
                "titlul_proiect":             "OBIECTUL CONTRACTULUI",
            },
            "base_contracte_speciale": {
                "cod_identificare":           "NR. CONTRACT",
                "acronim_contracte_proiecte": "🔽 TIPUL DE CONTRACT",
                "status_contract_proiect":    "🔽 STATUS CONTRACT",
                "titlul_proiect":             "OBIECTUL CONTRACTULUI",
            },
            "base_proiecte_fdi": {
                "cod_identificare":        "ID PROIECT FDI",
                "status_contract_proiect": "🔽 STATUS PROIECT",
                "titlul_proiect":          "TITLUL PROIECTULUI",
                "suma_solicitata_fdi":     "SUMA SOLICITATA",
                "cofinantare_upt_fdi":     "COFINANTARE UPT",
            },
            "base_proiecte_pncdi": {
                "cod_identificare":        "NR.CONTRACT / COD PROIECT",
                "status_contract_proiect": "🔽 STATUS PROIECT",
                "titlul_proiect":          "TITLUL PROIECTULUI",
            },
            "base_proiecte_pnrr": {
                "cod_identificare":        "COD PROIECT PNRR",
                "status_contract_proiect": "🔽 STATUS PROIECT",
                "titlul_proiect":          "TITLUL PROIECTULUI",
            },
            "base_proiecte_internationale": {
                "cod_identificare":        "COD / NR. PROIECT",
                "status_contract_proiect": "🔽 STATUS PROIECT",
                "titlul_proiect":          "TITLUL PROIECTULUI",
                "rol_upt":                 "ROL UPT IN PROIECT",
            },
            "base_proiecte_interreg": {
                "cod_identificare":        "COD PROIECT INTERREG",
                "status_contract_proiect": "🔽 STATUS PROIECT",
                "titlul_proiect":          "TITLUL PROIECTULUI",
                "rol_upt":                 "ROL UPT IN PROIECT",
            },
            "base_proiecte_noneu": {
                "cod_identificare":        "COD / NR. PROIECT",
                "status_contract_proiect": "🔽 STATUS PROIECT",
                "titlul_proiect":          "TITLUL PROIECTULUI",
                "rol_upt":                 "ROL UPT IN PROIECT",
            },
            "base_evenimente_stiintifice": {
                "cod_identificare":  "COD EVENIMENT",
                "titlul_eveniment":  "TITLUL EVENIMENTULUI",
                "natura_eveniment":  "NATURA EVENIMENTULUI",
                "format_eveniment":  "FORMATUL EVENIMENTULUI",
                "loc_desfasurare":   "LOCUL DE DESFASURARE",
            },
            "base_prop_intelect": {
                "cod_identificare":       "NR. CERERE / BREVET",
                "acronim_prop_intelect":  "FORMA DE PROTECTIE",
                "titlul_proiect":         "TITLUL INVENTIEI / LUCRARII",
                "data_depozit_cerere":    "DATA DEPUNERE LA OSIM",
                "data_oficiala_acordare": "DATA ACORDARE",
                "numar_oficial_acordare": "NR. OFICIAL ACORDARE",
            },
        }

        # [FIX-6] Override etichete in tabele auxiliare pe baza contextului (contract vs proiect)
        # ctx = tabela_baza_ctx sau table_name insusi
        ctx = tabela_baza_ctx or table_name
        is_contract_ctx = ctx in TABELE_CONTRACTE

        def _col_label_admin(col: str, tbl: str = None) -> str:
            # 1. Override per tabela de baza (cel mai specific)
            if tbl and tbl in COL_LABELS_PER_TABLE_ADMIN:
                if col in COL_LABELS_PER_TABLE_ADMIN[tbl]:
                    return COL_LABELS_PER_TABLE_ADMIN[tbl][col]
            # 2. Override contextual pentru tabele auxiliare (echipa, financiar, etc.)
            if is_contract_ctx and tbl not in COL_LABELS_PER_TABLE_ADMIN:
                if col == "cod_identificare":
                    return "NR. CONTRACT"
                if col == "functia_specifica":
                    return "ROLUL IN CONTRACT"
            # 3. Label generic
            return COL_LABELS_ADMIN.get(col, col.replace("_", " ").capitalize())

        rel = DROPDOWN_MAP.get(table_name, {})
        cfg = {}

        # [3] Coloanele auto-preluate din selectoare nu mai au dropdown — sunt TextColumn disabled
        AUTO_FILLED_COLS = {"denumire_categorie", "acronim_contracte_proiecte"}

        for target_col, (src_table, src_col) in rel.items():
            if target_col not in df.columns:
                continue
            # [3] Daca e coloana auto-completata, afisam ca text readonly
            if target_col in AUTO_FILLED_COLS:
                cfg[target_col] = st.column_config.TextColumn(
                    label=_col_label_admin(target_col, table_name),
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
                label=_col_label_admin(target_col, table_name),
                options=options,
                required=False,
                help="🔽 Selectează din listă",
            )

        if table_name == "com_echipe_proiect" and "persoana_contact" in df.columns:
            df["persoana_contact"] = df["persoana_contact"].apply(
                lambda v: True if v is True or str(v).strip().upper() in ("TRUE", "DA", "1") else False
            )
            # [FIX-6iv] Ascundem coloana persoana_contact pentru contracte
            if not is_contract_ctx:
                cfg["persoana_contact"] = st.column_config.CheckboxColumn(
                    label=_col_label_admin("persoana_contact", table_name),
                    help="Bifează dacă persoana reprezintă IDBDC în proiect",
                    default=False,
                )

        if table_name == "com_echipe_proiect" and "functie_upt" in df.columns:
            cfg["functie_upt"] = st.column_config.TextColumn(
                label=_col_label_admin("functie_upt", table_name),
                help="Completat automat din det_resurse_umane",
                disabled=True,
            )

        for c in df.columns:
            if c in CONTROL_COLS:
                continue
            if is_date_col(c):
                cfg[c] = st.column_config.DateColumn(
                    label=_col_label_admin(c, table_name),
                    format="YYYY-MM-DD",
                    step=1,
                    help="📅 Click pentru a selecta data din calendar",
                )

        for c in df.columns:
            if c in CONTROL_COLS:
                continue
            if is_year_col(c):
                cfg[c] = st.column_config.NumberColumn(
                    label=_col_label_admin(c, table_name),
                    min_value=1900,
                    max_value=2100,
                    step=1,
                    format="%d",
                )

        if "nr_crt" in df.columns and "nr_crt" not in cfg:
            cfg["nr_crt"] = st.column_config.NumberColumn(
                label="NR.CRT.",
                disabled=True,
                format="%d",
            )

        for c in df.columns:
            if c in cfg:
                continue
            if c in CONTROL_COLS:
                continue
            if is_numeric_col(c, df):
                cfg[c] = st.column_config.NumberColumn(
                    label=_col_label_admin(c, table_name),
                    step=1,
                )

        for c in df.columns:
            if c in cfg:
                continue
            if c in CONTROL_COLS:
                continue
            cfg[c] = st.column_config.TextColumn(
                label=_col_label_admin(c, table_name),
            )

        return cfg

    # ============================
    # NOMENCLATOARE & DETALII (ADMIN ONLY)
    # ============================

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
                    to_delete = edited[edited["__STERGE__"] == True]  # noqa: E712
                    for _, row in to_delete.iterrows():
                        key_val = row.get(pk)
                        if key_val is None or str(key_val).strip() == "":
                            continue
                        supabase.table(tabela).delete().eq(pk, key_val).execute()

                    to_upsert = edited[edited["__STERGE__"] != True].copy()  # noqa: E712
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

    # ============================
    # FILTRE OPERATOR din session_state
    # ============================
    _rol_c2            = (st.session_state.get("operator_rol") or "").strip().upper()
    _filtru_categorii  = st.session_state.get("operator_filtru_categorie") or []
    _filtru_tipuri     = st.session_state.get("operator_filtru_tipuri") or []

    # Toate categoriile posibile
    _toate_cat = ["Contracte", "Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"]
    # Daca operatorul are filtru_categorie completat, limitam; altfel (ADMIN fara filtru) arata tot
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
            _toate_proiecte = ["FDI", "PNRR", "PNCDI", "INTERNATIONALE", "INTERREG", "NONEU"]
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
                # ── 1. Date de bază ──────────────────────────────────────
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

                    # ── 2. Date financiare ───────────────────────────────
                    try:
                        _res_fin = (supabase.table("com_date_financiare")
                                    .select("cod_identificare, valoare_totala_contract, "
                                            "cofinantare_totala_contract, valuta")
                                    .in_("cod_identificare", _coduri)
                                    .execute())
                        _df_fin = pd.DataFrame(_res_fin.data or [])
                        if not _df_fin.empty:
                            # Pastreaza doar coloanele cu cel putin o valoare non-nula
                            _df_fin = _df_fin.dropna(axis=1, how="all")
                            _df_fin = _df_fin.groupby("cod_identificare", as_index=False).first()
                    except Exception:
                        _df_fin = pd.DataFrame()

                    # ── 3. Echipă — concatenare membri per contract ──────
                    try:
                        _res_ech = (supabase.table("com_echipe_proiect")
                                    .select("cod_identificare, nume_prenume, "
                                            "functia_specifica, persoana_contact")
                                    .in_("cod_identificare", _coduri)
                                    .execute())
                        _df_ech = pd.DataFrame(_res_ech.data or [])
                        if not _df_ech.empty:
                            # Persoana de contact prima, apoi restul alfabetic
                            _df_ech = _df_ech.sort_values(
                                ["cod_identificare", "persoana_contact"],
                                ascending=[True, False]
                            )
                            _df_ech_grp = (_df_ech.groupby("cod_identificare", as_index=False)
                                           .agg(membri_echipa=("nume_prenume", lambda x: ", ".join(x.dropna()))))
                        else:
                            _df_ech_grp = pd.DataFrame()
                    except Exception:
                        _df_ech_grp = pd.DataFrame()

                    # ── 4. Join toate ────────────────────────────────────
                    _df_final = _df_base.copy()
                    if not _df_fin.empty and "cod_identificare" in _df_fin.columns:
                        _df_final = _df_final.merge(_df_fin, on="cod_identificare", how="left")
                    if not _df_ech_grp.empty and "cod_identificare" in _df_ech_grp.columns:
                        _df_final = _df_final.merge(_df_ech_grp, on="cod_identificare", how="left")

                    # ── 5. Elimina coloanele complet goale ───────────────
                    _df_final = _df_final.dropna(axis=1, how="all")
                    _df_final = _df_final.loc[:, (_df_final != "").any(axis=0)]

                    # ── 6. Etichete frumoase ─────────────────────────────
                    _rename_spec = {
                        "cod_identificare":           "NR. CONTRACT",
                        "titlul_proiect":             "OBIECTUL CONTRACTULUI",
                        "denumire_beneficiar":        "BENEFICIAR",
                        "derulat_prin":               "DERULAT PRIN",
                        "responsabil_idbdc":          "RESPONSABIL",
                        "data_contract":              "DATA CONTRACT",
                        "data_inceput":               "DATA ÎNCEPUT",
                        "data_sfarsit":               "DATA SFÂRȘIT",
                        "status_contract_proiect":    "STATUS",
                        "valoare_totala_contract":    "VALOARE TOTALĂ",
                        "cofinantare_totala_contract":"COFINANȚARE",
                        "valuta":                     "VALUTĂ",
                        "membri_echipa":              "MEMBRI ECHIPĂ",
                    }
                    _df_final = _df_final.rename(columns={k: v for k, v in _rename_spec.items() if k in _df_final.columns})

                    st.dataframe(_df_final, use_container_width=True, height=400)
                    st.caption(f"Total: {len(_df_final)} contracte SPECIALE")

            except Exception as e:
                st.error(f"Eroare la încărcarea listei: {e}")
        st.markdown("---")

    # [4] Avertismente daca operatorul introduce cod fara sa selecteze categoria/tipul
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
        "PNCDI": "base_proiecte_pncdi",
    }

    # [1][2] Mapari pentru auto-preluare in gridul Date de baza
    map_categorie_label = {
        "Contracte":               "Contracte",
        "Proiecte":                "Proiecte",
        "Evenimente stiintifice":  "Evenimente stiintifice",
        "Proprietate intelectuala":"Proprietate intelectuala",
    }
    map_tip_label = {
        "CEP": "CEP", "TERTI": "TERTI", "SPECIALE": "SPECIALE",
        "FDI": "FDI", "PNRR": "PNRR", "PNCDI": "PNCDI",
        "INTERNATIONALE": "INTERNATIONALE", "INTERREG": "INTERREG", "NONEU": "NONEU",
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
            ("Date de bază", tabela_baza),
            ("Date financiare", "com_date_financiare"),
            ("Echipă", "com_echipe_proiect"),
            ("Aspecte tehnice", "com_aspecte_tehnice"),
        ]
    else:
        tabele = [
            ("Date de bază", tabela_baza),
            ("Echipă", "com_echipe_proiect"),
        ]

    table_names = [t for _, t in tabele]

    # ============================
    # [FIX-4] Curățare session_state la schimbarea codului
    # ============================

    _prev_cod_key = "admin_prev_cod"
    _prev_tabela_key = "admin_prev_tabela"
    prev_cod = st.session_state.get(_prev_cod_key)
    prev_tabela = st.session_state.get(_prev_tabela_key)

    if prev_cod != cod or prev_tabela != tabela_baza:
        # Cod sau categoria s-a schimbat — ștergem datele vechi din session_state
        for _, tn in tabele:
            for k in (f"df_admin__{tn}", f"df_admin_raw__{tn}",
                      f"editor_{tn}_{prev_cod}", f"editor_echipa_rep_{prev_cod}",
                      f"editor_echipa_rest_{prev_cod}", f"echipa_filter_{prev_cod}",
                      f"toggle_deblocat_{prev_cod}"):
                if k in st.session_state:
                    del st.session_state[k]
        st.session_state[_prev_cod_key] = cod
        st.session_state[_prev_tabela_key] = tabela_baza

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
    if actiune == "Modificare / completare fișă existentă" and not base_exists:
        st.warning("Nu există fișă pentru acest cod în baza de date. Alege «Fișă nouă» dacă vrei să creezi.")
        return

    for _, table_name in tabele:
        # Nu suprascrie session_state dacă datele sunt deja încărcate pentru același cod
        # (evităm pierderea editărilor la rerun-uri intermediare)
        if state_key_raw(table_name) in st.session_state:
            continue

        df, cols = loaded[table_name]
        if df.empty and cols:
            df_full = prepare_empty_single_row(cols, cod)
        else:
            df_full = df.copy()

        # [1][2] Auto-preluare categorie si tip din selectoarele de sus — pentru tabela de baza
        if table_name == tabela_baza:
            if "denumire_categorie" in df_full.columns and cat_admin:
                # Cautam valoarea exacta din nomenclator care corespunde categoriei selectate
                opts_cat = load_dropdown_options("nom_categorie", "denumire_categorie")
                match_cat = next((o for o in opts_cat if cat_admin.upper() in o.upper()), None)
                if match_cat:
                    df_full["denumire_categorie"] = match_cat
            if "acronim_contracte_proiecte" in df_full.columns and tip_admin:
                # Contracte sau Proiecte — sursa diferita
                src_tip = "nom_contracte" if cat_admin == "Contracte" else "nom_proiecte"
                col_tip = "acronim_tip_contract" if cat_admin == "Contracte" else "acronim_tip_proiect"
                opts_tip = load_dropdown_options(src_tip, col_tip)
                match_tip = next((o for o in opts_tip if tip_admin.upper() in o.upper()), None)
                if match_tip:
                    df_full["acronim_contracte_proiecte"] = match_tip
                else:
                    # Fallback direct — dacă nomenclatorul nu are valoarea exactă
                    df_full["acronim_contracte_proiecte"] = tip_admin
        st.session_state[state_key_raw(table_name)] = df_full.copy()
        st.session_state[state_key(table_name)] = hide_control_cols(df_full)

    base_full = st.session_state[state_key_raw(tabela_baza)]

    # ============================
    # BLOCARE / DEBLOCARE FIȘĂ
    # ============================

    toggle_key = f"toggle_deblocat_{cod}"

    if toggle_key not in st.session_state:
        st.session_state[toggle_key] = True

    _toggle_color = "#22c55e" if st.session_state[toggle_key] else "#ef4444"
    st.markdown(
        f"""
        <style>
        div[data-testid="stToggle"] input:checked + div,
        div[data-testid="stToggle"] input:checked ~ div[data-baseweb="toggle"] > div {{
            background-color: #22c55e !important;
        }}
        div[data-testid="stToggle"] input:not(:checked) + div,
        div[data-testid="stToggle"] input:not(:checked) ~ div[data-baseweb="toggle"] > div {{
            background-color: #ef4444 !important;
        }}
        div[data-baseweb="toggle"] > div {{
            background-color: {_toggle_color} !important;
            border-color: {_toggle_color} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    deblocat = st.toggle(
        "🔓 Fișa este deblocată" if st.session_state[toggle_key] else "🔒 Fișa este blocată",
        key=toggle_key,
        help="OFF = Fișa este blocată (doar citire). ON = Fișa este deblocată (editare activă).",
    )

    editing_blocked = not deblocat

    if deblocat:
        st.markdown(
            "<div style='background:rgba(34,197,94,0.18);border:1px solid rgba(34,197,94,0.60);"
            "border-radius:10px;padding:8px 16px;margin-bottom:6px;'>"
            "<span style='color:#4ade80;font-weight:700;font-size:0.97rem;'>"
            "✅ Fișa este deblocată. Editarea este activă."
            "</span></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='background:rgba(239,68,68,0.18);border:1px solid rgba(239,68,68,0.60);"
            "border-radius:10px;padding:8px 16px;margin-bottom:6px;'>"
            "<span style='color:#f87171;font-weight:700;font-size:0.97rem;'>"
            "🔒 Fișa este blocată. Mută toggle-ul pe ON pentru a edita."
            "</span></div>",
            unsafe_allow_html=True,
        )

    # ============================
    # EDITOR ECHIPĂ — două zone separate
    # ============================

    def _render_echipa_editor(df_show, col_cfg, cod, editing_blocked, edited_data, state_key, table_name):
        """
        Un singur tabel pentru toata echipa.
        Coloana persoana_contact (True/False) vizibila doar operatorului — determina cine e persoana de contact.
        """
        persoane_disponibile = load_dropdown_options("det_resurse_umane", "nume_prenume")

        col_cfg_echipa = dict(col_cfg)

        if "nume_prenume" in df_show.columns:
            col_cfg_echipa["nume_prenume"] = st.column_config.SelectboxColumn(
                label="🔽 NUME SI PRENUME",
                options=persoane_disponibile,
                required=True,
                help="🔽 Selecteaza persoana din lista angajatilor",
            )

        if "persoana_contact" in df_show.columns:
            col_cfg_echipa["persoana_contact"] = st.column_config.CheckboxColumn(
                label="PERSOANA DE CONTACT",
                help="Bifeaza daca persoana este persoana de contact pentru acest contract/proiect",
                default=False,
            )

        # cod_identificare ascuns din editor — se completeaza automat la salvare
        cols_echipa_show = [c for c in df_show.columns if c != "cod_identificare"]
        df_show_edit = df_show[cols_echipa_show].copy()
        col_cfg_echipa.pop("cod_identificare", None)

        # Asiguram ca persoana_contact e boolean
        if "persoana_contact" in df_show_edit.columns:
            df_show_edit["persoana_contact"] = df_show_edit["persoana_contact"].apply(
                lambda v: True if v is True or str(v).strip().upper() in ("TRUE", "DA", "1") else False
            )

        filter_key = f"echipa_filter_{cod}"
        filtru = st.text_input(
            "🔍 Filtreaza dupa nume",
            value="",
            key=filter_key,
            placeholder="Tasteaza pentru a filtra lista...",
            label_visibility="collapsed",
        ).strip().lower()

        df_filtered = df_show_edit.copy()
        if filtru and "nume_prenume" in df_filtered.columns:
            df_filtered = df_filtered[
                df_filtered["nume_prenume"].astype(str).str.lower().str.contains(filtru, na=False)
            ].reset_index(drop=True)

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
            df_filtered,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config=col_cfg_echipa,
            disabled=editing_blocked,
            key=key_editor,
            height=420,
        )

        # Completam cod_identificare pe toate randurile
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
        edited_data[table_name] = edited_echipa
    # ============================
    # TAB-URI + EDITOR
    # ============================

    tabs = st.tabs([label for label, _ in tabele])
    edited_data = {}

    for i, (label, table_name) in enumerate(tabele):
        with tabs[i]:
            df_show = st.session_state[state_key(table_name)].copy()

            # Ascunde an_referinta din Date de baza pentru tabele de contracte
            if table_name in ("base_contracte_terti", "base_contracte_speciale", "base_contracte_cep"):
                df_show = df_show.drop(columns=["an_referinta"], errors="ignore")

            if table_name == "com_date_financiare" and "an_referinta" in df_show.columns and "valuta" in df_show.columns:
                cols = list(df_show.columns)
                cols.remove("valuta")
                idx = cols.index("an_referinta") + 1
                cols.insert(idx, "valuta")
                df_show = df_show[cols]

            col_cfg = build_column_config_for_table(table_name, df_show, tabela_baza_ctx=tabela_baza)

            if table_name == "com_echipe_proiect":
                _render_echipa_editor(
                    df_show, col_cfg, cod, editing_blocked,
                    edited_data, state_key, table_name,
                )
                continue

            num_rows_mode = "dynamic" if table_name == "com_date_financiare" else "fixed"
            editor_key = f"editor_{table_name}_{cod}"

            edited = st.data_editor(
                df_show,
                use_container_width=True,
                hide_index=True,
                num_rows=num_rows_mode,
                column_config=col_cfg,
                disabled=editing_blocked,
                key=editor_key,
            )
            edited_data[table_name] = edited

    # ============================
    # STATUS FIȘĂ
    # ============================

    if len(base_full) > 0 and st.session_state.get("operator_rol") == "ADMIN":
        with st.expander("Status fișă (ADMIN)", expanded=False):
            r = base_full.iloc[0].to_dict()
            s1, s2, s3, s4 = st.columns([1.2, 2.2, 1.0, 1.6])
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

    # ============================
    # MESAJ PERSISTENT
    # ============================

    if "admin_msg" in st.session_state:
        msg_type, msg_text = st.session_state.pop("admin_msg")
        if msg_type == "success":
            st.markdown(
                f"""
                <div style='
                    background: rgba(30,180,80,0.22);
                    border: 2px solid rgba(30,220,100,0.75);
                    border-radius: 14px;
                    padding: 18px 28px;
                    margin: 12px 0 16px 0;
                    text-align: center;
                '>
                    <span style='font-size:2.2rem;'>✅</span><br>
                    <span style='color:#80ffb0;font-size:1.35rem;font-weight:900;letter-spacing:0.02em;'>
                        {msg_text}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            parts = str(msg_text).split(":", 1)
            titlu_err = parts[0].strip()
            detaliu_err = parts[1].strip() if len(parts) > 1 else ""
            st.markdown(
                f"""
                <div style='
                    background: rgba(220,50,50,0.20);
                    border: 2px solid rgba(255,80,80,0.70);
                    border-radius: 14px;
                    padding: 18px 28px;
                    margin: 12px 0 16px 0;
                    text-align: center;
                '>
                    <span style='font-size:2.2rem;'>❌</span><br>
                    <span style='color:#ffaaaa;font-size:1.35rem;font-weight:900;'>
                        {titlu_err}
                    </span>
                    {"<br><span style='color:rgba(255,180,180,0.85);font-size:0.95rem;font-weight:600;margin-top:6px;display:block;'>Motiv: " + detaliu_err + "</span>" if detaliu_err else ""}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ============================
    # BUTOANE
    # ============================

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        btn_save = st.button("💾 SALVARE FIȘĂ", disabled=editing_blocked)
    with b2:
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
                    # [FIX-3] Citim din session_state — supraviețuiește rerun-ului
                    df_edit_visible = st.session_state.get(
                        f"echipa_reunited_{cod}",
                        edited_data.get(table_name, df_base)
                    )
                else:
                    editor_key = f"editor_{table_name}_{cod}"
                    editor_state = st.session_state.get(editor_key)

                    if editor_state is not None and isinstance(editor_state, dict):
                        edited_rows  = editor_state.get("edited_rows", {})
                        added_rows   = editor_state.get("added_rows", [])
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
                    # Echipa: nu folosim merge_back (ar trunchia rândurile)
                    # Setăm cod_identificare direct pe toate rândurile
                    df_for_save = df_edit_visible.copy()
                    df_for_save["cod_identificare"] = cod
                    df_for_save = autofill_functie_upt(df_for_save)
                else:
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
                    items.append({"table": table_name, "payload": payload})

            ok, msg = direct_save_all_tables(items, operator)
            if ok:
                st.session_state["admin_msg"] = ("success", "✅ Fișa a fost salvată")
            else:
                st.session_state["admin_msg"] = ("error", f"Fișa nu a putut fi salvată: {msg}")
            st.rerun()

        except Exception as e:
            st.session_state["admin_msg"] = ("error", f"Fișa nu a putut fi salvată: {e}")
            st.rerun()

    # ============================
    # ȘTERGERE + CONFIRMARE
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
                    st.session_state["admin_msg"] = ("success", msg)
                else:
                    st.session_state["admin_msg"] = ("error", f"Eroare la ștergere: {msg}")
                st.rerun()
            except Exception as e:
                st.session_state["admin_msg"] = ("error", f"Eroare la ștergere: {e}")
                st.rerun()
        else:
            st.info("Bifează confirmarea și tastează exact codul pentru a executa ștergerea.")
