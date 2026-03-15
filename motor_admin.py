import streamlit as st
import pandas as pd
from datetime import datetime


def porneste_motorul(supabase):

    # ============================
    # CONFIG
    # ============================
    # Câmpuri vizibile și editabile DOAR de ADMIN
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

    def empty_row(columns):
        row = {c: None for c in columns}
        if "status_confirmare" in row:
            row["status_confirmare"] = False
        if "validat_idbdc" in row:
            row["validat_idbdc"] = False
        if "reprezinta_idbdc" in row:
            row["reprezinta_idbdc"] = False
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

        # Forțăm tipul corect pentru coloanele date — explicit datetime.date sau None
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
            return df  # ADMIN vede toate coloanele
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
        """Rândul e 'gol' doar dacă lipsește și cod_identificare."""
        cod = d.get("cod_identificare")
        if cod is None or (isinstance(cod, str) and cod.strip() == ""):
            return True
        return False

    def cleanup_payload(payload: dict) -> dict:
        """Păstrează toate câmpurile cu valoare, plus întotdeauna cod_identificare."""
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
                # cod_identificare se păstrează mereu dacă e prezent
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
        """Insert dacă nu există, update dacă există — fără upsert (evităm dep. de UNIQUE constraint)."""
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

    def build_column_config_for_table(table_name: str, df: pd.DataFrame):
        DROPDOWN_MAP = {
            "base_contracte_cep": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_contracte", "acronim_contracte"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            },
            "base_contracte_terti": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_contracte", "acronim_contracte"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            },
            "base_contracte_speciale": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_contracte", "acronim_contracte"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            },
            "base_proiecte_fdi": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_proiecte", "acronim_proiecte"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
                "cod_domeniu_fdi": ("nom_domenii_fdi", "cod_domeniu_fdi"),
            },
            "base_proiecte_internationale": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_proiecte", "acronim_proiecte"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            },
            "base_proiecte_interreg": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_proiecte", "acronim_proiecte"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            },
            "base_proiecte_noneu": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_proiecte", "acronim_proiecte"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            },
            "base_proiecte_pncdi": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_proiecte", "acronim_proiecte"),
                "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            },
            "base_proiecte_pnrr": {
                "denumire_categorie": ("nom_categorie", "denumire_categorie"),
                "acronim_contracte_proiecte": ("nom_proiecte", "acronim_proiecte"),
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

        # Etichete frumoase pentru coloane în data_editor
        COL_LABELS_ADMIN = {
            # Dropdown-uri — emoji 🔽 important pentru editor
            "denumire_categorie":         "🔽 Categorie",
            "acronim_contracte_proiecte": "🔽 Tipul de contract sau proiect",
            "status_contract_proiect":    "🔽 Status contract/proiect",
            "cod_domeniu_fdi":            "🔽 Cod domeniu FDI",
            "natura_eveniment":           "🔽 Natura evenimentului stiintific",
            "format_eveniment":           "🔽 Formatul evenimentului stiintific",
            "acronim_prop_intelect":      "🔽 Forme de protectie",
            "nume_prenume":               "🔽 Nume si prenume",
            "status_personal":            "🔽 Status personal",
            "valuta":                     "🔽 Valuta",
            "acronim_functie_upt":        "🔽 Abreviere functie UPT",
            "acronim_departament":        "🔽 Acronim departament",
            "cod_universitate":           "🔽 Cod universitate",
            "reprezinta_idbdc":           "Reprezinta contractul/proiectul",
            "functie_upt":                "Abreviere functie UPT (auto)",
            # Date — emoji 📅
            "data_contract":              "📅 Data contractului",
            "data_inceput":               "📅 Data de inceput",
            "data_sfarsit":               "📅 Data de sfarsit",
            "data_semnare":               "📅 Data semnare",
            "data_depunere":              "📅 Data depunere",
            "data_acordare":              "📅 Data acordare",
            "data_eveniment":             "📅 Data eveniment",
            "data_inceput_rol":           "📅 Data de inceput rol",
            "data_sfarsit_rol":           "📅 Data de sfarsit rol",
            "data_depozit_cerere":        "📅 Data depunere cerere la OSIM",
            "data_oficiala_acordare":     "📅 Data oficiala de acordare",
            "data_inceput_valabilitate":  "📅 Data de inceput valabilitate",
            "data_sfarsit_valabilitate":  "📅 Data de sfarsit valabilitate",
            "data_apel":                  "📅 Data apelului",
            "abreviere_domeniu_fdi": "DOMENIUL FDI",
            "acronim_contracte": "ACRONIM TIP PROIECTE",
            "acronim_proiect": "ACRONIM TIP PROIECTE",
            "acronim_proiecte": "ACRONIM TIP PROIECTE",
            "activitati_proiect": "ACTIVIATI",
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
            "id_proiect_contract_sursa": "ID PROIECT (CONTRACT SURSA0",
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

        COL_LABELS_ADMIN_PER_TABLE = {
            "base_contracte_cep": {
                "cod_identificare":        "NR.CONTRACT",
                "status_contract_proiect": "STATUS CONTRACT",
                "titlul_proiect":          "OBIECTUL CONTRACTULUI",
            },
            "base_contracte_speciale": {
                "cod_identificare":        "NR.CONTRACT",
                "status_contract_proiect": "STATUS CONTRACT",
            },
            "base_contracte_terti": {
                "cod_identificare":        "NR.CONTRACT",
                "status_contract_proiect": "STATUS CONTRACT",
            },
        }

        def _col_label_admin(col: str, table: str = None) -> str:
            if table and table in COL_LABELS_ADMIN_PER_TABLE:
                if col in COL_LABELS_ADMIN_PER_TABLE[table]:
                    return COL_LABELS_ADMIN_PER_TABLE[table][col]
            return COL_LABELS_ADMIN.get(col, col.replace("_", " ").capitalize())

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
                label=_col_label_admin(target_col),
                options=options,
                required=False,
                help="🔽 Selectează din listă",
            )

        if table_name == "com_echipe_proiect" and "reprezinta_idbdc" in df.columns:
            df["reprezinta_idbdc"] = df["reprezinta_idbdc"].apply(
                lambda v: True if v is True or str(v).strip().upper() in ("TRUE", "DA", "1") else False
            )
            cfg["reprezinta_idbdc"] = st.column_config.CheckboxColumn(
                label=_col_label_admin("reprezinta_idbdc"),
                help="Bifează dacă persoana reprezintă IDBDC în proiect",
                default=False,
            )

        if table_name == "com_echipe_proiect" and "functie_upt" in df.columns:
            cfg["functie_upt"] = st.column_config.TextColumn(
                label=_col_label_admin("functie_upt"),
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

    c1, c2, c3 = st.columns(3)
    with c1:
        cat_admin = st.selectbox(
            "Categoria de date",
            ["", "Contracte", "Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"],
        )
    with c2:
        if cat_admin == "Contracte":
            _rol_c2 = (st.session_state.get("operator_rol") or "").strip().upper()
            _optiuni_contracte = ["", "CEP", "TERTI", "SPECIALE"] if _rol_c2 == "ADMIN" else ["", "CEP", "TERTI"]
            tip_admin = st.selectbox("Tipul de contract", _optiuni_contracte)
        elif cat_admin == "Proiecte":
            tip_admin = st.selectbox("Tipul de proiect", ["", "FDI", "PNRR", "PNCDI", "INTERNATIONALE", "INTERREG", "NONEU"])
        else:
            tip_admin = ""
    with c3:
        id_admin = st.text_input("Filtru numar contract sau id proiect")

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

    if cat_admin in ("Contracte", "Proiecte"):
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

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ============================
    # STRUCTURĂ TAB-URI
    # ============================

    if cat_admin in ("Contracte", "Proiecte"):
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

    editing_blocked = False

    # ============================
    # EDITOR ECHIPA — doua zone separate
    # ============================

    def _render_echipa_editor(df_show, col_cfg, cod, editing_blocked, edited_data, state_key, table_name):
        """
        Randare editor echipa in doua zone:
        - Zona 1 (sus): reprezentanti IDBDC — editor mic fix, proeminent
        - Zona 2 (jos): restul echipei — editor dinamic cu inaltime fixa + scroll intern
        Ambele zone folosesc dropdown pentru nume_prenume.
        La salvare, cele doua zone se reunesc intr-un singur DataFrame.
        """

        # Incarcam lista de persoane pentru dropdown
        persoane_disponibile = load_dropdown_options("det_resurse_umane", "nume_prenume")

        # Inlocuim SelectboxColumn pentru nume_prenume cu lista completa
        col_cfg_echipa = dict(col_cfg)
        if "nume_prenume" in df_show.columns:
            col_cfg_echipa["nume_prenume"] = st.column_config.SelectboxColumn(
                label="🔽 Nume și prenume",
                options=persoane_disponibile,
                required=True,
                help="🔽 Selectează persoana din lista angajaților",
            )

        # Impartim df in reprezentanti si restul
        if "reprezinta_idbdc" in df_show.columns:
            mask_rep = df_show["reprezinta_idbdc"].apply(
                lambda v: v is True or str(v).strip().upper() in ("TRUE", "DA", "1")
            )
            df_rep   = df_show[mask_rep].copy().reset_index(drop=True)
            df_rest  = df_show[~mask_rep].copy().reset_index(drop=True)
        else:
            df_rep  = pd.DataFrame(columns=df_show.columns)
            df_rest = df_show.copy()

        # ── ZONA 1 — Reprezentanti IDBDC ──────────────────────────────────
        st.markdown(
            "<div style='background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.30);"
            "border-radius:10px;padding:8px 14px;margin-bottom:6px;'>"            "<span style='color:#ffffff;font-weight:800;font-size:0.92rem;'>"
            "⭐ Reprezentanți IDBDC</span> "
            "<span style='color:rgba(255,255,255,0.55);font-size:0.80rem;'>(director / responsabil proiect)</span>"
            "</div>",
            unsafe_allow_html=True,
        )

        key_rep = f"editor_echipa_rep_{cod}"
        edited_rep = st.data_editor(
            df_rep,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config=col_cfg_echipa,
            disabled=editing_blocked,
            key=key_rep,
            height=min(200, 60 + max(1, len(df_rep)) * 38),
        )

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ── ZONA 2 — Restul echipei ────────────────────────────────────────
        nr_rest = len(df_rest)
        st.markdown(
            f"<div style='background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.18);"
            f"border-radius:10px;padding:8px 14px;margin-bottom:6px;'>"            f"<span style='color:#ffffff;font-weight:800;font-size:0.92rem;'>"
            f"👥 Membri echipă</span> "
            f"<span style='color:rgba(255,255,255,0.55);font-size:0.80rem;'>{nr_rest} persoane</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Filtru rapid text deasupra editorului
        filter_key = f"echipa_filter_{cod}"
        filtru = st.text_input(
            "🔍 Filtrează după nume",
            value="",
            key=filter_key,
            placeholder="Tastează pentru a filtra lista...",
            label_visibility="collapsed",
        ).strip().lower()

        df_rest_filtered = df_rest.copy()
        if filtru and "nume_prenume" in df_rest_filtered.columns:
            df_rest_filtered = df_rest_filtered[
                df_rest_filtered["nume_prenume"].astype(str).str.lower().str.contains(filtru, na=False)
            ].reset_index(drop=True)

        key_rest = f"editor_echipa_rest_{cod}"
        edited_rest = st.data_editor(
            df_rest_filtered,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config=col_cfg_echipa,
            disabled=editing_blocked,
            key=key_rest,
            height=400,
        )

        # ── Reunim cele doua zone pentru salvare ──────────────────────────
        # Forțam reprezinta_idbdc corect pentru fiecare zona
        if "reprezinta_idbdc" in edited_rep.columns:
            edited_rep = edited_rep.copy()
            edited_rep["reprezinta_idbdc"] = True
        if "reprezinta_idbdc" in edited_rest.columns:
            edited_rest = edited_rest.copy()
            edited_rest["reprezinta_idbdc"] = False

        df_reunited = pd.concat([edited_rep, edited_rest], ignore_index=True)

        # Eliminam randuri fara nume (goale)
        if "nume_prenume" in df_reunited.columns:
            df_reunited = df_reunited[
                df_reunited["nume_prenume"].notna() &
                (df_reunited["nume_prenume"].astype(str).str.strip() != "")
            ].reset_index(drop=True)

        edited_data[table_name] = df_reunited

    # ============================
    # TAB-URI + EDITOR
    # ============================

    tabs = st.tabs([label for label, _ in tabele])
    edited_data = {}

    for i, (label, table_name) in enumerate(tabele):
        with tabs[i]:
            df_show = st.session_state[state_key(table_name)].copy()

            if table_name == "com_date_financiare" and "an_referinta" in df_show.columns and "valuta" in df_show.columns:
                cols = list(df_show.columns)
                cols.remove("valuta")
                idx = cols.index("an_referinta") + 1
                cols.insert(idx, "valuta")
                df_show = df_show[cols]

            col_cfg = build_column_config_for_table(table_name, df_show)

            # ── Editor special pentru echipa: doua zone separate ──────────
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
    # MESAJ PERSISTENT — mare, vizibil
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
            # Separăm motivul tehnic de mesajul principal dacă există ":"
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
    # BUTOANE — după editori
    # ============================

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3)
    with b1:
        btn_save = st.button("💾 SALVARE (toată fișa)", disabled=editing_blocked)
    with b2:
        btn_validate = st.button("✅ VALIDARE (toată fișa)")
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

                # Reconstruim DataFrame-ul din starea editorului — supraviețuiește rerun-ului
                df_base = st.session_state[state_key(table_name)].copy()

                # Pentru echipa: _render_echipa_editor a reunit deja cele doua zone in edited_data
                if table_name == "com_echipe_proiect":
                    df_edit_visible = edited_data.get(table_name, df_base)
                else:
                    editor_key = f"editor_{table_name}_{cod}"
                    editor_state = st.session_state.get(editor_key)

                    if editor_state is not None and isinstance(editor_state, dict):
                        edited_rows = editor_state.get("edited_rows", {})
                        added_rows  = editor_state.get("added_rows", [])
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

                df_for_save = merge_back_control_cols(df_edit_visible, df_raw_original)

                if table_name == "com_echipe_proiect":
                    df_for_save = autofill_functie_upt(df_for_save)

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
    # VALIDARE
    # ============================

    if btn_validate:
        operator = st.session_state.operator_identificat
        try:
            ok, msg = direct_validate_all_tables(cod, table_names, operator)
            if ok:
                st.session_state["admin_msg"] = ("success", "✅ Fișa a fost validată")
            else:
                st.session_state["admin_msg"] = ("error", f"Fișa nu a putut fi validată: {msg}")
            st.rerun()
        except Exception as e:
            st.session_state["admin_msg"] = ("error", f"Fișa nu a putut fi validată: {e}")
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
