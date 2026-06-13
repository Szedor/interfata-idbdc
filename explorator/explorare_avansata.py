# =========================================================
# IDBDC/explorator/explorare_avansata.py
# VERSIUNE: 3.0
# STATUS: RESCRIS - 5 criterii corecte, Sursa de finantare ca pivot
# DATA: 2026.06.13
# =========================================================
# MODIFICĂRI VERSIUNEA 3.0:
#   - Criteriul 2 corectat: "Sursa de finantare" înlocuiește
#     "Titlu / denumire / obiect" (care era redundant cu Tab1)
#   - 5 criterii: Categorie, Sursa finantare, Perioada,
#     Entitati implicate, Status
#   - Afișare implicită 250 rezultate cu selector 100/250/500/Toate
#   - Tabel de rezultate cu coloane comune tuturor categoriilor
#   - Export CSV și Excel
# =========================================================

import io
from datetime import date, datetime
from typing import Any, Dict, List

import pandas as pd
import streamlit as st
from supabase import Client


# =========================================================
# CONFIGURARE TABELE
# =========================================================

TABLE_CONFIG = {
    "base_contracte_cep": {
        "label":      "📄 Contracte CEP",
        "categorie":  "Contracte",
        "subcategorie": "CEP",
    },
    "base_contracte_terti": {
        "label":      "📄 Contracte TERȚI",
        "categorie":  "Contracte",
        "subcategorie": "TERȚI",
    },
    "base_contracte_speciale": {
        "label":      "📄 Contracte SPECIALE",
        "categorie":  "Contracte",
        "subcategorie": "SPECIALE",
    },
    "base_proiecte_fdi": {
        "label":      "🔬 Proiecte FDI",
        "categorie":  "Proiecte",
        "subcategorie": "FDI",
    },
    "base_proiecte_pncdi": {
        "label":      "🔬 Proiecte PNCDI",
        "categorie":  "Proiecte",
        "subcategorie": "PNCDI",
    },
    "base_proiecte_pnrr": {
        "label":      "🔬 Proiecte PNRR",
        "categorie":  "Proiecte",
        "subcategorie": "PNRR",
    },
    "base_proiecte_internationale": {
        "label":      "🌍 Proiecte Internaționale",
        "categorie":  "Proiecte",
        "subcategorie": "Internaționale",
    },
    "base_proiecte_interreg": {
        "label":      "🌍 Proiecte INTERREG",
        "categorie":  "Proiecte",
        "subcategorie": "INTERREG",
    },
    "base_proiecte_nonue": {
        "label":      "🌍 Proiecte NON-EU",
        "categorie":  "Proiecte",
        "subcategorie": "NON-EU",
    },
    "base_proiecte_see": {
        "label":      "🌍 Proiecte SEE",
        "categorie":  "Proiecte",
        "subcategorie": "SEE",
    },
    "base_evenimente_stiintifice": {
        "label":      "🎓 Evenimente Științifice",
        "categorie":  "Evenimente",
        "subcategorie": "Științifice",
    },
    "base_prop_industr": {
        "label":      "💡 Proprietate Industrială",
        "categorie":  "Proprietate Industrială",
        "subcategorie": "PI",
    },
}

ALL_TABLES = list(TABLE_CONFIG.keys())

# Câmpuri în care se caută sursa de finanțare (criteriul 2-pivot)
SURSA_FIELDS = [
    "program_finantare",
    "programul_de_finantare",
    "program",
    "programul",
    "schema_de_finantare",
    "sursa_finantatoare",
    "mecanism_finantare",
    "mecanism_financiar",
    "apel_pentru_propuneri",
    "identificare_apel",
    "linia_de_finantare",
    "categoria",
]

# Câmpuri în care se caută entitățile implicate (criteriul 4)
ENTITATE_FIELDS = [
    "denumire_beneficiar",
    "denumire_participanti",
    "parteneri",
    "denumire_solicitant",
    "denumire_titular",
    "institutii_organizatoare",
    "institutii_organizare",
    "coordonator",
    "director_proiect",
    "acronim_departament",
    "denumire_departament",
    "rol_upt",
    "tematica",
    "domeniu_cercetare",
    "domeniu_aplicare",
]

