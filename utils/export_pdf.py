# =========================================================
# utils/export_pdf.py
# vers.modul.3.3
# 2026.04.28
# Cautare exhaustiva fonturi sistem
# =========================================================

import io
import os
import glob

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
    Caută exhaustiv orice font TTF disponibil pe sistem care suportă Unicode.
    Returnează (font_name, debug_msg).
    """
    log = []
    font_name = "UniFont"

    # Căutare în toate locațiile standard Linux
    search_patterns = [
        "/usr/share/fonts/**/*.ttf",
        "/usr/local/share/fonts/**/*.ttf",
        "/home/**/.fonts/*.ttf",
        "/root/.fonts/*.ttf",
    ]

    # Fonturi preferate în ordine
    preferred = [
        "FreeSans",
        "FreeSerif",
        "NotoSans",
        "NotoSans-Regular",
        "DejaVuSans",
        "LiberationSans-Regular",
        "Ubuntu-R",
        "Arial",
    ]

    # Colectăm toate TTF-urile găsite
    all_ttf = []
    for pattern in search_patterns:
        found = glob.glob(pattern, recursive=True)
        all_ttf.extend(found)

    log.append(f"Total TTF gasite pe sistem: {len(all_ttf)}")
    if all_ttf:
        log.append(f"Exemple: {all_ttf[:5]}")

    # Încercăm mai întâi fonturile preferate
    for pref in preferred:
        for path in all_ttf:
            if pref.lower() in os.path.basename(path).lower():
                try:
                    pdfmetrics.registerFont(TTFont(font_name, path))
                    log.append(f"REGISTERED OK: {path}")
                    return font_name, " | ".join(str(x) for x in log)
                except Exception as e:
                    log.append(f"FAILED {path}: {e}")
                    continue

    # Dacă nu am găsit niciun preferat, încercăm orice TTF
    for path in all_ttf:
        try:
            pdfmetrics.registerFont(TTFont(font_name, path))
            log.append(f"REGISTERED fallback OK: {path}")
            return font_name, " | ".join(str(x) for x in log)
        except Exception:
            continue

    log.append("FALLBACK Helvetica — niciun font TTF utilizabil")
    return "Helvetica", " | ".join(str(x) for x in log)


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
