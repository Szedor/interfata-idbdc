# =========================================================
# TAB 1 — FIȘA COMPLETĂ (după cod)
# !! FIȘIER COMPLET - VERSIUNE FINALĂ !!
# =========================================================

import streamlit as st
import pandas as pd
import html as _html
import io
import streamlit.components.v1 as components
from supabase import Client
from datetime import datetime

# =========================================================
# CONSTANTE ȘI CONFIGURĂRI
# =========================================================

COL_LABELS = {
    "cod_identificare": "NR.CONTRACT/ID PROIECT",
    "denumire_categorie": "CATEGORIA DE DOCUMENTE",
    "status_contract_proiect": "STATUS CONTRACT/PROIECT",
    "data_contract": "DATA CONTRACTULUI",
    "data_inceput": "DATA DE INCEPUT",
    "data_sfarsit": "DATA DE SFARSIT",
    "durata": "DURATA",
    "valuta": "VALUTA",
    "valoare_contract_cep_terti_speciale": "VALOARE CONTRACT",
    "titlul_proiect": "OBIECTUL/TITLUL CONTRACTULUI/PROIECTULUI",
    "denumire_beneficiar": "DENUMIREA BENEFICIARULUI",
    "obiectul_contractului": "OBIECTUL CONTRACTULUI",
}

TABLE_LABELS = {
    "base_contracte_cep": "📄 Contract CEP",
    "base_contracte_terti": "📄 Contract TERȚI",
    "base_contracte_speciale": "📄 Contract SPECIAL",
}

ALL_BASE_TABLES = ["base_contracte_cep", "base_contracte_terti", "base_contracte_speciale"]

COLS_HIDDEN_FISA = {"responsabil_idbdc", "observatii_idbdc", "status_confirmare", 
                    "data_ultimei_modificari", "validat_idbdc", "creat_de", "creat_la", 
                    "modificat_de", "modificat_la", "nr_crt"}

_TABELE_CONTRACTE = {"base_contracte_cep", "base_contracte_terti", "base_contracte_speciale"}
_COLS_EXCLUDE_CONTRACTE = {"an_referinta"}

CARD_PRIORITY = ["cod_identificare", "data_contract", "titlul_proiect", "denumire_beneficiar",
                 "data_inceput", "data_sfarsit", "durata", "status_contract_proiect"]

TEHNIC_COL_ORDER = ["cod_identificare", "obiectiv_general", "obiective_specifice", 
                    "activitati_proiect", "rezultate_proiect"]

# =========================================================
# FUNCȚII AJUTĂTOARE
# =========================================================

def _fmt_numeric(val, col_name: str = "") -> str:
    if val is None:
        return ""
    raw = str(val).strip()
    if raw == "":
        return ""
    try:
        f = float(raw.replace(",", "."))
    except (ValueError, TypeError):
        return raw
    if f.is_integer():
        return str(int(f))
    return f"{f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def _col_label(col: str, table: str = None) -> str:
    return COL_LABELS.get(col, col.replace("_", " ").capitalize())

def _safe_select_eq(supabase: Client, table: str, col: str, value: str, limit: int = 2000) -> list:
    try:
        res = supabase.table(table).select("*").eq(col, value).limit(limit).execute()
        return res.data or []
    except Exception:
        return []

def _is_persoana_contact(r: dict) -> bool:
    v = r.get("persoana_contact")
    return v is True or str(v).strip().upper() in ("TRUE", "DA", "1")

def _get_contact_info(supabase, nume: str) -> list:
    if not supabase or not nume:
        return []
    try:
        res = supabase.table("det_resurse_umane").select("email,telefon_mobil,acronim_departament").eq("nume_prenume", nume.strip()).limit(1).execute()
        if not res.data:
            return []
        d = res.data[0]
        out = []
        acronim = str(d.get("acronim_departament") or "").strip()
        email = str(d.get("email") or "").strip()
        tel = str(d.get("telefon_mobil") or "").strip()
        if acronim:
            out.append(f"Dept: {acronim}")
        if email:
            out.append(f"Email: {email}")
        if tel:
            out.append(f"Mobil: {tel}")
        return out
    except Exception:
        return []

# =========================================================
# FUNCȚII PENTRU EXPORT (orizontal - Excel/CSV, vertical - PDF/Print)
# =========================================================

def _get_section_fields_ordered(section_name: str, rows: list, table: str = None, tabela_baza_ctx: str = None) -> list:
    if not rows:
        return []
    is_contract_ctx = (tabela_baza_ctx or table or "") in _TABELE_CONTRACTE
    extra_hidden = _COLS_EXCLUDE_CONTRACTE if is_contract_ctx else set()
    for row in rows:
        visible_cols = [c for c in row.keys() if c not in COLS_HIDDEN_FISA and c not in extra_hidden and row[c] is not None and str(row[c]).strip() not in ("", "None", "nan")]
        if table == "com_date_financiare":
            order = ["cod_identificare", "valuta", "valoare_contract_cep_terti_speciale"]
        else:
            order = ["cod_identificare", "data_contract", "titlul_proiect", "denumire_beneficiar", "data_inceput", "data_sfarsit", "durata", "status_contract_proiect"]
        ordered = [c for c in order if c in visible_cols]
        rest = [c for c in visible_cols if c not in order]
        return ordered + rest
    return []

