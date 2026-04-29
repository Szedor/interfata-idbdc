# =========================================================
# IDBDC/utils/fisa_completa_orchestrator.py
# VERSIUNE: 1.6
# STATUS: Orchestrator cu autentificare export reala
# DATA: 2026.04.28
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


def _render_export_auth_tab1(supabase) -> bool:
    auth_key = "export_auth_tab1"
    pattern = _re.compile(r"^[a-z]+(?:\.[a-z]+)+@upt\.ro$", _re.IGNORECASE)

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
                    st.session_state[auth_key] = True
                    st.session_state.user_email = email_exp
                    st.session_state.user_name = (user.get("nume_prenume") or "").strip() or email_exp
                    st.rerun()
                else:
                    st.error("Emailul nu există în baza de date IDBDC.")
            except Exception as e:
                st.error(f"Eroare verificare: {e}")
    return False


def render_fisa_completa(supabase, cod: str, tabela_gasita: str, titlu_eticheta: str):
    _p1, _p2, _p3, _p4, _lbl = st.columns([0.7, 0.7, 0.7, 0.7, 5.2])
    with _p1:
        pin_gen = st.checkbox("Generale", key=f"fisa_pin_{cod}_generale")
    with _p2:
        pin_fin = st.checkbox("Financiar", key=f"fisa_pin_{cod}_financiar")
    with _p3:
        pin_ech = st.checkbox("Echipă", key=f"fisa_pin_{cod}_echipa")
    with _p4:
        pin_teh = st.checkbox("Tehnic", key=f"fisa_pin_{cod}_tehnic")
    with _lbl:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.45);font-size:0.875rem;padding-top:6px;"
            "font-style:italic;'>Bifează o secțiune pentru a afișa informațiile existente în aceasta.</div>",
            unsafe_allow_html=True,
        )

    sectiuni_active = []
    if pin_gen:
        sectiuni_active.append(("Generale", tabela_gasita, "generale"))
    if pin_fin:
        sectiuni_active.append(("Financiar", "com_date_financiare", "financiar"))
    if pin_ech:
        sectiuni_active.append(("Echipa", "com_echipe_proiect", "echipa"))
    if pin_teh:
        sectiuni_active.append(("Tehnic", "com_aspecte_tehnice", "tehnic"))

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
                st.markdown(
                    f"<div style='color:rgba(255,255,255,0.45);font-size:0.74rem;font-weight:800;"
                    f"text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px;'>"
                    f"{_html.escape(sec_label)}</div>",
                    unsafe_allow_html=True,
                )
                rows = safe_select_eq(supabase, sec_table, "cod_identificare", cod, limit=2000)
                if not rows:
                    st.info("Nu există membri echipă pentru acest contract.")
                else:
                    render_echipa_compact(rows, cod_ctx=cod, supabase=supabase)
            else:
                rows = safe_select_eq(supabase, sec_table, "cod_identificare", cod, limit=50)
                if not rows:
                    st.info(f"Nu există informații pentru secțiunea {sec_label}.")
                else:
                    render_sectiune_tabel(sec_label, rows, sec_table, tabela_baza_ctx=tabela_gasita)
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

    export_data_horizontal = build_horizontal_export_data(supabase, cod, tabela_gasita)
    if not export_data_horizontal["headers"]:
        st.info("Nu există date de exportat pentru acest cod.")
        return

    csv_bytes   = build_csv_bytes(export_data_horizontal)
    excel_bytes = build_excel_bytes(export_data_horizontal)

    pdf_result = generate_pdf_vertical(
        supabase, cod, tabela_gasita, TABLE_LABELS.get(tabela_gasita, "Fișă"),
        lambda s, c, t: build_vertical_export_data(s, c, t)
    )
    pdf_bytes = pdf_result[0] if isinstance(pdf_result, tuple) else pdf_result

    print_html = generate_print_html_vertical(
        supabase, cod, tabela_gasita, TABLE_LABELS.get(tabela_gasita, "Fișă"),
        lambda s, c, t: build_vertical_export_data(s, c, t)
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
            components.html(print_html, height=700, width=800, scrolling=True)
