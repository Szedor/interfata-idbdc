# =========================================================
# TAB 1 — FIȘA COMPLETĂ (după cod)
# Versiune: 5.0 - PDF cu diacritice folosind fpdf2
# =========================================================

import streamlit as st
import pandas as pd
import html as _html
import io
import re
import os
import urllib.request
import streamlit.components.v1 as components
from supabase import Client

# ------------------------------------------------------------
# DICTIONARE ȘI CONFIGURĂRI (identice cu versiunea stabilă)
# ------------------------------------------------------------

COL_LABELS = {
    "abreviere_domeniu_fdi": "DOMENIUL FDI",
    "acronim_contracte": "ACRONIM TIP PROIECTE",
    "acronim_contracte_proiecte": "TIPUL DE CONTRACT",
    "acronim_departament": "ACRONIM DEPARTAMENT",
    "acronim_functie_upt": "ABREVIERE FUNCTIE UPT",
    "acronim_proiect": "ACRONIM TIP PROIECTE",
    "acronim_proiecte": "ACRONIM TIP PROIECTE",
    "acronim_prop_intelect": "FORME DE PROTECTIE A PROPRIETATII INDUSTRIALE",
    "activitati_proiect": "ACTIVITATI",
    "an_referinta": "ANUL DE REFERINTA",
    "apel_pentru_propuneri": "APELUL PENTRU PROPUNERI",
    "autori": "AUTORI",
    "clasificare_eveniment": "CLASIFICAREA EVENIMENTULUI",
    "cod_depunere": "COD DEPUNERE",
    "cod_domeniu_fdi": "COD DOMENIU FDI",
    "cod_identificare": "NR.CONTRACT/ID PROIECT",
    "cod_operatori": "COD OPERATORI",
    "cod_temporar": "COD DEPUNERE",
    "cod_universitate": "COD UNIVERSITATE CONF. CLASIFICARE CNFIS / UEFISCDI",
    "cofinantare_anuala_contract": "COFINANTARE ANUALA CONTRACT",
    "cofinantare_totala_contract": "COFINANTARE TOTALA CONTRACT",
    "cofinantare_upt_fdi": "COFINANTARE UPT PROIECTE FDI",
    "comentarii_diverse": "COMENTARII DIVERSE",
    "comentarii_document": "COMENTARII DOCUMENTE",
    "contract_cesiune_inventatori_externi": "CONTRACT CESIUNE / INVENTATORI EXTERNI UPT",
    "contributie_ue_proiect_upt": "CONTRIBUTIE UE PENTRU UPT",
    "contributie_ue_total_proiect": "CONTRIBUTIE UE PROIECT",
    "cost_proiect_upt": "COST UPT IN PROIECT",
    "cost_total_proiect": "COST TOTAL PROIECT",
    "data_apel": "DATA APELULUI",
    "data_contract": "DATA CONTRACTULUI",
    "data_depozit_cerere": "DATA DEPUNERE CERERE LA OSIM",
    "data_inceput": "DATA DE INCEPUT",
    "data_inceput_rol": "DATA DE INCEPUT ROL",
    "data_inceput_valabilitate": "DATA DE INCEPUT VALABILITATE",
    "data_oficiala_acordare": "DATA OFICIALA DE ACORDARE",
    "data_sfarsit": "DATA DE SFARSIT",
    "data_sfarsit_rol": "DATA DE SFARSIT ROL",
    "data_sfarsit_valabilitate": "DATA DE SFARSIT VALABILITATE",
    "denumire_beneficiar": "DENUMIREA BENEFICIARULUI",
    "denumire_categorie": "CATEGORIA DE DOCUMENTE",
    "denumire_completa": "DENUMIRE TIP CONTRACT",
    "denumire_departament": "DENUMIRE DEPARTAMENT",
    "denumire_domeniu_fdi": "DENUMIREA DOMENIULUI FDI",
    "denumire_functie_upt": "DENUMIRE FUNCTIE UPT",
    "denumire_institutie": "DENUMIREA INSTITUTIEI",
    "denumire_participanti": "DENUMIRE PARTICIPANTI",
    "denumire_prop_intelect": "DENUMIREA FORMEI DE PROTECTIE",
    "denumire_solicitant": "DENUMIRE SOLICITANT",
    "denumire_titular": "DENUMIRE TITULAR",
    "derulat_prin": "DERULAT PRIN",
    "document_oficial_original": "DOCUMENT OFICIAL ORIGINAL",
    "domenii_studii": "DOMENIILE DE STUDII SUPERIOARE",
    "domeniu_aplicare": "DOMENIUL DE APLICARE",
    "domeniu_cercetare": "DOMENIUL DE CERCETARE",
    "durata": "DURATA (în nr. luni)",
    "durata_luni": "DURATA",
    "email": "EMAIL",
    "email_upt": "EMAIL",
    "explicatii_format_evenimente": "DESCRIERE FORMAT EVENIMENT",
    "explicatii_satus_personal": "DESCRIERE STATUS PERSONAL",
    "explicatii_satus_proiect": "DESCRIERE STATUS CONTRACT/PROIECT",
    "facultate": "FACULTATEA",
    "filtru_categorie": "FILTRU CATEGORIE",
    "filtru_proiect": "FILTRU PROIECT",
    "format_eveniment": "FORMATUL EVENIMENTULUI STIINTIFIC",
    "functia_specifica": "ROLUL IN CONTRACT/PROIECT",
    "functie_upt": "ABREVIERE FUNCTIE UPT",
    "id_proiect_contract_sursa": "ID PROIECT (CONTRACT SURSA)",
    "institutii_organizare": "INSTITUTIILE ORGANIZATOARE",
    "interval_finantare": "TOTAL PROIECTE FINANTATE",
    "link_espacenet": "LINK ESPACENET",
    "loc_desfasurare": "LOCUL DE DESFASURARE",
    "natura_eveniment": "NATURA EVENIMENTULUI STIINTIFIC",
    "nr_crt": "NR.CRT.",
    "numar_autori_total": "NUMAR AUTORI TOTAL",
    "numar_autori_upt": "NUMAR AUTORI UPT",
    "numar_data_notificare_intern": "NR. SI DATA NOTIFICARE INTERNA UPT",
    "numar_oficial_acordare": "NUMAR OFICIAL DE ACORDARE",
    "numar_participanti": "NUMAR DE PARTICIPANTI",
    "numar_publicare_cerere": "NUMAR PUBLICARE CERERE",
    "nume_prenume": "NUME SI PRENUME",
    "obiectiv_general": "OBIECTIV GENERAL",
    "obiective_specifice": "OBIECTIVE SPECIFICE",
    "parteneri": "PARTENERI",
    "perioada_valabilitate": "PERIOADA DE VALABILITATE A TITLULUI DE PROTECTIE",
    "perioada_valabilitate_ani": "PERIOADA DE VALABILITATE A FORMEI DE PROTECTIE",
    "persoana_contact": "PERSOANA DE CONTACT",
    "pozitie_clasament": "POZITIE IN CLASAMENT",
    "programul_de_finantare": "PROGRAMUL DE FINANTARE",
    "punctaj": "PUNCTAJ",
    "rezultate_proiect": "REZULTATE",
    "rol": "ROL OPERATOR",
    "rol_upt": "ROL UPT",
    "schema_de_finantare": "SCHEMA DE FINANTARE",
    "scor_evaluare": "SCORUL EVALUARII",
    "spin_off": "SPIN OFF",
    "status_activ": "STATUS ACTIV",
    "status_contract_proiect": "STATUS CONTRACT/PROIECT",
    "status_document": "STATUS DOCUMENT",
    "status_personal": "STATUS PERSONAL",
    "suma_aprobata": "SUMA APROBATA MEC",
    "suma_aprobata_mec": "SUMA APROBATA MEC",
    "suma_solicitata": "SUMA SOLICITATA",
    "suma_solicitata_fdi": "SUMA SOLICITATA",
    "telefon_mobil": "TELEFON MOBIL",
    "telefon_upt": "TELEFON UPT",
    "tema_specifica": "TEMA SPECIFICA",
    "titlu_engleza_diploma": "TITLUL IN ENGLEZA CONF. DIPLOMA",
    "titlu_engleza_epo": "TITLUL IN ENGLEZA CONF. EPO",
    "titlu_engleza_fisa_inventiei": "TITLUL IN ENGLEZA CONF. FISA INVENTIEI",
    "titlu_engleza_google_translate": "TITLUL IN ENGLEZA CONF. GOOGLE TRANSLATE",
    "titlul": "TITLUL",
    "titlul_eveniment": "TITLUL EVENIMENTULUI STIINTIFIC",
    "titlul_proiect": "OBIECTUL/TITLULUI CONTRACTULUI/PROIECTULUI",
    "total_proiecte": "TOTAL PROIECTE DEPUSE",
    "username_sistem": "USERNAME",
    "valoare_anuala_contract": "VALOAREA ANUALA A CONTRACTULUI",
    "valoare_contract_cep_terti_speciale": "VALOARE CONTRACT CEP",
    "valoare_totala_contract": "VALOAREA TOTALA A CONTRACTULUI",
    "valuta": "VALUTA",
    "website": "WEBSITE",
}