def _get_section_values_ordered(section_name: str, rows: list, field_order: list, table: str = None) -> list:
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
            values.append(_fmt_numeric(val, field) if is_num else str(val))
    return values

def _get_echipa_export_data(rows_ech: list, supabase: Client) -> tuple:
    if not rows_ech:
        return [], []
    persoane_cont = [r for r in rows_ech if _is_persoana_contact(r)]
    membri = [r for r in rows_ech if not _is_persoana_contact(r)]
    contact_parts = []
    for r in persoane_cont:
        nume = str(r.get("nume_prenume") or "").strip()
        rol = str(r.get("rol") or "").strip()
        txt = f"{nume} ({rol})" if rol else nume
        contact = _get_contact_info(supabase, nume)
        if contact:
            txt += " | " + " | ".join(contact)
        if txt:
            contact_parts.append(txt)
    val_contact = " | ".join(contact_parts) if contact_parts else "-"
    membri_list = [f"{str(r.get('nume_prenume','')).strip()} ({str(r.get('rol','')).strip()})" if r.get('rol') else str(r.get('nume_prenume','')).strip() for r in membri if r.get('nume_prenume')]
    val_membri = " · ".join(membri_list) if membri_list else "-"
    return ["PERSOANA DE CONTACT", "MEMBRII ECHIPEI"], [val_contact, val_membri]

def _build_horizontal_export_data(supabase: Client, cod: str, tabela_gasita: str) -> dict:
    export_data = {"headers": [], "values": []}
    sections = [("Generale", tabela_gasita), ("Financiar", "com_date_financiare"), ("Echipa", "com_echipe_proiect")]
    for section_name, table_name in sections:
        if table_name == "com_echipe_proiect":
            rows = _safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=2000)
            if rows:
                headers, values = _get_echipa_export_data(rows, supabase)
                export_data["headers"].extend(headers)
                export_data["values"].extend(values)
                export_data["headers"].append("")
                export_data["values"].append("")
        else:
            rows = _safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=50)
            if rows:
                field_order = _get_section_fields_ordered(section_name, rows, table_name, tabela_gasita)
                if field_order:
                    values = _get_section_values_ordered(section_name, rows, field_order, table_name)
                    headers = [_col_label(f, table_name).upper() for f in field_order]
                    export_data["headers"].extend(headers)
                    export_data["values"].extend(values)
                    export_data["headers"].append("")
                    export_data["values"].append("")
    if export_data["headers"] and export_data["headers"][-1] == "":
        export_data["headers"] = export_data["headers"][:-1]
        export_data["values"] = export_data["values"][:-1]
    return export_data

def _render_export_auth_tab1(supabase: Client) -> bool:
    import re as _re
    auth_key = "export_auth_tab1"
    pattern = _re.compile(r"^[a-z]+(?:\.[a-z]+)+@upt\.ro$", _re.IGNORECASE)
    if st.session_state.get("auth_ai", False) or st.session_state.get(auth_key, False):
        nume = st.session_state.get("user_name") or st.session_state.get("user_email", "")
        st.markdown(f"<div style='background:rgba(255,255,255,0.10);border-radius:10px;padding:8px 16px;color:#ffffff;font-weight:700;margin-bottom:0.5rem;'>✅ Export autorizat — {_html.escape(str(nume))}</div>", unsafe_allow_html=True)
        return True
    st.markdown("<div style='background:rgba(255,255,255,0.08);border-radius:12px;padding:12px 18px;margin-bottom:0.6rem;'><span style='color:#ffffff;font-weight:800;'>🔐 Export disponibil exclusiv pentru cadrele UPT — autentificare cu email instituțional</span></div>", unsafe_allow_html=True)
    ea1, ea2, _ = st.columns([2.0, 1.0, 3.0])
    with ea1:
        email_exp = st.text_input("Email", value="", key="export_email_tab1", label_visibility="collapsed", placeholder="prenume.nume@upt.ro").strip().lower()
    with ea2:
        auth_clicked = st.button("✅ Autorizare", key="export_auth_btn_tab1")
    if auth_clicked:
        if not pattern.match(email_exp):
            st.error("Email invalid. Format: prenume.nume@upt.ro")
        else:
            try:
                res = supabase.table("det_resurse_umane").select("nume_prenume,email").eq("email", email_exp).limit(1).execute()
                if res.data:
                    user = res.data[0]
                    st.session_state[auth_key] = True
                    st.session_state.user_email = email_exp
                    st.session_state.user_name = (user.get("nume_prenume") or "").strip() or email_exp
                    st.rerun()
                else:
                    st.error("Emailul nu există în baza de date IDBDC.")
            except Exception as e:
                st.error(f"Eroare verificare: {e}")
    return False

