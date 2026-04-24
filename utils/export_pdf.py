# =========================================================
# utils/export_pdf.py
# v.modul.2.0 - Folosește weasyprint (HTML -> PDF)
# =========================================================

import io
from weasyprint import HTML

def generate_pdf_vertical(supabase, cod: str, tabela_gasita: str, titlu_fisa: str, build_vertical_export_data_func) -> bytes:
    """
    Generează PDF folosind weasyprint, bazat pe HTML-ul existent de la Print.
    Avantaj: diacriticele sunt păstrate 100%.
    """
    try:
        # Obținem datele structurate pentru export vertical
        export_data = build_vertical_export_data_func(supabase, cod, tabela_gasita)
        
        # Construim HTML-ul (același care funcționează la Print)
        html_content = _build_print_html(export_data, cod, titlu_fisa)
        
        # Convertim HTML în PDF
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
    except Exception as e:
        return None

def _build_print_html(export_data: dict, cod: str, titlu_fisa: str) -> str:
    """Construiește HTML-ul pentru print (același care funcționează corect)."""
    import html as _html
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Fișa {cod}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #ffffff; }}
        h2 {{ color: #0B2A52; }}
        h3 {{ color: #0B2A52; margin-top: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 10px; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ccc; padding: 6px; text-align: left; vertical-align: top; }}
        th {{ background-color: #0B2A52; color: white; font-size: 11px; }}
        td {{ color: #000000; font-size: 10px; }}
        @media print {{
            button {{ display: none; }}
        }}
    </style>
</head>
<body>
    <h2>IDBDC UPT - Fișa {titlu_fisa} - Cod: {cod}</h2>
"""
    for section in export_data["sections"]:
        html += f"<h3>{section['name'].upper()}</h3>"
        html += " <table> <tr><th>Camp</th><th>Valoare</th></tr>"
        for f, v in zip(section["fields"], section["values"]):
            html += f" hilabbert<td>{_html.escape(str(f))}</td>\n<td>{_html.escape(str(v))}</td\n</tr>"
        html += "</table>"
    html += """
</body>
</html>"""
    return html
