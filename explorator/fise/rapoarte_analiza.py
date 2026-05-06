# =========================================================
# TAB 3 — RAPOARTE ȘI ANALIZĂ
# Fișier nou — construit integral de la zero
# =========================================================

import io
from datetime import date, datetime

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
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

ALL_TABLES = list(TABLE_CONFIG.keys())

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

GROUP_DIMENSIONS = {
    "Sursă": "Sursa",
    "Tip": "Tip",
    "Subtip": "Subtip",
    "An referință": "an_referinta",
    "Status": "status_rezolvat",
    "Persoană": "persoana_relevanta",
    "Entitate": "entitate_relevanta",
}

REPORT_PRESETS = {
    "Distribuție pe categorii": {
        "group_by": "Sursă",
        "measure": "Număr înregistrări",
        "top_n": 20,
        "chart": "Bară",
    },
    "Distribuție pe ani": {
        "group_by": "An referință",
        "measure": "Număr înregistrări",
        "top_n": 50,
        "chart": "Linie",
    },
    "Distribuție pe status": {
        "group_by": "Status",
        "measure": "Număr înregistrări",
        "top_n": 20,
        "chart": "Bară",
    },
    "Top persoane": {
        "group_by": "Persoană",
        "measure": "Număr înregistrări",
        "top_n": 15,
        "chart": "Bară",
    },
    "Top entități": {
        "group_by": "Entitate",
        "measure": "Număr înregistrări",
        "top_n": 15,
        "chart": "Bară",
    },
    "Valoare totală pe categorii": {
        "group_by": "Sursă",
        "measure": "Sumă valori",
        "top_n": 20,
        "chart": "Bară",
    },
    "Valoare totală pe ani": {
        "group_by": "An referință",
        "measure": "Sumă valori",
        "top_n": 50,
        "chart": "Linie",
    },
}


def _safe_text(v) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    if s.lower() in ("nan", "none"):
        return ""
    return s


def _first_nonempty(row, fields):
    for f in fields:
        if f in row:
            v = _safe_text(row.get(f))
            if v:
                return v
    return ""


def _try_parse_date(v):
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


def _to_float(v):
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


def _fetch_table_all(supabase: Client, table: str, page_size: int = 1000, max_rows: int = 20000):
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


def _rows_to_df(rows, table_name: str) -> pd.DataFrame:
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

    value_num = []
    for _, r in df.iterrows():
        val = None
        for f in VALUE_FIELDS:
            if f in r and _safe_text(r.get(f)):
                val = _to_float(r.get(f))
                if val is not None:
                    break
        value_num.append(val if val is not None else 0.0)
    df["valoare_num"] = value_num

    for dcol in DATE_FIELDS:
        if dcol in df.columns:
            df[dcol] = df[dcol].apply(_try_parse_date)

    if "an_referinta" in df.columns:
        df["an_referinta"] = df["an_referinta"].apply(
            lambda x: int(float(x)) if _to_float(x) is not None else None
        )
    else:
        df["an_referinta"] = None

    return df


def _apply_global_filters(
    df: pd.DataFrame,
    selected_sources,
    an_de_la,
    an_pana_la,
    status_text,
    text_search,
):
    if df.empty:
        return df

    out = df.copy()

    if selected_sources:
        out = out[out["Sursa"].isin(selected_sources)]

    if an_de_la is not None:
        out = out[out["an_referinta"].fillna(-999999) >= int(an_de_la)]

    if an_pana_la is not None:
        out = out[out["an_referinta"].fillna(999999) <= int(an_pana_la)]

    if status_text.strip():
        needle = status_text.strip().lower()
        out = out[out["status_rezolvat"].fillna("").astype(str).str.lower().str.contains(needle, na=False)]

    if text_search.strip():
        needle = text_search.strip().lower()

        def _row_match(row):
            for col in [
                "cod_identificare",
                "titlu_rezolvat",
                "status_rezolvat",
                "persoana_relevanta",
                "entitate_relevanta",
                "Sursa",
                "Tip",
                "Subtip",
            ]:
                if col in row.index and needle in _safe_text(row[col]).lower():
                    return True
            return False

        out = out[out.apply(_row_match, axis=1)]

    return out


def _build_aggregate(df: pd.DataFrame, group_label: str, measure: str, top_n: int):
    if df.empty:
        return pd.DataFrame()

    group_col = GROUP_DIMENSIONS[group_label]
    work = df.copy()

    if group_col not in work.columns:
        work[group_col] = ""

    work[group_col] = work[group_col].apply(_safe_text)
    work[group_col] = work[group_col].replace("", "Necompletat")

    if measure == "Număr înregistrări":
        agg = (
            work.groupby(group_col, dropna=False)
            .size()
            .reset_index(name="Valoare")
        )
    else:
        agg = (
            work.groupby(group_col, dropna=False)["valoare_num"]
            .sum()
            .reset_index(name="Valoare")
        )

    agg = agg.sort_values("Valoare", ascending=False, kind="stable").reset_index(drop=True)

    if top_n and len(agg) > top_n:
        agg = agg.head(top_n).copy()

    agg = agg.rename(columns={group_col: "Dimensiune"})
    return agg


