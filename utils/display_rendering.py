# =========================================================
# utils/display_rendering.py
# v.modul.1.0 - Funcții de randare pe ecran pentru fișa completă
# =========================================================

import streamlit as st
import html as _html
from utils.display_config import CARD_PRIORITY, _TABELE_CONTRACTE, _COLS_EXCLUDE_CONTRACTE, COLS_HIDDEN_FISA, TEHNIC_COL_ORDER
from utils.display_helpers import col_label, fmt_numeric, get_contact_info, is_persoana_contact
from utils.supabase_helpers import safe_select_eq

# =========================================================
# Randare secțiune generică (tabel cu două coloane: câmp | valoare)
# =========================================================
def render_sectiune_tabel(section_label: str, rows: list, table: str = None, tabela_baza_ctx: str = None):
    """
    Afișează o secțiune (Generale, Financiar, Tehnic) sub formă de tabel vertical.
    rows: lista de rânduri din tabela respectivă (de obicei un singur rând, dar poate fi mai multe).
    """
    if not rows:
        return

    is_contract_ctx = (tabela_baza_ctx or table or "") in _TABELE_CONTRACTE
    extra_hidden = _COLS_EXCLUDE_CONTRACTE if is_contract_ctx else set()

    # Construim lista (label, value) pentru toate câmpurile vizibile din toate rândurile
    all_items = []
    for row in rows:
        # Determinăm ordinea câmpurilor
        if table == "com_aspecte_tehnice":
            ordered = [c for c in TEHNIC_COL_ORDER if c in row and row[c] is not None and str(row[c]).strip() not in ("", "None", "nan") and c not in COLS_HIDDEN_FISA and c not in extra_hidden]
            rest = [c for c in row.keys() if c not in TEHNIC_COL_ORDER and c not in COLS_HIDDEN_FISA and c not in extra_hidden and row[c] is not None and str(row[c]).strip() not in ("", "None", "nan")]
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
            ordered = [c for c in COL_ORDER_FINANCIAR if c in row and row[c] is not None and str(row[c]).strip() not in ("", "None", "nan") and c not in COLS_HIDDEN_FISA and c not in extra_hidden]
            rest = [c for c in row.keys() if c not in COL_ORDER_FINANCIAR and c not in COLS_HIDDEN_FISA and c not in extra_hidden and row[c] is not None and str(row[c]).strip() not in ("", "None", "nan")]
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
            ordered = [c for c in COL_ORDER_GENERALE if c in row and row[c] is not None and str(row[c]).strip() not in ("", "None", "nan") and c not in COLS_HIDDEN_FISA and c not in extra_hidden]
            rest = [c for c in row.keys() if c not in COL_ORDER_GENERALE and c not in COLS_HIDDEN_FISA and c not in extra_hidden and row[c] is not None and str(row[c]).strip() not in ("", "None", "nan")]
            visible_cols = ordered + rest

        for c in visible_cols:
            raw_val = row[c]
            try:
                float(str(raw_val).replace(",", ".").strip())
                is_num = True
            except (ValueError, TypeError):
                is_num = False
            val_str = fmt_numeric(raw_val, c) if is_num else str(raw_val)
            all_items.append((col_label(c, table), _html.escape(val_str)))

    if not all_items:
        st.info(f"Nu există câmpuri completate pentru secțiunea {section_label}.")
        return

    # Generare tabel HTML cu două coloane: prima coloană = numele câmpului, a doua = valoarea
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


# =========================================================
# Randare secțiune Echipă (compact, cu detalii de contact)
# =========================================================
def render_echipa_compact(rows: list, cod_ctx: str = "", supabase=None):
    """Afișează echipa: persoana de contact evidențiată, apoi lista membrilor."""
    if not rows:
        st.info("Nu există echipă înregistrată pentru această fișă.")
        return

    rows_sorted = sorted(rows, key=lambda r: (0 if is_persoana_contact(r) else 1, str(r.get("nume_prenume") or "")))
    persoane_cont = [r for r in rows_sorted if is_persoana_contact(r)]
    membri = [r for r in rows_sorted if not is_persoana_contact(r)]

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
            contact = get_contact_info(supabase, nume)
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
