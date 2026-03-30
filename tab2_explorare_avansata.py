# =========================================================
# TAB 2 — EXPLORARE AVANSATĂ MULTI-CRITERIALĂ
# Fișier nou — construit integral de la zero
# =========================================================

import io
from datetime import date, datetime
from typing import List, Dict, Any

import pandas as pd
import streamlit as st
from supabase import Client


TABLE_CONFIG = {
    "base_contracte_cep": {
        "label": "📄 Contracte CEP",
        "categorie": "Contracte",
        "subcategorie": "CEP",
    },
    "base_contracte_terti": {
        "label": "📄 Contracte TERȚI",
        "categorie": "Contracte",
        "subcategorie": "TERȚI",
    },
    "base_contracte_speciale": {
        "label": "📄 Contracte SPECIALE",
        "categorie": "Contracte",
        "subcategorie": "SPECIALE",
    },
    "base_proiecte_fdi": {
        "label": "🔬 Proiecte FDI",
        "categorie": "Proiecte",
        "subcategorie": "FDI",
    },
    "base_proiecte_pncdi": {
        "label": "🔬 Proiecte PNCDI",
        "categorie": "Proiecte",
        "subcategorie": "PNCDI",
    },
    "base_proiecte_pnrr": {
        "label": "🔬 Proiecte PNRR",
        "categorie": "Proiecte",
        "subcategorie": "PNRR",
    },
    "base_proiecte_internationale": {
        "label": "🌍 Proiecte Internaționale",
        "categorie": "Proiecte",
        "subcategorie": "Internaționale",
    },
    "base_proiecte_interreg": {
        "label": "🌍 Proiecte INTERREG",
        "categorie": "Proiecte",
        "subcategorie": "INTERREG",
    },
    "base_proiecte_noneu": {
        "label": "🌍 Proiecte NON-EU",
        "categorie": "Proiecte",
        "subcategorie": "NON-EU",
    },
    "base_proiecte_see": {
        "label": "🌍 Proiecte SEE",
        "categorie": "Proiecte",
        "subcategorie": "SEE",
    },
    "base_evenimente_stiintifice": {
        "label": "🎓 Evenimente Științifice",
        "categorie": "Evenimente",
        "subcategorie": "Științifice",
    },
    "base_prop_intelect": {
        "label": "💡 Proprietate Industrială",
        "categorie": "Proprietate Industrială",
        "subcategorie": "PI",
    },
}

DEFAULT_TABLES = list(TABLE_CONFIG.keys())

DISPLAY_PRIORITY = [
    "Sursa",
    "Tip",
    "Subtip",
    "cod_identificare",
    "titlu_rezolvat",
    "status_rezolvat",
    "an_referinta",
    "data_inceput",
    "data_sfarsit",
    "data_contract",
    "data_apel",
    "data_depozit_cerere",
    "data_oficiala_acordare",
    "valoare_rezolvata",
    "persoana_relevanta",
    "entitate_relevanta",
]

TITLE_FIELDS = [
    "titlul_proiect",
    "titlu_proiect",
    "titlul_eveniment",
    "titlul",
    "denumire",
    "obiect_contract",
    "denumire_completa",
]

STATUS_FIELDS = [
    "status_contract_proiect",
    "status_document",
    "status_personal",
    "status_activ",
]

PERSON_FIELDS = [
    "persoana_contact",
    "nume_prenume",
    "director_proiect",
    "coordonator",
    "responsabil_idbdc",
]

ENTITY_FIELDS = [
    "denumire_beneficiar",
    "denumire_titular",
    "denumire_institutie",
    "facultate",
    "denumire_departament",
    "acronim_departament",
    "parteneri",
    "institutii_organizare",
]

VALUE_FIELDS = [
    "valoare_totala_contract",
    "valoare_anuala_contract",
    "cost_total_proiect",
    "cost_proiect_upt",
    "suma_solicitata",
    "suma_solicitata_fdi",
    "suma_aprobata",
    "suma_aprobata_mec",
    "contributie_ue_total_proiect",
    "contributie_ue_proiect_upt",
    "cofinantare_totala_contract",
    "cofinantare_anuala_contract",
    "cofinantare_upt_fdi",
]