def _export_excel_bytes(df_summary: pd.DataFrame, df_details: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name="Sumar", index=False)
        df_details.to_excel(writer, sheet_name="Detalii", index=False)
    buf.seek(0)
    return buf.getvalue()


def _prepare_detail_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    cols = [
        "Sursa",
        "Tip",
        "Subtip",
        "cod_identificare",
        "titlu_rezolvat",
        "status_rezolvat",
        "an_referinta",
        "persoana_relevanta",
        "entitate_relevanta",
        "valoare_num",
        "data_inceput",
        "data_sfarsit",
        "data_contract",
        "data_apel",
        "data_depozit_cerere",
        "data_oficiala_acordare",
    ]
    cols = [c for c in cols if c in df.columns]

    out = df[cols].copy()

    for c in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[c]):
            out[c] = out[c].apply(lambda x: x.strftime("%d.%m.%Y") if pd.notna(x) else "")

    if "valoare_num" in out.columns:
        out["valoare_num"] = out["valoare_num"].apply(lambda x: _format_number_ro(x, 2) if pd.notna(x) else "")

    out = out.rename(columns={
        "Sursa": "SURSĂ",
        "Tip": "TIP",
        "Subtip": "SUBTIP",
        "cod_identificare": "COD IDENTIFICARE",
        "titlu_rezolvat": "TITLU / DENUMIRE / OBIECT",
        "status_rezolvat": "STATUS",
        "an_referinta": "AN REFERINȚĂ",
        "persoana_relevanta": "PERSOANĂ",
        "entitate_relevanta": "ENTITATE",
        "valoare_num": "VALOARE",
        "data_inceput": "DATA ÎNCEPUT",
        "data_sfarsit": "DATA SFÂRȘIT",
        "data_contract": "DATA CONTRACT",
        "data_apel": "DATA APEL",
        "data_depozit_cerere": "DATA DEPUNERE",
        "data_oficiala_acordare": "DATA ACORDARE",
    })

    return out


