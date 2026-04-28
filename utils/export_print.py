# =========================================================
# STATUS: FUNCTIONAL
# DATA CONFIRMARE: 2026.04.28
# VERSIUNE: 2.0
# =========================================================

import html as _html


def generate_print_html_vertical(
    supabase,
    cod: str,
    tabela_gasita: str,
    titlu_fisa: str,
    build_vertical_export_data_func,
) -> str:
    """
    Generează HTML pentru print, cu structură verticală (câmp | valoare).
    """
    export_data = build_vertical_export_data_func(supabase, cod, tabela_gasita)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Fișa {_html.escape(cod)}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: Arial, sans-serif;
            background: #ffffff;
            color: #0b1f3a;
            margin: 24px;
        }}

        /* Titlu principal */
        .titlu-fisa {{
            background: #ffffff;
            border: 2px solid #0b2a52;
            border-radius: 8px;
            padding: 12px 20px;
            margin-bottom: 24px;
            display: inline-block;
        }}
        .titlu-fisa span {{
            font-size: 15px;
            font-weight: 900;
            color: #0b2a52;
            letter-spacing: 0.03em;
        }}

        /* Titlu secțiune */
        h3 {{
            font-size: 11px;
            font-weight: 900;
            color: #ffffff;
            background-color: #0b2a52;
            padding: 5px 10px;
            margin-top: 20px;
            margin-bottom: 0;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}

        /* Tabel */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 16px;
        }}
        td {{
            border: 1px solid #c0cce0;
            padding: 5px 8px;
            text-align: left;
            vertical-align: top;
            font-size: 10px;
            color: #0b1f3a;
        }}
        /* Coloana câmp — fundal albăstrui deschis */
        td:first-child {{
            background-color: #eef2f7;
            font-weight: 700;
            width: 30%;
            color: #0b2a52;
        }}
        /* Coloana valoare — rânduri alternante */
        tr:nth-child(even) td:last-child {{
            background-color: #f7f9fc;
        }}
        tr:nth-child(odd) td:last-child {{
            background-color: #ffffff;
        }}

        /* Buton print */
        .btn-print {{
            display: inline-block;
            margin-bottom: 20px;
            padding: 8px 20px;
            background: #0b2a52;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
        }}
        .btn-print:hover {{
            background: #1a3a6c;
        }}

        @media print {{
            .btn-print {{ display: none; }}
            body {{ margin: 10px; }}
        }}
    </style>
</head>
<body>
    <button class="btn-print" onclick="window.print()">🖨️ Tipărire</button>

    <div class="titlu-fisa">
        <span>IDBDC UPT &mdash; Fișa {_html.escape(titlu_fisa)} &mdash; Cod: {_html.escape(cod)}</span>
    </div>
"""

    for section in export_data.get("sections", []):
        html += f"\n    <h3>{_html.escape(str(section['name']))}</h3>"
        html += "\n    <table>"
        for f, v in zip(section.get("fields", []), section.get("values", [])):
            f_esc = _html.escape(str(f))
            v_esc = _html.escape(str(v)) if v is not None else ""
            html += f"\n        <tr><td>{f_esc}</td><td>{v_esc}</td></tr>"
        html += "\n    </table>"

    html += """
</body>
</html>"""

    return html
