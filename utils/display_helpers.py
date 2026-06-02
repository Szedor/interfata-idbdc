# =========================================================
# utils/display_helpers.py
# VERSIUNE: 2.0
# STATUS: ACTUALIZAT - câmpuri compuse DEPARTAMENT și TELEFON
# DATA: 2026.05.09
# =========================================================
# MODIFICĂRI VERSIUNEA 2.0:
#   - get_contact_info returnează acum DEPARTAMENT ca
#     "acronim - denumire" și TELEFON ca "mobil / fix",
#     conform mapării definitive contracte_cep.
#   - col_label folosește COL_LABELS_PER_TABLE cu fallback
#     la COL_LABELS global.
#   - COLS_HIDDEN_FISA extins cu câmpurile de audit și
#     câmpurile componente ale câmpurilor compuse.
# =========================================================

import streamlit as st
import pandas as pd
import html as _html
from utils.display_config import (
    COL_LABELS, COL_LABELS_PER_TABLE, CARD_PRIORITY,
    _TABELE_CONTRACTE, _COLS_EXCLUDE_CONTRACTE,
    COLS_HIDDEN_FISA, TEHNIC_COL_ORDER,
)
from utils.date_helpers import to_date, calc_durata, add_months, sub_months
from utils.supabase_helpers import safe_select_eq


def fmt_numeric(val, col_name: str = "") -> str:
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


def col_label(col: str, table: str = None) -> str:
    if table and table in COL_LABELS_PER_TABLE:
        if col in COL_LABELS_PER_TABLE[table]:
            return COL_LABELS_PER_TABLE[table][col]
    return COL_LABELS.get(col, col.replace("_", " ").capitalize())


def get_visible_ordered_fields(row: dict, table: str, tabela_baza_ctx: str = None) -> list:
    is_contract_ctx = (tabela_baza_ctx or table or "") in _TABELE_CONTRACTE
    extra_hidden = _COLS_EXCLUDE_CONTRACTE if is_contract_ctx else set()
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
        return ordered + rest
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
        return ordered + rest
    elif (tabela_baza_ctx or table or "") == "base_proiecte_fdi":
        COL_ORDER_FDI = [
            "denumire_categorie",
            "acronim_tip_proiecte",
            "cod_identificare",
            "titlul_proiect",
            "acronim_proiect",
            "data_inceput",
            "data_sfarsit",
            "durata",
            "status_contract_proiect",
            "program",
            "cod_domeniu_fdi",
            "cod_temporar",
        ]
        ordered = [c for c in COL_ORDER_FDI if c in visible_cols]
        rest = [c for c in visible_cols if c not in COL_ORDER_FDI]
        return ordered + rest
    elif (tabela_baza_ctx or table or "") == "base_proiecte_see":
        COL_ORDER_SEE = [
            "denumire_categorie", "acronim_tip_proiecte", "cod_identificare",
            "titlul_proiect", "acronim_proiect",
            "data_inceput", "data_sfarsit", "durata",
            "status_contract_proiect",
            "numar_participanti", "denumire_participanti",
            "rol_upt", "identificare_apel", "data_inchidere_apel",
            "mecanism_finantare", "program_finantare",
            "sector_prioritar_specific", "domeniul", "website",
            # observatii exclus — vizibil doar în Calea2
        ]
        ordered = [c for c in COL_ORDER_SEE if c in visible_cols]
        rest = [c for c in visible_cols if c not in COL_ORDER_SEE]
        return ordered + rest
    elif (tabela_baza_ctx or table or "") == "base_proiecte_interreg":
        COL_ORDER_INTERREG = [
            "denumire_categorie", "acronim_tip_proiecte", "cod_identificare",
            "titlul_proiect", "acronim_proiect",
            "data_inceput", "data_sfarsit", "durata",
            "status_contract_proiect",
            "numar_participanti", "denumire_participanti",
            "rol_upt", "identificare_apel", "data_inchidere_apel",
            "program_finantare", "prioritatea_programului", "obiectivul",
            "website",
            # observatii exclus — vizibil doar în Calea2
        ]
        ordered = [c for c in COL_ORDER_INTERREG if c in visible_cols]
        rest = [c for c in visible_cols if c not in COL_ORDER_INTERREG]
        return ordered + rest
    elif (tabela_baza_ctx or table or "") == "base_proiecte_internationale":
        # Ordinea exactă din mapare — coloane tehnice în ordinea etichetelor vizuale
        COL_ORDER_INT = [
            "denumire_categorie",
            "acronim_tip_proiecte",
            "cod_identificare",
            "titlul_proiect",
            "acronim_proiect",
            "data_inceput",
            "data_sfarsit",
            "durata",
            "status_contract_proiect",
            "scor_evaluare",
            "numar_participanti",
            "denumire_participanti",
            "rol_upt",
            "identificare_apel",
            "data_inchidere_apel",
            "program_finantare",
            "tema_topic",
            "schema_de_finantare",
            "website",
            # observatii exclus — vizibil doar în Calea2
        ]
        ordered = [c for c in COL_ORDER_INT if c in visible_cols]
        rest = [c for c in visible_cols if c not in COL_ORDER_INT]
        return ordered + rest
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
        return ordered + rest


def get_contact_info(supabase, nume: str) -> list:
    """
    Returnează lista de informații de contact pentru un membru al echipei.
    Câmpuri compuse conform mapării definitive:
      DEPARTAMENT = acronim_departament + denumire_departament
      TELEFON     = telefon_mobil + telefon_fix
    """
    if not supabase or not nume:
        return []
    try:
        res = supabase.table("det_resurse_umane") \
            .select("email,telefon_mobil,telefon_fix,acronim_departament") \
            .eq("nume_prenume", nume.strip()).limit(1).execute()
        if not res.data:
            res = supabase.table("det_resurse_umane") \
                .select("email,telefon_mobil,telefon_fix,acronim_departament") \
                .ilike("nume_prenume", nume.strip()).limit(1).execute()
        if not res.data:
            return []
        d = res.data[0]
        out = []

        # DEPARTAMENT = acronim + denumire
        acronim = str(d.get("acronim_departament") or "").strip()
        if acronim:
            try:
                dep_res = supabase.table("nom_departament") \
                    .select("denumire_departament") \
                    .eq("acronim_departament", acronim).limit(1).execute()
                den = str(dep_res.data[0].get("denumire_departament") or "").strip() if dep_res.data else ""
                dept_label = f"{acronim} - {den}" if den else acronim
            except Exception:
                dept_label = acronim
            out.append(f"Dept: {dept_label}")

        # EMAIL
        email = str(d.get("email") or "").strip()
        if email:
            out.append(f"Email: {email}")

        # TELEFON = mobil / fix
        mob = str(d.get("telefon_mobil") or "").strip()
        fix = str(d.get("telefon_fix") or "").strip()
        if mob and fix:
            out.append(f"Telefon: {mob} / {fix}")
        elif mob:
            out.append(f"Telefon: {mob}")
        elif fix:
            out.append(f"Telefon: {fix}")

        return out
    except Exception:
        return []


def is_persoana_contact(r: dict) -> bool:
    v = r.get("persoana_contact")
    return v is True or str(v).strip().upper() in ("TRUE", "DA", "1")