# Câmpuri dată — pentru criteriul 3 (perioadă)
DATE_FIELDS = [
    "data_inceput",
    "data_sfarsit",
    "data_contract",
    "data_apel",
    "data_depozit_cerere",
    "data_oficiala_de_acordare",
    "data_inceput_rol",
    "data_sfarsit_rol",
    "data_inchidere_apel",
]

# Câmpuri status — pentru criteriul 5
STATUS_FIELDS = [
    "status_contract_proiect",
    "status_document",
    "status_personal",
    "status_activ",
]

# Câmpuri titlu/denumire — pentru coloana tabel rezultate
TITLE_FIELDS = [
    "titlul_proiect",
    "titlul_eveniment",
    "titlul_proprietatii",
    "denumire_completa",
    "obiectul_contractului",
    "denumire",
]

# Câmpuri valoare — pentru coloana tabel rezultate
VALUE_FIELDS = [
    "valoare_contract_cep_terti_speciale",
    "valoare_totala_contract",
    "cost_total_proiect",
    "suma_solicitata_fdi",
    "suma_aprobata_mec",
    "contributie_ue_proiect_upt",
    "costuri_totale_proiect",
    "grant_aprobat",
]


# =========================================================
# FUNCȚII AJUTĂTOARE
# =========================================================

def _safe_text(v: Any) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    return "" if s.lower() in ("nan", "none") else s


def _first_nonempty(row: dict, fields: list) -> str:
    for f in fields:
        v = _safe_text(row.get(f))
        if v:
            return v
    return ""


def _try_parse_date(v: Any):
    if v is None:
        return pd.NaT
    if isinstance(v, (datetime, date)):
        return pd.to_datetime(v, errors="coerce")
    s = str(v).strip()
    if not s:
        return pd.NaT
    return pd.to_datetime(s, errors="coerce", dayfirst=True)


def _to_float(v: Any):
    if v is None:
        return None
    s = _safe_text(v).replace(" ", "")
    if not s:
        return None
    # normalizare separator
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None


def _format_number_ro(v: float, decimals: int = 2) -> str:
    if decimals == 0:
        return f"{int(round(v)):,}".replace(",", ".")
    return f"{v:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fetch_table_all(supabase: Client, table: str,
                     page_size: int = 1000, max_rows: int = 10000) -> list:
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


def _rows_to_df(rows: list, table_name: str) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows).copy()
    cfg = TABLE_CONFIG.get(table_name, {})
    df["_sursa"]      = cfg.get("label", table_name)
    df["_categorie"]  = cfg.get("categorie", "")
    df["_subcategorie"] = cfg.get("subcategorie", "")
    df["_titlu"]      = df.apply(lambda r: _first_nonempty(r, TITLE_FIELDS), axis=1)
    df["_status"]     = df.apply(lambda r: _first_nonempty(r, STATUS_FIELDS), axis=1)

    # Valoare numerică (primul câmp nevid din VALUE_FIELDS)
    val_list = []
    for _, r in df.iterrows():
        v = None
        for f in VALUE_FIELDS:
            raw = _safe_text(r.get(f))
            if raw:
                v = _to_float(raw)
                if v is not None:
                    break
        val_list.append(_format_number_ro(v, 2) if v is not None else "")
    df["_valoare"] = val_list

    # Date
    for dcol in DATE_FIELDS:
        if dcol in df.columns:
            df[dcol] = df[dcol].apply(_try_parse_date)

    # An referință — extras din data_inceput dacă nu există explicit
    if "an_referinta" in df.columns:
        df["_an"] = df["an_referinta"].apply(
            lambda x: int(float(x)) if _to_float(x) is not None else None
        )
    elif "data_inceput" in df.columns:
        df["_an"] = df["data_inceput"].apply(
            lambda x: x.year if pd.notna(x) else None
        )
    else:
        df["_an"] = None

    return df


# =========================================================
# FILTRARE
# =========================================================

def _contains_in_fields(row: pd.Series, needle: str, fields: list) -> bool:
    needle = needle.strip().lower()
    if not needle:
        return True
    for f in fields:
        if f in row.index:
            if needle in _safe_text(row[f]).lower():
                return True
    return False