DATE_FIELDS = [
    "data_inceput",
    "data_sfarsit",
    "data_contract",
    "data_apel",
    "data_depozit_cerere",
    "data_oficiala_acordare",
    "data_inceput_rol",
    "data_sfarsit_rol",
    "data_inceput_valabilitate",
    "data_sfarsit_valabilitate",
]

SEARCHABLE_TEXT_FIELDS = list(
    dict.fromkeys(
        TITLE_FIELDS
        + STATUS_FIELDS
        + PERSON_FIELDS
        + ENTITY_FIELDS
        + [
            "cod_identificare",
            "cod_depunere",
            "cod_temporar",
            "numar_oficial_acordare",
            "numar_publicare_cerere",
            "numar_data_notificare_intern",
            "acronim_prop_intelect",
            "natura_eveniment",
            "format_eveniment",
            "loc_desfasurare",
            "programul_de_finantare",
            "schema_de_finantare",
            "rol_upt",
            "functia_specifica",
            "comentarii_diverse",
            "comentarii_document",
            "obiectiv_general",
            "obiective_specifice",
            "activitati_proiect",
            "rezultate_proiect",
        ]
    )
)


def _safe_text(v: Any) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    if s.lower() in ("nan", "none"):
        return ""
    return s


def _try_parse_date(v: Any):
    if v is None:
        return pd.NaT
    if isinstance(v, (datetime, date)):
        return pd.to_datetime(v, errors="coerce")
    s = str(v).strip()
    if not s:
        return pd.NaT
    return pd.to_datetime(s, errors="coerce", dayfirst=True)


def _normalize_numeric_string(s: str) -> str:
    s = s.replace(" ", "")
    if not s:
        return s
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    else:
        if "," in s:
            s = s.replace(".", "").replace(",", ".")
    return s


def _to_float(v: Any):
    if v is None:
        return None
    s = _safe_text(v)
    if not s:
        return None
    try:
        return float(_normalize_numeric_string(s))
    except Exception:
        return None


def _format_number_ro(v: float, decimals: int = 2) -> str:
    if decimals == 0:
        return f"{int(round(v)):,}".replace(",", ".")
    return f"{v:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _format_value(v: Any, col: str = "") -> str:
    s = _safe_text(v)
    if not s:
        return ""

    if col == "cod_identificare":
        fv = _to_float(v)
        if fv is not None and float(fv).is_integer():
            return str(int(fv))
        return s

    if col in VALUE_FIELDS:
        fv = _to_float(v)
        if fv is not None:
            return _format_number_ro(fv, 2)
        return s

    fv = _to_float(v)
    if fv is not None:
        if fv.is_integer():
            return str(int(fv))
        return _format_number_ro(fv, 2)

    return s


def _first_nonempty(row: Dict[str, Any], fields: List[str]) -> str:
    for f in fields:
        v = _safe_text(row.get(f))
        if v:
            return v
    return ""


def _fetch_table_all(supabase: Client, table: str, page_size: int = 1000, max_rows: int = 10000) -> List[Dict[str, Any]]:
    all_rows = []
    start = 0

    while start < max_rows:
        end = min(start + page_size - 1, max_rows - 1)
        try:
            res = supabase.table(table).select("*").range(start, end).execute()
            batch = res.data or []
        except Exception:
            batch = []

        if not batch:
            break

        all_rows.extend(batch)

        if len(batch) < page_size:
            break

        start += page_size

    return all_rows


def _rows_to_df(rows: List[Dict[str, Any]], table_name: str) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows).copy()
    cfg = TABLE_CONFIG.get(table_name, {})

    df["Sursa"] = cfg.get("label", table_name)
    df["Tip"] = cfg.get("categorie", "")
    df["Subtip"] = cfg.get("subcategorie", "")
    df["titlu_rezolvat"] = df.apply(lambda r: _first_nonempty(r, TITLE_FIELDS), axis=1)
    df["status_rezolvat"] = df.apply(lambda r: _first_nonempty(r, STATUS_FIELDS), axis=1)
    df["persoana_relevanta"] = df.apply(lambda r: _first_nonempty(r, PERSON_FIELDS), axis=1)
    df["entitate_relevanta"] = df.apply(lambda r: _first_nonempty(r, ENTITY_FIELDS), axis=1)

    valoare_rezolvata = []
    for _, r in df.iterrows():
        raw = None
        for f in VALUE_FIELDS:
            if _safe_text(r.get(f)):
                raw = r.get(f)
                break
        if raw is None:
            valoare_rezolvata.append("")
        else:
            fv = _to_float(raw)
            valoare_rezolvata.append(_format_number_ro(fv, 2) if fv is not None else _safe_text(raw))
    df["valoare_rezolvata"] = valoare_rezolvata

    for dcol in DATE_FIELDS:
        if dcol in df.columns:
            df[dcol] = df[dcol].apply(_try_parse_date)

    if "an_referinta" in df.columns:
        df["an_referinta"] = df["an_referinta"].apply(lambda x: int(float(x)) if _to_float(x) is not None else None)

    return df