COLS_HIDDEN_FISA = {
    "responsabil_idbdc", "observatii_idbdc",
    "status_confirmare", "data_ultimei_modificari", "validat_idbdc",
    "creat_de", "creat_la", "modificat_de", "modificat_la",
    "nr_crt",
}

CARD_PRIORITY = [
    "titlul_proiect", "titlu_proiect", "titlu", "titlu_eveniment", "titlu_lucrare",
    "denumire", "denumire_proiect", "obiect_contract",
    "acronim", "acronim_proiect", "acronim_contracte_proiecte",
    "denumire_categorie", "status_contract_proiect",
    "finantator", "coordonator", "director_proiect",
    "an", "an_referinta", "an_inceput", "an_sfarsit",
    "data_contract", "data_inceput", "data_sfarsit",
    "numar_contract", "valoare_contract", "valoare_totala", "valoare_upt",
    "cod_domeniu_fdi", "partener", "tara_partener",
    "natura_eveniment", "format_eveniment",
    "acronim_prop_intelect", "nr_cerere", "nr_brevet",
    "data_depunere", "data_acordare", "inventatori",
    "cuvinte_cheie", "descriere", "observatii",
]

TEHNIC_COL_ORDER = [
    "cod_identificare",
    "obiectiv_general",
    "obiective_specifice",
    "activitati_proiect",
    "rezultate_proiect",
]

_TABELE_CONTRACTE = {
    "base_contracte_cep",
    "base_contracte_terti",
    "base_contracte_speciale",
}

_COLS_EXCLUDE_CONTRACTE = {"an_referinta"}

TABLE_LABELS = {
    "base_contracte_cep":           "📄 Contract CEP",
    "base_contracte_terti":         "📄 Contract TERȚI",
    "base_contracte_speciale":      "📄 Contract SPECIAL",
    "base_proiecte_fdi":            "🔬 Proiect FDI",
    "base_proiecte_pncdi":          "🔬 Proiect PNCDI",
    "base_proiecte_pnrr":           "🔬 Proiect PNRR",
    "base_proiecte_internationale": "🌍 Proiect Internațional",
    "base_proiecte_interreg":       "🌍 Proiect INTERREG",
    "base_proiecte_noneu":          "🌍 Proiect NON-EU",
    "base_proiecte_see":            "🌍 Proiect SEE",
    "base_evenimente_stiintifice":  "🎓 Eveniment Științific",
    "base_prop_intelect":           "💡 Proprietate Industrială",
}

