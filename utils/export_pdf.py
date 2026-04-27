# =========================================================
# utils/export_pdf.py
# vers.modul.5.0
# 2026.04.28
# Font DejaVuSans din matplotlib — garantat pe Streamlit Cloud
# =========================================================

import os
from fpdf import FPDF


def _get_font_path() -> str:
    """
    Returnează calea către DejaVuSans.ttf din matplotlib,
    care este preinstalat pe Streamlit Cloud.
    """
    try:
        import matplotlib
        path = os.path.join(
            os.path.dirname(matplotlib.__file__),
            "mpl-data", "fonts", "ttf", "DejaVuSans.ttf"
        )
        if os.path.exists(path):
            return path
    except Exception:
        pass
    return None


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
        font_path = _get_font_path()
        if not font_path:
            return None, "Font DejaVuSans negasit (matplotlib indisponibil)"

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.add_font("DejaVu", fname=font_path)

        # Titlu
        pdf.set_font("DejaVu", size=13)
        pdf.set_text_color(11, 42, 82)
        pdf.cell(
            0, 10,
            f"IDBDC UPT \u2014 Fi\u0219a {titlu_fisa} \u2014 Cod: {cod}",
            new_x="LMARGIN", new_y="NEXT", align="C"
        )
        pdf.ln(4)

        export_data = build_vertical_export_data_func(supabase, cod, tabela_gasita)

        col1_w = 55
        col2_w = 125
        row_h  = 6

        for section in export_data.get("sections", []):
            # Header secțiune
            pdf.set_font("DejaVu", size=10)
            pdf.set_fill_color(11, 42, 82)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 7, str(section["name"]).upper(), new_x="LMARGIN", new_y="NEXT", fill=True)
            pdf.ln(1)

            fields = section.get("fields", [])
            values = section.get("values", [])

            for row_idx, (f, v) in enumerate(zip(fields, values)):
                pdf.set_font("DejaVu", size=8)
                y_start = pdf.get_y()
                x_start = pdf.get_x()

                # Coloana 1 — câmp
                pdf.set_xy(x_start, y_start)
                pdf.set_fill_color(238, 242, 247)
                pdf.set_text_color(11, 42, 82)
                pdf.multi_cell(col1_w, row_h, str(f), border=1, fill=True, new_x="RIGHT", new_y="TOP")
                y_after1 = pdf.get_y()

                # Coloana 2 — valoare
                pdf.set_xy(x_start + col1_w, y_start)
                if row_idx % 2 == 0:
                    pdf.set_fill_color(247, 249, 252)
                else:
                    pdf.set_fill_color(255, 255, 255)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(col2_w, row_h, str(v) if v is not None else "", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
                y_after2 = pdf.get_y()

                pdf.set_y(max(y_after1, y_after2))

            pdf.ln(4)

        pdf_bytes = bytes(pdf.output())
        return pdf_bytes, f"OK — DejaVu din matplotlib: {font_path}"

    except Exception as e:
        return None, f"EXCEPTIE: {e}"
