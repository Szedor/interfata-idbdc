# =========================================================
# utils/export_pdf.py
# v.modul.1.2 - Generare PDF (vertical, cu diacritice)
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

def _register_font_with_diacritics():
    """
    Înregistrează un font care suportă diacritice românești.
    Returnează numele fontului de utilizat.
    """
    # Lista de fonturi care suportă diacritice (în ordinea preferinței)
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "/tmp/DejaVuSans.ttf",
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("DiacriticFont", path))
                return "DiacriticFont"
            except:
                continue
    
    # Dacă niciun font nu există, îl descărcăm
    try:
        font_url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
        font_local = "/tmp/DejaVuSans.ttf"
        urllib.request.urlretrieve(font_url, font_local)
        pdfmetrics.registerFont(TTFont("DiacriticFont", font_local))
        return "DiacriticFont"
    except:
        pass
    
    # Fallback la Helvetica (fără diacritice)
    return "Helvetica"

def generate_pdf_vertical(supabase, cod: str, tabela_gasita: str, titlu_fisa: str, build_vertical_export_data_func) -> bytes:
    """
    Generează PDF cu structură verticală (câmp | valoare).
    build_vertical_export_data_func: funcția care returnează datele structurate (din export_common.py)
    """
    try:
        # Înregistrare font cu suport diacritice
        font_name = _register_font_with_diacritics()

        pdf_buf = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buf, pagesize=A4,
                                leftMargin=1.5*cm, rightMargin=1.5*cm,
                                topMargin=1.5*cm, bottomMargin=1.5*cm)

        styles = getSampleStyleSheet()
        
        # Stiluri care folosesc noul font
        title_style = ParagraphStyle(
            "TitleStyle", parent=styles["Title"],
            fontName=font_name, fontSize=12, textColor=HexColor("#0B2A52"), alignment=1
        )
        section_style = ParagraphStyle(
            "SectionStyle", parent=styles["Normal"],
            fontName=font_name, fontSize=10, textColor=HexColor("#0B2A52"), alignment=0
        )
        cell_style = ParagraphStyle(
            "CellStyle", parent=styles["Normal"],
            fontName=font_name, fontSize=8, leading=9
        )

        story = []
        story.append(Paragraph(f"IDBDC UPT - Fișa {titlu_fisa} - Cod: {cod}", title_style))
        story.append(Spacer(1, 0.5*cm))

        export_data = build_vertical_export_data_func(supabase, cod, tabela_gasita)

        for section in export_data["sections"]:
            story.append(Paragraph(section["name"].upper(), section_style))
            story.append(Spacer(1, 0.2*cm))
            table_data = []
            for f, v in zip(section["fields"], section["values"]):
                # Escapăm caracterele speciale pentru PDF
                f_safe = str(f).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                v_safe = str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                table_data.append([Paragraph(f_safe, cell_style), Paragraph(v_safe, cell_style)])
            if table_data:
                t = Table(table_data, colWidths=[4.5*cm, 11*cm])
                t.setStyle(TableStyle([
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                story.append(t)
                story.append(Spacer(1, 0.3*cm))

        doc.build(story)
        pdf_buf.seek(0)
        return pdf_buf.getvalue()
    except Exception as e:
        return None
