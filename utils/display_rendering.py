# =========================================================
# utils/display_rendering.py
# VERSIUNE: 2.3
# STATUS: CORECTAT - Spargere automată rânduri pentru enumerări instituții
# DATA: 2026.06.08
# =========================================================

import streamlit as st
import html as _html
import re as _re
from utils.display_config import (
    CARD_PRIORITY, _TABELE_CONTRACTE, _COLS_EXCLUDE_CONTRACTE,
    COLS_HIDDEN_FISA, TEHNIC_COL_ORDER
)
from utils.display_helpers import col_label, fmt_numeric, get_contact_info, is_persoana_contact
from utils.supabase_helpers import safe_select_eq

_COLS_HIDDEN_CAL1 = COLS_HIDDEN_FISA | {
    "observatii",
    "creat_de", "creat_la", "modificat_de", "modificat_la",
}

_COL_ORDER_FDI = [
    "denumire_categorie", "acronim_tip_proiecte", "cod_identificare",
    "titlul_proiect", "acronim_proiect",
    "data_inceput", "data_sfarsit", "durata",
    "status_contract_proiect", "program", "cod_domeniu_fdi", "cod_temporar",
]

_COL_ORDER_EV_ST = [
    "denumire_categorie",
    "cod_identificare",
    "titlul_eveniment",
    "data_inceput",
    "data_sfarsit",
    "format_eveniment",
    "loc_desfasurare",
    "institutii_organizatoare",
    "natura_eveniment",
    "cotatie_eveniment",
    "website",
]

_COL_ORDER_PI = [
    "denumire_categorie",
    "acronim_prop_industr",
    "denumire_prop_industr",
    "titlul_proprietatii",
    "cod_identificare",
    "data_depozit_cerere",
    "numar_publicare_cerere",
    "numar_oficial_acordare",
    "data_oficiala_de_acordare",
    "data_inceput_valabilitate",
    "ani_de_valabilitate",
    "data_sfarsit_valabilitate",
    "id_proiect_contract_sursa",
    "denumire_solicitant",
    "denumire_titular",
    "link_espacenet",
    "titlu_engleza_diploma",
]

_COL_ORDER_EV = [
    "denumire_categorie",
    "natura_eveniment",
    "cod_identificare",
    "titlul_eveniment",
    "data_inceput",
    "data_sfarsit",
    "format_eveniment",
    "loc_desfasurare",
    "institutii_organizare",
    "clasificare_eveniment",
    "website",
]

_COL_ORDER_PNRR = [
    "denumire_categorie", "acronim_tip_proiecte", "cod_identificare",
    "data_contract", "titlul_proiect", "acronim_proiect",
    "domeniu_cercetare",
    "data_inceput", "data_sfarsit", "durata",
    "status_contract_proiect",
    "numar_participanti", "denumire_participanti",
    "rol_upt", "identificare_apel", "data_inchidere_apel",
    "pilonul", "componenta", "investitia", "subinvestitia",
    "website",
]

_COL_ORDER_PNCDI = [
    "denumire_categorie", "acronim_tip_proiecte", "cod_identificare",
    "data_contract", "titlul_proiect", "acronim_proiect",
    "domeniu_cercetare",
    "data_inceput", "data_sfarsit", "durata",
    "status_contract_proiect",
    "numar_participanti", "denumire_participanti",
    "rol_upt", "identificare_apel", "data_inchidere_apel",
    "programul", "subprogramul", "instrument_finantare",
    "website",
]

_COL_ORDER_STRUCTURALE = [
    "denumire_categorie", "acronim_tip_proiecte", "cod_identificare",
    "titlul_proiect", "acronim_proiect",
    "data_inceput", "data_sfarsit", "durata",
    "status_contract_proiect",
    "numar_participanti", "denumire_participanti",
    "rol_upt", "identificare_apel", "data_inchidere_apel",
    "programul", "axa_specifica", "prioritatea", "obiectivul",
    "website",
]

_COL_ORDER_NONUE = [
    "denumire_categorie", "acronim_tip_proiecte", "cod_identificare",
    "titlul_proiect", "acronim_proiect",
    "data_inceput", "data_sfarsit", "durata",
    "status_contract_proiect",
    "numar_participanti", "denumire_participanti",
    "rol_upt", "identificare_apel", "data_inchidere_apel",
    "sursa_finantatoare", "categoria", "tematica",
    "operatiunea", "mecanism_financiar", "instrument_implementare",
    "website",
]