COL_LABELS_PER_TABLE = {
    "base_contracte_cep": {
        "cod_identificare":        "NR.CONTRACT",
        "status_contract_proiect": "STATUS CONTRACT",
        "titlul_proiect":          "OBIECTUL CONTRACTULUI",
    },
    "base_contracte_terti": {
        "cod_identificare":        "NR.CONTRACT",
        "status_contract_proiect": "STATUS CONTRACT",
        "titlul_proiect":          "OBIECTUL CONTRACTULUI",
    },
    "base_contracte_speciale": {
        "cod_identificare":        "NR.CONTRACT",
        "status_contract_proiect": "STATUS CONTRACT",
        "titlul_proiect":          "OBIECTUL CONTRACTULUI",
    },
    "base_proiecte_fdi": {
        "cod_identificare":        "ID PROIECT FDI",
        "status_contract_proiect": "STATUS PROIECT",
        "titlul_proiect":          "TITLUL PROIECTULUI",
        "suma_solicitata_fdi":     "SUMA SOLICITATA",
        "cofinantare_upt_fdi":     "COFINANTARE UPT",
    },
    "base_proiecte_pncdi": {
        "cod_identificare":        "NR.CONTRACT / COD PROIECT",
        "status_contract_proiect": "STATUS PROIECT",
        "titlul_proiect":          "TITLUL PROIECTULUI",
    },
    "base_proiecte_pnrr": {
        "cod_identificare":        "COD PROIECT PNRR",
        "status_contract_proiect": "STATUS PROIECT",
        "titlul_proiect":          "TITLUL PROIECTULUI",
    },
    "base_proiecte_internationale": {
        "cod_identificare":        "COD / NR. PROIECT",
        "status_contract_proiect": "STATUS PROIECT",
        "titlul_proiect":          "TITLUL PROIECTULUI",
        "rol_upt":                 "ROL UPT IN PROIECT",
    },
    "base_proiecte_interreg": {
        "cod_identificare":        "COD PROIECT INTERREG",
        "status_contract_proiect": "STATUS PROIECT",
        "titlul_proiect":          "TITLUL PROIECTULUI",
        "rol_upt":                 "ROL UPT IN PROIECT",
    },
    "base_proiecte_noneu": {
        "cod_identificare":        "COD / NR. PROIECT",
        "status_contract_proiect": "STATUS PROIECT",
        "titlul_proiect":          "TITLUL PROIECTULUI",
        "rol_upt":                 "ROL UPT IN PROIECT",
    },
    "base_proiecte_see": {
        "cod_identificare":        "COD / NR. PROIECT",
        "status_contract_proiect": "STATUS PROIECT",
        "titlul_proiect":          "TITLUL PROIECTULUI",
        "rol_upt":                 "ROL UPT IN PROIECT",
    },
    "base_evenimente_stiintifice": {
        "cod_identificare": "COD EVENIMENT",
        "titlul_eveniment": "TITLUL EVENIMENTULUI",
        "natura_eveniment": "NATURA EVENIMENTULUI",
        "format_eveniment": "FORMATUL EVENIMENTULUI",
        "loc_desfasurare":  "LOCUL DE DESFASURARE",
    },
    "base_prop_intelect": {
        "cod_identificare":       "NR. CERERE / BREVET",
        "acronim_prop_intelect":  "FORMA DE PROTECTIE",
        "titlul_proiect":         "TITLUL INVENTIEI / LUCRARII",
        "data_depozit_cerere":    "DATA DEPUNERE LA OSIM",
        "data_oficiala_acordare": "DATA ACORDARE",
        "numar_oficial_acordare": "NR. OFICIAL ACORDARE",
    },
    "com_date_financiare": {
        "cod_identificare": "NR.CONTRACT",
    },
    "com_aspecte_tehnice": {
        "cod_identificare": "NR.CONTRACT",
    },
}

ALL_BASE_TABLES = [
    "base_contracte_terti",
    "base_contracte_cep",
    "base_proiecte_fdi",
    "base_proiecte_pncdi",
    "base_proiecte_pnrr",
    "base_proiecte_internationale",
    "base_proiecte_interreg",
    "base_proiecte_noneu",
    "base_proiecte_see",
    "base_evenimente_stiintifice",
    "base_prop_intelect",
]

# ------------------------------------------------------------
# FUNCȚII AJUTĂTOARE (comune)
# ------------------------------------------------------------

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
    col_name = (col_name or "").lower().strip()
    no_decimal_fields = {
        "cod_identificare", "numar_contract", "nr_contract", "nr_contract_achizitie",
        "nr_contract_subsecvent", "numar_oficial_acordare", "numar_publicare_cerere",
        "numar_data_notificare_intern", "telefon_mobil", "telefon_upt",
        "cod_depunere", "cod_temporar",
    }
    if col_name in no_decimal_fields:
        return str(int(round(f)))
    financial_keys = ("valoare", "buget", "suma", "cost", "contributie", "cofinantare")
    is_financial = any(k in col_name for k in financial_keys)
    if is_financial:
        return f"{f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if f.is_integer():
        return str(int(f))
    return f"{f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def _col_label(col: str, table: str = None) -> str:
    if table and table in COL_LABELS_PER_TABLE:
        if col in COL_LABELS_PER_TABLE[table]:
            return COL_LABELS_PER_TABLE[table][col]
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

def _to_float_if_numeric(val):
    if val is None:
        return None
    raw = str(val).strip()
    if raw == "":
        return None
    raw = raw.replace(" ", "")
    if not re.fullmatch(r"[-+]?\d+(?:[.,]\d+)?", raw):
        return None
    try:
        return float(raw.replace(",", "."))
    except Exception:
        return None

# ------------------------------------------------------------
# RENDER SECȚIUNI (afișare în aplicație)
# ------------------------------------------------------------