def _apply_filters(
    df: pd.DataFrame,
    categorii_selectate: list,
    sursa_text: str,
    an_de_la,
    an_pana_la,
    data_de_la,
    data_pana_la,
    entitate_text: str,
    status_text: str,
) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()

    # Criteriul 1 — Categoria principală
    if categorii_selectate:
        out = out[out["_sursa"].isin(categorii_selectate)]

    # Criteriul 2 — Sursa de finanțare (pivot)
    if sursa_text.strip():
        needle = sursa_text.strip().lower()
        out = out[out.apply(
            lambda r: _contains_in_fields(r, needle, SURSA_FIELDS), axis=1
        )]

    # Criteriul 3 — Perioadă / interval
    if an_de_la is not None and "_an" in out.columns:
        out = out[out["_an"].fillna(-999999) >= int(an_de_la)]
    if an_pana_la is not None and "_an" in out.columns:
        out = out[out["_an"].fillna(999999) <= int(an_pana_la)]

    if (data_de_la or data_pana_la):
        existing = [c for c in DATE_FIELDS if c in out.columns]
        if existing:
            def _date_ok(row):
                vals = [row[c] for c in existing if pd.notna(row[c])]
                if not vals:
                    return False
                for dt in vals:
                    d = pd.to_datetime(dt).date()
                    ok1 = True if data_de_la is None else d >= data_de_la
                    ok2 = True if data_pana_la is None else d <= data_pana_la
                    if ok1 and ok2:
                        return True
                return False
            out = out[out.apply(_date_ok, axis=1)]

    # Criteriul 4 — Entități implicate
    if entitate_text.strip():
        needle = entitate_text.strip().lower()
        out = out[out.apply(
            lambda r: _contains_in_fields(r, needle, ENTITATE_FIELDS), axis=1
        )]

    # Criteriul 5 — Status
    if status_text.strip():
        needle = status_text.strip().lower()
        out = out[out["_status"].fillna("").str.lower().str.contains(needle, na=False)]

    return out


# =========================================================
# AFIȘARE REZULTATE
# =========================================================

def _prepare_display_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    cols_display = []
    rename_map = {}

    # Codul identificare
    if "cod_identificare" in df.columns:
        cols_display.append("cod_identificare")
        rename_map["cod_identificare"] = "COD IDENTIFICARE"

    cols_display += ["_sursa", "_titlu", "_status", "_an"]
    rename_map.update({
        "_sursa":    "SURSĂ / CATEGORIE",
        "_titlu":    "TITLU / DENUMIRE / OBIECT",
        "_status":   "STATUS",
        "_an":       "AN",
    })

    if "data_inceput" in df.columns:
        cols_display.append("data_inceput")
        rename_map["data_inceput"] = "DATA ÎNCEPUT"
    if "data_sfarsit" in df.columns:
        cols_display.append("data_sfarsit")
        rename_map["data_sfarsit"] = "DATA SFÂRȘIT"

    cols_display.append("_valoare")
    rename_map["_valoare"] = "VALOARE"

    final = [c for c in cols_display if c in df.columns]
    disp = df[final].copy()

    # Formatare date
    for c in disp.columns:
        if pd.api.types.is_datetime64_any_dtype(disp[c]):
            disp[c] = disp[c].apply(
                lambda x: x.strftime("%d.%m.%Y") if pd.notna(x) else ""
            )

    # Formatare cod_identificare — fără zecimale
    if "cod_identificare" in disp.columns:
        def _fmt_cod(v):
            s = _safe_text(v)
            f = _to_float(s)
            if f is not None and float(f).is_integer():
                return str(int(f))
            return s
        disp["cod_identificare"] = disp["cod_identificare"].apply(_fmt_cod)

    # An fără zecimale
    if "_an" in disp.columns:
        disp["_an"] = disp["_an"].apply(
            lambda x: str(int(x)) if pd.notna(x) and x is not None else ""
        )

    disp = disp.rename(columns=rename_map)
    return disp


def _export_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Explorare", index=False)
    buf.seek(0)
    return buf.getvalue()


# =========================================================
# RENDER PRINCIPAL
# =========================================================

