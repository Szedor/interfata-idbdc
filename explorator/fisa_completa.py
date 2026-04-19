def render_fisa_completa(supabase: Client):
    st.markdown("## 📄 Fișă completă")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.88);font-size:1.02rem;font-weight:600;"
        "margin-bottom:0.85rem;'>Introduceți codul și consultați toate informațiile asociate.</div>",
        unsafe_allow_html=True,
    )
    c1, c2, _ = st.columns([1.2, 0.5, 3.3])
    with c1:
        cod = st.text_input(
            "Cod identificare", value="", key="fisa_cod",
            placeholder="Ex: 998877 sau 26FDI26",
        ).strip()
    cod_found = False
    tabela_gasita = None
    if cod and len(cod) >= 3:
        for t in ALL_BASE_TABLES:
            rows_check = _safe_select_eq(supabase, t, "cod_identificare", cod, limit=1)
            if rows_check:
                cod_found = True
                tabela_gasita = t
                break
        with c2:
            if cod_found:
                st.markdown("<div style='margin-top:28px;font-size:1.4rem;'>✅</div>", unsafe_allow_html=True)
            elif cod and len(cod) >= 3:
                st.markdown("<div style='margin-top:28px;font-size:1.4rem;'>❌</div>", unsafe_allow_html=True)
    if not cod or len(cod) < 3:
        st.info("Introduceți codul identificare (minim 3 caractere).", icon="ℹ️")
        return
    if cod_found:
        st.markdown(
            "<div style='background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.45);"
            "border-radius:10px;padding:7px 14px;margin-bottom:4px;display:inline-block;'>"
            "<span style='color:#4ade80;font-weight:700;font-size:0.92rem;'>"
            "✅ Înregistrarea este confirmată — fișa este disponibilă și pregătită pentru consultare."
            "</span></div>",
            unsafe_allow_html=True,
        )
    if not cod_found:
        st.warning("Codul introdus nu a fost găsit în nicio tabelă de bază.")
        return
    st.divider()
    titlu_fisa = TABLE_LABELS.get(tabela_gasita, "Fișă")
    titlu_fisa_curat = titlu_fisa.split(" ", 1)[-1] if " " in titlu_fisa else titlu_fisa
    st.markdown(
        f"<div style='color:#ffffff;font-size:1.35rem;font-weight:900;"
        f"letter-spacing:0.03em;margin-bottom:1rem;'>"
        f"INFORMAȚII {titlu_fisa_curat.upper()}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
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
                rows = _safe_select_eq(supabase, sec_table, "cod_identificare", cod, limit=2000)
                if not rows:
                    st.info("Nu există membri echipă pentru acest contract.")
                else:
                    _render_echipa_compact(rows, cod_ctx=cod, supabase=supabase)
            else:
                rows = _safe_select_eq(supabase, sec_table, "cod_identificare", cod, limit=50)
                if not rows:
                    st.info(f"Nu există informații pentru secțiunea {sec_label}.")
                else:
                    _render_sectiune_tabel(sec_label, rows, sec_table, tabela_baza_ctx=tabela_gasita)
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

    export_data = _build_horizontal_export_data(supabase, cod, tabela_gasita)

    if not export_data["headers"]:
        st.info("Nu există date de exportat pentru acest cod.")
        return

    csv_df = pd.DataFrame([export_data["values"]], columns=export_data["headers"])
    csv_bytes = csv_df.to_csv(index=False).encode("utf-8-sig")

    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
        df_export = pd.DataFrame([export_data["values"]], columns=export_data["headers"])
        df_export.to_excel(writer, index=False, sheet_name="Fisa completa")
    excel_buf.seek(0)

    pdf_buf = _generate_pdf_vertical(supabase, cod, tabela_gasita, titlu_fisa_curat)

    print_html = _generate_print_html_vertical(supabase, cod, tabela_gasita, titlu_fisa_curat)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.download_button("⬇️ CSV", data=csv_bytes, file_name=f"fisa_{cod}.csv", mime="text/csv", key="fisa_csv")
    with col2:
        st.download_button("⬇️ Excel", data=excel_buf, file_name=f"fisa_{cod}.xlsx",
                          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="fisa_xlsx")
    with col3:
        if pdf_buf:
            st.download_button("⬇️ PDF", data=pdf_buf, file_name=f"fisa_{cod}.pdf", mime="application/pdf", key="fisa_pdf")
        else:
            st.button("⬇️ PDF", disabled=True, help="PDF indisponibil - verificați reportlab")
    with col4:
        if st.button("🖨️ Print", key="fisa_print"):
            components.html(print_html, height=700, scrolling=True)


def _build_horizontal_export_data(supabase: Client, cod: str, tabela_gasita: str) -> dict:
    export_data = {
        "headers": [],
        "values": [],
        "sections_order": []
    }
    sections = [
        ("Generale", tabela_gasita),
        ("Financiar", "com_date_financiare"),
        ("Echipa", "com_echipe_proiect"),
        ("Tehnic", "com_aspecte_tehnice"),
    ]
    for section_name, table_name in sections:
        if table_name == "com_echipe_proiect":
            rows = _safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=2000)
            if rows:
                headers, values = _get_echipa_export_data(rows, supabase)
                export_data["headers"].extend([h.upper() for h in headers])
                export_data["values"].extend(values)
                export_data["sections_order"].append(section_name)
                export_data["headers"].append("")
                export_data["values"].append("")
        else:
            rows = _safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=50)
            if rows:
                field_order = _get_section_fields_ordered(section_name, rows, table_name, tabela_gasita)
                if field_order:
                    values = _get_section_values_ordered(section_name, rows, field_order, table_name)
                    headers = [_col_label(f, table_name).upper() for f in field_order]
                    export_data["headers"].extend(headers)
                    export_data["values"].extend(values)
                    export_data["sections_order"].append(section_name)
                    export_data["headers"].append("")
                    export_data["values"].append("")
    if export_data["headers"] and export_data["headers"][-1] == "":
        export_data["headers"] = export_data["headers"][:-1]
        export_data["values"] = export_data["values"][:-1]
    return export_data


