# =========================================================
# utils/export_print.py
# v.modul.1.2 - Revenire la formatul original validat (doar culoare text negru)
# =========================================================

import html as _html

def generate_print_html_vertical(supabase, cod: str, tabela_gasita: str, titlu_fisa: str, build_vertical_export_data_func) -> str:
    """
    Generează HTML pentru print, cu structură verticală (câmp | valoare).
    Format original validat, doar culoarea textului este neagră.
    """
    export_data = build_vertical_export_data_func(supabase, cod, tabela_gasita)

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
        td {{ color: #000000; font-size: 10px; }}
        @media print {{
            button {{ display: none; }}
        }}
    </style>
</head>
<body>
    <button onclick="window.print()">Print</button>
    <h2>IDBDC UPT - Fișa {titlu_fisa} - Cod: {cod}</h2>
"""
    for section in export_data["sections"]:
        html += f"<h3>{section['name'].upper()}</h3>"
        html += " <table> <tr><th>Camp</th><th>Valoare</th></tr>"
        for f, v in zip(section["fields"], section["values"]):
            html += f"<tr><br>{_html.escape(str(f))}</td><br>{_html.escape(str(v))}</td></tr>"
        html += "</table>"
    html += """
</body>
</html>"""
    return html