def render_tab2_explorare_avansata(supabase: Client):
    st.markdown("## 🔎 Explorare avansată")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.88);font-size:1.02rem;font-weight:600;"
        "margin-bottom:0.85rem;'>Găsiți seturi de înregistrări folosind între 2 și 5 criterii "
        "combinate. Criteriile 1 și 2 sunt recomandate ca punct de plecare.</div>",
        unsafe_allow_html=True,
    )

    # ── Zona filtre ────────────────────────────────────────────────────
    st.markdown(
        "<div style='background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.14);"
        "border-radius:14px;padding:14px 16px;margin-bottom:12px;'>",
        unsafe_allow_html=True,
    )

    tabel_labels = [TABLE_CONFIG[t]["label"] for t in ALL_TABLES]

    # Criteriul 1 — Categoria principală
    st.markdown(
        "<div style='color:rgba(255,255,255,0.70);font-size:0.88rem;font-weight:700;"
        "text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;'>"
        "1. Categoria principală</div>",
        unsafe_allow_html=True,
    )
    categorii_selectate = st.multiselect(
        "Categoria",
        options=tabel_labels,
        default=[],
        placeholder="Gol = toate categoriile",
        key="tab2_categorii",
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Criteriul 2 — Sursa de finanțare (pivot)
    st.markdown(
        "<div style='color:rgba(255,255,255,0.70);font-size:0.88rem;font-weight:700;"
        "text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;'>"
        "2. Sursa de finanțare</div>",
        unsafe_allow_html=True,
    )
    sursa_text = st.text_input(
        "Sursa",
        value="",
        placeholder="Ex: Horizon Europe, PNCDI, FDI, INTERREG, UEFISCDI, bilateral...",
        key="tab2_sursa",
        label_visibility="collapsed",
    ).strip()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Criteriul 3 — Perioadă / interval
    st.markdown(
        "<div style='color:rgba(255,255,255,0.70);font-size:0.88rem;font-weight:700;"
        "text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;'>"
        "3. Perioadă / interval</div>",
        unsafe_allow_html=True,
    )
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        an_de_la = st.number_input(
            "An de la", min_value=1990, max_value=2100,
            value=None, step=1, key="tab2_an_de_la",
        )
    with p2:
        an_pana_la = st.number_input(
            "An până la", min_value=1990, max_value=2100,
            value=None, step=1, key="tab2_an_pana_la",
        )
    with p3:
        data_de_la = st.date_input(
            "📅 Dată de la", value=None,
            key="tab2_data_de_la", format="DD.MM.YYYY",
        )
    with p4:
        data_pana_la = st.date_input(
            "📅 Dată până la", value=None,
            key="tab2_data_pana_la", format="DD.MM.YYYY",
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Criteriile 4 și 5 — pe același rând
    c4, c5 = st.columns(2)
    with c4:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.70);font-size:0.88rem;font-weight:700;"
            "text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;'>"
            "4. Entități implicate</div>",
            unsafe_allow_html=True,
        )
        entitate_text = st.text_input(
            "Entitate",
            value="",
            placeholder="Beneficiar, partener, departament, rol UPT, domeniu...",
            key="tab2_entitate",
            label_visibility="collapsed",
        ).strip()
    with c5:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.70);font-size:0.88rem;font-weight:700;"
            "text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;'>"
            "5. Status</div>",
            unsafe_allow_html=True,
        )
        status_text = st.text_input(
            "Status",
            value="",
            placeholder="Ex: activ, finalizat, în evaluare, respins...",
            key="tab2_status",
            label_visibility="collapsed",
        ).strip()

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Butoane acțiune ────────────────────────────────────────────────
    b1, b2, b3 = st.columns([1.4, 1.2, 4.4])
    with b1:
        cauta = st.button(
            "🔎 Explorează baza de date",
            use_container_width=True,
            key="tab2_search_btn",
        )
    with b2:
        reset = st.button(
            "🧹 Resetează",
            use_container_width=True,
            key="tab2_reset_btn",
        )

    if reset:
        for k in [
            "tab2_categorii", "tab2_sursa", "tab2_an_de_la", "tab2_an_pana_la",
            "tab2_data_de_la", "tab2_data_pana_la", "tab2_entitate", "tab2_status",
            "tab2_results_df",
        ]:
            st.session_state.pop(k, None)
        st.rerun()

    # ── Număr criterii active ──────────────────────────────────────────
    n_criterii = sum([
        bool(categorii_selectate),
        bool(sursa_text),
        bool(an_de_la is not None or an_pana_la is not None
             or data_de_la is not None or data_pana_la is not None),
        bool(entitate_text),
        bool(status_text),
    ])
    st.markdown(
        f"<div style='color:rgba(255,255,255,0.50);font-size:0.86rem;"
        f"margin-top:6px;margin-bottom:8px;'>"
        f"Criterii active: <b style='color:rgba(255,255,255,0.85);'>{n_criterii}</b> din 5</div>",
        unsafe_allow_html=True,
    )

    # ── Execuție căutare ───────────────────────────────────────────────
    if cauta:
        if n_criterii < 1:
            st.warning("Completați cel puțin un criteriu de căutare.")
            return

        selected_tables = (
            [t for t, cfg in TABLE_CONFIG.items() if cfg["label"] in categorii_selectate]
            if categorii_selectate
            else ALL_TABLES
        )

        with st.spinner("Se explorează baza de date..."):
            frames = []
            for t in selected_tables:
                rows = _fetch_table_all(supabase, t)
                if rows:
                    df_t = _rows_to_df(rows, t)
                    if not df_t.empty:
                        frames.append(df_t)

            if not frames:
                st.warning("Nu au fost identificate date în categoriile selectate.")
                return

            df_all = pd.concat(frames, ignore_index=True, sort=False)
            df_filtered = _apply_filters(
                df=df_all,
                categorii_selectate=categorii_selectate,
                sursa_text=sursa_text,
                an_de_la=an_de_la,
                an_pana_la=an_pana_la,
                data_de_la=data_de_la,
                data_pana_la=data_pana_la,
                entitate_text=entitate_text,
                status_text=status_text,
            )
            st.session_state["tab2_results_df"] = df_filtered.copy()

    # ── Afișare rezultate ──────────────────────────────────────────────
    if "tab2_results_df" not in st.session_state:
        return

    results_df = st.session_state["tab2_results_df"].copy()

    if results_df.empty:
        st.info("Nu au fost identificate înregistrări pentru combinația selectată.")
        return

    total_rows = len(results_df)
    st.divider()

    st.markdown(
        f"<div style='color:#ffffff;font-size:1.02rem;font-weight:800;margin-bottom:10px;'>"
        f"Rezultate identificate: {total_rows}"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Selector limită afișare
    s1, s2, s3 = st.columns([1.4, 1.4, 4.2])
    with s1:
        optiuni_limita = [100, 250, 500, 1000, "Toate"]
        # Implicit 250, sau primul din listă mai mare decât total
        idx_default = 1  # 250
        if total_rows <= 100:
            idx_default = 0
        limita = st.selectbox(
            "Afișare",
            options=optiuni_limita,
            index=idx_default,
            key="tab2_limita",
        )
    with s2:
        sortare = st.selectbox(
            "Sortare",
            options=["SURSĂ / CATEGORIE", "COD IDENTIFICARE", "STATUS", "AN"],
            index=0,
            key="tab2_sortare",
        )

    display_df = _prepare_display_df(results_df)

    # Sortare
    if sortare in display_df.columns:
        try:
            display_df = display_df.sort_values(by=sortare, kind="stable", na_position="last")
        except Exception:
            pass

    # Aplicare limită
    if limita != "Toate":
        limita_int = int(limita)
        if total_rows > limita_int:
            st.info(
                f"Au fost identificate {total_rows} rezultate. "
                f"Se afișează primele {limita_int}. "
                f"Selectați „Toate" sau rafinați criteriile."
            )
        shown_df = display_df.head(limita_int).copy()
    else:
        shown_df = display_df.copy()

    st.dataframe(
        shown_df,
        use_container_width=True,
        hide_index=True,
        height=520,
    )

    # ── Export ────────────────────────────────────────────────────────
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    e1, e2 = st.columns([1.2, 1.2])
    with e1:
        csv_bytes = shown_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Export CSV",
            data=csv_bytes,
            file_name="explorare_avansata.csv",
            mime="text/csv",
            use_container_width=True,
            key="tab2_export_csv",
        )
    with e2:
        xlsx_bytes = _export_excel_bytes(shown_df)
        st.download_button(
            "⬇️ Export Excel",
            data=xlsx_bytes,
            file_name="explorare_avansata.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="tab2_export_xlsx",
        )
