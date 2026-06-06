# =========================================================
# utils/export_common.py
# VERSIUNE: 2.1
# STATUS: CORECTAT - tabelă financiară corectă pentru PNCDI/PNRR
# DATA: 2026.06.06
# =========================================================
# MODIFICĂRI VERSIUNEA 2.1:
#   - Fallback-ul din sectiuni_active (când nu e transmis din
#     orchestrator) folosește com_date_financiare_pn pentru
#     PNCDI și PNRR, și com_date_financiare pentru restul.
#
# MODIFICĂRI VERSIUNEA 2.0:
#   - build_horizontal_export_data și build_vertical_export_data
#     primesc parametrul sectiuni_active (lista secțiunilor
#     bifate de explorator). Exportul conține exclusiv
#     secțiunile vizibile pe ecran.
#   - NR.CONTRACT inclus ca prim câmp în secțiunea Echipă.
# =========================================================

import pandas as pd
from utils.display_helpers import col_label, fmt_numeric, get_contact_info, is_persoana_contact, get_visible_ordered_fields
from utils.supabase_helpers import safe_select_eq


def get_section_fields_ordered(section_name: str, rows: list, table: str = None,
                                tabela_baza_ctx: str = None) -> list:
    if not rows:
        return []
    for row in rows:
        return get_visible_ordered_fields(row, table, tabela_baza_ctx)
    return []


def get_section_values_ordered(section_name: str, rows: list, field_order: list,
                                table: str = None) -> list:
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


def get_echipa_export_data(rows_ech: list, supabase, cod: str = "") -> tuple:
    if not rows_ech:
        return [], []
    persoane_cont = [r for r in rows_ech if is_persoana_contact(r)]
    membri = sorted([r for r in rows_ech if not is_persoana_contact(r)],
                    key=lambda r: str(r.get("nume_prenume") or ""))

    nr_contract = str(rows_ech[0].get("cod_identificare") or cod or "").strip()

    contact_parts = []
    for r in persoane_cont:
        nume = str(r.get("nume_prenume") or "").strip()
        rol  = str(r.get("rol") or r.get("functia_specifica") or "").strip()
        txt  = ", ".join(p for p in [nume, rol] if p)
        contact = get_contact_info(supabase, nume)
        if contact:
            txt += "  |  " + "  ".join(contact)
        if txt:
            contact_parts.append(txt)
    val_contact = "  |  ".join(contact_parts) if contact_parts else "-"

    def _fmt_m(r):
        nume = str(r.get("nume_prenume") or "").strip()
        rol  = str(r.get("rol") or r.get("functia_specifica") or "").strip()
        if nume and rol:
            return f"{nume} ({rol})"
        return nume or rol

    val_membri = "  ·  ".join(_fmt_m(r) for r in membri if _fmt_m(r)) or "-"

    headers = ["NR.CONTRACT", "PERSOANA DE CONTACT", "MEMBRII ECHIPEI"]
    values  = [nr_contract, val_contact, val_membri]
    return headers, values


def build_horizontal_export_data(supabase, cod: str, tabela_gasita: str,
                                  sectiuni_active: list = None) -> dict:
    export_data = {"headers": [], "values": []}

    if sectiuni_active is None:
        _TABELE_FIN_PN = {"base_proiecte_pncdi", "base_proiecte_pnrr"}
        _tabela_fin = "com_date_financiare_pn" if tabela_gasita in _TABELE_FIN_PN else "com_date_financiare"
        sectiuni_active = [
            ("Generale", tabela_gasita, "generale"),
            ("Financiar", _tabela_fin,  "financiar"),
            ("Echipa", "com_echipe_proiect", "echipa"),
            ("Tehnic", "com_aspecte_tehnice", "tehnic"),
        ]

    for section_name, table_name, sec_key in sectiuni_active:
        if sec_key == "echipa":
            rows = safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=2000)
            if rows:
                headers, values = get_echipa_export_data(rows, supabase, cod)
                export_data["headers"].extend(headers)
                export_data["values"].extend(values)
                export_data["headers"].append("")
                export_data["values"].append("")
        else:
            rows = safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=50)
            if rows:
                field_order = get_section_fields_ordered(section_name, rows, table_name, tabela_gasita)
                if field_order:
                    values  = get_section_values_ordered(section_name, rows, field_order, table_name)
                    headers = [col_label(f, table_name).upper() for f in field_order]
                    export_data["headers"].extend(headers)
                    export_data["values"].extend(values)
                    export_data["headers"].append("")
                    export_data["values"].append("")

    if export_data["headers"] and export_data["headers"][-1] == "":
        export_data["headers"] = export_data["headers"][:-1]
        export_data["values"]  = export_data["values"][:-1]

    return export_data


def build_vertical_export_data(supabase, cod: str, tabela_gasita: str,
                                sectiuni_active: list = None) -> dict:
    export_data = {"sections": []}

    if sectiuni_active is None:
        _TABELE_FIN_PN = {"base_proiecte_pncdi", "base_proiecte_pnrr"}
        _tabela_fin = "com_date_financiare_pn" if tabela_gasita in _TABELE_FIN_PN else "com_date_financiare"
        sectiuni_active = [
            ("Generale", tabela_gasita, "generale"),
            ("Financiar", _tabela_fin,  "financiar"),
            ("Echipa", "com_echipe_proiect", "echipa"),
            ("Tehnic", "com_aspecte_tehnice", "tehnic"),
        ]

    for section_name, table_name, sec_key in sectiuni_active:
        section_data = {"name": section_name, "fields": [], "values": []}

        if sec_key == "echipa":
            rows = safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=2000)
            if rows:
                headers, values = get_echipa_export_data(rows, supabase, cod)
                for h, v in zip(headers, values):
                    section_data["fields"].append(h)
                    section_data["values"].append(v)
                export_data["sections"].append(section_data)
        else:
            rows = safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=50)
            if rows:
                field_order = get_section_fields_ordered(section_name, rows, table_name, tabela_gasita)
                if field_order:
                    values  = get_section_values_ordered(section_name, rows, field_order, table_name)
                    headers = [col_label(f, table_name).upper() for f in field_order]
                    for h, v in zip(headers, values):
                        section_data["fields"].append(h)
                        section_data["values"].append(v)
                    export_data["sections"].append(section_data)

    return export_data