_COL_ORDER_SEE = [
    "denumire_categorie", "acronim_tip_proiecte", "cod_identificare",
    "titlul_proiect", "acronim_proiect",
    "data_inceput", "data_sfarsit", "durata",
    "status_contract_proiect",
    "numar_participanti", "denumire_participanti",
    "rol_upt", "identificare_apel", "data_inchidere_apel",
    "mecanism_finantare", "program_finantare",
    "sector_prioritar_specific", "domeniul", "website",
]

_COL_ORDER_INTERREG = [
    "denumire_categorie", "acronim_tip_proiecte", "cod_identificare",
    "titlul_proiect", "acronim_proiect",
    "data_inceput", "data_sfarsit", "durata",
    "status_contract_proiect",
    "numar_participanti", "denumire_participanti",
    "rol_upt", "identificare_apel", "data_inchidere_apel",
    "program_finantare", "prioritatea_programului", "obiectivul",
    "website",
]

_COL_ORDER_INTERNATIONALE = [
    "denumire_categorie", "acronim_tip_proiecte", "cod_identificare",
    "titlul_proiect", "acronim_proiect",
    "data_inceput", "data_sfarsit", "durata",
    "status_contract_proiect", "scor_evaluare",
    "numar_participanti", "denumire_participanti",
    "rol_upt", "identificare_apel", "data_inchidere_apel",
    "program_finantare", "tema_topic", "schema_de_finantare", "website",
]

_COL_ORDER_PROIECTE_GENERIC = [
    "denumire_categorie", "acronim_tip_proiecte", "cod_identificare",
    "titlul_proiect", "acronim_proiect",
    "data_inceput", "data_sfarsit", "durata",
    "status_contract_proiect", "program", "programul_de_finantare",
    "schema_de_finantare", "apel_pentru_propuneri", "rol_upt",
    "parteneri", "coordonator", "director_proiect",
    "cod_temporar",
]

_COL_ORDER_PER_TABLE = {
    "base_proiecte_fdi":            _COL_ORDER_FDI,
    "base_evenimente_stiintifice":  _COL_ORDER_EV_ST,
    "base_prop_industr":            _COL_ORDER_PI,
    "base_evenimente_stiintifice":  _COL_ORDER_EV,
    "base_proiecte_pnrr":           _COL_ORDER_PNRR,
    "base_proiecte_pncdi":          _COL_ORDER_PNCDI,
    "base_proiecte_structurale":    _COL_ORDER_STRUCTURALE,
    "base_proiecte_nonue":          _COL_ORDER_NONUE,
    "base_proiecte_see":            _COL_ORDER_SEE,
    "base_proiecte_interreg":       _COL_ORDER_INTERREG,
    "base_proiecte_internationale": _COL_ORDER_INTERNATIONALE,
}

_COL_ORDER_GENERALE = [
    "denumire_categorie", "acronim_tip_contract", "acronim_tip_proiecte",
    "cod_identificare",
    "data_contract", "obiectul_contractului", "denumire_beneficiar",
    "data_inceput", "data_sfarsit", "durata", "status_contract_proiect",
    "titlul_proiect", "acronim_proiect", "program", "programul_de_finantare",
    "schema_de_finantare", "apel_pentru_propuneri", "rol_upt",
    "parteneri", "coordonator", "director_proiect",
    "data_depunere", "data_depozit_cerere", "data_apel",
    "an_referinta", "an_inceput", "an_sfarsit", "durata_luni",
    "natura_eveniment", "format_eveniment", "loc_desfasurare",
    "numar_participanti", "institutii_organizare",
    "acronim_prop_intelect", "nr_cerere", "nr_brevet",
    "data_acordare", "data_oficiala_acordare", "numar_oficial_acordare",
    "inventatori", "cuvinte_cheie", "descriere",
]

_COL_ORDER_FINANCIAR = [
    "cod_identificare", "valuta",
    "valoare_contract_cep_terti_speciale",
    "valoare_anuala_contract", "valoare_totala_contract",
    "cofinantare_anuala_contract", "cofinantare_totala_contract",
    "suma_solicitata_fdi", "suma_aprobata_mec",
    "cofinantare_upt_fdi", "total_buget_proiect_fdi",
    "an_referinta", "valoare_contract_an_referinta",
    "cofinantare_contract_an_referinta",
    "valoare_totala_contract", "cofinantare_totala_contract",
    "cheltuieli_neeligibile", "costuri_totale_upt",
    "cheltuieli_eligibile", "grant_solicitat", "grant_aprobat",
    "buget_upt", "cofinantare_nationala", "cofinantare_upt",
    "costuri_totale_proiect",
    "contributie_totala_finantator",
    "costuri_totale_upt",
    "contributie_finantator",
    "costuri_eligibile_estimate_total",
    "valoare_grant_solicitat_total",
    "costuri_eligibile_estimate_upt",
    "valoare_grant_solicitat_upt",
    "cost_total_proiect", "cost_proiect_upt",
    "contributie_ue_total_proiect", "contributie_ue_proiect_upt",
]