def _get_section_fields_ordered(section_name: str, rows: list, table: str = None,
                                 tabela_baza_ctx: str = None) -> list:
    if not rows:
        return []
    is_contract_ctx = (tabela_baza_ctx or table or "") in _TABELE_CONTRACTE
    extra_hidden = _COLS_EXCLUDE_CONTRACTE if is_contract_ctx else set()
    field_order = []
    for row in rows:
        visible_cols = [
            c for c in row.keys()
            if c not in COLS_HIDDEN_FISA
            and c not in extra_hidden
            and row[c] is not None
            and str(row[c]).strip() not in ("", "None", "nan")
        ]
        if table == "com_aspecte_tehnice":
            ordered = [c for c in TEHNIC_COL_ORDER if c in visible_cols]
            rest = [c for c in visible_cols if c not in TEHNIC_COL_ORDER]
            visible_cols = ordered + rest
        elif table == "com_date_financiare":
            COL_ORDER_FINANCIAR = [
                "cod_identificare", "valuta",
                "valoare_contract_cep_terti_speciale",
                "valoare_anuala_contract", "valoare_totala_contract",
                "cofinantare_anuala_contract", "cofinantare_totala_contract",
                "suma_solicitata_fdi", "cofinantare_upt_fdi",
                "cost_total_proiect", "cost_proiect_upt",
                "contributie_ue_total_proiect", "contributie_ue_proiect_upt",
            ]
            ordered = [c for c in COL_ORDER_FINANCIAR if c in visible_cols]
            rest = [c for c in visible_cols if c not in COL_ORDER_FINANCIAR]
            visible_cols = ordered + rest
        else:
            COL_ORDER_GENERALE = [
                "denumire_categorie", "acronim_tip_contract", "cod_identificare",
                "data_contract", "obiectul_contractului", "denumire_beneficiar",
                "data_inceput", "data_sfarsit", "durata", "status_contract_proiect",
                "titlul_proiect", "acronim_proiect", "programul_de_finantare",
                "schema_de_finantare", "apel_pentru_propuneri", "rol_upt",
                "parteneri", "coordonator", "director_proiect",
                "data_depunere", "data_depozit_cerere", "data_apel",
                "an_referinta", "an_inceput", "an_sfarsit", "durata_luni",
                "natura_eveniment", "format_eveniment", "loc_desfasurare",
                "numar_participanti", "institutii_organizare",
                "acronim_prop_intelect", "nr_cerere", "nr_brevet",
                "data_acordare", "data_oficiala_acordare", "numar_oficial_acordare",
                "inventatori", "cuvinte_cheie", "descriere", "observatii",
            ]
            ordered = [c for c in COL_ORDER_GENERALE if c in visible_cols]
            rest = [c for c in visible_cols if c not in COL_ORDER_GENERALE]
            visible_cols = ordered + rest
        field_order = visible_cols
        break
    return field_order


