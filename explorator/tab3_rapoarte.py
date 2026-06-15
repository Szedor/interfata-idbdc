# =========================================================
# IDBDC/explorator/tab3_rapoarte.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.06.14
# =========================================================
# RAPOARTE + GRAFICE INTERACTIVE (Plotly)
# - 7 rapoarte presetate
# - rapoarte personalizate prin filtre combinate
# - grafice interactive Plotly (tip ales automat per raport)
# - export CSV, Excel, PDF, Print
# - autentificare email UPT (identic Tab1)
# =========================================================

import io
import re
import html as _html
from datetime import date, datetime
from typing import Any

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
from supabase import Client

# =========================================================
# CONFIGURARE
# =========================================================

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
    "base_proiecte_nonue": {
        "label": "🌍 Proiecte NON-EU",
        "categorie": "Proiecte",
        "subcategorie": "NON-EU",
    },
    "base_proiecte_see": {
        "label": "🌍 Proiecte SEE",
        "categorie": "Proiecte",
        "subcategorie": "SEE",
    },
    "base_proiecte_structurale": {
        "label": "🌍 Proiecte Structurale",
        "categorie": "Proiecte",
        "subcategorie": "STRUCTURALE",
    },
    "base_evenimente_stiintifice": {
        "label": "🎓 Evenimente Științifice",
        "categorie": "Evenimente",
        "subcategorie": "Științifice",
    },
    "base_prop_industr": {
        "label": "💡 Proprietate Industrială",
        "categorie": "Proprietate Industrială",
        "subcategorie": "PI",
    },
}

ALL_TABLES = list(TABLE_CONFIG.keys())

TITLE_FIELDS = [
    "titlul_proiect", "titlul_eveniment", "titlul_proprietatii",
    "obiectul_contractului", "denumire",
]

STATUS_FIELDS = [
    "status_contract_proiect", "status_document",
    "status_personal", "status_activ",
]

PERSON_FIELDS = [
    "persoana_contact", "director_proiect", "coordonator",
]

ENTITY_FIELDS = [
    "denumire_beneficiar", "denumire_participanti", "parteneri",
    "denumire_solicitant", "denumire_titular", "institutii_organizatoare",
    "coordonator", "director_proiect",
]

VALUE_FIELDS = [
    "valoare_contract_cep_terti_speciale", "valoare_totala_contract",
    "cost_total_proiect", "suma_solicitata_fdi", "suma_aprobata_mec",
    "contributie_ue_proiect_upt", "costuri_totale_proiect", "grant_aprobat",
]

DATE_FIELDS = [
    "data_inceput", "data_sfarsit", "data_contract", "data_apel",
    "data_depozit_cerere", "data_oficiala_de_acordare",
]

GROUP_DIMENSIONS = {
    "Sursă / Categorie":  "Sursa",
    "Tip":                "Tip",
    "Subtip":             "Subtip",
    "An referință":       "an_referinta",
    "Status":             "status_rezolvat",
    "Persoană":           "persoana_relevanta",
    "Entitate":           "entitate_relevanta",
}

REPORT_PRESETS = {
    "Distribuție pe categorii": {
        "group_by": "Sursă / Categorie",
        "measure":  "Număr înregistrări",
        "top_n":    20,
        "chart":    "auto",
    },
    "Distribuție pe ani": {
        "group_by": "An referință",
        "measure":  "Număr înregistrări",
        "top_n":    50,
        "chart":    "auto",
    },
    "Distribuție pe status": {
        "group_by": "Status",
        "measure":  "Număr înregistrări",
        "top_n":    20,
        "chart":    "auto",
    },
    "Top persoane": {
        "group_by": "Persoană",
        "measure":  "Număr înregistrări",
        "top_n":    15,
        "chart":    "auto",
    },
    "Top entități": {
        "group_by": "Entitate",
        "measure":  "Număr înregistrări",
        "top_n":    15,
        "chart":    "auto",
    },
    "Valoare totală pe categorii": {
        "group_by": "Sursă / Categorie",
        "measure":  "Sumă valori",
        "top_n":    20,
        "chart":    "auto",
    },
    "Valoare totală pe ani": {
        "group_by": "An referință",
        "measure":  "Sumă valori",
        "top_n":    50,
        "chart":    "auto",
    },
}

