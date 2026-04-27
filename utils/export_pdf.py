# =========================================================
# utils/export_pdf.py
# vers.modul.4.0
# 2026.04.28
# Rescris cu fpdf2 — suport Unicode nativ, fara dependenta sistem
# =========================================================

import os
from fpdf import FPDF


# Calea fontului din repository
_BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FONT_PATH  = os.path.join(_BASE_DIR, "assets", "fonts", "DejaVuSans.ttf")


def generate_pdf_vertical(
    supabase,
    cod: str,
    tabela_gasita: str,
    titlu_fisa: str,
    build_vertical_export_data_func,
) -> tuple:
    """
    Generează PDF cu structură verticală (câmp | valoare).
    Returnează (pdf_bytes, debug_msg).
    """
    try:
        # Verificare font
        if not os.path.exists(_FONT_PATH):
            return None, f"Font negasit la: {_FONT_PATH}"

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Înregistrare font Unicode
        pdf.add_font("DejaVu", style="", fname=_FONT_PATH)

        # Titlu
        pdf.set_font("DejaVu", size=13)
        pdf.set_text_color(11, 42, 82)
        pdf.cell(0, 10, f"IDBDC UPT — Fișa {titlu_fisa} — Cod: {cod}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(4)

        # Date
        export_data = build_vertical_export_data_func(supabase, cod, tabela_gasita)

        for section in export_data.get("sections", []):
            # Titlu secțiune
            pdf.set_font("DejaVu", size=10)
            pdf.set_text_color(11, 42, 82)
            pdf.set_fill_color(11, 42, 82)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 7, str(section["name"]).upper(), new_x="LMARGIN", new_y="NEXT", fill=True)
            pdf.ln(1)

            # Rânduri câmp | valoare
            fields = section.get("fields", [])
            values = section.get("values", [])
            row_idx = 0
            for f, v in zip(fields, values):
                # Fundal alternant
                if row_idx % 2 == 0:
                    pdf.set_fill_color(247, 249, 252)
                else:
                    pdf.set_fill_color(255, 255, 255)

                # Coloana câmp (stânga, fundal albăstrui)
                pdf.set_fill_color(238, 242, 247)
                pdf.set_text_color(11, 42, 82)
                pdf.set_font("DejaVu", size=8)

                # Calculăm înălțimea necesară pentru multi_cell
                col1_w = 55
                col2_w = 125
                row_h  = 6

                x_start = pdf.get_x()
                y_start = pdf.get_y()

                # Câmp (coloana 1)
                pdf.set_xy(x_start, y_start)
                pdf.set_fill_color(238, 242, 247)
                pdf.set_text_color(11, 42, 82)
                pdf.multi_cell(col1_w, row_h, str(f), border=1, fill=True, new_x="RIGHT", new_y="TOP")
                y_after_col1 = pdf.get_y()

                # Valoare (coloana 2)
                pdf.set_xy(x_start + col1_w, y_start)
                if row_idx % 2 == 0:
                    pdf.set_fill_color(247, 249, 252)
                else:
                    pdf.set_fill_color(255, 255, 255)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(col2_w, row_h, str(v) if v is not None else "", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
                y_after_col2 = pdf.get_y()

                # Aliniem y la maximul dintre cele două coloane
                pdf.set_y(max(y_after_col1, y_after_col2))
                row_idx += 1

            pdf.ln(4)

        pdf_bytes = pdf.output()
        return bytes(pdf_bytes), "OK — fpdf2 cu DejaVu"

    except Exception as e:
        return None, f"EXCEPTIE fpdf2: {e}"
