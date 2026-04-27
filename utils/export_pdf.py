# =========================================================
# utils/export_pdf.py
# vers.modul.2.0
# 2026.04.28
# Diacritice corecte prin font local (assets/fonts/DejaVuSans.ttf)
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


# ----------------------------------------------------------
# Calea spre fontul local — relativ la rădăcina proiectului.
# Fontul trebuie pus manual în assets/fonts/DejaVuSans.ttf
# Descarcă de la:
# https://github.com/dejavu-fonts/dejavu-fonts/releases
# ----------------------------------------------------------
_BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FONT_LOCAL = os.path.join(_BASE_DIR, "assets", "fonts", "DejaVuSans.ttf")
_FONT_NAME  = "DejaVuSans"
_font_ready = False


def _ensure_font():
    """Înregistrează fontul DejaVuSans o singură dată."""
    global _font_ready, _FONT_NAME
    if _font_ready:
        return _FONT_NAME

    # 1. Font local din proiect (calea preferată)
    if os.path.exists(_FONT_LOCAL):
        try:
            pdfmetrics.registerFont(TTFont(_FONT_NAME, _FONT_LOCAL))
            _font_ready = True
            return _FONT_NAME
        except Exception:
            pass

    # 2. Fonturi instalate pe sistem (Linux)
    sistem_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in sistem_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(_FONT_NAME, path))
                _font_ready = True
                return _FONT_NAME
            except Exception:
                continue

    # 3. Fallback Helvetica (fara diacritice — doar pentru debugging)
    _FONT_NAME = "Helvetica"
    _font_ready = True
    return _FONT_NAME


def generate_pdf_vertical(
    supabase,
    cod: str,
    tabela_gasita: str,
    titlu_fisa: str,
    build_vertical_export_data_func,
) -> bytes:
    """
    Generează PDF cu structură verticală (câmp | valoare).
    """
    try:
        font_name = _ensure_font()

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
            leading=10,
        )

        story = []
        story.append(
            Paragraph(f"IDBDC UPT — Fișa {titlu_fisa} — Cod: {cod}", title_style)
        )
        story.append(Spacer(1, 0.5 * cm))

        export_data = build_vertical_export_data_func(supabase, cod, tabela_gasita)

        for section in export_data.get("sections", []):
            story.append(Paragraph(str(section["name"]).upper(), section_style))
            story.append(Spacer(1, 0.2 * cm))

            table_data = []
            for f, v in zip(section.get("fields", []), section.get("values", [])):
                f_safe = (
                    str(f)
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                v_safe = (
                    str(v)
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                table_data.append(
                    [Paragraph(f_safe, cell_style), Paragraph(v_safe, cell_style)]
                )

            if table_data:
                t = Table(table_data, colWidths=[4.5 * cm, 11 * cm])
                t.setStyle(
                    TableStyle(
                        [
                            ("FONTNAME",    (0, 0), (-1, -1), font_name),
                            ("FONTSIZE",    (0, 0), (-1, -1), 8),
                            ("GRID",        (0, 0), (-1, -1), 0.3, colors.grey),
                            ("VALIGN",      (0, 0), (-1, -1), "TOP"),
                            ("BACKGROUND",  (0, 0), (0, -1), HexColor("#EEF2F7")),
                            ("TEXTCOLOR",   (0, 0), (0, -1), HexColor("#0B2A52")),
                            ("FONTNAME",    (0, 0), (0, -1), font_name),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1),
                             [HexColor("#FFFFFF"), HexColor("#F7F9FC")]),
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