def _render_chart(df_summary: pd.DataFrame, chart_type: str, title: str):
    if df_summary.empty:
        return

    fig, ax = plt.subplots(figsize=(11, 5.5))

    x = df_summary["Dimensiune"].astype(str).tolist()
    y = df_summary["Valoare"].tolist()

    if chart_type == "Linie":
        ax.plot(x, y, marker="o")
    elif chart_type == "Pie":
        ax.pie(y, labels=x, autopct="%1.1f%%")
    else:
        ax.bar(x, y)

    ax.set_title(title)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def render_tab3_rapoarte_analiza(supabase: Client):
    st.markdown("## 📊 Rapoarte și analiză")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.88);font-size:1.02rem;font-weight:600;"
        "margin-bottom:0.85rem;'>Agregări, statistici, topuri și evoluții pe baza înregistrărilor existente.</div>",
        unsafe_allow_html=True,
    )

    source_labels = [TABLE_CONFIG[t]["label"] for t in ALL_TABLES]

    st.markdown(
        "<div style='background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.14);"
        "border-radius:14px;padding:14px 16px;margin-bottom:12px;'>",
        unsafe_allow_html=True,
    )

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        preset = st.selectbox(
            "Raport presetat",
            options=list(REPORT_PRESETS.keys()) + ["Personalizat"],
            index=0,
            key="tab3_preset",
        )

    with r1c2:
        selected_sources = st.multiselect(
            "Surse incluse",
            options=source_labels,
            default=[],
            placeholder="Gol = toate sursele",
            key="tab3_sources",
        )

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1:
        an_de_la = st.number_input("An de la", min_value=1900, max_value=2100, value=None, step=1, key="tab3_an_de_la")
    with r2c2:
        an_pana_la = st.number_input("An până la", min_value=1900, max_value=2100, value=None, step=1, key="tab3_an_pana_la")
    with r2c3:
        status_text = st.text_input("Filtru status", value="", key="tab3_status").strip()
    with r2c4:
        text_search = st.text_input("Căutare generală", value="", key="tab3_search").strip()

    if preset != "Personalizat":
        preset_cfg = REPORT_PRESETS[preset]
        default_group = preset_cfg["group_by"]
        default_measure = preset_cfg["measure"]
        default_top_n = preset_cfg["top_n"]
        default_chart = preset_cfg["chart"]
    else:
        default_group = "Sursă"
        default_measure = "Număr înregistrări"
        default_top_n = 20
        default_chart = "Bară"

    r3c1, r3c2, r3c3, r3c4 = st.columns(4)
    with r3c1:
        group_by_label = st.selectbox(
            "Grupează după",
            options=list(GROUP_DIMENSIONS.keys()),
            index=list(GROUP_DIMENSIONS.keys()).index(default_group),
            key="tab3_group_by",
        )
    with r3c2:
        measure = st.selectbox(
            "Măsură",
            options=["Număr înregistrări", "Sumă valori"],
            index=0 if default_measure == "Număr înregistrări" else 1,
            key="tab3_measure",
        )
    with r3c3:
        top_n = st.selectbox(
            "Top rezultate",
            options=[10, 15, 20, 30, 50, 100],
            index=[10, 15, 20, 30, 50, 100].index(default_top_n if default_top_n in [10, 15, 20, 30, 50, 100] else 20),
            key="tab3_top_n",
        )
    with r3c4:
        chart_type = st.selectbox(
            "Tip grafic",
            options=["Bară", "Linie", "Pie"],
            index=["Bară", "Linie", "Pie"].index(default_chart if default_chart in ["Bară", "Linie", "Pie"] else "Bară"),
            key="tab3_chart_type",
        )

    st.markdown("</div>", unsafe_allow_html=True)

    a1, a2 = st.columns([1.2, 5.8])
    with a1:
        genereaza = st.button("📈 Generează raport", use_container_width=True, key="tab3_generate")

    if genereaza:
        with st.spinner("Se construiește raportul..."):
            frames = []
            for t in ALL_TABLES:
                rows = _fetch_table_all(supabase, t, page_size=1000, max_rows=20000)
                if rows:
                    df_t = _rows_to_df(rows, t)
                    if not df_t.empty:
                        frames.append(df_t)

            if not frames:
                st.warning("Nu există date disponibile pentru raportare.")
                return

            df_all = pd.concat(frames, ignore_index=True, sort=False)
            df_filtered = _apply_global_filters(
                df=df_all,
                selected_sources=selected_sources,
                an_de_la=an_de_la,
                an_pana_la=an_pana_la,
                status_text=status_text,
                text_search=text_search,
            )

            st.session_state["tab3_df_filtered"] = df_filtered.copy()
            st.session_state["tab3_summary"] = _build_aggregate(
                df_filtered, group_by_label, measure, top_n
            )

    if "tab3_df_filtered" not in st.session_state or "tab3_summary" not in st.session_state:
        return

    df_filtered = st.session_state["tab3_df_filtered"].copy()
    df_summary = st.session_state["tab3_summary"].copy()

    if df_filtered.empty or df_summary.empty:
        st.info("Nu au fost identificate date pentru combinația selectată.")
        return

    total_records = len(df_filtered)
    total_value = float(df_filtered["valoare_num"].fillna(0).sum()) if "valoare_num" in df_filtered.columns else 0.0
    distinct_sources = df_filtered["Sursa"].nunique() if "Sursa" in df_filtered.columns else 0
    distinct_years = df_filtered["an_referinta"].dropna().nunique() if "an_referinta" in df_filtered.columns else 0

    st.divider()

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total înregistrări", f"{total_records}")
    with k2:
        st.metric("Total valori", _format_number_ro(total_value, 2))
    with k3:
        st.metric("Surse distincte", f"{distinct_sources}")
    with k4:
        st.metric("Ani distincți", f"{distinct_years}")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    _render_chart(
        df_summary,
        chart_type=chart_type,
        title=f"{preset} — {group_by_label} / {measure}" if preset != "Personalizat" else f"Raport personalizat — {group_by_label} / {measure}",
    )

    st.markdown(
        "<div style='color:#ffffff;font-size:1.00rem;font-weight:800;margin-top:6px;margin-bottom:8px;'>"
        "Tabel de sinteză"
        "</div>",
        unsafe_allow_html=True,
    )

    df_summary_display = df_summary.copy()
    if measure == "Sumă valori":
        df_summary_display["Valoare"] = df_summary_display["Valoare"].apply(lambda x: _format_number_ro(float(x), 2))
    else:
        df_summary_display["Valoare"] = df_summary_display["Valoare"].apply(lambda x: str(int(x)))

    df_summary_display = df_summary_display.rename(columns={
        "Dimensiune": "DIMENSIUNE",
        "Valoare": "VALOARE",
    })

    st.dataframe(
        df_summary_display,
        use_container_width=True,
        hide_index=True,
        height=360,
    )

    with st.expander("Detalii înregistrări incluse în raport", expanded=False):
        detail_df = _prepare_detail_df(df_filtered)
        st.dataframe(
            detail_df,
            use_container_width=True,
            hide_index=True,
            height=480,
        )

    export_summary = df_summary_display.copy()
    export_details = _prepare_detail_df(df_filtered)

    e1, e2 = st.columns(2)
    with e1:
        csv_data = export_summary.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Export sumar CSV",
            data=csv_data,
            file_name="tab3_raport_sumar.csv",
            mime="text/csv",
            use_container_width=True,
            key="tab3_export_csv",
        )

    with e2:
        xlsx_data = _export_excel_bytes(export_summary, export_details)
        st.download_button(
            "⬇️ Export raport Excel",
            data=xlsx_data,
            file_name="tab3_raport_analiza.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="tab3_export_xlsx",
        )
