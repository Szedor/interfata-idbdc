# =========================================================
# IDBDC/domenii/proprietate_industriala/baza.py
# VERSIUNE: 2.0
# STATUS: RESTRUCTURAT - layout pe rânduri conform mapare
# DATA: 2026.06.09
# =========================================================
# MODIFICĂRI VERSIUNEA 2.0:
#   - Adăugat titlu secțiune "📋 Date de bază" înainte de câmpuri
#   - Layout reorganizat pe rânduri exacte din mapare:
#     R1: ACRONIM TIP PROPRIETATE(25%) | DENUMIRE(50%) | NR.INREG(25%)
#     R2: TITLUL PROPRIETATII (100%)
#     R3: DATA DEPOZIT(25%) | NR.PUBLICARE(25%) | DATA ACORDARE(25%) | NR.ACORDARE(25%)
#     R4: DATA INCEPUT VAL(25%) | DURATA VAL auto(25%) | DATA SFARSIT VAL auto(25%) | ID SURSA(25%)
#     R5: DENUMIRE TITULAR(33%) | DENUMIRE SOLICITANT(33%) | LINK ESPACENET(33%)
#     R6: TITLU ENGLEZA DIPLOMA (100%)
#   - DURATA DE VALABILITATE preluata automat din nom_prop_industr
#   - DATA SFARSIT VALABILITATE calculata automat
#   - Adăugat titlu secțiune "🔒 Date suplimentare" înainte de câmpuri
#   - Layout Date suplimentare reorganizat:
#     R1: NR.NOTIF.INTERNA(25%) | DOC.OFICIAL(50%) | STATUS DOC(25%)
#     R2: DOMENIU APLICARE(33%) | SPIN OFF(33%) | CONTRACT CESIUNE(33%)
#     R3: NR.AUTORI TOTAL(25%) | TITLU EPO(75%)
#     R4: NR.AUTORI UPT(25%) | TITLU FISA INVENTIEI(75%)
#     R5: COMENTARII DOCUMENT (100%)
#     R6: COMENTARII DIVERSE (100%)
# =========================================================

import streamlit as st
import pandas as pd
from datetime import date as _date
from core.helpers import to_date, fmt_date


# ── Cache nomenclatoare ────────────────────────────────────────────────

@st.cache_data(show_spinner=False, ttl=600)
def _get_tip_prop_map(_supabase):
    """Returneaza dict {acronim_prop_industr: {denumire, ani}}."""
    try:
        res = _supabase.table("nom_prop_industr") \
            .select("acronim_prop_industr,denumire_prop_industr,ani_de_valabilitate").execute()
        return {
            r["acronim_prop_industr"]: {
                "denumire": r.get("denumire_prop_industr", "") or "",
                "ani":      int(r.get("ani_de_valabilitate") or 0),
            }
            for r in (res.data or []) if r.get("acronim_prop_industr")
        }
    except Exception:
        return {}


@st.cache_data(show_spinner=False, ttl=600)
def _get_status_doc_list(_supabase):
    try:
        res = _supabase.table("nom_status_document").select("status_document").execute()
        return [r["status_document"] for r in (res.data or []) if r.get("status_document")]
    except Exception:
        return []


def _add_ani(d, ani):
    """Adauga un numar de ani la o data."""
    if not d or not ani:
        return None
    try:
        return _date(d.year + int(ani), d.month, d.day)
    except (ValueError, TypeError):
        return None


# ── SECTIUNEA 1: DATE DE BAZA ──────────────────────────────────────────

