# =========================================================
# IDBDC/domenii/proprietate_industriala/baza.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.06.06
# =========================================================
# SECTIUNEA DATE DE BAZA — campuri vizibile in Calea1 si Calea2:
#  1. CATEGORIE
#  2. ACRONIM TIP PROPRIETATE        <- 🔖 nom_prop_industr
#  3. DENUMIRE PROPRIETATE INDUSTRIALA (readonly, din nomenclator)
#  4. TITLUL PROPRIETATII
#  5. NR.INREGISTRARE CERERE         (cod_identificare, readonly)
#  6. DATA DEPOZIT CERERE            <- 📅
#  7. NR.PUBLICARE CERERE
#  8. NR.OFICIAL DE ACORDARE
#  9. DATA OFICIALA DE ACORDARE      <- 📅
# 10. DATA DE INCEPUT VALABILITATE   <- 📅
# 11. DURATA DE VALABILITATE (ani)
# 12. DATA DE SFARSIT VALABILITATE   <- 📅 (calculata automat)
# 13. ID PROIECT SURSA/CONTRACT
# 14. DENUMIRE SOLICITANT
# 15. DENUMIRE TITULAR
# 16. LINK ESPACENET
# 17. TITLU ENGLEZA DIPLOMA
#
# SECTIUNEA DATE SUPLIMENTARE — campuri vizibile NUMAI in Calea2:
#  1. NR.SI DATA DE NOTIFICARE INTERNA
#  2. DOCUMENT OFICIAL ORIGINAL
#  3. STATUS DOCUMENT                <- 🔖
#  4. SPIN OFF
#  5. COMENTARII DOCUMENT
#  6. COMENTARII DIVERSE
#  7. NUMAR AUTORI TOTAL
#  8. NUMAR AUTORI UPT
#  9. DOMENIU APLICARE
# 10. CONTRACT CESIUNE INVENTATORI EXTERNI
# 11. TITLU ENGLEZA EPO
# 12. TITLU ENGLEZA FISA INVENTIEI
# =========================================================

import streamlit as st
import pandas as pd
from datetime import date as _date
from core.helpers import to_date, fmt_date


# ── Cache nomenclatoare ────────────────────────────────────────────────