def _contains_any_text(row: pd.Series, text: str) -> bool:
    text = (text or "").strip().lower()
    if not text:
        return True

    for col in SEARCHABLE_TEXT_FIELDS:
        if col in row.index:
            v = _safe_text(row[col]).lower()
            if text in v:
                return True

    for col in ["titlu_rezolvat", "status_rezolvat", "persoana_relevanta", "entitate_relevanta", "Sursa", "Tip", "Subtip"]:
        if col in row.index:
            v = _safe_text(row[col]).lower()
            if text in v:
                return True

    return False


def _apply_filters(
    df: pd.DataFrame,
    categorii_selectate: List[str],
    cod_text: str,
    titlu_text: str,
    actor_text: str,
    an_de_la,
    an_pana_la,
    data_de_la,
    data_pana_la,
) -> pd.DataFrame:
    if df.empty:
        return df

    out = df.copy()

    if categorii_selectate:
        out = out[out["Sursa"].isin(categorii_selectate)]

    if cod_text.strip():
        needle = cod_text.strip().lower()
        def _match_cod(row):
            for c in ["cod_identificare", "cod_depunere", "cod_temporar", "numar_oficial_acordare", "numar_publicare_cerere"]:
                if c in row.index and needle in _safe_text(row[c]).lower():
                    return True
            return False
        out = out[out.apply(_match_cod, axis=1)]

    if titlu_text.strip():
        needle = titlu_text.strip().lower()
        def _match_titlu(row):
            for c in TITLE_FIELDS:
                if c in row.index and needle in _safe_text(row[c]).lower():
                    return True
            return needle in _safe_text(row.get("titlu_rezolvat")).lower()
        out = out[out.apply(_match_titlu, axis=1)]

    if actor_text.strip():
        needle = actor_text.strip().lower()
        out = out[out.apply(lambda r: _contains_any_text(r, needle), axis=1)]

    if an_de_la is not None:
        if "an_referinta" in out.columns:
            out = out[out["an_referinta"].fillna(-999999) >= int(an_de_la)]

    if an_pana_la is not None:
        if "an_referinta" in out.columns:
            out = out[out["an_referinta"].fillna(999999) <= int(an_pana_la)]

    if data_de_la or data_pana_la:
        existing_date_cols = [c for c in DATE_FIELDS if c in out.columns]
        if existing_date_cols:
            def _date_in_range(row):
                vals = [row[c] for c in existing_date_cols if pd.notna(row[c])]
                if not vals:
                    return False
                ok = False
                for dt in vals:
                    d = pd.to_datetime(dt).date()
                    cond1 = True if data_de_la is None else d >= data_de_la
                    cond2 = True if data_pana_la is None else d <= data_pana_la
                    if cond1 and cond2:
                        ok = True
                        break
                return ok
            out = out[out.apply(_date_in_range, axis=1)]

    return out


def _prepare_display_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    disp = df.copy()

    for c in disp.columns:
        if pd.api.types.is_datetime64_any_dtype(disp[c]):
            disp[c] = disp[c].apply(lambda x: x.strftime("%d.%m.%Y") if pd.notna(x) else "")

    final_cols = []
    for col in DISPLAY_PRIORITY:
        if col in disp.columns and col not in final_cols:
            final_cols.append(col)

    extra_cols = [
        c for c in disp.columns
        if c not in final_cols
        and not c.endswith("_rezolvat")
    ]
    final_cols.extend(extra_cols)

    disp = disp[final_cols].copy()

    for col in disp.columns:
        disp[col] = disp[col].apply(lambda v: _format_value(v, col))

    rename_map = {
        "Sursa": "SURSĂ",
        "Tip": "TIP",
        "Subtip": "SUBTIP",
        "cod_identificare": "COD IDENTIFICARE",
        "titlu_rezolvat": "TITLU / DENUMIRE / OBIECT",
        "status_rezolvat": "STATUS",
        "an_referinta": "AN REFERINȚĂ",
        "data_inceput": "DATA ÎNCEPUT",
        "data_sfarsit": "DATA SFÂRȘIT",
        "data_contract": "DATA CONTRACT",
        "data_apel": "DATA APEL",
        "data_depozit_cerere": "DATA DEPUNERE",
        "data_oficiala_acordare": "DATA ACORDARE",
        "valoare_rezolvata": "VALOARE",
        "persoana_relevanta": "PERSOANĂ",
        "entitate_relevanta": "ENTITATE",
    }
    disp = disp.rename(columns=rename_map)

    return disp


