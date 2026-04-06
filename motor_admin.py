# =========================================================
# MOTOR ADMIN — coordonator principal pentru c2
# Foloseste:
# - admin_config.py
# - admin_rules.py
# - admin_ui.py
# - admin_data_ops.py
# =========================================================

import pandas as pd
import streamlit as st
from datetime import datetime
from typing import List, Dict, Tuple

from admin_config import (
    BASE_TABLE_MAP,
    COMPLEMENTARY_TABLES,
    CATEGORY_TABS,
    CATEGORY_TYPES,
    get_base_table,
    get_tabs_for_category,
    get_types_for_category,
)

from admin_ui import (
    create_tabs,
    get_editor_height,
    get_tab_title,
    render_financial_info_box,
    render_team_info_box,
    render_light_category_info,
)

from admin_data_ops import (
    now_iso,
    current_year,
    append_observatii,
    normalize_identifier_column,
    empty_row,
    prepare_empty_single_row,
    cleanup_payload,
    is_row_effectively_empty,
    direct_upsert_single_row,
    direct_delete_all_tables,
    direct_validate_all_tables,
)


def porneste_motorul(supabase):

    # ============================
    # CONFIG
    # ============================

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

    TABELE_CONTRACTE = {
        "base_contracte_cep",
        "base_contracte_terti",
        "base_contracte_speciale",
    }

    is_admin = st.session_state.get("operator_rol") == "ADMIN"

    # ============================
    # HELPERS GENERALI
    # ============================

    def _fmt_numeric(val) -> str:
        if val is None:
            return ""
        try:
            f = float(str(val).replace(",", ".").strip())
            return f"{f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            return str(val)

    @st.cache_data(show_spinner=False, ttl=600)
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

    # ============================
    # LABEL-URI
    # ============================

    COL_LABELS_ADMIN = {
        "nr_crt": "NR.CRT.",
        "cod_identificare": "NR.CONTRACT/ID PROIECT",
        "denumire_categorie": "CATEGORIE",
        "acronim_contracte_proiecte": "TIP CONTRACT / PROIECT",
        "titlul_proiect": "TITLUL PROIECTULUI",
        "titlul_eveniment": "TITLUL EVENIMENTULUI",
        "obiect_contract": "OBIECTUL CONTRACTULUI",
        "nume_prenume": "NUME SI PRENUME",
        "functie_upt": "FUNCTIE UPT",
        "functia_specifica": "ROL",
        "persoana_contact": "PERSOANA DE CONTACT",
        "acronim_departament": "DEPARTAMENT",
        "status_contract_proiect": "STATUS CONTRACT / PROIECT",
        "data_contract": "📅 DATA CONTRACT",
        "data_inceput": "📅 DATA INCEPUT",
        "data_sfarsit": "📅 DATA SFARSIT",
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
        "acronim_prop_intelect": "FORMA DE PROTECTIE",
        "natura_eveniment": "NATURA EVENIMENTULUI",
        "format_eveniment": "FORMATUL EVENIMENTULUI",
        "loc_desfasurare": "LOCUL DE DESFASURARE",
        "numar_oficial_acordare": "NR. OFICIAL ACORDARE",
        "valoare_totala_contract": "VALOARE TOTALA CONTRACT",
        "valoare_anuala_contract": "VALOARE ANUALA CONTRACT",
        "suma_solicitata": "SUMA SOLICITATA",
        "suma_aprobata": "SUMA APROBATA",
        "suma_aprobata_mec": "SUMA APROBATA MEC",
        "valuta": "VALUTA",
        "buget_anual": "BUGET ANUAL",
        "buget_total": "BUGET TOTAL",
    }

    COL_LABELS_PER_TABLE_ADMIN = {
        "base_contracte_cep": {
            "cod_identificare": "NR. CONTRACT",
            "obiect_contract": "OBIECTUL CONTRACTULUI",
            "status_contract_proiect": "🔽 STATUS CONTRACT",
        },
        "base_contracte_terti": {
            "cod_identificare": "NR. CONTRACT",
            "obiect_contract": "OBIECTUL CONTRACTULUI",
            "status_contract_proiect": "🔽 STATUS CONTRACT",
        },
        "base_contracte_speciale": {
            "cod_identificare": "NR. CONTRACT",
            "obiect_contract": "OBIECTUL CONTRACTULUI",
            "status_contract_proiect": "🔽 STATUS CONTRACT",
        },
        "base_proiecte_fdi": {
            "cod_identificare": "ID PROIECT",
            "titlul_proiect": "TITLUL PROIECTULUI",
            "rol_upt": "ROL UPT IN PROIECT",
            "status_contract_proiect": "🔽 STATUS PROIECT",
        },
        "base_proiecte_pncdi": {
            "cod_identificare": "ID PROIECT",
            "titlul_proiect": "TITLUL PROIECTULUI",
            "rol_upt": "ROL UPT IN PROIECT",
            "status_contract_proiect": "🔽 STATUS PROIECT",
        },
        "base_proiecte_pnrr": {
            "cod_identificare": "ID PROIECT",
            "titlul_proiect": "TITLUL PROIECTULUI",
            "rol_upt": "ROL UPT IN PROIECT",
            "status_contract_proiect": "🔽 STATUS PROIECT",
        },
        "base_proiecte_internationale": {
            "cod_identificare": "ID PROIECT",
            "titlul_proiect": "TITLUL PROIECTULUI",
            "rol_upt": "ROL UPT IN PROIECT",
            "status_contract_proiect": "🔽 STATUS PROIECT",
        },
        "base_proiecte_interreg": {
            "cod_identificare": "ID PROIECT",
            "titlul_proiect": "TITLUL PROIECTULUI",
            "rol_upt": "ROL UPT IN PROIECT",
            "status_contract_proiect": "🔽 STATUS PROIECT",
        },
        "base_proiecte_noneu": {
            "cod_identificare": "ID PROIECT",
            "titlul_proiect": "TITLUL PROIECTULUI",
            "rol_upt": "ROL UPT IN PROIECT",
            "status_contract_proiect": "🔽 STATUS PROIECT",
        },
        "base_proiecte_see": {
            "cod_identificare": "ID PROIECT",
            "titlul_proiect": "TITLUL PROIECTULUI",
            "rol_upt": "ROL UPT IN PROIECT",
            "status_contract_proiect": "🔽 STATUS PROIECT",
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

    # ============================
    # DROPDOWN MAP
    # ============================

    DROPDOWN_MAP = {
        "base_contracte_cep": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_contracte", "acronim_tip_contract"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            "valuta": ("__STATIC__", "VALUTA_3"),
        },
        "base_contracte_terti": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_contracte", "acronim_tip_contract"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            "valuta": ("__STATIC__", "VALUTA_3"),
        },
        "base_contracte_speciale": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_contracte", "acronim_tip_contract"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            "valuta": ("__STATIC__", "VALUTA_3"),
        },
        "base_proiecte_fdi": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            "valuta": ("__STATIC__", "VALUTA_3"),
            "abreviere_domeniu_fdi": ("nom_domenii_fdi", "abreviere_domeniu_fdi"),
        },
        "base_proiecte_pncdi": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            "valuta": ("__STATIC__", "VALUTA_3"),
        },
        "base_proiecte_pnrr": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            "valuta": ("__STATIC__", "VALUTA_3"),
        },
        "base_proiecte_internationale": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            "valuta": ("__STATIC__", "VALUTA_3"),
        },
        "base_proiecte_interreg": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            "valuta": ("__STATIC__", "VALUTA_3"),
        },
        "base_proiecte_noneu": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            "valuta": ("__STATIC__", "VALUTA_3"),
        },
        "base_proiecte_see": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "acronim_contracte_proiecte": ("nom_proiecte", "acronim_tip_proiect"),
            "status_contract_proiect": ("nom_status_proiect", "status_contract_proiect"),
            "valuta": ("__STATIC__", "VALUTA_3"),
        },
        "base_evenimente_stiintifice": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "valuta": ("__STATIC__", "VALUTA_3"),
        },
        "base_prop_intelect": {
            "denumire_categorie": ("nom_categorie", "denumire_categorie"),
            "valuta": ("__STATIC__", "VALUTA_3"),
        },
        "com_date_financiare": {
            "valuta": ("__STATIC__", "VALUTA_3"),
        },
        "com_echipe_proiect": {
            "nume_prenume": ("det_resurse_umane", "nume_prenume"),
            "acronim_departament": ("nom_departament", "acronim_departament"),
            "functie_upt": ("nom_functie_upt", "acronim_functie_upt"),
        },
    }

    def build_column_config_for_table(table_name: str, df: pd.DataFrame, tabela_baza_ctx: str = None):
        ctx = tabela_baza_ctx or table_name
        is_contract_ctx = ctx in TABELE_CONTRACTE

        def _col_label_admin(col: str, tbl: str = None) -> str:
            if tbl and tbl in COL_LABELS_PER_TABLE_ADMIN:
                if col in COL_LABELS_PER_TABLE_ADMIN[tbl]:
                    return COL_LABELS_PER_TABLE_ADMIN[tbl][col]
            if is_contract_ctx and tbl not in COL_LABELS_PER_TABLE_ADMIN:
                if col == "cod_identificare":
                    return "NR. CONTRACT"
                if col == "functia_specifica":
                    return "ROLUL IN CONTRACT"
            return COL_LABELS_ADMIN.get(col, col.replace("_", " ").capitalize())

        rel = DROPDOWN_MAP.get(table_name, {})
        cfg = {}

        AUTO_FILLED_COLS = {"denumire_categorie", "acronim_contracte_proiecte"}

        for target_col, (src_table, src_col) in rel.items():
            if target_col not in df.columns:
                continue
            if target_col in AUTO_FILLED_COLS and table_name == tabela_baza_ctx:
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
                help="Selecteaza din lista",
            )

        if table_name == "com_echipe_proiect" and "persoana_contact" in df.columns:
            df["persoana_contact"] = df["persoana_contact"].apply(
                lambda v: True if v is True or str(v).strip().upper() in ("TRUE", "DA", "1") else False
            )
            if not is_contract_ctx:
                cfg["persoana_contact"] = st.column_config.CheckboxColumn(
                    label=_col_label_admin("persoana_contact", table_name),
                    help="Bifeaza daca persoana este persoana de contact",
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

        if "cod_identificare" in df.columns:
            cfg["cod_identificare"] = st.column_config.TextColumn(
                label=_col_label_admin("cod_identificare", table_name),
            )

        VALUE_COLS_KEYWORDS = (
            "valoare_",
            "suma_",
            "cost_",
            "buget_",
            "cofinantare_",
            "contributie_",
            "punctaj",
            "scor_",
            "interval_",
            "total_",
        )

        for c in df.columns:
            if c in CONTROL_COLS:
                continue
            if c in cfg:
                continue
            if any(c.startswith(k) for k in VALUE_COLS_KEYWORDS) or is_numeric_col(c, df):
                cfg[c] = st.column_config.NumberColumn(
                    label=_col_label_admin(c, table_name),
                    format="%.2f",
                )

        for c in df.columns:
            if c in CONTROL_COLS:
                continue
            if c in cfg:
                continue
            cfg[c] = st.column_config.TextColumn(
                label=_col_label_admin(c, table_name),
            )

        return cfg

    # ============================
    # SALVARE
    # ============================

    def direct_save_all_tables(items: list, operator: str) -> Tuple[bool, str]:
        if not items:
            return False, "Nu exista date de salvat."

        by_table: Dict[str, list[dict]] = {}
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

                direct_upsert_single_row(supabase, table_name, clean_payloads[0], cod0)
                ok_any = True

            except Exception as e:
                errors.append(f"{table_name}: {e}")

        if not ok_any and errors:
            return False, " | ".join(errors)
        if not ok_any:
            return False, "Nu s-a putut salva."
        if errors:
            return True, "Salvare partiala."
        return True, "Salvarea realizata cu succes!"

    # ============================
    # BOX NOMENCLATOARE
    # ============================

    def _nomdet_clean_payload(d: dict) -> dict:
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

    def _nomdet_build_column_config(tabela: str, df: pd.DataFrame):
        rel = NOMDET_DROPDOWN_MAP.get(tabela, {})
        cfg = {}

        for target_col, (src_table, src_col) in rel.items():
            if target_col not in df.columns:
                continue
            options = load_dropdown_options(src_table, src_col)
            if options:
                cfg[target_col] = st.column_config.SelectboxColumn(
                    label=COL_LABELS_ADMIN.get(target_col, target_col),
                    options=options,
                    required=False,
                )

        for c in df.columns:
            if c in cfg:
                continue
            if c == "__STERGE__":
                cfg[c] = st.column_config.CheckboxColumn(label="Sterge", default=False)
            elif is_year_col(c):
                cfg[c] = st.column_config.NumberColumn(label=COL_LABELS_ADMIN.get(c, c), format="%d")
            elif is_numeric_col(c, df):
                cfg[c] = st.column_config.NumberColumn(label=COL_LABELS_ADMIN.get(c, c), format="%.2f")
            else:
                cfg[c] = st.column_config.TextColumn(label=COL_LABELS_ADMIN.get(c, c))
        return cfg

    def render_nomenclatoare_admin_box():
        with st.expander("Nomenclatoare / tabele auxiliare", expanded=False):
            tabela = st.selectbox(
                "Alege tabelul de administrat",
                [""] + NOMDET_WHITELIST,
                key="nomdet_table",
            )
            if not tabela:
                return

            cols = get_table_columns(tabela)
            if not cols:
                st.warning("Nu s-au putut incarca coloanele.")
                return

            pk = cols[0]

            try:
                res = supabase.table(tabela).select("*").execute()
                data = res.data or []
                df = pd.DataFrame(data)
            except Exception as e:
                st.error(f"Eroare la incarcare: {e}")
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

            if st.button("SALVARE", key="nomdet_save"):
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

                    st.success("Salvare realizata.")
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
        f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.get('operator_identificat', '')}</h3>",
        unsafe_allow_html=True,
    )

    render_nomenclatoare_admin_box()

    st.divider()

    # ============================
    # FILTRE OPERATOR
    # ============================

    _filtru_categorii = st.session_state.get("operator_filtru_categorie") or []
    _filtru_tipuri = st.session_state.get("operator_filtru_tipuri") or []

    toate_categoriile = list(CATEGORY_TYPES.keys())
    categorii_disponibile = [""] + [c for c in toate_categoriile if not _filtru_categorii or c in _filtru_categorii]

    c1, c2, c3 = st.columns(3)

    with c1:
        cat_admin = st.selectbox("Categoria de date", categorii_disponibile)

    with c2:
        if cat_admin:
            tipuri = get_types_for_category(cat_admin)
            if tipuri:
                tipuri_disponibile = [""] + [t for t in tipuri if not _filtru_tipuri or t in _filtru_tipuri]
                tip_admin = st.selectbox("Tip", tipuri_disponibile)
            else:
                tip_admin = ""
                st.text_input("Tip", value="(nu este necesar)", disabled=True)
        else:
            tip_admin = ""
            st.text_input("Tip", value="", disabled=True)

    with c3:
        id_admin = st.text_input("Cod identificare / contract / proiect / eveniment")

    if not cat_admin:
        st.info("Selecteaza categoria.")
        return

    tabela_baza = get_base_table(cat_admin, tip_admin)

    if not tabela_baza:
        st.info("Selecteaza categoria si tipul.")
        return

    if not id_admin or str(id_admin).strip() == "":
        st.info("Introdu filtrul pentru a deschide fisa.")
        return

    cod = str(id_admin).strip()

    # ============================
    # ACTIUNE
    # ============================

    st.markdown("**Actiune**")
    actiune = st.radio(
        label="",
        options=["Modificare / completare fișă existentă", "Fișă nouă"],
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ============================
    # STRUCTURA TAB-URI
    # ============================

    tab_labels = get_tabs_for_category(cat_admin)
    table_map = {"Date de baza": tabela_baza}
    table_map.update(COMPLEMENTARY_TABLES)

    visible_labels, streamlit_tabs = create_tabs(cat_admin, tab_labels)
    table_names = [table_map[t] for t in visible_labels if t in table_map]

    render_light_category_info(cat_admin)

    # ============================
    # CURATARE SESSION_STATE
    # ============================

    _prev_cod_key = "admin_prev_cod"
    _prev_tabela_key = "admin_prev_tabela"
    prev_cod = st.session_state.get(_prev_cod_key)
    prev_tabela = st.session_state.get(_prev_tabela_key)

    if prev_cod != cod or prev_tabela != tabela_baza:
        for tn in table_names:
            for k in (
                f"df_admin__{tn}",
                f"df_admin_raw__{tn}",
                f"editor_{tn}_{prev_cod}",
                f"echipa_reunited_{prev_cod}",
                f"toggle_deblocat_{prev_cod}",
            ):
                if k in st.session_state:
                    del st.session_state[k]
        st.session_state[_prev_cod_key] = cod
        st.session_state[_prev_tabela_key] = tabela_baza

    # ============================
    # INCARCARE
    # ============================

    state_key = lambda t: f"df_admin__{t}"
    state_key_raw = lambda t: f"df_admin_raw__{t}"

    loaded = {}
    exists_map = {}

    for table_name in table_names:
        df, cols, exista = load_single_row(table_name, cod)
        loaded[table_name] = (df, cols)
        exists_map[table_name] = exista

    base_exists = exists_map.get(tabela_baza, False)
    if actiune == "Modificare / completare fișă existentă" and not base_exists:
        st.warning("Nu exista fișa pentru acest cod. Alege «Fisa noua» daca vrei sa creezi.")
        return

    for table_name in table_names:
        if state_key_raw(table_name) in st.session_state:
            continue

        df, cols = loaded[table_name]
        if df.empty and cols:
            df_full = prepare_empty_single_row(cols, cod)
        else:
            df_full = df.copy()

        if table_name == tabela_baza:
            if "denumire_categorie" in df_full.columns and cat_admin:
                opts_cat = load_dropdown_options("nom_categorie", "denumire_categorie")
                match_cat = next((o for o in opts_cat if cat_admin.upper() in o.upper()), None)
                if match_cat:
                    df_full["denumire_categorie"] = match_cat

            if "acronim_contracte_proiecte" in df_full.columns and tip_admin:
                src_tip = "nom_contracte" if cat_admin == "Contracte" else "nom_proiecte"
                col_tip = "acronim_tip_contract" if cat_admin == "Contracte" else "acronim_tip_proiect"
                opts_tip = load_dropdown_options(src_tip, col_tip)
                match_tip = next((o for o in opts_tip if tip_admin.upper() in o.upper()), None)
                df_full["acronim_contracte_proiecte"] = match_tip or tip_admin

        df_full = normalize_identifier_column(df_full)
        st.session_state[state_key_raw(table_name)] = df_full.copy()
        st.session_state[state_key(table_name)] = hide_control_cols(df_full)

        if table_name == "com_echipe_proiect":
            echipa_key = f"echipa_reunited_{cod}"
            if echipa_key not in st.session_state:
                df_echipa_init = df_full.copy()
                df_echipa_init["cod_identificare"] = cod
                if "persoana_contact" not in df_echipa_init.columns:
                    df_echipa_init["persoana_contact"] = False
                st.session_state[echipa_key] = df_echipa_init

    base_full = normalize_identifier_column(st.session_state[state_key_raw(tabela_baza)])
    st.session_state[state_key_raw(tabela_baza)] = base_full

    # ============================
    # BLOCARE / DEBLOCARE
    # ============================

    toggle_key = f"toggle_deblocat_{cod}"
    if toggle_key not in st.session_state:
        st.session_state[toggle_key] = True

    st.toggle(
        "Deblocare editare",
        key=toggle_key,
        help="Debifeaza pentru blocare temporara a editarii",
    )
    deblocat = st.session_state[toggle_key]

    # ============================
    # TAB-URI
    # ============================

    collected_items = []

    for tab_label, tab_obj in zip(visible_labels, streamlit_tabs):
        table_name = table_map[tab_label]

        with tab_obj:
            st.markdown(f"### {get_tab_title(tab_label, cat_admin, tip_admin)}")

            if table_name == "com_date_financiare":
                render_financial_info_box(tip_admin)

            if table_name == "com_echipe_proiect":
                render_team_info_box()

            df_raw = st.session_state[state_key_raw(table_name)].copy()
            df_edit = hide_control_cols(df_raw).copy()

            if table_name == "com_echipe_proiect":
                df_edit = autofill_functie_upt(df_edit)

            cfg = build_column_config_for_table(table_name, df_edit, tabela_baza_ctx=tabela_baza)

            edited = st.data_editor(
                df_edit,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                disabled=not deblocat,
                column_config=cfg,
                key=f"editor_{table_name}_{cod}",
                height=get_editor_height(table_name),
            )

            edited = normalize_identifier_column(edited)

            if "cod_identificare" in edited.columns:
                edited["cod_identificare"] = cod

            if table_name == "com_echipe_proiect":
                edited = autofill_functie_upt(edited)
                st.session_state[f"echipa_reunited_{cod}"] = edited.copy()

            st.session_state[state_key(table_name)] = edited.copy()

            merged = merge_back_control_cols(edited, df_raw)
            merged = normalize_identifier_column(merged)
            st.session_state[state_key_raw(table_name)] = merged.copy()

            for _, row in merged.iterrows():
                payload = row.to_dict()
                payload["cod_identificare"] = cod
                collected_items.append({
                    "table": table_name,
                    "payload": payload,
                })

    st.divider()

    # ============================
    # ACTIUNI FINALE
    # ============================

    a1, a2, a3 = st.columns(3)
    operator = st.session_state.get("operator_identificat", "operator")

    with a1:
        if st.button("💾 SALVARE", use_container_width=True, disabled=not deblocat):
            ok, msg = direct_save_all_tables(collected_items, operator)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    with a2:
        if st.button("✅ VALIDARE", use_container_width=True, disabled=not deblocat):
            ok, msg = direct_validate_all_tables(supabase, cod, table_names, operator)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    with a3:
        if st.button("🗑️ ȘTERGERE FIȘĂ", use_container_width=True, disabled=not deblocat):
            ok, msg = direct_delete_all_tables(supabase, cod, table_names)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