def _render_sectiune_tabel(section_label: str, rows: list, table: str = None,
                           tabela_baza_ctx: str = None):
    if not rows:
        return
    priority_set = {c: i for i, c in enumerate(CARD_PRIORITY)}
    is_contract_ctx = (tabela_baza_ctx or table or "") in _TABELE_CONTRACTE
    extra_hidden = _COLS_EXCLUDE_CONTRACTE if is_contract_ctx else set()
    all_items = []
    for row in rows:
        visible_cols = [
            c for c in row.keys()
            if c not in COLS_HIDDEN_FISA
            and c not in extra_hidden
            and row[c] is not None
            and str(row[c]).strip() not in ("", "None", "nan")
        ]
        COL_ORDER_GENERALE = [
            "denumire_categorie", "acronim_tip_contract", "cod_identificare",
            "data_contract", "obiectul_contractului", "denumire_beneficiar",
            "data_inceput", "data_sfarsit", "durata",
            "status_contract_proiect",
            "titlul_proiect", "acronim_proiect", "programul_de_finantare",
            "schema_de_finantare", "apel_pentru_propuneri", "rol_upt",
            "parteneri", "coordonator", "director_proiect",
            "data_depunere", "data_depozit_cerere", "data_apel",
            "an_referinta", "an_inceput", "an_sfarsit", "durata_luni",
            "natura_eveniment", "format_eveniment", "loc_desfasurare",
            "numar_participanti", "institutii_organizare",
            "acronim_prop_intelect", "nr_cerere", "nr_brevet",
            "data_acordare", "data_oficiala_acordare", "numar_oficial_acordare",
            "inventatori", "cuvinte_cheie", "descriere", "observatii",
        ]
        COL_ORDER_FINANCIAR = [
            "cod_identificare", "valuta",
            "valoare_contract_cep_terti_speciale",
            "valoare_anuala_contract", "valoare_totala_contract",
            "cofinantare_anuala_contract", "cofinantare_totala_contract",
            "suma_solicitata_fdi", "cofinantare_upt_fdi",
            "cost_total_proiect", "cost_proiect_upt",
            "contributie_ue_total_proiect", "contributie_ue_proiect_upt",
        ]
        if table == "com_aspecte_tehnice":
            ordered = [c for c in TEHNIC_COL_ORDER if c in visible_cols]
            rest = [c for c in visible_cols if c not in TEHNIC_COL_ORDER]
            visible_cols = ordered + rest
        elif table == "com_date_financiare":
            ordered = [c for c in COL_ORDER_FINANCIAR if c in visible_cols]
            rest = [c for c in visible_cols if c not in COL_ORDER_FINANCIAR]
            visible_cols = ordered + rest
        else:
            ordered = [c for c in COL_ORDER_GENERALE if c in visible_cols]
            rest = [c for c in visible_cols if c not in COL_ORDER_GENERALE]
            visible_cols = ordered + rest
        for c in visible_cols:
            raw_val = row[c]
            try:
                float(str(raw_val).replace(",", ".").strip())
                is_num = True
            except (ValueError, TypeError):
                is_num = False
            val_str = _fmt_numeric(raw_val, c) if is_num else str(raw_val)
            all_items.append((_col_label(c, table), _html.escape(val_str)))
    if not all_items:
        st.info(f"Nu există câmpuri completate pentru secțiunea {section_label}.")
        return
    rows_html = ""
    for i, (label, value) in enumerate(all_items):
        sec_cell = ""
        if i == 0:
            sec_cell = (
                f"<td rowspan='{len(all_items)}' style='vertical-align:top;padding:6px 10px 6px 0;width:10%;'>"
                f"<span style='color:rgba(255,255,255,0.45);font-size:0.74rem;font-weight:800;"
                f"text-transform:uppercase;letter-spacing:0.07em;white-space:nowrap;'>"
                f"{_html.escape(section_label)}</span>"
                f"</td>"
            )
        rows_html += (
            f"<tr>{sec_cell}"
            f"<td style='padding:3px 12px 3px 0;width:23%;vertical-align:top;'>"
            f"<span style='color:rgba(255,255,255,0.50);font-size:0.76rem;font-weight:700;"
            f"text-transform:uppercase;letter-spacing:0.04em;'>{label}</span></td>"
            f"<td style='padding:3px 0 3px 0;width:67%;vertical-align:top;'>"
            f"<span style='color:#ffffff;font-size:0.95rem;font-weight:700;'>{value}</span></td>"
            f"</tr>"
        )
    st.markdown(
        f"<table style='width:100%;border-collapse:collapse;margin-bottom:0;'>{rows_html}</table>",
        unsafe_allow_html=True,
    )

def _get_contact_info(supabase, nume: str, debug_st=None) -> list:
    if not supabase or not nume:
        return []
    try:
        res = supabase.table("det_resurse_umane") \
            .select("email,telefon_mobil,acronim_departament") \
            .eq("nume_prenume", nume.strip()).limit(1).execute()
        if not res.data:
            res = supabase.table("det_resurse_umane") \
                .select("email,telefon_mobil,acronim_departament") \
                .ilike("nume_prenume", nume.strip()).limit(1).execute()
        if not res.data:
            return []
        d = res.data[0]
        out = []
        acronim = str(d.get("acronim_departament") or "").strip()
        email = str(d.get("email") or "").strip()
        tel = str(d.get("telefon_mobil") or "").strip()
        if acronim:
            try:
                dep_res = supabase.table("nom_departament") \
                    .select("denumire_departament") \
                    .eq("acronim_departament", acronim).limit(1).execute()
                den = ""
                if dep_res.data:
                    den = str(dep_res.data[0].get("denumire_departament") or "").strip()
                dept_label = f"{acronim} - {den}" if den else acronim
            except Exception:
                dept_label = acronim
            out.append(f"Dept: {dept_label}")
        if email:
            out.append(f"Email: {email}")
        if tel:
            out.append(f"Mobil: {tel}")
        return out
    except Exception:
        return []

def _render_echipa_compact(rows: list, cod_ctx: str = "", supabase=None):
    if not rows:
        st.info("Nu există echipă înregistrată pentru această fișă.")
        return
    rows_sorted = sorted(rows, key=lambda r: (0 if _is_persoana_contact(r) else 1, str(r.get("nume_prenume") or "")))
    persoane_cont = [r for r in rows_sorted if _is_persoana_contact(r)]
    membri = [r for r in rows_sorted if not _is_persoana_contact(r)]
    if persoane_cont:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.50);font-size:0.76rem;font-weight:700;"
            "text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;'>"
            "⭐ Persoana de contact</div>",
            unsafe_allow_html=True,
        )
        for r in persoane_cont:
            nume = str(r.get("nume_prenume") or "").strip()
            rol = str(r.get("functia_specifica") or "").strip()
            contact = _get_contact_info(supabase, nume)
            titlu_contact = " · ".join(p for p in [nume, rol] if p)
            contact_html = ""
            if contact:
                contact_html = (
                    "<div style='margin-top:4px;color:rgba(255,255,255,0.82);font-size:0.86rem;line-height:1.55;'>" +
                    "  ·  ".join(_html.escape(c) for c in contact) +
                    "</div>"
                )
            st.markdown(
                f"<div style='padding:7px 12px;margin-bottom:4px;background:rgba(255,255,255,0.08);"
                f"border-radius:8px;border-left:3px solid rgba(255,220,80,0.70);'>"
                f"<div style='color:#ffffff;font-size:0.96rem;line-height:1.45;'>"
                f"⭐ {_html.escape(titlu_contact)}"
                f"</div>"
                f"{contact_html}</div>",
                unsafe_allow_html=True,
            )
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    if not membri:
        return
    st.markdown(
        f"<div style='color:rgba(255,255,255,0.50);font-size:0.76rem;font-weight:700;"
        f"text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;'>"
        f"👥 Membrii echipei ({len(membri)})</div>",
        unsafe_allow_html=True,
    )
    PREVIEW = 6
    show_all_key = f"echipa_show_all_{cod_ctx or id(rows)}"
    if show_all_key not in st.session_state:
        st.session_state[show_all_key] = False
    membri_display = membri if st.session_state[show_all_key] else membri[:PREVIEW]
    if st.session_state[show_all_key] and len(membri) > PREVIEW:
        filtru = st.text_input(
            "Cauta", value="", key=f"echipa_filter_{cod_ctx or id(rows)}",
            placeholder="Filtrează după nume...", label_visibility="collapsed",
        ).strip().lower()
        if filtru:
            membri_display = [r for r in membri if filtru in str(r.get("nume_prenume") or "").lower()]
    def _fmt_membru(r):
        nume = str(r.get("nume_prenume") or "").strip()
        rol = str(r.get("rol") or r.get("functia_specifica") or "").strip()
        if nume and rol:
            return f"{_html.escape(nume)} ({_html.escape(rol)})"
        return _html.escape(nume or rol)
    inline_text = "  ·  ".join(_fmt_membru(r) for r in membri_display if _fmt_membru(r))
    st.markdown(
        f"<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.12);"
        f"border-radius:10px;padding:10px 14px;line-height:1.9;font-size:0.88rem;"
        f"color:rgba(255,255,255,0.88);'>{inline_text}</div>",
        unsafe_allow_html=True,
    )
    if len(membri) > PREVIEW:
        if st.session_state[show_all_key]:
            if st.button("▲ Restrânge lista", key=f"echipa_collapse_{cod_ctx or id(rows)}", use_container_width=False):
                st.session_state[show_all_key] = False
                st.rerun()
        else:
            ramasi = len(membri) - PREVIEW
            if st.button(f"▼ Arată toți cei {len(membri)} membri  (+{ramasi} ascunși)",
                         key=f"echipa_expand_{cod_ctx or id(rows)}", use_container_width=False):
                st.session_state[show_all_key] = True
                st.rerun()

