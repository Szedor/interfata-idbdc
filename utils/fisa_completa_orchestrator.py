# =========================================================
# utils/fisa_completa_orchestrator.py
# VERSIUNE: 2.2
# STATUS: CORECTAT - afisare si export financiar dedicat PNCDI/PNRR
# DATA: 2026.06.06
# =========================================================
# MODIFICĂRI VERSIUNEA 2.2:
#   - Adaugata functia _render_financiar_pn() care afiseaza
#     datele din com_date_financiare_pn in ordinea:
#     COD PROIECT, VALUTA, apoi pentru fiecare an:
#     ANUL DE REFERINTA, VALOARE AN REFERINTA,
#     COFINANTARE AN REFERINTA, iar la final:
#     VALOARE TOTALA, COFINANTARE TOTALA.
#   - Adaugata functia _build_financiar_pn_items() care
#     construieste aceeasi lista de campuri/valori pentru
#     export (CSV, Excel, PDF, Print).
#   - sectiuni_active pentru PNCDI/PNRR folosesc sec_key
#     "financiar_pn" in loc de "financiar" pentru a
#     declansa logica dedicata.
#
# MODIFICĂRI VERSIUNEA 2.1:
#   - Sectiunea Financiar foloseste com_date_financiare_pn
#     pentru proiectele PNCDI si PNRR.
#
# MODIFICĂRI VERSIUNEA 2.0:
#   - sectiuni_active transmise la build_horizontal_export_data
#     si build_vertical_export_data.
#
# MODIFICĂRI VERSIUNEA 1.9:
#   - tabela_baza_ctx transmisa la render_echipa_compact.
# =========================================================

import streamlit as st
import html as _html
import re as _re
import streamlit.components.v1 as components

from utils.display_config import TABLE_LABELS
from utils.display_rendering import render_sectiune_tabel, render_echipa_compact
from utils.export_common import build_horizontal_export_data, build_vertical_export_data
from utils.export_csv_excel import build_csv_bytes, build_excel_bytes
from utils.export_pdf import generate_pdf_vertical
from utils.export_print import generate_print_html_vertical
from utils.supabase_helpers import safe_select_eq


# Tabele care folosesc com_date_financiare_pn (cu valori anuale)
_TABELE_FIN_PN = {"base_proiecte_pncdi", "base_proiecte_pnrr"}


def _fmt_numeric(val, col_name: str = "") -> str:
    """Formatare numerica cu separator mii si doua zecimale pentru valori financiare."""
    if val is None:
        return ""
    raw = str(val).strip()
    if not raw or raw in ("None", "nan"):
        return ""
    try:
        f = float(raw.replace(",", "."))
    except (ValueError, TypeError):
        return raw
    financial_keys = ("valoare", "cofinantare")
    if any(k in col_name.lower() for k in financial_keys):
        return f"{f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if f.is_integer():
        return str(int(f))
    return f"{f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _build_financiar_pn_items(rows: list, cod: str) -> list:
    """
    Construieste lista de perechi (eticheta, valoare) pentru
    datele din com_date_financiare_pn, in ordinea:
      COD PROIECT, VALUTA,
      [pentru fiecare an sortat]:
        ANUL DE REFERINTA, VALOARE AN REFERINTA, COFINANTARE AN REFERINTA,
      VALOARE TOTALA, COFINANTARE TOTALA.
    """
    if not rows:
        return []

    items = []

    # COD PROIECT
    items.append(("COD PROIECT", str(cod)))

    # VALUTA — din primul rand
    valuta = str(rows[0].get("valuta") or "").strip()
    items.append(("VALUTA", valuta))

    # Sortam randurile dupa an_referinta
    rows_sorted = sorted(
        rows,
        key=lambda r: int(r.get("an_referinta") or 0)
    )

    for r in rows_sorted:
        an = r.get("an_referinta")
        if not an:
            continue
        items.append(("ANUL DE REFERINTA", str(int(float(an)))))
        items.append((
            "VALOARE AN REFERINTA",
            _fmt_numeric(r.get("valoare_contract_an_referinta"), "valoare")
        ))
        items.append((
            "COFINANTARE AN REFERINTA",
            _fmt_numeric(r.get("cofinantare_contract_an_referinta"), "cofinantare")
        ))

    # Totalurile — din primul rand (sunt identice in toate randurile)
    items.append((
        "VALOARE TOTALA",
        _fmt_numeric(rows[0].get("valoare_totala_contract"), "valoare")
    ))
    items.append((
        "COFINANTARE TOTALA",
        _fmt_numeric(rows[0].get("cofinantare_totala_contract"), "cofinantare")
    ))

    return items


