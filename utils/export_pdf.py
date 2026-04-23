# =========================================================
# utils/export_pdf.py
# v.modul.1.3 - PDF cu antet frumos (logo text, culori academice)
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

def _register_font():
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:\\Windows\\Fonts\\arial.ttf",
        "/tmp/DejaVuSans.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("CustomFont", path))
                return "CustomFont"
            except:
                continue
    try:
        font_url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
        font_local = "/tmp/DejaVuSans.ttf"
        urllib.request.urlretrieve(font_url, font_local)
        pdfmetrics.registerFont(TTFont("CustomFont", font_local))
        return "CustomFont"
    except:
        return "Helvetica"

def generate_pdf_vertical(supabase, cod: str, tabela_gasita: str, titlu_fisa: str, build_vertical_export_data_func) -> bytes:
    try:
        font_name = _register_font()

        pdf_buf = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buf, pagesize=A4,
                                leftMargin=1.8*cm, rightMargin=1.8*cm,
                                topMargin=1.5*cm, bottomMargin=1.5*cm)

        styles = getSampleStyleSheet()
        
        # Stil antet frumos
        title_style = ParagraphStyle(
            "TitleStyle", parent=styles["Title"],
            fontName=font_name, fontSize=14, textColor=HexColor("#0B2A52"), alignment=1, spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            "SubtitleStyle", parent=styles["Normal"],
            fontName=font_name, fontSize=9, textColor=HexColor("#2C5F8A"), alignment=1, spaceAfter=12
        )
        section_style = ParagraphStyle(
            "SectionStyle", parent=styles["Normal"],
            fontName=font_name, fontSize=11, textColor=HexColor("#0B2A52"), alignment=0, spaceAfter=6
        )
        cell_label_style = ParagraphStyle(
            "CellLabelStyle", parent=styles["Normal"],
            fontName=font_name, fontSize=8, textColor=HexColor("#2C5F8A"), leading=10
        )
        cell_value_style = ParagraphStyle(
            "CellValueStyle", parent=styles["Normal"],
            fontName=font_name, fontSize=8, textColor=HexColor("#1A2A3A"), leading=10
        )

        story = []
        # Antet
        story.append(Paragraph("UNIVERSITATEA POLITEHNICA TIMIȘOARA", title_style))
        story.append(Paragraph("Departamentul Cercetare Dezvoltare Inovare - IDBDC", subtitle_style))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(f"Fișă {titlu_fisa} — Cod: {cod}", section_style))
        story.append(Spacer(1, 0.5*cm))

        export_data = build_vertical_export_data_func(supabase, cod, tabela_gasita)

        for section in export_data["sections"]:
            story.append(Paragraph(f"▸ {section['name'].upper()}", section_style))
            story.append(Spacer(1, 0.2*cm))
            table_data = []
            for f, v in zip(section["fields"], section["values"]):
                f_safe = str(f).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                v_safe = str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                table_data.append([Paragraph(f_safe, cell_label_style), Paragraph(v_safe, cell_value_style)])
            if table_data:
                t = Table(table_data, colWidths=[4.5*cm, 11*cm])
                t.setStyle(TableStyle([
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.append(t)
                story.append(Spacer(1, 0.3*cm))

        doc.build(story)
        pdf_buf.seek(0)
        return pdf_buf.getvalue()
    except Exception as e:
        return None