_TABELE_PROIECTE = {
    "base_proiecte_fdi", "base_proiecte_pncdi", "base_proiecte_pnrr",
    "base_proiecte_internationale", "base_proiecte_interreg",
    "base_proiecte_noneu", "base_proiecte_see", "base_proiecte_structurale",
}


@st.cache_data(show_spinner=False, ttl=600)
def _get_domeniu_abreviere(_supabase, cod_domeniu: str) -> str:
    if not cod_domeniu:
        return ""
    try:
        res = _supabase.table("nom_domenii_fdi") \
            .select("abreviere_domeniu_fdi") \
            .eq("cod_domeniu_fdi", cod_domeniu).limit(1).execute()
        if res.data:
            return str(res.data[0].get("abreviere_domeniu_fdi") or "").strip()
    except Exception:
        pass
    return ""


def render_sectiune_tabel(section_label: str, rows: list, table: str = None,
                           tabela_baza_ctx: str = None, supabase=None):
    if not rows:
        return

    is_contract_ctx = (tabela_baza_ctx or table or "") in _TABELE_CONTRACTE
    is_proiect_ctx  = (tabela_baza_ctx or table or "") in _TABELE_PROIECTE
    extra_hidden    = _COLS_EXCLUDE_CONTRACTE if is_contract_ctx else set()

    all_items = []
    for row in rows:
        if table == "com_aspecte_tehnice":
            ordered_keys = [c for c in TEHNIC_COL_ORDER if c in row and _is_visible(row, c, extra_hidden)] + \
                           [c for c in row.keys() if c not in TEHNIC_COL_ORDER and _is_visible(row, c, extra_hidden)]
        elif table == "com_date_financiare":
            ordered_keys = [c for c in _COL_ORDER_FINANCIAR if c in row and _is_visible(row, c, extra_hidden)] + \
                           [c for c in row.keys() if c not in _COL_ORDER_FINANCIAR and _is_visible(row, c, extra_hidden)]
        elif is_proiect_ctx:
            _tbl_key = tabela_baza_ctx or table or ""
            _col_order = _COL_ORDER_PER_TABLE.get(_tbl_key, _COL_ORDER_PROIECTE_GENERIC)
            ordered_keys = [c for c in _col_order if c in row and _is_visible(row, c, extra_hidden)] + \
                           [c for c in row.keys() if c not in _col_order and _is_visible(row, c, extra_hidden)]
        else:
            ordered_keys = [c for c in _COL_ORDER_GENERALE if c in row and _is_visible(row, c, extra_hidden)] + \
                           [c for c in row.keys() if c not in _COL_ORDER_GENERALE and _is_visible(row, c, extra_hidden)]

        for c in ordered_keys:
            raw_val = row[c]
            try:
                float(str(raw_val).replace(",", ".").strip())
                is_num = True
            except (ValueError, TypeError):
                is_num = False
            val_str = fmt_numeric(raw_val, c) if is_num else str(raw_val)

            if c == "cod_domeniu_fdi" and supabase:
                abrev = _get_domeniu_abreviere(supabase, str(raw_val).strip())
                if abrev:
                    val_str = f"{val_str} — {abrev}"

            # ── [2] Detecție și formatare automată a enumerărilor (1., 2.) în Calea 1 ──
            # Dacă suntem pe câmpul de instituții organizatoare și avem format de tip "1. ... 2. ..."
            val_html = _html.escape(val_str)
            if c in ("institutii_organizatoare", "institutii_organizare"):
                # Înlocuim punctele-virgulă sau spațiile care preced o cifră urmată de punct cu un rând nou (<br>)
                val_html = _re.sub(r'(?:;\s*|\s+)(?=\d+\.)', '<br>', val_html)

            all_items.append((col_label(c, table or tabela_baza_ctx), val_html))

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
            f"<td style='padding:3px 0 3px 0;width:67%;vertical-align:top;'> "
            f"<span style='color:#ffffff;font-size:0.95rem;font-weight:700;'>{value}</span></td>"
            f"</tr>"
        )
    st.markdown(
        f"<table style='width:100%;border-collapse:collapse;margin-bottom:0;'>{rows_html}</table>",
        unsafe_allow_html=True,
    )


def _is_visible(row: dict, col: str, extra_hidden: set) -> bool:
    if col in _COLS_HIDDEN_CAL1:
        return False
    if col in extra_hidden:
        return False
    val = row.get(col)
    if val is None:
        return False
    if str(val).strip() in ("", "None", "nan"):
        return False
    return True