def _render_financiar_pn(supabase, cod: str, sec_label: str):
    """
    Afiseaza sectiunea Financiar pentru PNCDI/PNRR direct in UI,
    folosind acelasi stil tabel ca render_sectiune_tabel().
    """
    rows = safe_select_eq(supabase, "com_date_financiare_pn", "cod_identificare", cod, limit=100)
    if not rows:
        st.info("Nu există informații financiare pentru această fișă.")
        return

    items = _build_financiar_pn_items(rows, cod)
    if not items:
        return

    rows_html = ""
    for i, (label, value) in enumerate(items):
        sec_cell = ""
        if i == 0:
            sec_cell = (
                f"<td rowspan='{len(items)}' style='vertical-align:top;padding:6px 10px 6px 0;width:10%;'>"
                f"<span style='color:rgba(255,255,255,0.45);font-size:0.74rem;font-weight:800;"
                f"text-transform:uppercase;letter-spacing:0.07em;white-space:nowrap;'>"
                f"{_html.escape(sec_label)}</span>"
                f"</td>"
            )
        rows_html += (
            f"<tr>{sec_cell}"
            f"<td style='padding:3px 12px 3px 0;width:23%;vertical-align:top;'>"
            f"<span style='color:rgba(255,255,255,0.50);font-size:0.76rem;font-weight:700;"
            f"text-transform:uppercase;letter-spacing:0.04em;'>{_html.escape(label)}</span></td>"
            f"<td style='padding:3px 0 3px 0;width:67%;vertical-align:top;'>"
            f"<span style='color:#ffffff;font-size:0.95rem;font-weight:700;'>{_html.escape(value)}</span></td>"
            f"</tr>"
        )

    st.markdown(
        f"<table style='width:100%;border-collapse:collapse;margin-bottom:0;'>{rows_html}</table>",
        unsafe_allow_html=True,
    )


def _build_vertical_financiar_pn(supabase, cod: str) -> dict:
    """
    Construieste sectiunea Financiar pentru export vertical (PDF/Print)
    pentru PNCDI/PNRR.
    """
    rows = safe_select_eq(supabase, "com_date_financiare_pn", "cod_identificare", cod, limit=100)
    items = _build_financiar_pn_items(rows, cod)
    section = {"name": "Financiar", "fields": [], "values": []}
    for label, value in items:
        section["fields"].append(label)
        section["values"].append(value)
    return section


def _build_horizontal_financiar_pn(supabase, cod: str) -> tuple:
    """
    Construieste datele Financiar pentru export orizontal (CSV/Excel)
    pentru PNCDI/PNRR. Returneaza (headers, values).
    """
    rows = safe_select_eq(supabase, "com_date_financiare_pn", "cod_identificare", cod, limit=100)
    items = _build_financiar_pn_items(rows, cod)
    headers = [label for label, _ in items]
    values  = [value for _, value in items]
    return headers, values