# Culori consistente per categorie
CULORI_CATEGORII = [
    "#4e9af1", "#f1c40f", "#2ecc71", "#e74c3c", "#9b59b6",
    "#1abc9c", "#e67e22", "#34495e", "#e91e8c", "#00bcd4",
    "#ff5722", "#607d8b", "#795548",
]


# =========================================================
# HELPERS DATE
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
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") \
            if s.rfind(",") > s.rfind(".") else s.replace(",", "")
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


# =========================================================
# FETCH DATE
# =========================================================

def _fetch_table_all(supabase: Client, table: str,
                     page_size: int = 1000, max_rows: int = 20000) -> list:
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
    df["Sursa"]             = cfg.get("label", table_name)
    df["Tip"]               = cfg.get("categorie", "")
    df["Subtip"]            = cfg.get("subcategorie", "")
    df["titlu_rezolvat"]    = df.apply(lambda r: _first_nonempty(r, TITLE_FIELDS), axis=1)
    df["status_rezolvat"]   = df.apply(lambda r: _first_nonempty(r, STATUS_FIELDS), axis=1)
    df["persoana_relevanta"]= df.apply(lambda r: _first_nonempty(r, PERSON_FIELDS), axis=1)
    df["entitate_relevanta"]= df.apply(lambda r: _first_nonempty(r, ENTITY_FIELDS), axis=1)

    val_list = []
    for _, r in df.iterrows():
        v = None
        for f in VALUE_FIELDS:
            raw = _safe_text(r.get(f))
            if raw:
                v = _to_float(raw)
                if v is not None:
                    break
        val_list.append(v if v is not None else 0.0)
    df["valoare_num"] = val_list

    for dcol in DATE_FIELDS:
        if dcol in df.columns:
            df[dcol] = df[dcol].apply(_try_parse_date)

    if "an_referinta" in df.columns:
        df["an_referinta"] = df["an_referinta"].apply(
            lambda x: int(float(x)) if _to_float(x) is not None else None
        )
    elif "data_inceput" in df.columns:
        df["an_referinta"] = df["data_inceput"].apply(
            lambda x: x.year if pd.notna(x) else None
        )
    else:
        df["an_referinta"] = None

    return df


# =========================================================
# FILTRARE
# =========================================================

def _apply_global_filters(df, selected_sources, an_de_la, an_pana_la,
                           status_text, text_search):
    if df.empty:
        return df
    out = df.copy()

    if selected_sources:
        out = out[out["Sursa"].isin(selected_sources)]

    if an_de_la is not None and "an_referinta" in out.columns:
        out = out[out["an_referinta"].fillna(-999999) >= int(an_de_la)]

    if an_pana_la is not None and "an_referinta" in out.columns:
        out = out[out["an_referinta"].fillna(999999) <= int(an_pana_la)]

    if status_text.strip():
        needle = status_text.strip().lower()
        out = out[out["status_rezolvat"].fillna("").str.lower().str.contains(needle, na=False)]

    if text_search.strip():
        needle = text_search.strip().lower()
        def _row_match(row):
            for col in ["cod_identificare", "titlu_rezolvat", "status_rezolvat",
                        "persoana_relevanta", "entitate_relevanta", "Sursa", "Tip", "Subtip"]:
                if col in row.index and needle in _safe_text(row[col]).lower():
                    return True
            return False
        out = out[out.apply(_row_match, axis=1)]

    return out


# =========================================================
# AGREGARE
# =========================================================

def _build_aggregate(df: pd.DataFrame, group_label: str,
                     measure: str, top_n: int) -> pd.DataFrame:
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