def _get_section_values_ordered(section_name: str, rows: list, field_order: list,
                                 table: str = None) -> list:
    if not rows or not field_order:
        return []
    values = []
    for field in field_order:
        val = None
        for row in rows:
            if field in row and row[field] is not None and str(row[field]).strip() not in ("", "None", "nan"):
                val = row[field]
                break
        if val is None:
            values.append("")
        else:
            try:
                float(str(val).replace(",", ".").strip())
                is_num = True
            except (ValueError, TypeError):
                is_num = False
            values.append(_fmt_numeric(val, field) if is_num else str(val))
    return values


def _get_echipa_export_data(rows_ech: list, supabase: Client) -> tuple:
    if not rows_ech:
        return [], []
    persoane_cont = [r for r in rows_ech if _is_persoana_contact(r)]
    membri = sorted([r for r in rows_ech if not _is_persoana_contact(r)],
                    key=lambda r: str(r.get("nume_prenume") or ""))
    contact_parts = []
    for r in persoane_cont:
        nume = str(r.get("nume_prenume") or "").strip()
        rol = str(r.get("rol") or r.get("functia_specifica") or "").strip()
        txt = ", ".join(p for p in [nume, rol] if p)
        contact = _get_contact_info(supabase, nume)
        if contact:
            txt += "  |  " + "  ".join(contact)
        if txt:
            contact_parts.append(txt)
    val_contact = "  |  ".join(contact_parts) if contact_parts else "-"
    def _fmt_m(r):
        nume = str(r.get("nume_prenume") or "").strip()
        rol = str(r.get("rol") or r.get("functia_specifica") or "").strip()
        if nume and rol:
            return f"{nume} ({rol})"
        return nume or rol
    val_membri = "  ·  ".join(_fmt_m(r) for r in membri if _fmt_m(r)) or "-"
    return ["Persoana de contact", "Membrii echipei"], [val_contact, val_membri]