def render_generale(supabase, cod_introdus, cat_sel, tabela_nume, is_new, date_existente):
    tip_prop_map = _get_tip_prop_map(supabase)
    tip_list     = [""] + sorted(tip_prop_map.keys())

    key_tip = f"pi_tip_{cod_introdus}"

    if key_tip not in st.session_state:
        st.session_state[key_tip] = date_existente.get("acronim_prop_industr", "") or ""

    # ── Titlu secțiune ─────────────────────────────────────────────────
    st.markdown(
        "<div style='color:rgba(255,255,255,0.70);font-size:0.95rem;font-weight:800;"
        "text-transform:uppercase;letter-spacing:0.05em;margin-bottom:10px;"
        "border-bottom:1px solid rgba(255,255,255,0.20);padding-bottom:6px;'>"
        "📋 Date de bază</div>",
        unsafe_allow_html=True,
    )

    # ── R1: ACRONIM TIP(25%) | DENUMIRE(50%) | NR.INREG(25%) ──────────
    col_tip, col_den, col_cod = st.columns([25, 50, 25])
    with col_tip:
        idx_tip = tip_list.index(st.session_state[key_tip]) \
                  if st.session_state[key_tip] in tip_list else 0
        tip_ales = st.selectbox(
            "🔖 ACRONIM TIP PROPRIETATE",
            options=tip_list,
            index=idx_tip,
            key=key_tip,
        )
    tip_info = tip_prop_map.get(tip_ales, {"denumire": "", "ani": 0}) if tip_ales else {"denumire": "", "ani": 0}
    den_auto = tip_info["denumire"]
    ani_auto = tip_info["ani"]

    with col_den:
        st.text_input(
            "DENUMIRE PROPRIETATE INDUSTRIALA",
            value=den_auto,
            disabled=True,
            key=f"pi_den_display_{cod_introdus}",
        )
    with col_cod:
        st.text_input(
            "NR.INREGISTRARE CERERE",
            value=cod_introdus,
            disabled=True,
            key=f"pi_cod_{cod_introdus}",
        )

    # ── R2: TITLUL PROPRIETATII (100%) ─────────────────────────────────
    titlu = st.text_input(
        "TITLUL PROPRIETATII",
        value=date_existente.get("titlul_proprietatii", "") or "",
        key=f"pi_titlu_{cod_introdus}",
    )

    # ── R3: DATA DEPOZIT(25%) | NR.PUBLICARE(25%) | DATA ACORDARE(25%) | NR.ACORDARE(25%) ──
    col_d1, col_n1, col_d2, col_n2 = st.columns([25, 25, 25, 25])
    with col_d1:
        data_depozit = st.date_input(
            "📅 DATA DEPOZIT CERERE",
            value=to_date(date_existente.get("data_depozit_cerere")),
            format="YYYY-MM-DD",
            key=f"pi_data_dep_{cod_introdus}",
        )
    with col_n1:
        nr_publicare = st.text_input(
            "NR.PUBLICARE CERERE",
            value=str(date_existente.get("numar_publicare_cerere") or ""),
            key=f"pi_nr_pub_{cod_introdus}",
        )
    with col_d2:
        data_acordare = st.date_input(
            "📅 DATA OFICIALA DE ACORDARE",
            value=to_date(date_existente.get("data_oficiala_de_acordare")),
            format="YYYY-MM-DD",
            key=f"pi_data_ac_{cod_introdus}",
        )
    with col_n2:
        nr_acordare = st.text_input(
            "NR.OFICIAL DE ACORDARE",
            value=str(date_existente.get("numar_oficial_acordare") or ""),
            key=f"pi_nr_ac_{cod_introdus}",
        )

    # ── R4: DATA INCEPUT VAL(25%) | DURATA(25%) | DATA SFARSIT VAL(25%) | ID SURSA(25%) ──
    col_iv, col_dur, col_sv, col_sursa = st.columns([25, 25, 25, 25])
    with col_iv:
        data_inceput_val = st.date_input(
            "📅 DATA INCEPUT VALABILITATE",
            value=to_date(date_existente.get("data_inceput_valabilitate")),
            format="YYYY-MM-DD",
            key=f"pi_data_iv_{cod_introdus}",
        )
    with col_dur:
        # Prioritate: durata din nomenclator (pe baza acronim selectat)
        # Fallback: valoarea existenta in BD
        ani_bd = int(date_existente.get("ani_de_valabilitate") or 0)
        ani_display = ani_auto if ani_auto > 0 else ani_bd
        st.text_input(
            "DURATA DE VALABILITATE (ani)",
            value=str(ani_display) if ani_display else "",
            disabled=True,
            key=f"pi_ani_val_display_{cod_introdus}",
        )
    with col_sv:
        data_sfarsit_val = _add_ani(data_inceput_val, ani_display)
        sf_str = fmt_date(data_sfarsit_val) or ""
        st.text_input(
            "📅 DATA SFARSIT VALABILITATE",
            value=sf_str,
            disabled=True,
            key=f"pi_data_sv_{cod_introdus}",
        )
    with col_sursa:
        id_sursa = st.text_input(
            "ID PROIECT SURSA/CONTRACT",
            value=date_existente.get("id_proiect_contract_sursa", "") or "",
            key=f"pi_id_sursa_{cod_introdus}",
        )

    # ── R5: DENUMIRE TITULAR(33%) | DENUMIRE SOLICITANT(33%) | LINK ESPACENET(33%) ──
    col_tit, col_sol, col_link = st.columns([33, 33, 33])
    with col_tit:
        titular = st.text_input(
            "DENUMIRE TITULAR",
            value=date_existente.get("denumire_titular", "") or "",
            key=f"pi_titular_{cod_introdus}",
        )
    with col_sol:
        solicitant = st.text_input(
            "DENUMIRE SOLICITANT",
            value=date_existente.get("denumire_solicitant", "") or "",
            key=f"pi_solicitant_{cod_introdus}",
        )
    with col_link:
        link_esp = st.text_input(
            "LINK ESPACENET",
            value=date_existente.get("link_espacenet", "") or "",
            key=f"pi_link_{cod_introdus}",
        )

    # ── R6: TITLU ENGLEZA DIPLOMA (100%) ───────────────────────────────
    titlu_en = st.text_input(
        "TITLU ENGLEZA DIPLOMA",
        value=date_existente.get("titlu_engleza_diploma", "") or "",
        key=f"pi_titlu_en_{cod_introdus}",
    )

    def _str(v):
        return str(v).strip() if v else None

    return {
        "cod_identificare":          cod_introdus,
        "denumire_categorie":        cat_sel,
        "acronim_prop_industr":      tip_ales if tip_ales else None,
        "denumire_prop_industr":     den_auto if den_auto else None,
        "titlul_proprietatii":       _str(titlu),
        "data_depozit_cerere":       fmt_date(data_depozit),
        "numar_publicare_cerere":    _str(nr_publicare),
        "numar_oficial_acordare":    _str(nr_acordare),
        "data_oficiala_de_acordare": fmt_date(data_acordare),
        "data_inceput_valabilitate": fmt_date(data_inceput_val),
        "ani_de_valabilitate":       int(ani_display) if ani_display else None,
        "data_sfarsit_valabilitate": sf_str if sf_str else None,
        "id_proiect_contract_sursa": _str(id_sursa),
        "denumire_solicitant":       _str(solicitant),
        "denumire_titular":          _str(titular),
        "link_espacenet":            _str(link_esp),
        "titlu_engleza_diploma":     _str(titlu_en),
    }


