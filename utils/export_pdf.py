# =========================================================
# utils/export_pdf.py
# vers.modul.3.2
# 2026.04.28
# DEBUG cai font
# =========================================================

import io
import os

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def _get_font() -> tuple:
    """
    Returnează (font_name, debug_msg).
    """
    font_name = "DejaVuSans"
    log = []

    base_dir   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_local = os.path.join(base_dir, "assets", "fonts", "DejaVuSans.ttf")
    log.append(f"__file__={__file__}")
    log.append(f"base_dir={base_dir}")
    log.append(f"font_local={font_local} exists={os.path.exists(font_local)}")

    sistem_paths = [
        font_local,
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]

    for path in sistem_paths:
        exists = os.path.exists(path)
        log.append(f"trying {path} exists={exists}")
        if exists:
            try:
                pdfmetrics.registerFont(TTFont(font_name, path))
                log.append(f"REGISTERED OK from {path}")
                return font_name, " | ".join(log)
            except Exception as e:
                log.append(f"registerFont FAILED: {e}")
                continue

    log.append("FALLBACK Helvetica")
    return "Helvetica", " | ".join(log)


def generate_pdf_vertical(
    supabase,
    cod: str,
    tabela_gasita: str,
    titlu_fisa: str,
    build_vertical_export_data_func,
) -> tuple:
    """
    Returnează (pdf_bytes, debug_msg).
    """
    try:
        font_name, debug_msg = _get_font()

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
            "TitleStyle", parent=styles["Title"],
            fontName=font_name, fontSize=12,
            textColor=HexColor("#0B2A52"), alignment=1,
        )
        section_style = ParagraphStyle(
            "SectionStyle", parent=styles["Normal"],
            fontName=font_name, fontSize=10,
            textColor=HexColor("#0B2A52"), alignment=0,
        )
        cell_style = ParagraphStyle(
            "CellStyle", parent=styles["Normal"],
            fontName=font_name, fontSize=8, leading=10,
        )

        story = []
        story.append(Paragraph(f"IDBDC UPT — Fisa {titlu_fisa} — Cod: {cod}", title_style))
        story.append(Spacer(1, 0.5 * cm))

        export_data = build_vertical_export_data_func(supabase, cod, tabela_gasita)

        for section in export_data.get("sections", []):
            story.append(Paragraph(str(section["name"]).upper(), section_style))
            story.append(Spacer(1, 0.2 * cm))

            table_data = []
            for f, v in zip(section.get("fields", []), section.get("values", [])):
                f_safe = str(f).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                v_safe = str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                table_data.append(
                    [Paragraph(f_safe, cell_style), Paragraph(v_safe, cell_style)]
                )

            if table_data:
                t = Table(table_data, colWidths=[4.5 * cm, 11 * cm])
                t.setStyle(TableStyle([
                    ("FONTNAME",       (0, 0), (-1, -1), font_name),
                    ("FONTSIZE",       (0, 0), (-1, -1), 8),
                    ("GRID",           (0, 0), (-1, -1), 0.3, colors.grey),
                    ("VALIGN",         (0, 0), (-1, -1), "TOP"),
                    ("BACKGROUND",     (0, 0), (0, -1),  HexColor("#EEF2F7")),
                    ("TEXTCOLOR",      (0, 0), (0, -1),  HexColor("#0B2A52")),
                    ("ROWBACKGROUNDS", (0, 0), (-1, -1),
                     [HexColor("#FFFFFF"), HexColor("#F7F9FC")]),
                ]))
                story.append(t)
                story.append(Spacer(1, 0.3 * cm))

        doc.build(story)
        pdf_buf.seek(0)
        return pdf_buf.getvalue(), debug_msg

    except Exception as e:
        return None, f"EXCEPTIE: {e}"