# =========================================================
# GRAFICE PLOTLY — tip ales automat
# =========================================================

def _choose_chart_type(group_label: str, df_agg: pd.DataFrame) -> str:
    """
    Alege tipul de grafic optim pentru fiecare combinație:
    - An → Linie (evoluție temporală)
    - Persoană / Entitate → Bară orizontală (multe etichete)
    - Categorie / Tip / Subtip cu ≤ 6 valori → Pie
    - Altceva → Bară verticală
    """
    n = len(df_agg)
    if "an" in group_label.lower():
        return "linie"
    if group_label in ("Persoană", "Entitate"):
        return "bara_orizontala"
    if group_label in ("Sursă / Categorie", "Tip", "Subtip", "Status") and n <= 8:
        return "pie"
    return "bara"


def _render_chart_plotly(df_agg: pd.DataFrame, group_label: str,
                         measure: str, titlu: str, chart_override: str = "auto"):
    if df_agg.empty:
        return

    tip = chart_override if chart_override != "auto" else _choose_chart_type(group_label, df_agg)

    x_vals = df_agg["Dimensiune"].astype(str).tolist()
    y_vals = df_agg["Valoare"].tolist()

    culori = CULORI_CATEGORII[:len(x_vals)]
    if len(culori) < len(x_vals):
        culori = culori * (len(x_vals) // len(culori) + 1)
    culori = culori[:len(x_vals)]

    layout_common = dict(
        title=dict(text=titlu, font=dict(color="#ffffff", size=14)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.04)",
        font=dict(color="rgba(255,255,255,0.85)"),
        margin=dict(l=60, r=30, t=50, b=80),
        hoverlabel=dict(bgcolor="#0b2a52", font_color="#ffffff"),
    )

    if tip == "linie":
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_vals,
            mode="lines+markers",
            line=dict(color="#4e9af1", width=2.5),
            marker=dict(size=7, color="#4e9af1"),
            hovertemplate="<b>%{x}</b><br>" + measure + ": %{y:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            **layout_common,
            xaxis=dict(title=group_label, tickangle=-45,
                       gridcolor="rgba(255,255,255,0.10)"),
            yaxis=dict(title=measure, gridcolor="rgba(255,255,255,0.10)"),
        )

    elif tip == "bara_orizontala":
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=y_vals, y=x_vals,
            orientation="h",
            marker_color=culori,
            hovertemplate="<b>%{y}</b><br>" + measure + ": %{x:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            **layout_common,
            xaxis=dict(title=measure, gridcolor="rgba(255,255,255,0.10)"),
            yaxis=dict(title=group_label, autorange="reversed"),
            margin=dict(l=200, r=30, t=50, b=40),
        )

    elif tip == "pie":
        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels=x_vals, values=y_vals,
            marker=dict(colors=culori),
            hole=0.35,
            hovertemplate="<b>%{label}</b><br>" + measure +
                          ": %{value:,.0f}<br>%{percent}<extra></extra>",
            textinfo="label+percent",
            textfont=dict(color="#ffffff", size=11),
        ))
        fig.update_layout(
            **layout_common,
            showlegend=True,
            legend=dict(font=dict(color="rgba(255,255,255,0.80)")),
        )

    else:  # bara verticală
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=x_vals, y=y_vals,
            marker_color=culori,
            hovertemplate="<b>%{x}</b><br>" + measure + ": %{y:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            **layout_common,
            xaxis=dict(title=group_label, tickangle=-45,
                       gridcolor="rgba(255,255,255,0.10)"),
            yaxis=dict(title=measure, gridcolor="rgba(255,255,255,0.10)"),
        )

    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# EXPORT
# =========================================================

def _build_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def _build_excel_bytes(df_summary: pd.DataFrame, df_details: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name="Sumar", index=False)
        df_details.to_excel(writer, sheet_name="Detalii", index=False)
    buf.seek(0)
    return buf.getvalue()


