# =========================================================
# IDBDC/explorator/explorare_avansata.py
# VERSIUNE: 5.0
# STATUS: ACTUALIZAT
# DATA: 2026.06.13
# =========================================================
# MODIFICĂRI VERSIUNEA 5.0:
#   - [1] Eliminat "Contracte SPECIALE" din lista Categoria principală
#   - [2] Click pe cod din tabel → deschide Tab1 cu codul completat
#   - [3] Butoane CSV/Excel/PDF/Print la tabelul de rezultate
#   - [4] UI autorizare Tab2 identic cu gate_control din Calea1
#   - Tabel: implicit max 10 randuri; daca >10 apare selector
# =========================================================

import io
import html as _html
from datetime import date, datetime
from typing import Any

import pandas as pd
import streamlit as st
from supabase import Client

ACADEMIC_BLUE = "#0b2a52"

# =========================================================
# CONFIGURARE TABELE
# =========================================================

TABLE_CONFIG = {
    "base_contracte_cep": {
        "label":        "📄 Contracte CEP",
        "categorie":    "Contracte",
        "subcategorie": "CEP",
    },
    "base_contracte_terti": {
        "label":        "📄 Contracte TERȚI",
        "categorie":    "Contracte",
        "subcategorie": "TERȚI",
    },
    # base_contracte_speciale exclus [1]
    "base_proiecte_fdi": {
        "label":        "🔬 Proiecte FDI",
        "categorie":    "Proiecte",
        "subcategorie": "FDI",
    },
    "base_proiecte_pncdi": {
        "label":        "🔬 Proiecte PNCDI",
        "categorie":    "Proiecte",
        "subcategorie": "PNCDI",
    },
    "base_proiecte_pnrr": {
        "label":        "🔬 Proiecte PNRR",
        "categorie":    "Proiecte",
        "subcategorie": "PNRR",
    },
    "base_proiecte_internationale": {
        "label":        "🌍 Proiecte Internaționale",
        "categorie":    "Proiecte",
        "subcategorie": "Internaționale",
    },
    "base_proiecte_interreg": {
        "label":        "🌍 Proiecte INTERREG",
        "categorie":    "Proiecte",
        "subcategorie": "INTERREG",
    },
    "base_proiecte_nonue": {
        "label":        "🌍 Proiecte NON-EU",
        "categorie":    "Proiecte",
        "subcategorie": "NON-EU",
    },
    "base_proiecte_see": {
        "label":        "🌍 Proiecte SEE",
        "categorie":    "Proiecte",
        "subcategorie": "SEE",
    },
    "base_evenimente_stiintifice": {
        "label":        "🎓 Evenimente Științifice",
        "categorie":    "Evenimente",
        "subcategorie": "Științifice",
    },
    "base_prop_industr": {
        "label":        "💡 Proprietate Industrială",
        "categorie":    "Proprietate Industrială",
        "subcategorie": "PI",
    },
}

ALL_TABLES = list(TABLE_CONFIG.keys())

SURSA_FIELDS = [
    "program_finantare", "programul_de_finantare", "program", "programul",
    "schema_de_finantare", "sursa_finantatoare", "mecanism_finantare",
    "mecanism_financiar", "apel_pentru_propuneri", "identificare_apel",
    "linia_de_finantare", "categoria",
]

ENTITATE_FIELDS = [
    "denumire_beneficiar", "denumire_participanti", "parteneri",
    "denumire_solicitant", "denumire_titular", "institutii_organizatoare",
    "institutii_organizare", "coordonator", "director_proiect",
    "acronim_departament", "denumire_departament", "rol_upt",
    "tematica", "domeniu_cercetare", "domeniu_aplicare",
]

DATE_FIELDS = [
    "data_inceput", "data_sfarsit", "data_contract", "data_apel",
    "data_depozit_cerere", "data_oficiala_de_acordare",
    "data_inceput_rol", "data_sfarsit_rol", "data_inchidere_apel",
]

STATUS_FIELDS = [
    "status_contract_proiect", "status_document",
    "status_personal", "status_activ",
]

TITLE_FIELDS = [
    "titlul_proiect", "titlul_eveniment", "titlul_proprietatii",
    "denumire_completa", "obiectul_contractului", "denumire",
]