# ── SECTIUNEA 2: DATE SUPLIMENTARE (numai Calea2) ─────────────────────

def render_suplimentare(supabase, cod_introdus, tabela_nume, is_new, date_existente):
    status_doc_list = _get_status_doc_list(supabase)

    # ── Titlu secțiune ─────────────────────────────────────────────────
    st.markdown(
        "<div style='color:rgba(255,255,255,0.70);font-size:0.95rem;font-weight:800;"
        "text-transform:uppercase;letter-spacing:0.05em;margin-bottom:10px;"
        "border-bottom:1px solid rgba(255,255,255,0.20);padding-bottom:6px;'>"
        "🔒 Date suplimentare</div>",
        unsafe_allow_html=True,
    )

    # ── R1: NR.NOTIF.INTERNA(25%) | DOC.OFICIAL(50%) | STATUS DOC(25%) ──
    col_r1a, col_r1b, col_r1c = st.columns([25, 50, 25])
    with col_r1a:
        nr_notif = st.text_input(
            "NR.SI DATA DE NOTIFICARE INTERNA",
            value=date_existente.get("numar_data_notificare_intern", "") or "",
            key=f"pi_nr_notif_{cod_introdus}",
        )
    with col_r1b:
        doc_oficial = st.text_input(
            "DOCUMENT OFICIAL ORIGINAL",
            value=date_existente.get("document_oficial_original", "") or "",
            key=f"pi_doc_of_{cod_introdus}",
        )
    with col_r1c:
        status_val = date_existente.get("status_document", "") or ""
        opts_status = [""] + status_doc_list
        idx_status = opts_status.index(status_val) if status_val in opts_status else 0
        status_doc = st.selectbox(
            "🔖 STATUS DOCUMENT",
            options=opts_status,
            index=idx_status,
            key=f"pi_status_doc_{cod_introdus}",
        )

    # ── R2: DOMENIU APLICARE(33%) | SPIN OFF(33%) | CONTRACT CESIUNE(33%) ──
    col_r2a, col_r2b, col_r2c = st.columns([33, 33, 33])
    with col_r2a:
        domeniu_apl = st.text_input(
            "DOMENIU APLICARE",
            value=date_existente.get("domeniu_aplicare", "") or "",
            key=f"pi_dom_apl_{cod_introdus}",
        )
    with col_r2b:
        spin_off = st.text_input(
            "SPIN OFF",
            value=date_existente.get("spin_off", "") or "",
            key=f"pi_spin_{cod_introdus}",
        )
    with col_r2c:
        contract_ces = st.text_input(
            "CONTRACT CESIUNE INVENTATORI EXTERNI",
            value=date_existente.get("contract_cesiune_inventatori_externi", "") or "",
            key=f"pi_contract_ces_{cod_introdus}",
        )

    # ── R3: NR.AUTORI TOTAL(25%) | TITLU EPO(75%) ──────────────────────
    col_r3a, col_r3b = st.columns([25, 75])
    with col_r3a:
        nr_autori_total = st.number_input(
            "🔢 NUMAR AUTORI TOTAL",
            min_value=0,
            value=int(date_existente.get("numar_autori_total") or 0),
            key=f"pi_aut_total_{cod_introdus}",
        )
    with col_r3b:
        titlu_epo = st.text_input(
            "TITLU ENGLEZA EPO",
            value=date_existente.get("titlu_engleza_epo", "") or "",
            key=f"pi_titlu_epo_{cod_introdus}",
        )

    # ── R4: NR.AUTORI UPT(25%) | TITLU FISA INVENTIEI(75%) ────────────
    col_r4a, col_r4b = st.columns([25, 75])
    with col_r4a:
        nr_autori_upt = st.number_input(
            "🔢 NUMAR AUTORI UPT",
            min_value=0,
            value=int(date_existente.get("numar_autori_upt") or 0),
            key=f"pi_aut_upt_{cod_introdus}",
        )
    with col_r4b:
        titlu_fisa = st.text_input(
            "TITLU ENGLEZA FISA INVENTIEI",
            value=date_existente.get("titlu_engleza_fisa_inventiei", "") or "",
            key=f"pi_titlu_fisa_{cod_introdus}",
        )

    # ── R5: COMENTARII DOCUMENT (100%) ─────────────────────────────────
    com_doc = st.text_area(
        "COMENTARII DOCUMENT",
        value=date_existente.get("comentarii_document", "") or "",
        height=80,
        key=f"pi_com_doc_{cod_introdus}",
    )

    # ── R6: COMENTARII DIVERSE (100%) ──────────────────────────────────
    com_div = st.text_area(
        "COMENTARII DIVERSE",
        value=date_existente.get("comentarii_diverse", "") or "",
        height=80,
        key=f"pi_com_div_{cod_introdus}",
    )

    def _str(v):
        return str(v).strip() if v else None

    return {
        "cod_identificare":                       cod_introdus,
        "numar_data_notificare_intern":           _str(nr_notif),
        "document_oficial_original":              _str(doc_oficial),
        "status_document":                        status_doc if status_doc else None,
        "spin_off":                               _str(spin_off),
        "comentarii_document":                    _str(com_doc),
        "comentarii_diverse":                     _str(com_div),
        "numar_autori_total":                     int(nr_autori_total) if nr_autori_total else None,
        "numar_autori_upt":                       int(nr_autori_upt) if nr_autori_upt else None,
        "domeniu_aplicare":                       _str(domeniu_apl),
        "contract_cesiune_inventatori_externi":   _str(contract_ces),
        "titlu_engleza_epo":                      _str(titlu_epo),
        "titlu_engleza_fisa_inventiei":           _str(titlu_fisa),
    }
