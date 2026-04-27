# =========================================================
# utils/export_pdf.py
# vers.modul.1.1
# 2026.04.28
# Generare PDF (vertical, cu diacritice corecte)
# =========================================================

import io
import os
import urllib.request

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def generate_pdf_vertical(supabase, cod: str, tabela_gasita: str, titlu_fisa: str, build_vertical_export_data_func) -> bytes:
    """
    Generează PDF cu structură verticală (câmp | valoare).
    build_vertical_export_data_func: funcția care returnează datele structurate (din export_common.py)
    """
    try:
        # Înregistrare font cu suport diacritice (robust pentru ReportLab)
        font_name = "CustomFont"

        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/tmp/DejaVuSans.ttf",
        ]

        font_registered = False

        for path in font_paths:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, path))
                    font_registered = True
                    break
                except Exception:
                    continue

        if not font_registered:
            # fallback controlat: descărcăm DejaVuSans și încercăm iar
            try:
                font_url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
                font_local = "/tmp/DejaVuSans.ttf"
                urllib.request.urlretrieve(font_url, font_local)
                pdfmetrics.registerFont(TTFont(font_name, font_local))
                font_registered = True
            except Exception:
                font_registered = False

        if not font_registered:
            # dacă tot nu se poate, folosim Helvetica (dar atunci diacriticele vor rămâne greșite)
            font_name = "Helvetica"

        pdf_buf = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buf,
            pagesize=A4,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Title"],
            fontName=font_name,
            fontSize=12,
            textColor=HexColor("#0B2A52"),
            alignment=1,
        )
        section_style = ParagraphStyle(
            "SectionStyle",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=10,
            textColor=HexColor("#0B2A52"),
            alignment=0,
        )
        cell_style = ParagraphStyle(
            "CellStyle",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=8,
            leading=9,
        )

        story = []
        story.append(Paragraph(f"IDBDC UPT - Fișa {titlu_fisa} - Cod: {cod}", title_style))
        story.append(Spacer(1, 0.5 * cm))

        export_data = build_vertical_export_data_func(supabase, cod, tabela_gasita)

        for section in export_data["sections"]:
            story.append(Paragraph(str(section["name"]).upper(), section_style))
            story.append(Spacer(1, 0.2 * cm))

            table_data = []
            for f, v in zip(section["fields"], section["values"]):
                f_safe = str(f).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                v_safe = str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

                table_data.append([Paragraph(f_safe, cell_style), Paragraph(v_safe, cell_style)])

            if table_data:
                t = Table(table_data, colWidths=[4.5 * cm, 11 * cm])
                t.setStyle(
                    TableStyle(
                        [
                            ("FONTNAME", (0, 0), (-1, -1), font_name),
                            ("FONTSIZE", (0, 0), (-1, -1), 8),
                            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ]
                    )
                )
                story.append(t)
                story.append(Spacer(1, 0.3 * cm))

        doc.build(story)
        pdf_buf.seek(0)
        return pdf_buf.getvalue()

    except Exception:
        return None