VALUE_FIELDS = [
    "valoare_contract_cep_terti_speciale", "valoare_totala_contract",
    "cost_total_proiect", "suma_solicitata_fdi", "suma_aprobata_mec",
    "contributie_ue_proiect_upt", "costuri_totale_proiect", "grant_aprobat",
]

_TABELE_FIN_PN = {"base_proiecte_pncdi", "base_proiecte_pnrr"}


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
    df["_sursa"]        = cfg.get("label", table_name)
    df["_categorie"]    = cfg.get("categorie", "")
    df["_subcategorie"] = cfg.get("subcategorie", "")
    df["_titlu"]        = df.apply(lambda r: _first_nonempty(r, TITLE_FIELDS), axis=1)
    df["_status"]       = df.apply(lambda r: _first_nonempty(r, STATUS_FIELDS), axis=1)
    df["_table_name"]   = table_name

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

    for dcol in DATE_FIELDS:
        if dcol in df.columns:
            df[dcol] = df[dcol].apply(_try_parse_date)

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


def _apply_filters(df, categorii_selectate, sursa_text,
                   an_de_la, an_pana_la, data_de_la, data_pana_la,
                   entitate_text, status_text):
    if df.empty:
        return df
    out = df.copy()

    if categorii_selectate:
        out = out[out["_sursa"].isin(categorii_selectate)]

    if sursa_text.strip():
        needle = sursa_text.strip().lower()
        out = out[out.apply(lambda r: _contains_in_fields(r, needle, SURSA_FIELDS), axis=1)]

    if an_de_la is not None and "_an" in out.columns:
        out = out[out["_an"].fillna(-999999) >= int(an_de_la)]
    if an_pana_la is not None and "_an" in out.columns:
        out = out[out["_an"].fillna(999999) <= int(an_pana_la)]

    if data_de_la or data_pana_la:
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

    if entitate_text.strip():
        needle = entitate_text.strip().lower()
        out = out[out.apply(lambda r: _contains_in_fields(r, needle, ENTITATE_FIELDS), axis=1)]

    if status_text.strip():
        needle = status_text.strip().lower()
        out = out[out["_status"].fillna("").str.lower().str.contains(needle, na=False)]

    return out


# =========================================================
# AFIȘARE REZULTATE
# =========================================================

def _fmt_cod(v: Any) -> str:
    s = _safe_text(v)
    f = _to_float(s)
    if f is not None and float(f).is_integer():
        return str(int(f))
    return s