def _render_export_auth_tab1(supabase) -> bool:
    auth_key = "export_auth_tab1"
    pattern  = _re.compile(r"^[a-z]+(?:\.[a-z]+)+@upt\.ro$", _re.IGNORECASE)

    if st.session_state.get("auth_ai", False) or st.session_state.get(auth_key, False):
        nume = st.session_state.get("user_name") or st.session_state.get("user_email", "")
        st.markdown(
            f"<div style='background:rgba(255,255,255,0.10);border-radius:10px;padding:8px 16px;"
            f"color:#ffffff;font-weight:700;margin-bottom:0.5rem;'>"
            f"✅ Export autorizat — {_html.escape(str(nume))}</div>",
            unsafe_allow_html=True,
        )
        return True

    st.markdown(
        "<div style='background:rgba(255,255,255,0.08);border-radius:12px;padding:12px 18px;margin-bottom:0.6rem;'>"
        "<span style='color:#ffffff;font-weight:800;font-size:0.97rem;'>"
        "🔐 Export disponibil exclusiv pentru cadrele UPT — autentificare cu email instituțional"
        "</span></div>",
        unsafe_allow_html=True,
    )

    ea1, ea2, _ = st.columns([2.0, 1.0, 3.0])
    with ea1:
        email_exp = st.text_input(
            "Email", value="", key="export_email_tab1",
            label_visibility="collapsed", placeholder="prenume.nume@upt.ro",
        ).strip().lower()
    with ea2:
        auth_clicked = st.button("✅ Autorizare", key="export_auth_btn_tab1")

    if auth_clicked:
        if not pattern.match(email_exp):
            st.error("Email invalid. Format: prenume.nume@upt.ro")
        else:
            try:
                res = supabase.table("det_resurse_umane") \
                    .select("nume_prenume,email").eq("email", email_exp).limit(1).execute()
                if res.data:
                    user = res.data[0]
                    st.session_state[auth_key]   = True
                    st.session_state.user_email  = email_exp
                    st.session_state.user_name   = (user.get("nume_prenume") or "").strip() or email_exp
                    st.rerun()
                else:
                    st.error("Emailul nu există în baza de date IDBDC.")
            except Exception as e:
                st.error(f"Eroare verificare: {e}")
    return False