def _get_ordered(order_list, row, extra_hidden):
    ordered = [c for c in order_list if c in row and _is_visible(row, c, extra_hidden)]
    rest    = [c for c in row.keys() if c not in order_list and _is_visible(row, c, extra_hidden)]
    return ordered + rest


def render_echipa_compact(rows: list, cod_ctx: str = "", supabase=None, tabela_baza_ctx: str = ""):
    if not rows:
        st.info("Nu există echipă înregistrată pentru această fișă.")
        return

    eticheta_cod = "ID PROIECT" if tabela_baza_ctx in _TABELE_PROIECTE else "NR.CONTRACT"
    cod_id = str(rows[0].get("cod_identificare") or cod_ctx or "").strip()

    rows_sorted   = sorted(rows, key=lambda r: (0 if is_persoana_contact(r) else 1,
                                                str(r.get("nume_prenume") or "")))
    persoane_cont = [r for r in rows_sorted if is_persoana_contact(r)]
    membri        = [r for r in rows_sorted if not is_persoana_contact(r)]

    def _fmt_persoana(r):
        nume    = str(r.get("nume_prenume") or "").strip()
        rol     = str(r.get("rol") or r.get("functia_specifica") or "").strip()
        contact = get_contact_info(supabase, nume) if supabase else []
        linie1  = " · ".join(p for p in [_html.escape(nume), _html.escape(rol)] if p)
        if contact:
            linie2 = "  ·  ".join(_html.escape(c) for c in contact)
            return f"{linie1}<br><span style='font-size:0.84rem;color:rgba(255,255,255,0.72);'>{linie2}</span>"
        return linie1

    def _fmt_membru(r):
        nume = str(r.get("nume_prenume") or "").strip()
        rol  = str(r.get("rol") or r.get("functia_specifica") or "").strip()
        parts = [_html.escape(p) for p in [nume, rol] if p]
        return " · ".join(parts)

    randuri = []

    if cod_id:
        randuri.append((eticheta_cod, _html.escape(cod_id)))

    if persoane_cont:
        val_pc = "<br>".join(_fmt_persoana(r) for r in persoane_cont)
        randuri.append(("⭐ PERSOANĂ DE CONTACT", val_pc))

    if membri:
        PREVIEW = 6
        show_all_key = f"echipa_show_all_{cod_ctx or id(rows)}"
        if show_all_key not in st.session_state:
            st.session_state[show_all_key] = False

        membri_display = membri if st.session_state[show_all_key] else membri[:PREVIEW]
        val_m = "  ·  ".join(_fmt_membru(r) for r in membri_display if _fmt_membru(r))
        randuri.append((f"👥 MEMBRII ECHIPEI ({len(membri)})", val_m))

    if not randuri:
        return

    total = len(randuri)
    rows_html = ""
    for i, (eticheta_camp, valoare) in enumerate(randuri):
        sec_cell = ""
        if i == 0:
            sec_cell = (
                f"<td rowspan='{total}' style='vertical-align:top;padding:6px 10px 6px 0;width:10%;'>"
                f"<span style='color:rgba(255,255,255,0.45);font-size:0.74rem;font-weight:800;"
                f"text-transform:uppercase;letter-spacing:0.07em;white-space:nowrap;'>Echipa</span></td>"
            )
        rows_html += (
            f"<tr>{sec_cell}"
            f"<td style='padding:3px 12px 3px 0;width:23%;vertical-align:top inferiority;'>"
            f"<span style='color:rgba(255,255,255,0.50);font-size:0.76rem;font-weight:700;"
            f"text-transform:uppercase;letter-spacing:0.04em;'>{eticheta_camp}</span></td>"
            f"<td style='padding:3px 0 3px 0;width:67%;vertical-align:top;'>"
            f"<span style='color:#ffffff;font-size:0.95rem;font-weight:700;'>{valoare}</span></td>"
            f"</tr>"
        )

    st.markdown(
        f"<table style='width:100%;border-collapse:collapse;margin-bottom:8px;'>{rows_html}</table>",
        unsafe_allow_html=True,
    )

    if membri:
        PREVIEW = 6
        show_all_key = f"echipa_show_all_{cod_ctx or id(rows)}"
        if len(membri) > PREVIEW:
            if st.session_state[show_all_key]:
                if st.button("▲ Restrânge lista", key=f"echipa_collapse_{cod_ctx or id(rows)}"):
                    st.session_state[show_all_key] = False
                    st.rerun()
            else:
                ramasi = len(membri) - PREVIEW
                if st.button(f"▼ Arată toți cei {len(membri)} membri  (+{ramasi} ascunși)",
                             key=f"echipa_expand_{cod_ctx or id(rows)}"):
                    st.session_state[show_all_key] = True
                    st.rerun()