def _render_export_auth_tab1(supabase: Client) -> bool:
    import re as _re
    auth_key = "export_auth_tab1"
    pattern = _re.compile(r"^[a-z]+(?:\.[a-z]+)+@upt\.ro$", _re.IGNORECASE)
    if st.session_state.get("auth_ai", False) or st.session_state.get(auth_key, False):
        nume = st.session_state.get("user_name") or st.session_state.get("user_email", "")
        st.markdown(
            f"<div style='background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.25);"
            f"border-radius:10px;padding:8px 16px;color:#ffffff;font-weight:700;font-size:0.95rem;"
            f"margin-bottom:0.5rem;'>✅ Export autorizat — {_html.escape(str(nume))}</div>",
            unsafe_allow_html=True,
        )
        return True
    st.markdown(
        "<div style='background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.22);"
        "border-radius:12px;padding:12px 18px;margin-bottom:0.6rem;'>"
        "<span style='color:#ffffff;font-weight:800;font-size:0.97rem;'>"
        "🔐 Export disponibil exclusiv pentru cadrele UPT — autentificare cu email instituțional"
        "</span></div>",
        unsafe_allow_html=True,
    )
    ea1, ea2, _ = st.columns([2.0, 1.0, 3.0])
    with ea1:
        email_exp = st.text_input(
            "Email", value="", key="export_email_tab1",
            label_visibility="collapsed", placeholder="prenume.nume@upt.ro",
        ).strip().lower()
    with ea2:
        auth_clicked = st.button("✅ Autorizare", key="export_auth_btn_tab1")
    if auth_clicked:
        if not pattern.match(email_exp):
            st.error("Email invalid. Format: prenume.nume@upt.ro")
        else:
            try:
                res = supabase.table("det_resurse_umane") \
                    .select("nume_prenume,email").eq("email", email_exp).limit(1).execute()
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

# ------------------------------------------------------------
# FUNCȚII PENTRU EXPORT (CSV, Excel – identice cu platforma)
# ------------------------------------------------------------

def _get_section_fields_ordered(section_name: str, rows: list, table: str = None,
                                 tabela_baza_ctx: str = None) -> list:
    if not rows:
        return []
    is_contract_ctx = (tabela_baza_ctx or table or "") in _TABELE_CONTRACTE
    extra_hidden = _COLS_EXCLUDE_CONTRACTE if is_contract_ctx else set()
    field_order = []
    for row in rows:
        visible_cols = [
            c for c in row.keys()
            if c not in COLS_HIDDEN_FISA
            and c not in extra_hidden
            and row[c] is not None
            and str(row[c]).strip() not in ("", "None", "nan")
        ]
        if table == "com_aspecte_tehnice":
            ordered = [c for c in TEHNIC_COL_ORDER if c in visible_cols]
            rest = [c for c in visible_cols if c not in TEHNIC_COL_ORDER]
            visible_cols = ordered + rest
        elif table == "com_date_financiare":
            COL_ORDER_FINANCIAR = [
                "cod_identificare", "valuta",
                "valoare_contract_cep_terti_speciale",
                "valoare_anuala_contract", "valoare_totala_contract",
                "cofinantare_anuala_contract", "cofinantare_totala_contract",
                "suma_solicitata_fdi", "cofinantare_upt_fdi",
                "cost_total_proiect", "cost_proiect_upt",
                "contributie_ue_total_proiect", "contributie_ue_proiect_upt",
            ]
            ordered = [c for c in COL_ORDER_FINANCIAR if c in visible_cols]
            rest = [c for c in visible_cols if c not in COL_ORDER_FINANCIAR]
            visible_cols = ordered + rest
        else:
            COL_ORDER_GENERALE = [
                "denumire_categorie", "acronim_tip_contract", "cod_identificare",
                "data_contract", "obiectul_contractului", "denumire_beneficiar",
                "data_inceput", "data_sfarsit", "durata", "status_contract_proiect",
                "titlul_proiect", "acronim_proiect", "programul_de_finantare",
                "schema_de_finantare", "apel_pentru_propuneri", "rol_upt",
                "parteneri", "coordonator", "director_proiect",
                "data_depunere", "data_depozit_cerere", "data_apel",
                "an_referinta", "an_inceput", "an_sfarsit", "durata_luni",
                "natura_eveniment", "format_eveniment", "loc_desfasurare",
                "numar_participanti", "institutii_organizare",
                "acronim_prop_intelect", "nr_cerere", "nr_brevet",
                "data_acordare", "data_oficiala_acordare", "numar_oficial_acordare",
                "inventatori", "cuvinte_cheie", "descriere", "observatii",
            ]
            ordered = [c for c in COL_ORDER_GENERALE if c in visible_cols]
            rest = [c for c in visible_cols if c not in COL_ORDER_GENERALE]
            visible_cols = ordered + rest
        field_order = visible_cols
        break
    return field_order