def render_fisa_completa(supabase, cod: str, tabela_gasita: str, titlu_eticheta: str):
    _p1, _p2, _p3, _p4, _lbl = st.columns([0.7, 0.7, 0.7, 0.7, 5.2])
    with _p1:
        pin_gen = st.checkbox("Generale",  key=f"fisa_pin_{cod}_generale")
    with _p2:
        pin_fin = st.checkbox("Financiar", key=f"fisa_pin_{cod}_financiar")
    with _p3:
        pin_ech = st.checkbox("Echipă",    key=f"fisa_pin_{cod}_echipa")
    with _p4:
        pin_teh = st.checkbox("Tehnic",    key=f"fisa_pin_{cod}_tehnic")
    with _lbl:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.45);font-size:0.875rem;padding-top:6px;"
            "font-style:italic;'>Bifează o secțiune pentru a afișa informațiile existente în aceasta.</div>",
            unsafe_allow_html=True,
        )

    este_pn = tabela_gasita in _TABELE_FIN_PN
    _tabela_fin = "com_date_financiare_pn" if este_pn else "com_date_financiare"
    _sec_key_fin = "financiar_pn" if este_pn else "financiar"

    sectiuni_active = []
    if pin_gen:
        sectiuni_active.append(("Generale",  tabela_gasita,  "generale"))
    if pin_fin:
        sectiuni_active.append(("Financiar", _tabela_fin,    _sec_key_fin))
    if pin_ech:
        sectiuni_active.append(("Echipa",    "com_echipe_proiect",  "echipa"))
    if pin_teh:
        sectiuni_active.append(("Tehnic",    "com_aspecte_tehnice", "tehnic"))

    if sectiuni_active:
        st.markdown(
            "<div style='background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.15);"
            "border-radius:14px;padding:14px 20px 6px 20px;margin-top:12px;'>",
            unsafe_allow_html=True,
        )
        for idx, (sec_label, sec_table, sec_key) in enumerate(sectiuni_active):
            if idx > 0:
                st.markdown(
                    "<div style='height:18px;border-top:1px solid rgba(255,255,255,0.12);"
                    "margin:8px 0 10px 0;'></div>",
                    unsafe_allow_html=True,
                )
            if sec_key == "echipa":
                rows = safe_select_eq(supabase, sec_table, "cod_identificare", cod, limit=2000)
                if not rows:
                    st.info("Nu există membri echipă pentru acest contract.")
                else:
                    render_echipa_compact(rows, cod_ctx=cod, supabase=supabase,
                                          tabela_baza_ctx=tabela_gasita)
            elif sec_key == "financiar_pn":
                # Afisare dedicata pentru PNCDI/PNRR
                _render_financiar_pn(supabase, cod, sec_label)
            else:
                rows = safe_select_eq(supabase, sec_table, "cod_identificare", cod, limit=50)
                if not rows:
                    st.info(f"Nu există informații pentru secțiunea {sec_label}.")
                else:
                    render_sectiune_tabel(
                        sec_label, rows, sec_table,
                        tabela_baza_ctx=tabela_gasita,
                        supabase=supabase,
                    )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown(
        "<div style='color:rgba(255,255,255,0.75);font-size:0.90rem;font-weight:700;"
        "margin-bottom:6px;'>📤 Export fișă</div>",
        unsafe_allow_html=True,
    )

    if not _render_export_auth_tab1(supabase):
        return

    if not sectiuni_active:
        st.info("Bifați cel puțin o secțiune pentru a exporta.")
        return

    # ── Construire date export ────────────────────────────────────────
    # Pentru PNCDI/PNRR sectiunea financiara este tratata separat;
    # celelalte sectiuni merg prin calea generica.

    sectiuni_generice = [s for s in sectiuni_active if s[2] != "financiar_pn"]

    export_data_horizontal = build_horizontal_export_data(
        supabase, cod, tabela_gasita, sectiuni_active=sectiuni_generice
    )

    # Injectam datele financiare PN in pozitia corecta (dupa Generale)
    if este_pn and pin_fin:
        h_pn, v_pn = _build_horizontal_financiar_pn(supabase, cod)
        # Inseram dupa Generale (sau la inceput daca Generale nu e bifat)
        insert_pos = 0
        for i, h in enumerate(export_data_horizontal["headers"]):
            if h == "":
                insert_pos = i + 1
                break
        # Adaugam separator + date PN
        export_data_horizontal["headers"] = (
            export_data_horizontal["headers"][:insert_pos]
            + h_pn + [""]
            + export_data_horizontal["headers"][insert_pos:]
        )
        export_data_horizontal["values"] = (
            export_data_horizontal["values"][:insert_pos]
            + v_pn + [""]
            + export_data_horizontal["values"][insert_pos:]
        )
        # Curatam separatorul de la final daca exista
        if export_data_horizontal["headers"] and export_data_horizontal["headers"][-1] == "":
            export_data_horizontal["headers"].pop()
            export_data_horizontal["values"].pop()

    if not export_data_horizontal["headers"]:
        st.info("Nu există date de exportat pentru secțiunile selectate.")
        return

    csv_bytes   = build_csv_bytes(export_data_horizontal)
    excel_bytes = build_excel_bytes(export_data_horizontal)

    # Export vertical (PDF/Print) — construim manual sectiunile
    def _build_vertical_cu_pn(s, c, t):
        data = build_vertical_export_data(s, c, t, sectiuni_active=sectiuni_generice)
        if este_pn and pin_fin:
            sec_pn = _build_vertical_financiar_pn(s, c)
            # Inseram dupa prima sectiune (Generale) daca exista
            if data["sections"]:
                data["sections"].insert(1, sec_pn)
            else:
                data["sections"].append(sec_pn)
        return data

    pdf_result = generate_pdf_vertical(
        supabase, cod, tabela_gasita,
        TABLE_LABELS.get(tabela_gasita, "Fișă"),
        _build_vertical_cu_pn,
    )
    pdf_bytes = pdf_result[0] if isinstance(pdf_result, tuple) else pdf_result

    print_html = generate_print_html_vertical(
        supabase, cod, tabela_gasita,
        TABLE_LABELS.get(tabela_gasita, "Fișă"),
        _build_vertical_cu_pn,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.download_button("⬇️ CSV", data=csv_bytes, file_name=f"fisa_{cod}.csv",
                           mime="text/csv", key=f"fisa_csv_{cod}")
    with col2:
        st.download_button("⬇️ Excel", data=excel_bytes, file_name=f"fisa_{cod}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           key=f"fisa_xlsx_{cod}")
    with col3:
        if pdf_bytes:
            st.download_button("⬇️ PDF", data=pdf_bytes, file_name=f"fisa_{cod}.pdf",
                               mime="application/pdf", key=f"fisa_pdf_{cod}")
        else:
            st.button("⬇️ PDF", disabled=True, help="PDF indisponibil")
    with col4:
        if st.button("🖨️ Print", key=f"fisa_print_{cod}"):
            components.html(print_html, height=700, scrolling=True)