# =========================================================
# FUNCȚIA PRINCIPALĂ DE RENDER
# =========================================================

def render_fisa_completa(supabase: Client):
    st.markdown("## 📄 Fișă completă")
    st.markdown("<div style='color:rgba(255,255,255,0.88);margin-bottom:0.85rem;'>Introduceți codul și consultați toate informațiile asociate.</div>", unsafe_allow_html=True)
    
    c1, c2, _ = st.columns([1.2, 0.5, 3.3])
    with c1:
        cod = st.text_input("Cod identificare", value="", key="fisa_cod", placeholder="Ex: 998877 sau 26FDI26").strip()
    
    cod_found = False
    tabela_gasita = None
    if cod and len(cod) >= 3:
        for t in ALL_BASE_TABLES:
            if _safe_select_eq(supabase, t, "cod_identificare", cod, limit=1):
                cod_found = True
                tabela_gasita = t
                break
        with c2:
            if cod_found:
                st.markdown("<div style='margin-top:28px;font-size:1.4rem;'>✅</div>", unsafe_allow_html=True)
            elif cod and len(cod) >= 3:
                st.markdown("<div style='margin-top:28px;font-size:1.4rem;'>❌</div>", unsafe_allow_html=True)
    
    if not cod or len(cod) < 3:
        st.info("Introduceți codul identificare (minim 3 caractere).", icon="ℹ️")
        return
    
    if not cod_found:
        st.warning("Codul introdus nu a fost găsit în nicio tabelă de bază.")
        return
    
    st.divider()
    st.markdown(f"<div style='color:#ffffff;font-size:1.35rem;font-weight:900;margin-bottom:1rem;'>INFORMAȚII {TABLE_LABELS.get(tabela_gasita, 'FISA').upper()}</div>", unsafe_allow_html=True)
    
    # Secțiuni vizualizare
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        show_generale = st.checkbox("📋 Generale", key=f"show_gen_{cod}")
    with col2:
        show_financiar = st.checkbox("💰 Financiar", key=f"show_fin_{cod}")
    with col3:
        show_echipa = st.checkbox("👥 Echipă", key=f"show_ech_{cod}")
    with col4:
        show_tehnic = st.checkbox("🔧 Tehnic", key=f"show_teh_{cod}")
    
    # Afișare secțiuni
    if show_generale:
        rows = _safe_select_eq(supabase, tabela_gasita, "cod_identificare", cod, limit=50)
        if rows:
            st.markdown("### 📋 Generale")
            for row in rows:
                for k, v in row.items():
                    if k not in COLS_HIDDEN_FISA and v and str(v).strip() not in ("", "None", "nan"):
                        st.markdown(f"**{_col_label(k, tabela_gasita)}:** {v}")
        else:
            st.info("Nu există informații generale.")
    
    if show_financiar:
        rows = _safe_select_eq(supabase, "com_date_financiare", "cod_identificare", cod, limit=50)
        if rows:
            st.markdown("### 💰 Financiar")
            for row in rows:
                for k, v in row.items():
                    if k not in COLS_HIDDEN_FISA and v and str(v).strip() not in ("", "None", "nan"):
                        st.markdown(f"**{_col_label(k, 'com_date_financiare')}:** {_fmt_numeric(v, k)}")
        else:
            st.info("Nu există informații financiare.")
    
    if show_echipa:
        rows = _safe_select_eq(supabase, "com_echipe_proiect", "cod_identificare", cod, limit=200)
        if rows:
            st.markdown("### 👥 Echipă")
            for r in rows:
                nume = r.get("nume_prenume", "")
                rol = r.get("rol", "")
                contact = _get_contact_info(supabase, nume)
                st.markdown(f"**{nume}** ({rol})" + (f" - {', '.join(contact)}" if contact else ""))
        else:
            st.info("Nu există membri în echipă.")
    
    # Secțiune export
    st.divider()
    st.markdown("### 📤 Export fișă")
    
    if not _render_export_auth_tab1(supabase):
        return
    
    export_data = _build_horizontal_export_data(supabase, cod, tabela_gasita)
    if not export_data["headers"]:
        st.info("Nu există date de exportat.")
        return
    
    # CSV
    csv_df = pd.DataFrame([export_data["values"]], columns=export_data["headers"])
    csv_bytes = csv_df.to_csv(index=False).encode("utf-8-sig")
    
    # Excel
    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
        pd.DataFrame([export_data["values"]], columns=export_data["headers"]).to_excel(writer, index=False, sheet_name="Fisa completa")
    excel_buf.seek(0)
    
    # Butoane download
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.download_button("⬇️ CSV", data=csv_bytes, file_name=f"fisa_{cod}.csv", mime="text/csv", key="csv_export")
    with col_b:
        st.download_button("⬇️ Excel", data=excel_buf, file_name=f"fisa_{cod}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="xlsx_export")
    with col_c:
        st.info("PDF în curs de implementare")
    with col_d:
        st.info("Print în curs de implementare")