def _prepare_display_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    cols_display = []
    rename_map = {}

    if "cod_identificare" in df.columns:
        cols_display.append("cod_identificare")
        rename_map["cod_identificare"] = "COD IDENTIFICARE"

    cols_display += ["_sursa", "_titlu", "_status", "_an"]
    rename_map.update({
        "_sursa":  "SURSĂ / CATEGORIE",
        "_titlu":  "TITLU / DENUMIRE / OBIECT",
        "_status": "STATUS",
        "_an":     "AN",
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

    for c in disp.columns:
        if pd.api.types.is_datetime64_any_dtype(disp[c]):
            disp[c] = disp[c].apply(lambda x: x.strftime("%d.%m.%Y") if pd.notna(x) else "")

    if "cod_identificare" in disp.columns:
        disp["cod_identificare"] = disp["cod_identificare"].apply(_fmt_cod)

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
# BUTOANE EXPORT [3]
# =========================================================

def _render_butoane_export(shown_df: pd.DataFrame, shown_raw: pd.DataFrame):
    """CSV, Excel, PDF, Print pentru tabelul de rezultate."""
    from utils.export_common import build_vertical_export_data

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    e1, e2, e3, e4 = st.columns(4)

    # CSV
    with e1:
        csv_bytes = shown_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ CSV",
            data=csv_bytes,
            file_name="explorare_avansata.csv",
            mime="text/csv",
            use_container_width=True,
            key="tab2_export_csv",
        )

    # Excel
    with e2:
        xlsx_bytes = _export_excel_bytes(shown_df)
        st.download_button(
            "⬇️ Excel",
            data=xlsx_bytes,
            file_name="explorare_avansata.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="tab2_export_xlsx",
        )

    # PDF — generează un PDF cu toate înregistrările din tabel
    with e3:
        try:
            from utils.export_pdf import generate_pdf_vertical
            # Pentru tabelul agregat folosim primul cod din rezultate ca referință
            # și generăm un PDF simplu din DataFrame
            pdf_buf = io.BytesIO()
            try:
                from fpdf import FPDF
                import matplotlib, os
                font_path = os.path.join(
                    os.path.dirname(matplotlib.__file__),
                    "mpl-data", "fonts", "ttf", "DejaVuSans.ttf"
                )
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=10)
                pdf.add_page()
                if os.path.exists(font_path):
                    pdf.add_font("DejaVu", fname=font_path)
                    pdf.set_font("DejaVu", size=9)
                else:
                    pdf.set_font("Helvetica", size=9)

                pdf.set_text_color(11, 42, 82)
                pdf.cell(0, 8, "IDBDC UPT - Explorare avansata - Rezultate",
                         new_x="LMARGIN", new_y="NEXT", align="C")
                pdf.ln(3)

                cols = list(shown_df.columns)
                col_w = min(35, 190 // max(len(cols), 1))
                pdf.set_font("DejaVu" if os.path.exists(font_path) else "Helvetica", size=7)
                pdf.set_fill_color(11, 42, 82)
                pdf.set_text_color(255, 255, 255)
                for col in cols:
                    pdf.cell(col_w, 6, str(col)[:18], border=1, fill=True)
                pdf.ln()

                pdf.set_text_color(0, 0, 0)
                for i, (_, row) in enumerate(shown_df.iterrows()):
                    pdf.set_fill_color(247, 249, 252) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
                    for col in cols:
                        val = str(row.get(col, ""))[:20]
                        pdf.cell(col_w, 5, val, border=1, fill=True)
                    pdf.ln()

                pdf_bytes = bytes(pdf.output())
                st.download_button(
                    "⬇️ PDF",
                    data=pdf_bytes,
                    file_name="explorare_avansata.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="tab2_export_pdf",
                )
            except Exception:
                st.button("⬇️ PDF", disabled=True, use_container_width=True, key="tab2_export_pdf_d")
        except Exception:
            st.button("⬇️ PDF", disabled=True, use_container_width=True, key="tab2_export_pdf_d2")

    # Print HTML
    with e4:
        try:
            import html as _h
            cols = list(shown_df.columns)
            rows_html = ""
            for i, (_, row) in enumerate(shown_df.iterrows()):
                bg = "#f7f9fc" if i % 2 == 0 else "#ffffff"
                cells = "".join(
                    f"<td style='border:1px solid #c0cce0;padding:4px 7px;"
                    f"font-size:9px;background:{bg};'>{_h.escape(str(row.get(c,'')))}</td>"
                    for c in cols
                )
                rows_html += f"<tr>{cells}</tr>"
            hdrs = "".join(
                f"<th style='border:1px solid #c0cce0;padding:5px 7px;font-size:9px;"
                f"background:#0b2a52;color:#fff;'>{_h.escape(str(c))}</th>"
                for c in cols
            )
            print_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Explorare avansata</title>
<style>body{{font-family:Arial,sans-serif;margin:18px;}}
table{{border-collapse:collapse;width:100%;}}
.btn{{display:inline-block;margin-bottom:16px;padding:7px 18px;
background:#0b2a52;color:#fff;border:none;border-radius:6px;
font-weight:700;cursor:pointer;}}
@media print{{.btn{{display:none;}}}}
</style></head><body>
<button class="btn" onclick="window.print()">Tiparire</button>
<div style="font-size:12px;font-weight:900;color:#0b2a52;margin-bottom:10px;">
IDBDC UPT &mdash; Explorare avansata &mdash; Rezultate</div>
<table><thead><tr>{hdrs}</tr></thead><tbody>{rows_html}</tbody></table>
</body></html>"""
            st.download_button(
                "🖨️ Print",
                data=print_html.encode("utf-8"),
                file_name="explorare_avansata.html",
                mime="text/html",
                use_container_width=True,
                key="tab2_export_print",
            )
        except Exception:
            st.button("🖨️ Print", disabled=True, use_container_width=True, key="tab2_export_print_d")


# =========================================================
# UI AUTORIZARE TAB2 — identic cu gate_control Calea1 [4]
# =========================================================

def _gate_tab2_full(render_fn, secret_key: str, key_session: str):
    """
    Afișează ecran de autorizare full-page identic cu gate_control din Calea1.
    Odată introdusă corect, tab-ul rămâne deblocat pe toată sesiunea.
    """
    if st.session_state.get(key_session, False):
        render_fn()
        return

    parola_corecta = st.secrets.get(secret_key, "")

    st.markdown(
        f"""
        <style>
          div.block-container {{ padding-top: 4.0rem; padding-bottom: 2.0rem; }}
          .gate-box {{
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.25);
            border-radius: 18px;
            padding: 26px 22px 18px 22px;
          }}
          .gate-title {{
            text-align: center; font-size: 1.45rem;
            font-weight: 900; color: #ffffff;
          }}
          .gate-subtitle {{
            text-align: center;
            color: rgba(255,255,255,0.92);
            font-size: 1.02rem;
          }}
          .stTextInput input {{
            background: rgba(255,255,255,0.96) !important;
            color: #0b1f3a !important;
          }}
          .stButton > button {{
            width: 100%;
            background: rgba(255,255,255,0.96) !important;
            color: #0b1f3a !important;
            -webkit-text-fill-color: #0b1f3a !important;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, mid, right = st.columns([1.8, 1.0, 1.8])
    with mid:
        st.markdown('<div class="gate-box">', unsafe_allow_html=True)
        st.markdown('<div class="gate-title">🛡️ Acces securizat</div>', unsafe_allow_html=True)
        st.markdown('<div class="gate-subtitle">Interogare baze de date – DCDI</div>', unsafe_allow_html=True)
        parola = st.text_input("Parola acces:", type="password", key=f"pwd_{key_session}")
        if st.button("Autorizare acces", use_container_width=True, key=f"btn_{key_session}"):
            if parola == parola_corecta:
                st.session_state[key_session] = True
                st.rerun()
            else:
                st.error("Parola gresita.")
        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# RENDER PRINCIPAL
# =========================================================

def render_tab2_explorare_avansata(supabase: Client):

    def _render_continut():
        _render_explorare(supabase)

    _gate_tab2_full(
        render_fn   = _render_continut,
        secret_key  = "PASSWORD_TAB2",
        key_session = "tab2_deblocat",
    )


def _render_explorare(supabase: Client):

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

    st.markdown(
        "<div style='color:rgba(255,255,255,0.70);font-size:0.88rem;font-weight:700;"
        "text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;'>"
        "1. Categoria principală</div>",
        unsafe_allow_html=True,
    )
    categorii_selectate = st.multiselect(
        "Categoria", options=tabel_labels, default=[],
        placeholder="Gol = toate categoriile",
        key="tab2_categorii", label_visibility="collapsed",
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='color:rgba(255,255,255,0.70);font-size:0.88rem;font-weight:700;"
        "text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;'>"
        "2. Sursa de finanțare</div>",
        unsafe_allow_html=True,
    )
    sursa_text = st.text_input(
        "Sursa", value="",
        placeholder="Ex: Horizon Europe, PNCDI, FDI, INTERREG, UEFISCDI, bilateral...",
        key="tab2_sursa", label_visibility="collapsed",
    ).strip()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

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
            "Dată de la", value=None,
            key="tab2_data_de_la", format="DD.MM.YYYY",
        )
    with p4:
        data_pana_la = st.date_input(
            "Dată până la", value=None,
            key="tab2_data_pana_la", format="DD.MM.YYYY",
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    c4, c5 = st.columns(2)
    with c4:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.70);font-size:0.88rem;font-weight:700;"
            "text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;'>"
            "4. Entități implicate</div>",
            unsafe_allow_html=True,
        )
        entitate_text = st.text_input(
            "Entitate", value="",
            placeholder="Beneficiar, partener, departament, rol UPT, domeniu...",
            key="tab2_entitate", label_visibility="collapsed",
        ).strip()
    with c5:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.70);font-size:0.88rem;font-weight:700;"
            "text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;'>"
            "5. Status</div>",
            unsafe_allow_html=True,
        )
        status_text = st.text_input(
            "Status", value="",
            placeholder="Ex: activ, finalizat, în evaluare, respins...",
            key="tab2_status", label_visibility="collapsed",
        ).strip()

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Butoane acțiune ────────────────────────────────────────────────
    b1, b2, _ = st.columns([1.4, 1.2, 4.4])
    with b1:
        cauta = st.button(
            "🔎 Explorează baza de date",
            use_container_width=True, key="tab2_search_btn",
        )
    with b2:
        reset = st.button(
            "🧹 Resetează",
            use_container_width=True, key="tab2_reset_btn",
        )

    if reset:
        for k in [
            "tab2_categorii", "tab2_sursa", "tab2_an_de_la", "tab2_an_pana_la",
            "tab2_data_de_la", "tab2_data_pana_la", "tab2_entitate", "tab2_status",
            "tab2_results_df", "tab2_results_raw",
        ]:
            st.session_state.pop(k, None)
        st.rerun()

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
            st.warning("Completati cel putin un criteriu de cautare.")
            return

        selected_tables = (
            [t for t, cfg in TABLE_CONFIG.items() if cfg["label"] in categorii_selectate]
            if categorii_selectate else ALL_TABLES
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
                df_all, categorii_selectate, sursa_text,
                an_de_la, an_pana_la, data_de_la, data_pana_la,
                entitate_text, status_text,
            )
            st.session_state["tab2_results_raw"] = df_filtered.copy()
            st.session_state["tab2_results_df"]  = df_filtered.copy()

    # ── Afișare rezultate ──────────────────────────────────────────────
    if "tab2_results_df" not in st.session_state:
        return

    results_df  = st.session_state["tab2_results_df"].copy()
    results_raw = st.session_state.get("tab2_results_raw", results_df).copy()

    if results_df.empty:
        st.info("Nu au fost identificate inregistrari pentru combinatia selectata.")
        return

    total_rows = len(results_df)
    st.divider()

    display_df = _prepare_display_df(results_df)

    # ── Selector număr rânduri (apare doar dacă >10) [modificare] ─────
    if total_rows > 10:
        st.markdown(
            f"<div style='background:rgba(255,200,50,0.12);border:1px solid rgba(255,200,50,0.40);"
            f"border-radius:10px;padding:8px 14px;margin-bottom:10px;'>"
            f"<span style='color:#ffe082;font-weight:700;font-size:0.95rem;'>"
            f"Au fost identificate <b>{total_rows}</b> inregistrari. "
            f"Se afiseaza implicit 10. Puteti modifica numarul de randuri afisate:</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        optiuni = [10, 25, 50, 100, 250, 500, "Toate"]
        limita = st.selectbox(
            "Randuri de afisat",
            options=optiuni,
            index=0,
            key="tab2_limita",
            label_visibility="visible",
        )
    else:
        limita = total_rows

    st.markdown(
        f"<div style='color:#ffffff;font-size:1.02rem;font-weight:800;margin-bottom:10px;'>"
        f"Rezultate identificate: {total_rows}"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Aplicare limită
    if limita == "Toate":
        shown_df  = display_df.copy()
        shown_raw = results_raw.copy()
    else:
        shown_df  = display_df.head(int(limita)).copy()
        shown_raw = results_raw.head(int(limita)).copy()

    # ── Tabel rezultate ────────────────────────────────────────────────
    st.dataframe(
        shown_df,
        use_container_width=True,
        hide_index=True,
        height=min(40 + len(shown_df) * 35, 520),
    )

    # ── Click pe cod → deschide Tab1 cu codul completat [2] ───────────
    if "COD IDENTIFICARE" in shown_df.columns:
        coduri = shown_df["COD IDENTIFICARE"].dropna().unique().tolist()
        coduri = [c for c in coduri if str(c).strip()]
    else:
        coduri = []

    if coduri:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.70);font-size:0.88rem;font-weight:700;"
            "margin-top:10px;margin-bottom:4px;'>"
            "Fisa completa — selectati codul din lista:</div>",
            unsafe_allow_html=True,
        )
        col_sel, col_btn, _ = st.columns([1, 1, 2])
        with col_sel:
            cod_ales = st.selectbox(
                "Cod",
                options=["— selectati —"] + coduri,
                key="tab2_cod_ales",
                label_visibility="collapsed",
            )
        with col_btn:
            if st.button("📄 Deschide fisa", key="tab2_open_fisa", use_container_width=True):
                if cod_ales and cod_ales != "— selectati —":
                    st.session_state["tab2_goto_tab1"] = True
                    st.session_state["tab2_goto_tab1_cod"] = str(cod_ales)
                    st.rerun()

    # ── Butoane export [3] ─────────────────────────────────────────────
    _render_butoane_export(shown_df, shown_raw)