def _generate_pdf_vertical(supabase: Client, cod: str, tabela_gasita: str, titlu_fisa: str) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib.colors import HexColor
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os

        font_registered = False
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:\\Windows\\Fonts\\arial.ttf",
        ]
        for path in font_paths:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont("CustomFont", path))
                    font_registered = True
                    break
                except:
                    continue
        if not font_registered:
            font_name = "Helvetica"
        else:
            font_name = "CustomFont"

        pdf_buf = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buf, pagesize=A4,
                                leftMargin=1.5*cm, rightMargin=1.5*cm,
                                topMargin=1.5*cm, bottomMargin=1.5*cm)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle", parent=styles["Title"],
            fontName=font_name, fontSize=12, textColor=HexColor("#0B2A52"), alignment=1
        )
        header_style = ParagraphStyle(
            "HeaderStyle", parent=styles["Normal"],
            fontName=font_name, fontSize=8, textColor=colors.white, alignment=1
        )
        cell_style = ParagraphStyle(
            "CellStyle", parent=styles["Normal"],
            fontName=font_name, fontSize=7.5, leading=9
        )

        story = []
        story.append(Paragraph(f"IDBDC UPT - Fișa {titlu_fisa} - Cod: {cod}", title_style))
        story.append(Spacer(1, 0.5*cm))

        sections = [
            ("Generale", tabela_gasita),
            ("Financiar", "com_date_financiare"),
            ("Echipa", "com_echipe_proiect"),
            ("Tehnic", "com_aspecte_tehnice"),
        ]

        for section_name, table_name in sections:
            if table_name == "com_echipe_proiect":
                rows = _safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=2000)
                if rows:
                    story.append(Paragraph(section_name.upper(), header_style))
                    story.append(Spacer(1, 0.2*cm))
                    headers, values = _get_echipa_export_data(rows, supabase)
                    table_data = [[headers[0], values[0]], [headers[1], values[1]]]
                    t = Table(table_data, colWidths=[4*cm, 11*cm])
                    t.setStyle(TableStyle([
                        ("FONTNAME", (0, 0), (-1, -1), font_name),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 0.3*cm))
            else:
                rows = _safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=50)
                if rows:
                    story.append(Paragraph(section_name.upper(), header_style))
                    story.append(Spacer(1, 0.2*cm))
                    field_order = _get_section_fields_ordered(section_name, rows, table_name, tabela_gasita)
                    if field_order:
                        values = _get_section_values_ordered(section_name, rows, field_order, table_name)
                        headers = [_col_label(f, table_name) for f in field_order]
                        table_data = []
                        for h, v in zip(headers, values):
                            table_data.append([h, v])
                        t = Table(table_data, colWidths=[4*cm, 11*cm])
                        t.setStyle(TableStyle([
                            ("FONTNAME", (0, 0), (-1, -1), font_name),
                            ("FONTSIZE", (0, 0), (-1, -1), 8),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ]))
                        story.append(t)
                        story.append(Spacer(1, 0.3*cm))

        doc.build(story)
        pdf_buf.seek(0)
        return pdf_buf.getvalue()
    except Exception as e:
        return None


def _generate_print_html_vertical(supabase: Client, cod: str, tabela_gasita: str, titlu_fisa: str) -> str:
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Fișa {cod}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h2 {{ color: #0B2A52; }}
        h3 {{ color: #0B2A52; margin-top: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 10px; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ccc; padding: 6px; text-align: left; vertical-align: top; }}
        th {{ background-color: #0B2A52; color: white; font-size: 11px; }}
        td {{ font-size: 10px; }}
        @media print {{
            button {{ display: none; }}
        }}
    </style>
</head>
<body>
    <button onclick="window.print()">Print</button>
    <h2>IDBDC UPT - Fișa {titlu_fisa} - Cod: {cod}</h2>
"""
    sections = [
        ("Generale", tabela_gasita),
        ("Financiar", "com_date_financiare"),
        ("Echipa", "com_echipe_proiect"),
        ("Tehnic", "com_aspecte_tehnice"),
    ]
    for section_name, table_name in sections:
        if table_name == "com_echipe_proiect":
            rows = _safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=2000)
            if rows:
                html += f"<h3>{section_name.upper()}</h3>"
                html += "<table><tr><th>Camp</th><th>Valoare</th></tr>"
                headers, values = _get_echipa_export_data(rows, supabase)
                html += f"<tr><td>{_html.escape(headers[0])}</td><td>{_html.escape(values[0])}</td></tr>"
                html += f"<tr><td>{_html.escape(headers[1])}</td><td>{_html.escape(values[1])}</td></tr>"
                html += "</table>"
        else:
            rows = _safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=50)
            if rows:
                html += f"<h3>{section_name.upper()}</h3>"
                html += "<table><tr><th>Camp</th><th>Valoare</th></tr>"
                field_order = _get_section_fields_ordered(section_name, rows, table_name, tabela_gasita)
                if field_order:
                    values = _get_section_values_ordered(section_name, rows, field_order, table_name)
                    headers = [_col_label(f, table_name) for f in field_order]
                    for h, v in zip(headers, values):
                        html += f"<tr><td>{_html.escape(h)}</td><td>{_html.escape(v)}</td></tr>"
                html += "</table>"
    html += """
</body>
</html>"""
    return html