def _build_pdf_bytes(df_summary: pd.DataFrame, titlu: str) -> bytes | None:
    try:
        from fpdf import FPDF
        import matplotlib
        import os
        font_path = os.path.join(
            os.path.dirname(matplotlib.__file__),
            "mpl-data", "fonts", "ttf", "DejaVuSans.ttf"
        )
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=12)
        pdf.add_page()
        use_dv = os.path.exists(font_path)
        if use_dv:
            pdf.add_font("DejaVu", fname=font_path)
            pdf.set_font("DejaVu", size=12)
        else:
            pdf.set_font("Helvetica", size=12)

        pdf.set_text_color(11, 42, 82)
        pdf.cell(0, 10, f"IDBDC UPT — {titlu}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(4)

        cols = list(df_summary.columns)
        col_w = min(45, 180 // max(len(cols), 1))

        if use_dv:
            pdf.set_font("DejaVu", size=8)
        else:
            pdf.set_font("Helvetica", size=8)

        pdf.set_fill_color(11, 42, 82)
        pdf.set_text_color(255, 255, 255)
        for col in cols:
            pdf.cell(col_w, 7, str(col)[:20], border=1, fill=True)
        pdf.ln()

        pdf.set_text_color(0, 0, 0)
        for i, (_, row) in enumerate(df_summary.iterrows()):
            if i % 2 == 0:
                pdf.set_fill_color(238, 242, 247)
            else:
                pdf.set_fill_color(255, 255, 255)
            for col in cols:
                val = str(row.get(col, ""))[:22]
                pdf.cell(col_w, 6, val, border=1, fill=True)
            pdf.ln()

        pdf.ln(6)
        pdf.set_font("Helvetica" if not use_dv else "DejaVu", size=7)
        pdf.set_text_color(130, 130, 130)
        pdf.cell(0, 5, "Document generat automat — IDBDC UPT | Uz intern",
                 new_x="LMARGIN", new_y="NEXT", align="C")

        return bytes(pdf.output())
    except Exception:
        return None


def _build_print_html(df_summary: pd.DataFrame, titlu: str) -> str:
    cols = list(df_summary.columns)
    hdrs = "".join(
        f"<th style='border:1px solid #c0cce0;padding:5px 8px;font-size:10px;"
        f"background:#0b2a52;color:#fff;text-align:left;'>"
        f"{_html.escape(str(c))}</th>"
        for c in cols
    )
    rows_html = ""
    for i, (_, row) in enumerate(df_summary.iterrows()):
        bg = "#f7f9fc" if i % 2 == 0 else "#ffffff"
        cells = "".join(
            f"<td style='border:1px solid #c0cce0;padding:4px 8px;"
            f"font-size:10px;background:{bg};'>"
            f"{_html.escape(str(row.get(c, '')))}</td>"
            for c in cols
        )
        rows_html += f"<tr>{cells}</tr>"

    return (
        "<!DOCTYPE html><html><head><meta charset='UTF-8'>"
        f"<title>{_html.escape(titlu)}</title>"
        "<style>body{font-family:Arial,sans-serif;margin:20px;}"
        "table{border-collapse:collapse;width:100%;margin-top:12px;}"
        "h2{color:#0b2a52;font-size:14px;}"
        ".btn{display:inline-block;margin-bottom:14px;padding:7px 18px;"
        "background:#0b2a52;color:#fff;border:none;border-radius:6px;"
        "font-weight:700;cursor:pointer;font-size:12px;}"
        "@media print{.btn{display:none;}}"
        "</style></head><body>"
        "<button class='btn' onclick='window.print()'>🖨️ Tipărire</button>"
        f"<h2>IDBDC UPT &mdash; {_html.escape(titlu)}</h2>"
        f"<table><thead><tr>{hdrs}</tr></thead><tbody>{rows_html}</tbody></table>"
        "</body></html>"
    )


def _prepare_detail_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    cols = ["Sursa", "Tip", "Subtip", "cod_identificare", "titlu_rezolvat",
            "status_rezolvat", "an_referinta", "persoana_relevanta",
            "entitate_relevanta", "valoare_num", "data_inceput", "data_sfarsit"]
    cols = [c for c in cols if c in df.columns]
    out = df[cols].copy()
    for c in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[c]):
            out[c] = out[c].apply(lambda x: x.strftime("%d.%m.%Y") if pd.notna(x) else "")
    if "valoare_num" in out.columns:
        out["valoare_num"] = out["valoare_num"].apply(
            lambda x: _format_number_ro(float(x), 2) if pd.notna(x) else ""
        )
    out = out.rename(columns={
        "Sursa": "SURSĂ", "Tip": "TIP", "Subtip": "SUBTIP",
        "cod_identificare": "COD", "titlu_rezolvat": "TITLU / OBIECT",
        "status_rezolvat": "STATUS", "an_referinta": "AN",
        "persoana_relevanta": "PERSOANĂ", "entitate_relevanta": "ENTITATE",
        "valoare_num": "VALOARE", "data_inceput": "DATA ÎNCEPUT",
        "data_sfarsit": "DATA SFÂRȘIT",
    })
    return out


# =========================================================
# AUTENTIFICARE EMAIL UPT
# =========================================================

def _render_export_auth(supabase: Client) -> bool:
    auth_key = "export_auth_tab3"
    pattern  = re.compile(r"^[a-z]+(?:\.[a-z]+)+@upt\.ro$", re.IGNORECASE)

    if st.session_state.get("auth_ai", False) or st.session_state.get(auth_key, False):
        nume = st.session_state.get("user_name") or st.session_state.get("user_email", "")
        st.markdown(
            f"<div style='background:rgba(255,255,255,0.10);border-radius:10px;"
            f"padding:8px 16px;color:#ffffff;font-weight:700;margin-bottom:0.5rem;'>"
            f"✅ Export autorizat — {_html.escape(str(nume))}</div>",
            unsafe_allow_html=True,
        )
        return True

    st.markdown(
        "<div style='background:rgba(255,255,255,0.08);border-radius:12px;"
        "padding:12px 18px;margin-bottom:0.6rem;'>"
        "<span style='color:#ffffff;font-weight:800;font-size:0.97rem;'>"
        "🔐 Export disponibil exclusiv pentru cadrele UPT — "
        "autentificare cu email instituțional</span></div>",
        unsafe_allow_html=True,
    )

    ea1, ea2, _ = st.columns([2.0, 1.0, 3.0])
    with ea1:
        email_exp = st.text_input(
            "Email", value="", key="export_email_tab3",
            label_visibility="collapsed", placeholder="prenume.nume@upt.ro",
        ).strip().lower()
    with ea2:
        auth_clicked = st.button("✅ Autorizare", key="export_auth_btn_tab3")

    if auth_clicked:
        if not pattern.match(email_exp):
            st.error("Email invalid. Format: prenume.nume@upt.ro")
        else:
            try:
                res = supabase.table("det_resurse_umane") \
                    .select("nume_prenume,email").eq("email", email_exp).limit(1).execute()
                if res.data:
                    user = res.data[0]
                    st.session_state[auth_key]  = True
                    st.session_state.user_email = email_exp
                    st.session_state.user_name  = \
                        (user.get("nume_prenume") or "").strip() or email_exp
                    st.rerun()
                else:
                    st.error("Emailul nu există în baza de date IDBDC.")
            except Exception as e:
                st.error(f"Eroare verificare: {e}")
    return False


# =========================================================
# RENDER PRINCIPAL
# =========================================================

def render_tab3_rapoarte(supabase: Client):
    st.markdown("## 📊 Rapoarte și Grafice")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.88);font-size:1.02rem;font-weight:600;"
        "margin-bottom:0.85rem;'>Generați rapoarte și grafice interactive pe baza "
        "înregistrărilor din IDBDC. Exportul necesită autentificare UPT.</div>",
        unsafe_allow_html=True,
    )

    source_labels = [TABLE_CONFIG[t]["label"] for t in ALL_TABLES]

    # ── Panoul de configurare ─────────────────────────────────────────
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
            key="tab3r_preset",
        )
    with r1c2:
        selected_sources = st.multiselect(
            "Surse incluse",
            options=source_labels,
            default=[],
            placeholder="Gol = toate sursele",
            key="tab3r_sources",
        )

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1:
        an_de_la = st.number_input("An de la", min_value=1900, max_value=2100,
                                   value=None, step=1, key="tab3r_an_de_la")
    with r2c2:
        an_pana_la = st.number_input("An până la", min_value=1900, max_value=2100,
                                     value=None, step=1, key="tab3r_an_pana_la")
    with r2c3:
        status_text = st.text_input("Filtru status", value="", key="tab3r_status").strip()
    with r2c4:
        text_search = st.text_input("Căutare generală", value="", key="tab3r_search").strip()

    # Parametri raport
    if preset != "Personalizat":
        cfg = REPORT_PRESETS[preset]
        def_group   = cfg["group_by"]
        def_measure = cfg["measure"]
        def_top_n   = cfg["top_n"]
    else:
        def_group   = "Sursă / Categorie"
        def_measure = "Număr înregistrări"
        def_top_n   = 20

    r3c1, r3c2, r3c3 = st.columns(3)
    with r3c1:
        group_by_label = st.selectbox(
            "Grupează după",
            options=list(GROUP_DIMENSIONS.keys()),
            index=list(GROUP_DIMENSIONS.keys()).index(def_group),
            key="tab3r_group_by",
        )
    with r3c2:
        measure = st.selectbox(
            "Măsură",
            options=["Număr înregistrări", "Sumă valori"],
            index=0 if def_measure == "Număr înregistrări" else 1,
            key="tab3r_measure",
        )
    with r3c3:
        top_n = st.selectbox(
            "Top rezultate",
            options=[10, 15, 20, 30, 50, 100],
            index=[10, 15, 20, 30, 50, 100].index(
                def_top_n if def_top_n in [10, 15, 20, 30, 50, 100] else 20
            ),
            key="tab3r_top_n",
        )

    st.markdown("</div>", unsafe_allow_html=True)

    a1, _ = st.columns([1.5, 5.5])
    with a1:
        genereaza = st.button("📈 Generează raport", use_container_width=True,
                              key="tab3r_generate")

    # ── Generare date ─────────────────────────────────────────────────
    if genereaza:
        with st.spinner("Se construiește raportul..."):
            frames = []
            for t in ALL_TABLES:
                rows = _fetch_table_all(supabase, t)
                if rows:
                    df_t = _rows_to_df(rows, t)
                    if not df_t.empty:
                        frames.append(df_t)

            if not frames:
                st.warning("Nu există date disponibile.")
                return

            df_all = pd.concat(frames, ignore_index=True, sort=False)
            df_filtered = _apply_global_filters(
                df_all, selected_sources, an_de_la, an_pana_la,
                status_text, text_search,
            )
            st.session_state["tab3r_df_filtered"] = df_filtered.copy()
            st.session_state["tab3r_summary"] = _build_aggregate(
                df_filtered, group_by_label, measure, top_n
            )
            st.session_state["tab3r_group_label"]  = group_by_label
            st.session_state["tab3r_measure"]       = measure
            st.session_state["tab3r_preset_label"]  = preset

    if "tab3r_df_filtered" not in st.session_state:
        return

    df_filtered = st.session_state["tab3r_df_filtered"].copy()
    df_summary  = st.session_state["tab3r_summary"].copy()
    g_label     = st.session_state.get("tab3r_group_label", group_by_label)
    g_measure   = st.session_state.get("tab3r_measure", measure)
    g_preset    = st.session_state.get("tab3r_preset_label", preset)

    if df_filtered.empty or df_summary.empty:
        st.info("Nu au fost identificate date pentru combinația selectată.")
        return

    total_records   = len(df_filtered)
    total_value     = float(df_filtered["valoare_num"].fillna(0).sum()) \
        if "valoare_num" in df_filtered.columns else 0.0
    distinct_sources= df_filtered["Sursa"].nunique() if "Sursa" in df_filtered.columns else 0
    distinct_years  = df_filtered["an_referinta"].dropna().nunique() \
        if "an_referinta" in df_filtered.columns else 0

    st.divider()

    # ── KPI-uri ───────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total înregistrări", f"{total_records:,}".replace(",", "."))
    with k2:
        st.metric("Total valori", _format_number_ro(total_value, 0))
    with k3:
        st.metric("Surse distincte", f"{distinct_sources}")
    with k4:
        st.metric("Ani distincți", f"{distinct_years}")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Titlu raport ──────────────────────────────────────────────────
    titlu_raport = (
        f"{g_preset} — {g_label} / {g_measure}"
        if g_preset != "Personalizat"
        else f"Raport personalizat — {g_label} / {g_measure}"
    )

    # ── Grafic Plotly ─────────────────────────────────────────────────
    _render_chart_plotly(df_summary, g_label, g_measure, titlu_raport)

    # ── Tabel sinteză ─────────────────────────────────────────────────
    st.markdown(
        "<div style='color:#ffffff;font-size:1.00rem;font-weight:800;"
        "margin-top:6px;margin-bottom:8px;'>Tabel de sinteză</div>",
        unsafe_allow_html=True,
    )
    df_summary_display = df_summary.copy()
    if g_measure == "Sumă valori":
        df_summary_display["Valoare"] = df_summary_display["Valoare"].apply(
            lambda x: _format_number_ro(float(x), 2)
        )
    else:
        df_summary_display["Valoare"] = df_summary_display["Valoare"].apply(
            lambda x: str(int(x))
        )
    df_summary_display = df_summary_display.rename(
        columns={"Dimensiune": "DIMENSIUNE", "Valoare": "VALOARE"}
    )
    st.dataframe(df_summary_display, use_container_width=True,
                 hide_index=True, height=360)

    # ── Detalii ───────────────────────────────────────────────────────
    with st.expander("Detalii înregistrări incluse în raport", expanded=False):
        detail_df = _prepare_detail_df(df_filtered)
        st.dataframe(detail_df, use_container_width=True,
                     hide_index=True, height=480)

    # ── Export ───────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        "<div style='color:rgba(255,255,255,0.75);font-size:0.90rem;font-weight:700;"
        "margin-bottom:6px;'>📤 Export raport</div>",
        unsafe_allow_html=True,
    )

    if not _render_export_auth(supabase):
        return

    detail_df_export = _prepare_detail_df(df_filtered)

    e1, e2, e3, e4 = st.columns(4)
    with e1:
        st.download_button(
            "⬇️ CSV",
            data=_build_csv_bytes(df_summary_display),
            file_name=f"raport_sumar.csv",
            mime="text/csv",
            key="tab3r_csv",
        )
    with e2:
        st.download_button(
            "⬇️ Excel",
            data=_build_excel_bytes(df_summary_display, detail_df_export),
            file_name=f"raport_complet.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="tab3r_xlsx",
        )
    with e3:
        pdf_bytes = _build_pdf_bytes(df_summary_display, titlu_raport)
        if pdf_bytes:
            st.download_button(
                "⬇️ PDF",
                data=pdf_bytes,
                file_name=f"raport.pdf",
                mime="application/pdf",
                key="tab3r_pdf",
            )
        else:
            st.button("⬇️ PDF", disabled=True, key="tab3r_pdf_d",
                      help="PDF indisponibil")
    with e4:
        print_html = _build_print_html(df_summary_display, titlu_raport)
        if st.button("🖨️ Print", key="tab3r_print"):
            components.html(print_html, height=700, scrolling=True)
