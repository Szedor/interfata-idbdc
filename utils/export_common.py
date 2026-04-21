# =========================================================
# utils/export_common.py
# v.modul.1.0 - Structuri comune pentru export (orizontale și verticale)
# =========================================================

import pandas as pd
from utils.display_helpers import col_label, fmt_numeric, get_contact_info, is_persoana_contact, get_visible_ordered_fields
from utils.supabase_helpers import safe_select_eq

# =========================================================
# Export date financiare și generale – structură orizontală (pentru CSV/Excel)
# =========================================================
def get_section_fields_ordered(section_name: str, rows: list, table: str = None,
                                 tabela_baza_ctx: str = None) -> list:
    """Returnează lista ordonată a câmpurilor pentru o secțiune."""
    if not rows:
        return []
    field_order = []
    for row in rows:
        field_order = get_visible_ordered_fields(row, table, tabela_baza_ctx)
        break
    return field_order

def get_section_values_ordered(section_name: str, rows: list, field_order: list,
                                 table: str = None) -> list:
    """Returnează lista valorilor în aceeași ordine ca field_order."""
    if not rows or not field_order:
        return []
    values = []
    for field in field_order:
        val = None
        for row in rows:
            if field in row and row[field] is not None and str(row[field]).strip() not in ("", "None", "nan"):
                val = row[field]
                break
        if val is None:
            values.append("")
        else:
            try:
                float(str(val).replace(",", ".").strip())
                is_num = True
            except (ValueError, TypeError):
                is_num = False
            values.append(fmt_numeric(val, field) if is_num else str(val))
    return values

def get_echipa_export_data(rows_ech: list, supabase) -> tuple:
    """Returnează (header_list, values_list) pentru secțiunea Echipa în format orizontal."""
    if not rows_ech:
        return [], []
    persoane_cont = [r for r in rows_ech if is_persoana_contact(r)]
    membri = sorted([r for r in rows_ech if not is_persoana_contact(r)],
                    key=lambda r: str(r.get("nume_prenume") or ""))
    contact_parts = []
    for r in persoane_cont:
        nume = str(r.get("nume_prenume") or "").strip()
        rol = str(r.get("rol") or r.get("functia_specifica") or "").strip()
        txt = ", ".join(p for p in [nume, rol] if p)
        contact = get_contact_info(supabase, nume)
        if contact:
            txt += "  |  " + "  ".join(contact)
        if txt:
            contact_parts.append(txt)
    val_contact = "  |  ".join(contact_parts) if contact_parts else "-"
    def _fmt_m(r):
        nume = str(r.get("nume_prenume") or "").strip()
        rol = str(r.get("rol") or r.get("functia_specifica") or "").strip()
        if nume and rol:
            return f"{nume} ({rol})"
        return nume or rol
    val_membri = "  ·  ".join(_fmt_m(r) for r in membri if _fmt_m(r)) or "-"
    return ["Persoana de contact", "Membrii echipei"], [val_contact, val_membri]

def build_horizontal_export_data(supabase, cod: str, tabela_gasita: str) -> dict:
    """Construiește datele pentru export orizontal (CSV, Excel)."""
    export_data = {"headers": [], "values": []}
    sections = [
        ("Generale", tabela_gasita),
        ("Financiar", "com_date_financiare"),
        ("Echipa", "com_echipe_proiect"),
    ]
    for section_name, table_name in sections:
        if table_name == "com_echipe_proiect":
            rows = safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=2000)
            if rows:
                headers, values = get_echipa_export_data(rows, supabase)
                export_data["headers"].extend([h.upper() for h in headers])
                export_data["values"].extend(values)
                export_data["headers"].append("")  # separator
                export_data["values"].append("")
        else:
            rows = safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=50)
            if rows:
                field_order = get_section_fields_ordered(section_name, rows, table_name, tabela_gasita)
                if field_order:
                    values = get_section_values_ordered(section_name, rows, field_order, table_name)
                    headers = [col_label(f, table_name).upper() for f in field_order]
                    export_data["headers"].extend(headers)
                    export_data["values"].extend(values)
                    export_data["headers"].append("")  # separator
                    export_data["values"].append("")
    # Elimină ultimul separator gol
    if export_data["headers"] and export_data["headers"][-1] == "":
        export_data["headers"] = export_data["headers"][:-1]
        export_data["values"] = export_data["values"][:-1]
    return export_data

# =========================================================
# Structură verticală (pentru PDF și Print)
# =========================================================
def build_vertical_export_data(supabase, cod: str, tabela_gasita: str) -> dict:
    export_data = {"sections": []}
    sections = [
        ("Generale", tabela_gasita),
        ("Financiar", "com_date_financiare"),
        ("Echipa", "com_echipe_proiect"),
    ]
    for section_name, table_name in sections:
        section_data = {"name": section_name, "fields": [], "values": []}
        if table_name == "com_echipe_proiect":
            rows = safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=2000)
            if rows:
                headers, values = get_echipa_export_data(rows, supabase)
                for h, v in zip(headers, values):
                    section_data["fields"].append(h.upper())
                    section_data["values"].append(v)
                export_data["sections"].append(section_data)
        else:
            rows = safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=50)
            if rows:
                field_order = get_section_fields_ordered(section_name, rows, table_name, tabela_gasita)
                if field_order:
                    values = get_section_values_ordered(section_name, rows, field_order, table_name)
                    headers = [col_label(f, table_name).upper() for f in field_order]
                    for h, v in zip(headers, values):
                        section_data["fields"].append(h)
                        section_data["values"].append(v)
                    export_data["sections"].append(section_data)
    return export_data