def _export_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Explorare", index=False)
    buf.seek(0)
    return buf.getvalue()


def render_tab2_explorare_avansata(supabase: Client):
    st.markdown("## 🔎 Explorare avansată")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.88);font-size:1.02rem;font-weight:600;"
        "margin-bottom:0.85rem;'>Explorați baza de date folosind între 2 și 5 criterii simultan.</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.14);"
        "border-radius:14px;padding:14px 16px;margin-bottom:12px;'>",
        unsafe_allow_html=True,
    )

    tabel_labels = [TABLE_CONFIG[t]["label"] for t in DEFAULT_TABLES]

    c1, c2 = st.columns(2)
    with c1:
        categorii_selectate = st.multiselect(
            "1. Categoria principală",
            options=tabel_labels,
            default=[],
            placeholder="Selectați una sau mai multe categorii",
            key="tab2_categorii",
        )

    with c2:
        cod_text = st.text_input(
            "2. Cod / identificator",
            value="",
            placeholder="Ex: 26FDI26 / 998877 / nr. brevet / cod depunere",
            key="tab2_cod_text",
        ).strip()

    c3, c4 = st.columns(2)
    with c3:
        titlu_text = st.text_input(
            "3. Titlu / denumire / obiect",
            value="",
            placeholder="Căutare în titlu, denumire, obiect contract/proiect",
            key="tab2_titlu_text",
        ).strip()

    with c4:
        actor_text = st.text_input(
            "4. Actori / structură / status",
            value="",
            placeholder="Persoană, departament, beneficiar, partener, status",
            key="tab2_actor_text",
        ).strip()

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:rgba(255,255,255,0.70);font-size:0.92rem;font-weight:700;"
        "margin-bottom:8px;'>5. Interval</div>",
        unsafe_allow_html=True,
    )

    i1, i2, i3, i4 = st.columns(4)
    with i1:
        an_de_la = st.number_input("An de la", min_value=1900, max_value=2100, value=None, step=1, key="tab2_an_de_la")
    with i2:
        an_pana_la = st.number_input("An până la", min_value=1900, max_value=2100, value=None, step=1, key="tab2_an_pana_la")
    with i3:
        data_de_la = st.date_input("Dată de la", value=None, key="tab2_data_de_la", format="DD.MM.YYYY")
    with i4:
        data_pana_la = st.date_input("Dată până la", value=None, key="tab2_data_pana_la", format="DD.MM.YYYY")

    st.markdown("</div>", unsafe_allow_html=True)

    active_filters = 0
    if categorii_selectate:
        active_filters += 1
    if cod_text:
        active_filters += 1
    if titlu_text:
        active_filters += 1
    if actor_text:
        active_filters += 1
    if an_de_la is not None or an_pana_la is not None or data_de_la is not None or data_pana_la is not None:
        active_filters += 1

    b1, b2, b3 = st.columns([1.2, 1.2, 4.6])

    with b1:
        cauta = st.button("🔎 Explorează baza de date", use_container_width=True, key="tab2_search_btn")
    with b2:
        reset = st.button("🧹 Resetează filtrele", use_container_width=True, key="tab2_reset_btn")

    if reset:
        for k in [
            "tab2_categorii",
            "tab2_cod_text",
            "tab2_titlu_text",
            "tab2_actor_text",
            "tab2_an_de_la",
            "tab2_an_pana_la",
            "tab2_data_de_la",
            "tab2_data_pana_la",
            "tab2_results_df",
        ]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    st.markdown(
        f"<div style='color:rgba(255,255,255,0.55);font-size:0.86rem;margin-top:6px;margin-bottom:8px;'>"
        f"Criterii active: <b>{active_filters}</b> din 5"
        f"</div>",
        unsafe_allow_html=True,
    )

    if cauta:
        if active_filters < 2:
            st.warning("Completați minimum 2 criterii de căutare.")
            return

        if active_filters > 5:
            st.warning("Pot fi utilizate maximum 5 criterii.")
            return

        selected_table_names = [
            t for t, cfg in TABLE_CONFIG.items()
            if cfg["label"] in categorii_selectate
        ] if categorii_selectate else DEFAULT_TABLES

        with st.spinner("Se explorează baza de date..."):
            frames = []
            for t in selected_table_names:
                rows = _fetch_table_all(supabase, t, page_size=1000, max_rows=10000)
                if rows:
                    df_t = _rows_to_df(rows, t)
                    if not df_t.empty:
                        frames.append(df_t)

            if not frames:
                st.warning("Nu au fost identificate date în tabelele selectate.")
                return

            df_all = pd.concat(frames, ignore_index=True, sort=False)
            df_filtered = _apply_filters(
                df=df_all,
                categorii_selectate=categorii_selectate,
                cod_text=cod_text,
                titlu_text=titlu_text,
                actor_text=actor_text,
                an_de_la=an_de_la,
                an_pana_la=an_pana_la,
                data_de_la=data_de_la,
                data_pana_la=data_pana_la,
            )

            st.session_state["tab2_results_df"] = df_filtered.copy()

    if "tab2_results_df" not in st.session_state:
        return

    results_df = st.session_state["tab2_results_df"].copy()

    if results_df.empty:
        st.info("Nu au fost identificate înregistrări care să respecte combinația selectată.")
        return

    total_rows = len(results_df)

    st.divider()
    st.markdown(
        f"<div style='color:#ffffff;font-size:1.02rem;font-weight:800;margin-bottom:10px;'>"
        f"Rezultate identificate: {total_rows}"
        f"</div>",
        unsafe_allow_html=True,
    )

    s1, s2, s3 = st.columns([1.2, 1.2, 5.6])
    with s1:
        limita_afisare = st.selectbox(
            "Afișare",
            options=[100, 250, 500, 1000, "Toate"],
            index=2 if total_rows > 250 else 0,
            key="tab2_afisare_limit",
        )
    with s2:
        sorteaza_dupa = st.selectbox(
            "Sortare",
            options=[
                "SURSĂ",
                "COD IDENTIFICARE",
                "TITLU / DENUMIRE / OBIECT",
                "STATUS",
                "AN REFERINȚĂ",
            ],
            index=0,
            key="tab2_sort_by",
        )

    display_df = _prepare_display_df(results_df)

    sort_map = {
        "SURSĂ": "SURSĂ",
        "COD IDENTIFICARE": "COD IDENTIFICARE",
        "TITLU / DENUMIRE / OBIECT": "TITLU / DENUMIRE / OBIECT",
        "STATUS": "STATUS",
        "AN REFERINȚĂ": "AN REFERINȚĂ",
    }

    sort_col = sort_map.get(sorteaza_dupa)
    if sort_col in display_df.columns:
        try:
            display_df = display_df.sort_values(by=sort_col, kind="stable", na_position="last")
        except Exception:
            pass

    if limita_afisare != "Toate":
        shown_df = display_df.head(int(limita_afisare)).copy()
    else:
        shown_df = display_df.copy()

    if limita_afisare != "Toate" and total_rows > int(limita_afisare):
        st.info(f"Au fost identificate {total_rows} rezultate. Se afișează primele {limita_afisare}.")

    st.dataframe(
        shown_df,
        use_container_width=True,
        hide_index=True,
        height=560,
    )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    e1, e2 = st.columns([1.2, 1.2])
    with e1:
        csv_data = shown_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Export CSV",
            data=csv_data,
            file_name="explorare_avansata.csv",
            mime="text/csv",
            use_container_width=True,
            key="tab2_export_csv",
        )

    with e2:
        xlsx_data = _export_excel_bytes(shown_df)
        st.download_button(
            "⬇️ Export Excel",
            data=xlsx_data,
            file_name="explorare_avansata.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="tab2_export_xlsx",
        )