def _get_section_values_ordered(section_name: str, rows: list, field_order: list,
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
            values.append(_fmt_numeric(val, field) if is_num else str(val))
    return values

def _get_echipa_export_data(rows_ech: list, supabase: Client) -> tuple:
    if not rows_ech:
        return [], []
    persoane_cont = [r for r in rows_ech if _is_persoana_contact(r)]
    membri = sorted([r for r in rows_ech if not _is_persoana_contact(r)],
                    key=lambda r: str(r.get("nume_prenume") or ""))
    contact_parts = []
    for r in persoane_cont:
        nume = str(r.get("nume_prenume") or "").strip()
        rol = str(r.get("rol") or r.get("functia_specifica") or "").strip()
        txt = ", ".join(p for p in [nume, rol] if p)
        contact = _get_contact_info(supabase, nume)
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

def _build_horizontal_export_data(supabase: Client, cod: str, tabela_gasita: str) -> dict:
    export_data = {"headers": [], "values": []}
    sections = [
        ("Generale", tabela_gasita),
        ("Financiar", "com_date_financiare"),
        ("Echipa", "com_echipe_proiect"),
    ]
    for section_name, table_name in sections:
        if table_name == "com_echipe_proiect":
            rows = _safe_select_eq(supabase, table_name, "cod_identificare", cod, limit=2000)
            if rows:
                headers, values = _get_echipa_export_data(rows, supabase)
                export_data["headers"].extend([h.upper() for h in headers])
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

# ------------------------------------------------------------
# FUNCȚII PENTRU EXPORT PDF (folosind fpdf2)
# ------------------------------------------------------------

def _ensure_font():
    """Asigură existența fontului DejaVuSans.ttf în folderul assets/."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_dir = os.path.join(base_dir, "assets")
    font_path = os.path.join(font_dir, "DejaVuSans.ttf")
    if os.path.isfile(font_path):
        return font_path
    # Creează folderul assets dacă nu există
    os.makedirs(font_dir, exist_ok=True)
    # Încearcă să descarce fontul
    url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
    try:
        urllib.request.urlretrieve(url, font_path)
        return font_path
    except Exception:
        return None

def _generate_pdf_from_frames(export_frames: dict, cod: str) -> bytes:
    """Generează PDF cu diacritice folosind fpdf2."""
    try:
        from fpdf import FPDF
    except ImportError:
        return None

    font_path = _ensure_font()
    if not font_path:
        # Dacă nu avem font, încercăm să generăm fără diacritice (fallback)
        pass

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=1.5)
    pdf.add_page()

    # Înregistrare font dacă există
    if font_path:
        try:
            pdf.add_font("DejaVu", "", font_path, uni=True)
            pdf.set_font("DejaVu", size=10)
        except Exception:
            pdf.set_font("helvetica", size=10)
    else:
        pdf.set_font("helvetica", size=10)

    # Antet principal
    pdf.set_font_size(13)
    pdf.set_text_color(11, 42, 82)  # albastru închis
    pdf.cell(0, 8, "IDBDC — UPT", ln=True, align="C")
    pdf.set_font_size(9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, "Departamentul Cercetare Dezvoltare Inovare", ln=True, align="C")
    pdf.ln(4)

    # Subtitlu cu codul
    pdf.set_font_size(10)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(26, 74, 122)  # albastru mediu
    pdf.cell(0, 8, f"Fișă completă  |  Cod: {cod}", ln=True, align="C", fill=True)
    pdf.ln(6)

    # Parcurgem secțiunile
    for sec_name, df_sec in export_frames.items():
        # Titlu secțiune
        pdf.set_font_size(10)
        pdf.set_text_color(90, 127, 168)
        pdf.cell(0, 6, sec_name.upper(), ln=True, align="L")
        pdf.ln(2)

        # Tabel cu două coloane: Câmp și Valoare
        col_width = [50, 140]  # lățimi în mm
        pdf.set_font_size(8)
        pdf.set_text_color(44, 74, 110)
        pdf.set_fill_color(232, 240, 248)

        # Antet tabel
        pdf.cell(col_width[0], 6, "CÂMP", border=1, align="L", fill=True)
        pdf.cell(col_width[1], 6, "VALOARE", border=1, align="L", fill=True)
        pdf.ln()

        # Rânduri date
        fill = False
        for _, row in df_sec.iterrows():
            camp = str(row.get("Camp", ""))
            valoare = str(row.get("Valoare", ""))
            # Eliminăm emoji-urile rămase
            valoare = (valoare
                .replace("🏛 ", "Dept: ").replace("🏛", "Dept: ")
                .replace("✉ ", "Email: ").replace("✉", "Email: ")
                .replace("📱 ", "Mobil: ").replace("📱", "Mobil: ")
                .replace("⭐ ", "").replace("⭐", "")
                .replace("👥 ", "").replace("👥", "")
            )
            pdf.set_fill_color(238, 244, 251) if fill else pdf.set_fill_color(255, 255, 255)
            pdf.cell(col_width[0], 6, camp, border=1, align="L", fill=fill)
            pdf.multi_cell(col_width[1], 6, valoare, border=1, align="L", fill=fill)
            fill = not fill
        pdf.ln(2)

    # Footer
    pdf.set_y(-15)
    pdf.set_font_size(7)
    pdf.set_text_color(138, 173, 204)
    pdf.cell(0, 6, "Document generat automat — IDBDC UPT  |  Uz intern", ln=True, align="C")

    return pdf.output(dest='S').encode('latin-1')  # fpdf2 returnează bytes

# ------------------------------------------------------------
# FUNCȚII PENTRU PRINT (HTML) – neschimbată
# ------------------------------------------------------------

def _generate_print_html_from_frames(export_frames: dict, cod: str) -> str:
    html_sections = []
    for section_label, df_sec in export_frames.items():
        if df_sec.empty:
            continue
        camp_col = "Camp" if "Camp" in df_sec.columns else df_sec.columns[0]
        max_len = max((len(str(v)) for v in df_sec[camp_col]), default=10)
        col1_px = min(300, max(120, max_len * 7 + 16))
        rows_html = ""
        for r_idx, (_, row) in enumerate(df_sec.iterrows()):
            bg = "#f8f8f8" if r_idx % 2 == 0 else "#ffffff"
            camp_val = _html.escape(str(row.get(camp_col, "")))
            val_val = _html.escape(str(row.get(df_sec.columns[1], ""))) if len(df_sec.columns) > 1 else ""
            rows_html += (
                f"<tr style='background:{bg};'>"
                f"<td style='width:{col1_px}px;font-weight:600;color:#2c4a6e;white-space:nowrap;'>{camp_val}</td>"
                f"<td style='color:#000000;'>{val_val}</td>"
                f"</tr>"
            )
        tbl_html = (
            f"<table style='border-collapse:collapse;width:100%;margin-bottom:16px;'>"
            f"<thead>"
            f"<th style='width:{col1_px}px;background:#e8f0f8;text-align:left;'>{_html.escape(camp_col)}</th>"
            f"<th style='background:#e8f0f8;text-align:left;'>{_html.escape(df_sec.columns[1] if len(df_sec.columns) > 1 else '')}</th>"
            f"</thead><tbody>{rows_html}</tbody>"
            f"</tr>"
        )
        html_sections.append(f"<h3>{_html.escape(section_label)}</h3>{tbl_html}")

    titlu_html = f"""
    <div style="background-color: #ffffff; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #cccccc; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <h2 style="color: #000000; margin: 0; font-weight: 700;">Fișă — {_html.escape(cod)}</h2>
    </div>
    """

    full_html = f"""<html><head><meta charset="utf-8"/>
    <style>
    body{{font-family:Arial;padding:20px;font-size:11px; background-color: #ffffff;}}
    h3{{color:#0b2a52;margin-top:20px;font-size:13px;}}
    table{{border-collapse:collapse;width:100%;margin-bottom:16px;}}
    th,td{{border:1px solid #ccc;padding:5px;font-size:11px;vertical-align:top;}}
    th{{background:#e8f0f8;font-weight:700;}}
    @media print{{button{{display:none;}}}}
    </style></head><body>
    <button onclick="window.print()">Print</button>
    {titlu_html}
    {"".join(html_sections)}</body></html>"""
    return full_html

def _build_section_export_df(rows: list, table: str = None,
                              tabela_baza_ctx: str = None) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    priority_set = {c: i for i, c in enumerate(CARD_PRIORITY)}
    is_contract_ctx = (tabela_baza_ctx or table or "") in _TABELE_CONTRACTE
    extra_hidden = _COLS_EXCLUDE_CONTRACTE if is_contract_ctx else set()
    all_items = []
    for row in rows:
        visible_cols = [
            c for c in row.keys()
            if c not in COLS_HIDDEN_FISA
            and c not in extra_hidden
            and row[c] is not None
            and str(row[c]).strip() not in ("", "None", "nan")
        ]
        if table == "com_aspecte_tehnice":
            ordered = [c for c in TEHNIC_COL_ORDER if c in visible_cols]
            rest = sorted([c for c in visible_cols if c not in TEHNIC_COL_ORDER],
                          key=lambda c: (priority_set.get(c, 999), c))
            visible_cols = ordered + rest
        else:
            visible_cols.sort(key=lambda c: (priority_set.get(c, 999), c))
        for c in visible_cols:
            raw_val = row[c]
            numeric_val = _to_float_if_numeric(raw_val)
            val_str = _fmt_numeric(raw_val, c) if numeric_val is not None else str(raw_val)
            all_items.append({"Camp": _col_label(c, table), "Valoare": val_str})
    return pd.DataFrame(all_items) if all_items else pd.DataFrame()

def _build_echipa_export_rows(rows_ech: list, supabase: Client) -> pd.DataFrame:
    persoane_cont = [r for r in rows_ech if _is_persoana_contact(r)]
    membri = sorted([r for r in rows_ech if not _is_persoana_contact(r)],
                    key=lambda r: str(r.get("nume_prenume") or ""))
    contact_parts = []
    for r in persoane_cont:
        nume = str(r.get("nume_prenume") or "").strip()
        rol = str(r.get("rol") or r.get("functia_specifica") or "").strip()
        txt = ", ".join(p for p in [nume, rol] if p)
        contact = _get_contact_info(supabase, nume)
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
    return pd.DataFrame([
        {"Camp": "Persoana de contact", "Valoare": val_contact},
        {"Camp": "Membrii echipei", "Valoare": val_membri},
    ])

# ------------------------------------------------------------
# FUNCȚIA PRINCIPALĂ
# ------------------------------------------------------------

def render_fisa_completa(supabase: Client):
    st.markdown("## 📄 Fișă completă")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.88);font-size:1.02rem;font-weight:600;"
        "margin-bottom:0.85rem;'>Introduceți codul și consultați toate informațiile asociate.</div>",
        unsafe_allow_html=True,
    )
    c1, c2, _ = st.columns([1.2, 0.5, 3.3])
    with c1:
        cod = st.text_input(
            "Cod identificare", value="", key="fisa_cod",
            placeholder="Ex: 998877 sau 26FDI26",
        ).strip()
    cod_found = False
    tabela_gasita = None
    if cod and len(cod) >= 3:
        for t in ALL_BASE_TABLES:
            rows_check = _safe_select_eq(supabase, t, "cod_identificare", cod, limit=1)
            if rows_check:
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
    if cod_found:
        st.markdown(
            "<div style='background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.45);"
            "border-radius:10px;padding:7px 14px;margin-bottom:4px;display:inline-block;'>"
            "<span style='color:#4ade80;font-weight:700;font-size:0.92rem;'>"
            "✅ Înregistrarea este confirmată — fișa este disponibilă și pregătită pentru consultare."
            "</span></div>",
            unsafe_allow_html=True,
        )
    if not cod_found:
        st.markdown(
            "<div style='background:rgba(255,100,100,0.15);border:1px solid rgba(255,100,100,0.60);"
            "border-radius:10px;padding:7px 14px;margin-bottom:4px;display:inline-block;'>"
            "<span style='color:#ff8888;font-weight:700;font-size:0.92rem;'>"
            "❌ Codul introdus nu a fost găsit în baza de date."
            "</span></div>",
            unsafe_allow_html=True,
        )
        return
    st.divider()
    titlu_fisa = TABLE_LABELS.get(tabela_gasita, "Fișă")
    titlu_fisa_curat = titlu_fisa.split(" ", 1)[-1] if " " in titlu_fisa else titlu_fisa
    st.markdown(
        f"<div style='color:#ffffff;font-size:1.35rem;font-weight:900;"
        f"letter-spacing:0.03em;margin-bottom:1rem;'>"
        f"INFORMAȚII {titlu_fisa_curat.upper()}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    _p1, _p2, _p3, _p4, _lbl = st.columns([0.7, 0.7, 0.7, 0.7, 5.2])
    with _p1:
        pin_gen = st.checkbox("Generale", key=f"fisa_pin_{cod}_generale")
    with _p2:
        pin_fin = st.checkbox("Financiar", key=f"fisa_pin_{cod}_financiar")
    with _p3:
        pin_ech = st.checkbox("Echipă", key=f"fisa_pin_{cod}_echipa")
    with _p4:
        pin_teh = st.checkbox("Tehnic", key=f"fisa_pin_{cod}_tehnic")
    with _lbl:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.45);font-size:0.875rem;padding-top:6px;"
            "font-style:italic;'>Bifează o secțiune pentru a afișa informațiile existente în aceasta.</div>",
            unsafe_allow_html=True,
        )
    sectiuni_active = []
    if pin_gen:
        sectiuni_active.append(("Generale", tabela_gasita, "generale"))
    if pin_fin:
        sectiuni_active.append(("Financiar", "com_date_financiare", "financiar"))
    if pin_ech:
        sectiuni_active.append(("Echipa", "com_echipe_proiect", "echipa"))
    if pin_teh:
        sectiuni_active.append(("Tehnic", "com_aspecte_tehnice", "tehnic"))
    if sectiuni_active:
        st.markdown(
            "<div style='background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.15);"
            "border-radius:14px;padding:14px 20px 6px 20px;margin-top:12px;'>",
            unsafe_allow_html=True,
        )
        for idx, (sec_label, sec_table, sec_key) in enumerate(sectiuni_active):
            if idx > 0:
                st.markdown(
                    "<div style='height:18px;border-top:1px solid rgba(255,255,255,0.12);"
                    "margin:8px 0 10px 0;'></div>",
                    unsafe_allow_html=True,
                )
            if sec_key == "echipa":
                st.markdown(
                    f"<div style='color:rgba(255,255,255,0.45);font-size:0.74rem;font-weight:800;"
                    f"text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px;'>"
                    f"{_html.escape(sec_label)}</div>",
                    unsafe_allow_html=True,
                )
                rows = _safe_select_eq(supabase, sec_table, "cod_identificare", cod, limit=2000)
                if not rows:
                    st.info("Nu există membri echipă pentru acest contract.")
                else:
                    _render_echipa_compact(rows, cod_ctx=cod, supabase=supabase)
            else:
                rows = _safe_select_eq(supabase, sec_table, "cod_identificare", cod, limit=50)
                if not rows:
                    st.info(f"Nu există informații pentru secțiunea {sec_label}.")
                else:
                    _render_sectiune_tabel(sec_label, rows, sec_table, tabela_baza_ctx=tabela_gasita)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown(
        "<div style='color:rgba(255,255,255,0.75);font-size:0.90rem;font-weight:700;"
        "margin-bottom:6px;'>📤 Export fișă</div>",
        unsafe_allow_html=True,
    )
    if not _render_export_auth_tab1(supabase):
        return

    # Export CSV și Excel (orizontal, din platformă)
    export_data_horizontal = _build_horizontal_export_data(supabase, cod, tabela_gasita)
    if not export_data_horizontal["headers"]:
        st.info("Nu există date de exportat pentru acest cod.")
        return

    csv_df = pd.DataFrame([export_data_horizontal["values"]], columns=export_data_horizontal["headers"])
    csv_bytes = csv_df.to_csv(index=False).encode("utf-8-sig")

    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
        df_export = pd.DataFrame([export_data_horizontal["values"]], columns=export_data_horizontal["headers"])
        df_export.to_excel(writer, index=False, sheet_name="Fisa completa")
    excel_buf.seek(0)

    # Construim frame-urile pentru PDF și Print (vertical)
    export_frames = {}
    rows_gen = _safe_select_eq(supabase, tabela_gasita, "cod_identificare", cod, limit=50)
    if rows_gen:
        df_gen = _build_section_export_df(rows_gen, tabela_gasita, tabela_baza_ctx=tabela_gasita)
        if not df_gen.empty:
            export_frames["Generale"] = df_gen

    for com_label, com_table in [("Financiar", "com_date_financiare"), ("Tehnic", "com_aspecte_tehnice")]:
        rows_com = _safe_select_eq(supabase, com_table, "cod_identificare", cod, limit=50)
        if rows_com:
            df_com = _build_section_export_df(rows_com, com_table, tabela_baza_ctx=tabela_gasita)
            if not df_com.empty:
                export_frames[com_label] = df_com

    rows_ech = _safe_select_eq(supabase, "com_echipe_proiect", "cod_identificare", cod, limit=2000)
    if rows_ech:
        df_ech = _build_echipa_export_rows(rows_ech, supabase)
        if not df_ech.empty:
            export_frames["Echipa"] = df_ech

    _SECTIUNI_ORDINE = ["Generale", "Financiar", "Echipa", "Tehnic"]
    export_frames = {k: export_frames[k] for k in _SECTIUNI_ORDINE if k in export_frames}

    # Butoane de export
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.download_button("⬇️ CSV", data=csv_bytes, file_name=f"fisa_{cod}.csv", mime="text/csv", key="fisa_csv")
    with col2:
        st.download_button("⬇️ Excel", data=excel_buf, file_name=f"fisa_{cod}.xlsx",
                          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="fisa_xlsx")
    with col3:
        pdf_bytes = _generate_pdf_from_frames(export_frames, cod)
        if pdf_bytes:
            st.download_button("⬇️ PDF", data=pdf_bytes, file_name=f"fisa_{cod}.pdf", mime="application/pdf", key="fisa_pdf")
        else:
            st.button("⬇️ PDF", disabled=True, help="PDF indisponibil - verificați fpdf2")
    with col4:
        if st.button("🖨️ Print", key="fisa_print"):
            print_html = _generate_print_html_from_frames(export_frames, cod)
            components.html(print_html, height=700, scrolling=True)
