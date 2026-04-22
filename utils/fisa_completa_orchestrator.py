# =========================================================
# utils/fisa_completa_orchestrator.py
# v.modul.1.1 - Orchestrator pentru afișarea fișei complete (explorator)
# =========================================================

import streamlit as st
import pandas as pd
import html as _html
import streamlit.components.v1 as components

from utils.display_config import TABLE_LABELS
from utils.display_rendering import render_sectiune_tabel, render_echipa_compact
from utils.export_common import build_horizontal_export_data, build_vertical_export_data
from utils.export_csv_excel import build_csv_bytes, build_excel_bytes
from utils.export_pdf import generate_pdf_vertical
from utils.export_print import generate_print_html_vertical
from utils.supabase_helpers import safe_select_eq

# =========================================================
# Autentificare export (placeholder)
# =========================================================
def _render_export_auth_tab1(supabase):
    # TODO: implementați autentificarea reală
    return True

# =========================================================
# Funcția principală de randare a fișei complete
# =========================================================
def render_fisa_completa(supabase, cod: str, tabela_gasita: str, titlu_eticheta: str):
    """
    Funcția principală de afișare a fișei complete.
    Parametri:
        supabase: clientul Supabase
        cod: codul identificator (string)
        tabela_gasita: numele tabelei SQL de bază (ex: "base_contracte_cep")
        titlu_eticheta: eticheta vizuală (ex: "CEP") – nu se folosește direct, dar păstrată pentru consistență
    """
    st.markdown("## 📄 Fișă completă")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.88);font-size:1.02rem;font-weight:600;"
        "margin-bottom:0.85rem;'>Introduceți codul și consultați toate informațiile asociate.</div>",
        unsafe_allow_html=True,
    )
    
    # Afișare secțiuni cu checkbox-uri
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

    # Secțiunea de export
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown(
        "<div style='color:rgba(255,255,255,0.75);font-size:0.90rem;font-weight:700;"
        "margin-bottom:6px;'>📤 Export fișă</div>",
        unsafe_allow_html=True,
    )
    if not _render_export_auth_tab1(supabase):
        return

    # Construire date export
    export_data_horizontal = build_horizontal_export_data(supabase, cod, tabela_gasita)
    if not export_data_horizontal["headers"]:
        st.info("Nu există date de exportat pentru acest cod.")
        return

    # CSV și Excel (orizontal)
    csv_bytes = build_csv_bytes(export_data_horizontal)
    excel_bytes = build_excel_bytes(export_data_horizontal)

    # PDF (vertical)
    pdf_bytes = generate_pdf_vertical(
        supabase, cod, tabela_gasita, TABLE_LABELS.get(tabela_gasita, "Fișă"),
        lambda s, c, t: build_vertical_export_data(s, c, t)
    )

    # Print HTML (vertical)
    print_html = generate_print_html_vertical(
        supabase, cod, tabela_gasita, TABLE_LABELS.get(tabela_gasita, "Fișă"),
        lambda s, c, t: build_vertical_export_data(s, c, t)
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.download_button("⬇️ CSV", data=csv_bytes, file_name=f"fisa_{cod}.csv", mime="text/csv", key=f"fisa_csv_{cod}")
    with col2:
        st.download_button("⬇️ Excel", data=excel_bytes, file_name=f"fisa_{cod}.xlsx",
                          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"fisa_xlsx_{cod}")
    with col3:
        if pdf_bytes:
            st.download_button("⬇️ PDF", data=pdf_bytes, file_name=f"fisa_{cod}.pdf", mime="application/pdf", key=f"fisa_pdf_{cod}")
        else:
            st.button("⬇️ PDF", disabled=True, help="PDF indisponibil - verificați reportlab")
    with col4:
        if st.button("🖨️ Print", key=f"fisa_print_{cod}"):
            components.html(print_html, height=700, scrolling=True)