@st.cache_data(show_spinner=False, ttl=600)
def _get_tip_prop_map(_supabase):
    """Returneaza dict {acronim_prop_industr: denumire_prop_industr}."""
    try:
        res = _supabase.table("nom_prop_industr") \
            .select("acronim_prop_industr,denumire_prop_industr").execute()
        return {
            r["acronim_prop_industr"]: r.get("denumire_prop_industr", "") or ""
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
    key_den = f"pi_den_{cod_introdus}"

    if key_tip not in st.session_state:
        st.session_state[key_tip] = date_existente.get("acronim_prop_industr", "") or ""
    if key_den not in st.session_state:
        tip_init = st.session_state[key_tip]
        st.session_state[key_den] = tip_prop_map.get(tip_init, "") if tip_init else \
                                    (date_existente.get("denumire_prop_industr", "") or "")

    # Randul 1: CATEGORIE (readonly)
    st.markdown(
        f"<div style='color:rgba(255,255,255,0.55);font-size:0.78rem;font-weight:700;"
        f"text-transform:uppercase;margin-bottom:2px;'>CATEGORIE</div>"
        f"<div style='color:#ffffff;font-size:0.95rem;margin-bottom:12px;'>{cat_sel}</div>",
        unsafe_allow_html=True,
    )

    # Randul 2: TIP + DENUMIRE (readonly)
    col_tip, col_den = st.columns([1, 2])
    with col_tip:
        idx_tip = tip_list.index(st.session_state[key_tip]) \
                  if st.session_state[key_tip] in tip_list else 0
        tip_ales = st.selectbox(
            "🔖 ACRONIM TIP PROPRIETATE",
            options=tip_list,
            index=idx_tip,
            key=key_tip,
        )
        den_auto = tip_prop_map.get(tip_ales, "") if tip_ales else ""
        st.session_state[key_den] = den_auto
    with col_den:
        st.text_input(
            "DENUMIRE PROPRIETATE INDUSTRIALA",
            value=den_auto,
            disabled=True,
            key=f"pi_den_display_{cod_introdus}",
        )

    # Randul 3: TITLU + COD (readonly)
    col_tit, col_cod = st.columns([3, 1])
    with col_tit:
        titlu = st.text_input(
            "TITLUL PROPRIETATII",
            value=date_existente.get("titlul_proprietatii", "") or "",
            key=f"pi_titlu_{cod_introdus}",
        )
    with col_cod:
        st.text_input(
            "NR.INREGISTRARE CERERE",
            value=cod_introdus,
            disabled=True,
            key=f"pi_cod_{cod_introdus}",
        )

    # Randul 4: DATE
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        data_depozit = st.date_input(
            "📅 DATA DEPOZIT CERERE",
            value=to_date(date_existente.get("data_depozit_cerere")),
            format="YYYY-MM-DD",
            key=f"pi_data_dep_{cod_introdus}",
        )
    with col_d2:
        data_acordare = st.date_input(
            "📅 DATA OFICIALA DE ACORDARE",
            value=to_date(date_existente.get("data_oficiala_de_acordare")),
            format="YYYY-MM-DD",
            key=f"pi_data_ac_{cod_introdus}",
        )
    with col_d3:
        data_inceput_val = st.date_input(
            "📅 DATA INCEPUT VALABILITATE",
            value=to_date(date_existente.get("data_inceput_valabilitate")),
            format="YYYY-MM-DD",
            key=f"pi_data_iv_{cod_introdus}",
        )

    # Randul 5: NR-uri
    col_n1, col_n2, col_n3 = st.columns(3)
    with col_n1:
        nr_publicare = st.text_input(
            "NR.PUBLICARE CERERE",
            value=str(date_existente.get("numar_publicare_cerere") or ""),
            key=f"pi_nr_pub_{cod_introdus}",
        )
    with col_n2:
        nr_acordare = st.text_input(
            "NR.OFICIAL DE ACORDARE",
            value=str(date_existente.get("numar_oficial_acordare") or ""),
            key=f"pi_nr_ac_{cod_introdus}",
        )
    with col_n3:
        try:
            ani_ex = int(date_existente.get("ani_de_valabilitate") or 0)
        except (TypeError, ValueError):
            ani_ex = 0
        ani_val = st.number_input(
            "DURATA DE VALABILITATE (ani)",
            min_value=0, max_value=50,
            value=ani_ex,
            step=1,
            key=f"pi_ani_val_{cod_introdus}",
        )

    # Data sfarsit valabilitate — calculata automat
    data_sfarsit_val = _add_ani(data_inceput_val, ani_val)
    sf_str = fmt_date(data_sfarsit_val) or ""
    st.text_input(
        "📅 DATA SFARSIT VALABILITATE (calculata automat)",
        value=sf_str,
        disabled=True,
        key=f"pi_data_sv_{cod_introdus}",
    )

    # Randul 6: Alte campuri
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        id_sursa = st.text_input(
            "ID PROIECT SURSA/CONTRACT",
            value=date_existente.get("id_proiect_contract_sursa", "") or "",
            key=f"pi_id_sursa_{cod_introdus}",
        )
        solicitant = st.text_input(
            "DENUMIRE SOLICITANT",
            value=date_existente.get("denumire_solicitant", "") or "",
            key=f"pi_solicitant_{cod_introdus}",
        )
    with col_a2:
        titular = st.text_input(
            "DENUMIRE TITULAR",
            value=date_existente.get("denumire_titular", "") or "",
            key=f"pi_titular_{cod_introdus}",
        )
        link_esp = st.text_input(
            "LINK ESPACENET",
            value=date_existente.get("link_espacenet", "") or "",
            key=f"pi_link_{cod_introdus}",
        )

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
        "ani_de_valabilitate":       int(ani_val) if ani_val else None,
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

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        nr_notif = st.text_input(
            "NR.SI DATA DE NOTIFICARE INTERNA",
            value=date_existente.get("numar_data_notificare_intern", "") or "",
            key=f"pi_nr_notif_{cod_introdus}",
        )
        status_doc = st.selectbox(
            "🔖 STATUS DOCUMENT",
            options=[""] + status_doc_list,
            index=([""] + status_doc_list).index(date_existente.get("status_document", "") or "")
                  if (date_existente.get("status_document", "") or "") in status_doc_list else 0,
            key=f"pi_status_doc_{cod_introdus}",
        )
        spin_off = st.text_input(
            "SPIN OFF",
            value=date_existente.get("spin_off", "") or "",
            key=f"pi_spin_{cod_introdus}",
        )
        nr_autori_total = st.number_input(
            "NUMAR AUTORI TOTAL",
            min_value=0,
            value=int(date_existente.get("numar_autori_total") or 0),
            key=f"pi_aut_total_{cod_introdus}",
        )
        nr_autori_upt = st.number_input(
            "NUMAR AUTORI UPT",
            min_value=0,
            value=int(date_existente.get("numar_autori_upt") or 0),
            key=f"pi_aut_upt_{cod_introdus}",
        )
    with col_s2:
        doc_oficial = st.text_input(
            "DOCUMENT OFICIAL ORIGINAL",
            value=date_existente.get("document_oficial_original", "") or "",
            key=f"pi_doc_of_{cod_introdus}",
        )
        domeniu_apl = st.text_input(
            "DOMENIU APLICARE",
            value=date_existente.get("domeniu_aplicare", "") or "",
            key=f"pi_dom_apl_{cod_introdus}",
        )
        contract_ces = st.text_input(
            "CONTRACT CESIUNE INVENTATORI EXTERNI",
            value=date_existente.get("contract_cesiune_inventatori_externi", "") or "",
            key=f"pi_contract_ces_{cod_introdus}",
        )
        titlu_epo = st.text_input(
            "TITLU ENGLEZA EPO",
            value=date_existente.get("titlu_engleza_epo", "") or "",
            key=f"pi_titlu_epo_{cod_introdus}",
        )
        titlu_fisa = st.text_input(
            "TITLU ENGLEZA FISA INVENTIEI",
            value=date_existente.get("titlu_engleza_fisa_inventiei", "") or "",
            key=f"pi_titlu_fisa_{cod_introdus}",
        )

    com_doc = st.text_area(
        "COMENTARII DOCUMENT",
        value=date_existente.get("comentarii_document", "") or "",
        height=80,
        key=f"pi_com_doc_{cod_introdus}",
    )
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
