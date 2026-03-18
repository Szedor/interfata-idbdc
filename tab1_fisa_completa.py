# =========================================================
# TAB 1 — FIȘA COMPLETĂ (după cod)
# !! FIȘIER BETONAT — NU SE MODIFICĂ !!
# Ultima versiune validată: 17.03.2026
# =========================================================

import streamlit as st
import pandas as pd
import html as _html
import io
import streamlit.components.v1 as components
from supabase import Client

# =========================================================
# ETICHETE CÂMPURI
# =========================================================

COL_LABELS = {
    "abreviere_domeniu_fdi": "DOMENIUL FDI",
    "acronim_contracte": "ACRONIM TIP PROIECTE",
    "acronim_contracte_proiecte": "TIPUL DE CONTRACT SAU PROIECT",
    "acronim_departament": "ACRONIM DEPARTAMENT",
    "acronim_functie_upt": "ABREVIERE FUNCTIE UPT",
    "acronim_proiect": "ACRONIM TIP PROIECTE",
    "acronim_proiecte": "ACRONIM TIP PROIECTE",
    "acronim_prop_intelect": "FORME DE PROTECTIE A PROPRIETATII INDUSTRIALE",
    "activitati_proiect": "ACTIVIATI",
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
    "durata": "DURATA",
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
    "pozitie_clasament": "POZITIE IN CLASAMENT",
    "programul_de_finantare": "PROGRAMUL DE FINANTARE",
    "punctaj": "PUNCTAJ",
    "reprezinta_idbdc": "REPREZINTA CONTRACTUL/PROIECTUL",
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
    "titlul_proiect": "OBIECTUL/TITLUL CONTRACTULUI/PROIECTULUI",
    "total_proiecte": "TOTAL PROIECTE DEPUSE",
    "username_sistem": "USERNAME",
    "valoare_anuala_contract": "VALOAREA ANUALA A CONTRACTULUI",
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

TABLE_LABELS = {
    "base_contracte_cep":           "📄 Contract CEP",
    "base_contracte_terti":         "📄 Contract TERȚI",
    "base_proiecte_fdi":            "🔬 Proiect FDI",
    "base_proiecte_pncdi":          "🔬 Proiect PNCDI",
    "base_proiecte_pnrr":           "🔬 Proiect PNRR",
    "base_proiecte_internationale": "🌍 Proiect Internațional",
    "base_proiecte_interreg":       "🌍 Proiect INTERREG",
    "base_proiecte_noneu":          "🌍 Proiect NON-EU",
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
    "base_evenimente_stiintifice": {
        "cod_identificare":  "COD EVENIMENT",
        "titlul_eveniment":  "TITLUL EVENIMENTULUI",
        "natura_eveniment":  "NATURA EVENIMENTULUI",
        "format_eveniment":  "FORMATUL EVENIMENTULUI",
        "loc_desfasurare":   "LOCUL DE DESFASURARE",
    },
    "base_prop_intelect": {
        "cod_identificare":          "NR. CERERE / BREVET",
        "acronim_prop_intelect":     "FORMA DE PROTECTIE",
        "titlul_proiect":            "TITLUL INVENTIEI / LUCRARII",
        "data_depozit_cerere":       "DATA DEPUNERE LA OSIM",
        "data_oficiala_acordare":    "DATA ACORDARE",
        "numar_oficial_acordare":    "NR. OFICIAL ACORDARE",
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
    "base_evenimente_stiintifice",
    "base_prop_intelect",
]


# =========================================================
# HELPERS INTERNE
# =========================================================

def _col_label(col: str, table: str = None) -> str:
    if table and table in COL_LABELS_PER_TABLE:
        if col in COL_LABELS_PER_TABLE[table]:
            return COL_LABELS_PER_TABLE[table][col]
    return COL_LABELS.get(col, col.replace("_", " ").capitalize())


def _safe_select_eq(supabase: Client, table: str, col: str, value: str, limit: int = 2000) -> list[dict]:
    try:
        res = supabase.table(table).select("*").eq(col, value).limit(limit).execute()
        return res.data or []
    except Exception:
        return []


def _render_sectiune_tabel(section_label: str, rows: list[dict], table: str = None):
    """
    Afișează o secțiune ca tabel cu 3 coloane:
      Col 1 (~10%): numele secțiunii — o singură dată, aliniat sus
      Col 2 (~23%): eticheta câmpului
      Col 3 (~67%): valoarea efectivă
    Fără spațiu între rândurile din aceeași secțiune.
    """
    if not rows:
        return

    priority_set = {c: i for i, c in enumerate(CARD_PRIORITY)}

    all_items = []
    for row in rows:
        visible_cols = [
            c for c in row.keys()
            if c not in COLS_HIDDEN_FISA
            and row[c] is not None
            and str(row[c]).strip() not in ("", "None", "nan")
        ]
        visible_cols.sort(key=lambda c: (priority_set.get(c, 999), c))
        for c in visible_cols:
            all_items.append((_col_label(c, table), _html.escape(str(row[c]))))

    if not all_items:
        st.info(f"Nu există câmpuri completate pentru secțiunea {section_label}.")
        return

    rows_html = ""
    for i, (label, value) in enumerate(all_items):
        if i == 0:
            sec_cell = (
                f"<td rowspan='{len(all_items)}' style='"
                f"vertical-align:top;"
                f"padding:6px 10px 6px 0;"
                f"width:10%;'>"
                f"<span style='color:rgba(255,255,255,0.45);font-size:0.74rem;"
                f"font-weight:800;text-transform:uppercase;letter-spacing:0.07em;"
                f"white-space:nowrap;'>{_html.escape(section_label)}</span>"
                f"</td>"
            )
        else:
            sec_cell = ""

        rows_html += (
            f"<tr>"
            f"{sec_cell}"
            f"<td style='padding:3px 12px 3px 0;width:23%;vertical-align:top;'>"
            f"<span style='color:rgba(255,255,255,0.50);font-size:0.76rem;"
            f"font-weight:700;text-transform:uppercase;letter-spacing:0.04em;'>"
            f"{label}</span></td>"
            f"<td style='padding:3px 0 3px 0;width:67%;vertical-align:top;'>"
            f"<span style='color:#ffffff;font-size:0.95rem;font-weight:700;'>"
            f"{value}</span></td>"
            f"</tr>"
        )

    st.markdown(
        f"<table style='width:100%;border-collapse:collapse;margin-bottom:0;'>"
        f"{rows_html}"
        f"</table>",
        unsafe_allow_html=True,
    )


def _render_echipa_compact(rows: list[dict], cod_ctx: str = "", supabase=None):
    """
    Afișează echipa:
    - Reprezentant cu date de contact din det_resurse_umane
    - Membrii echipă în format inline, cu bife pentru câmpurile dorite
    """
    if not rows:
        st.info("Nu există echipă înregistrată pentru această fișă.")
        return

    toate_campuri_posibile = [
        "nume_prenume", "functia_specifica", "acronim_functie_upt",
        "status_personal", "data_inceput_rol", "data_sfarsit_rol",
    ]
    campuri_cu_date = [c for c in toate_campuri_posibile if any(r.get(c) for r in rows)]

    ETICHETE_ECH = {
        "nume_prenume":        "Nume",
        "functia_specifica":   "Rol",
        "acronim_functie_upt": "Funcție UPT",
        "status_personal":     "Status",
        "data_inceput_rol":    "De la",
        "data_sfarsit_rol":    "Până la",
    }

    ctx_key = cod_ctx or str(id(rows))
    sel_key = f"ech_campuri_{ctx_key}"
    if sel_key not in st.session_state:
        st.session_state[sel_key] = ["nume_prenume", "functia_specifica"]

    # Bife câmpuri — fără expander, direct inline
    cols_sel = st.columns(len(campuri_cu_date) or 1)
    selectie = []
    for i, c in enumerate(campuri_cu_date):
        checked = c in st.session_state[sel_key]
        if cols_sel[i].checkbox(ETICHETE_ECH.get(c, c), value=checked, key=f"ech_chk_{ctx_key}_{c}"):
            selectie.append(c)
    st.session_state[sel_key] = selectie if selectie else ["nume_prenume"]

    campuri_activi = [c for c in campuri_cu_date if c in st.session_state[sel_key]]
    if not campuri_activi:
        campuri_activi = ["nume_prenume"]

    def sort_key(r):
        rep = r.get("reprezinta_idbdc")
        is_rep = rep is True or str(rep).strip().upper() in ("TRUE", "DA", "1")
        return (0 if is_rep else 1, str(r.get("nume_prenume") or ""))

    rows_sorted = sorted(rows, key=sort_key)

    reprezentanti = [r for r in rows_sorted
                     if r.get("reprezinta_idbdc") is True
                     or str(r.get("reprezinta_idbdc", "")).strip().upper() in ("TRUE", "DA", "1")]
    membri = [r for r in rows_sorted
              if r.get("reprezinta_idbdc") is not True
              and str(r.get("reprezinta_idbdc", "")).strip().upper() not in ("TRUE", "DA", "1")]

    def _format_membru(r, campuri):
        parts = []
        for c in campuri:
            v = str(r.get(c) or "").strip()
            if v:
                parts.append(_html.escape(v))
        return ", ".join(parts)

    # ── Reprezentant cu date de contact ──────────────────────────────────
    if reprezentanti:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.50);font-size:0.76rem;font-weight:700;"
            "text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;'>"
            "⭐ Responsabil contract / Director proiect</div>",
            unsafe_allow_html=True,
        )
        for r in reprezentanti:
            txt = _format_membru(r, campuri_activi)
            # Preia date contact din det_resurse_umane
            contact_html = ""
            if supabase:
                try:
                    nume_rep = str(r.get("nume_prenume") or "").strip()
                    if nume_rep:
                        res_c = supabase.table("det_resurse_umane")                            .select("email_upt,telefon_upt,telefon_mobil")                            .eq("nume_prenume", nume_rep).limit(1).execute()
                        if res_c.data:
                            rc = res_c.data[0]
                            email = str(rc.get("email_upt") or "").strip()
                            tel1  = str(rc.get("telefon_upt") or "").strip()
                            tel2  = str(rc.get("telefon_mobil") or "").strip()
                            parts_c = []
                            if email:
                                parts_c.append(f"✉ {_html.escape(email)}")
                            if tel1:
                                parts_c.append(f"☎ {_html.escape(tel1)}")
                            if tel2 and tel2 != tel1:
                                parts_c.append(f"📱 {_html.escape(tel2)}")
                            if parts_c:
                                contact_html = (
                                    f" <span style='color:rgba(255,220,100,0.80);"
                                    f"font-size:0.82rem;font-weight:400;'>"
                                    f"{'  ·  '.join(parts_c)}</span>"
                                )
                except Exception:
                    pass
            st.markdown(
                f"<div style='padding:6px 12px;margin-bottom:3px;"
                f"background:rgba(255,255,255,0.10);border-radius:8px;"
                f"border-left:3px solid rgba(255,220,80,0.70);'>"
                f"<span style='font-weight:800;color:#ffffff;'>⭐ {txt}</span>"
                f"{contact_html}</div>",
                unsafe_allow_html=True,
            )
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if not membri:
        return

    # ── Membrii echipă — format inline ───────────────────────────────────
    st.markdown(
        f"<div style='color:rgba(255,255,255,0.50);font-size:0.76rem;font-weight:700;"
        f"text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;'>"
        f"👥 Membrii echipă ({len(membri)})</div>",
        unsafe_allow_html=True,
    )

    PREVIEW = 8
    show_all_key = f"echipa_show_all_{ctx_key}"
    if show_all_key not in st.session_state:
        st.session_state[show_all_key] = False

    def _build_inline(lista, campuri):
        parts = []
        for r in lista:
            txt = _format_membru(r, campuri)
            if txt:
                parts.append(txt)
        return "  ·  ".join(parts)

    membri_display = membri if st.session_state[show_all_key] else membri[:PREVIEW]

    if st.session_state[show_all_key] and len(membri) > PREVIEW:
        filter_key = f"echipa_filter_{ctx_key}"
        filtru = st.text_input(
            "Cauta", value="", key=filter_key,
            placeholder="Filtrează după nume...", label_visibility="collapsed",
        ).strip().lower()
        if filtru:
            membri_display = [r for r in membri if filtru in str(r.get("nume_prenume") or "").lower()]

    inline_text = _build_inline(membri_display, campuri_activi)
    st.markdown(
        f"<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.12);"
        f"border-radius:10px;padding:10px 14px;line-height:1.9;font-size:0.88rem;"
        f"color:rgba(255,255,255,0.88);'>"
        f"{inline_text}</div>",
        unsafe_allow_html=True,
    )

    if len(membri) > PREVIEW:
        ramasi = len(membri) - PREVIEW
        if st.session_state[show_all_key]:
            if st.button("▲ Restrânge lista", key=f"echipa_collapse_{ctx_key}", use_container_width=False):
                st.session_state[show_all_key] = False
                st.rerun()
        else:
            if st.button(
                f"▼ Arată toți cei {len(membri)} membri  (+{ramasi} ascunși)",
                key=f"echipa_expand_{ctx_key}", use_container_width=False,
            ):
                st.session_state[show_all_key] = True
                st.rerun()



# =========================================================
# RENDER PRINCIPAL — TAB 1
# =========================================================

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
                st.markdown(
                    "<div style='margin-top:28px;font-size:1.4rem;' title='Cod găsit'>✅</div>",
                    unsafe_allow_html=True,
                )
            elif cod and len(cod) >= 3:
                st.markdown(
                    "<div style='margin-top:28px;font-size:1.4rem;' title='Cod negăsit'>❌</div>",
                    unsafe_allow_html=True,
                )

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
        st.warning("Codul introdus nu a fost găsit în nicio tabelă de bază.")
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

    # ── Linie de control cu cele 4 bife ──────────────────────────────────
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    _p1, _p2, _p3, _p4, _lbl = st.columns([0.7, 0.7, 0.7, 0.7, 5.2])
    with _p1:
        pin_gen = st.checkbox("Generale",  key=f"fisa_pin_{cod}_generale")
    with _p2:
        pin_fin = st.checkbox("Financiar", key=f"fisa_pin_{cod}_financiar")
    with _p3:
        pin_ech = st.checkbox("Echipă",    key=f"fisa_pin_{cod}_echipa")
    with _p4:
        pin_teh = st.checkbox("Tehnic",    key=f"fisa_pin_{cod}_tehnic")
    with _lbl:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.45);font-size:0.875rem;"
            "padding-top:6px;font-style:italic;'>Bifează o secțiune pentru a afișa informațiile existente în aceasta.</div>",
            unsafe_allow_html=True,
        )

    # ── Afișare secțiuni bifate ───────────────────────────────────────────
    sectiuni_active = []
    if pin_gen: sectiuni_active.append(("Generale",  tabela_gasita,          "generale"))
    if pin_fin: sectiuni_active.append(("Financiar", "com_date_financiare",   "financiar"))
    if pin_ech: sectiuni_active.append(("Echipă",    "com_echipe_proiect",    "echipa"))
    if pin_teh: sectiuni_active.append(("Tehnic",    "com_aspecte_tehnice",   "tehnic"))

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
                    f"<div style='color:rgba(255,255,255,0.45);font-size:0.74rem;"
                    f"font-weight:800;text-transform:uppercase;letter-spacing:0.07em;"
                    f"margin-bottom:6px;'>{_html.escape(sec_label)}</div>",
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
                    _render_sectiune_tabel(sec_label, rows, sec_table)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Export fișă ───────────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown(
        "<div style='color:rgba(255,255,255,0.75);font-size:0.90rem;font-weight:700;"
        "margin-bottom:6px;'>📤 Export fișă</div>",
        unsafe_allow_html=True,
    )

    export_frames = {}
    rows_exp = _safe_select_eq(supabase, tabela_gasita, "cod_identificare", cod, limit=50)
    if rows_exp:
        df_t = pd.DataFrame(rows_exp)
        df_t = df_t[[c for c in df_t.columns if c not in COLS_HIDDEN_FISA]]
        df_t.columns = [_col_label(c, tabela_gasita) for c in df_t.columns]
        export_frames["Generale"] = df_t

    for com_label, com_table in [("Financiar", "com_date_financiare"), ("Tehnic", "com_aspecte_tehnice")]:
        rows_exp = _safe_select_eq(supabase, com_table, "cod_identificare", cod, limit=50)
        if rows_exp:
            df_t = pd.DataFrame(rows_exp)
            df_t = df_t[[c for c in df_t.columns if c not in COLS_HIDDEN_FISA]]
            df_t.columns = [_col_label(c, com_table) for c in df_t.columns]
            export_frames[com_label] = df_t

    rows_ech = _safe_select_eq(supabase, "com_echipe_proiect", "cod_identificare", cod, limit=2000)
    if rows_ech:
        # Format inline pentru PDF: o singura linie per sectiune
        def _is_rep(r):
            v = r.get("reprezinta_idbdc")
            return v is True or str(v).strip().upper() in ("TRUE", "DA", "1")

        reps_ech   = [r for r in rows_ech if _is_rep(r)]
        membri_ech = [r for r in rows_ech if not _is_rep(r)]

        campuri_pdf = ["nume_prenume", "functia_specifica", "status_personal"]

        def _fmt_r(r):
            return ", ".join(
                str(r.get(c) or "").strip()
                for c in campuri_pdf if str(r.get(c) or "").strip()
            )

        # Date contact reprezentant
        contact_rep = ""
        if reps_ech and supabase:
            try:
                nr = str(reps_ech[0].get("nume_prenume") or "").strip()
                rc = supabase.table("det_resurse_umane")                    .select("email_upt,telefon_upt,telefon_mobil")                    .eq("nume_prenume", nr).limit(1).execute()
                if rc.data:
                    d = rc.data[0]
                    parts_c = [p for p in [
                        str(d.get("email_upt") or "").strip(),
                        str(d.get("telefon_upt") or "").strip(),
                        str(d.get("telefon_mobil") or "").strip(),
                    ] if p]
                    if parts_c:
                        contact_rep = "  |  " + "  ·  ".join(parts_c)
            except Exception:
                pass

        rep_txt    = ("  |  ".join(_fmt_r(r) + contact_rep for r in reps_ech)) if reps_ech else "-"
        membri_txt = "  ·  ".join(_fmt_r(r) for r in membri_ech) if membri_ech else "-"

        df_ech = pd.DataFrame([
            {"Câmp": "Responsabil contract", "Valoare": rep_txt},
            {"Câmp": "Membrii echipă", "Valoare": membri_txt},
        ])
        export_frames["Echipă"] = df_ech

    ea1, ea2, ea3, ea4 = st.columns([1.0, 1.0, 1.0, 1.0])

    with ea1:
        csv_parts = []
        for section_label, df_sec in export_frames.items():
            csv_parts.append(f"=== {section_label} ===")
            csv_parts.append(df_sec.to_csv(index=False))
            csv_parts.append("")
        st.download_button(
            "⬇️ Export fișă (CSV)", data="\n".join(csv_parts).encode("utf-8-sig"),
            file_name=f"fisa_{cod}.csv", mime="text/csv", key="fisa_csv",
            use_container_width=True,
        )

    with ea2:
        try:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                for section_label, df_sec in export_frames.items():
                    sheet_name = section_label[:31].replace("/", "-").replace(":", "")
                    df_sec.to_excel(writer, index=False, sheet_name=sheet_name)
            buf.seek(0)
            st.download_button(
                "⬇️ Download fișă (Excel)", data=buf, file_name=f"fisa_{cod}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="fisa_xlsx", use_container_width=True,
            )
        except Exception:
            st.caption("Excel indisponibil")

    with ea3:
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib.colors import HexColor

            pdf_buf = io.BytesIO()
            doc = SimpleDocTemplate(
                pdf_buf, pagesize=A4,
                leftMargin=1.8*cm, rightMargin=1.8*cm,
                topMargin=1.8*cm, bottomMargin=1.8*cm,
            )
            styles = getSampleStyleSheet()
            style_title = ParagraphStyle("T", parent=styles["Title"],
                fontName="Helvetica-Bold", fontSize=13, textColor=colors.white, leading=18)
            style_sub = ParagraphStyle("S", parent=styles["Normal"],
                fontName="Helvetica-Bold", fontSize=9, textColor=colors.white)
            style_sec = ParagraphStyle("SC", parent=styles["Normal"],
                fontName="Helvetica-Bold", fontSize=7.5, textColor=HexColor("#5A7FA8"))
            style_label = ParagraphStyle("L", parent=styles["Normal"],
                fontName="Helvetica-Bold", fontSize=8, textColor=HexColor("#2C4A6E"), leading=10)
            style_val = ParagraphStyle("V", parent=styles["Normal"],
                fontName="Helvetica", fontSize=8.5, textColor=HexColor("#0D1F35"), leading=11)
            style_head = ParagraphStyle("H", parent=styles["Normal"],
                fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)

            BLUE_DARK  = HexColor("#0B2A52")
            BLUE_MED   = HexColor("#1A4A7A")
            BLUE_ROW   = HexColor("#EEF4FB")
            col_w = [2.5*cm, 5.5*cm, 9.44*cm]

            story = []
            hdr = Table([[Paragraph("IDBDC — UPT", style_title),
                          Paragraph("Departamentul Cercetare Dezvoltare Inovare", style_sub)]],
                        colWidths=[5*cm, 12.44*cm])
            hdr.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),BLUE_DARK),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
                ("LEFTPADDING",(0,0),(0,0),14),("LEFTPADDING",(1,0),(1,0),8),
            ]))
            story.append(hdr)
            story.append(Spacer(1, 0.2*cm))
            sub = Table([[Paragraph(f"Fișă completă  ·  Cod: {_html.escape(cod)}", style_sub)]],
                        colWidths=[17.44*cm])
            sub.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),BLUE_MED),
                ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                ("LEFTPADDING",(0,0),(-1,-1),14),
            ]))
            story.append(sub)
            story.append(Spacer(1, 0.3*cm))

            antet = Table([[Paragraph("SECȚIUNEA",style_head),
                            Paragraph("CÂMP",style_head),
                            Paragraph("VALOARE",style_head)]], colWidths=col_w)
            antet.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),BLUE_MED),
                ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
                ("LEFTPADDING",(0,0),(-1,-1),5),
                ("GRID",(0,0),(-1,-1),0.3,HexColor("#6A9CC8")),
            ]))
            story.append(antet)

            for df_sec_name, df_sec in export_frames.items():
                rows_data = []
                for r_idx, (_, row) in enumerate(df_sec.iterrows()):
                    bg = BLUE_ROW if r_idx % 2 == 0 else colors.white
                    for c_idx, col_name in enumerate(df_sec.columns):
                        val = str(row[col_name]) if row[col_name] is not None else ""
                        label = col_name
                        rows_data.append((df_sec_name if c_idx == 0 and r_idx == 0 else "",
                                          label, val, bg))

                tbl_data = [[Paragraph(r[0], style_sec),
                             Paragraph(r[1], style_label),
                             Paragraph(r[2].replace("\n","<br/>").encode("ascii","replace").decode("ascii"), style_val)]
                            for r in rows_data]
                if not tbl_data:
                    continue
                tbl = Table(tbl_data, colWidths=col_w)
                cmds = [
                    ("VALIGN",(0,0),(-1,-1),"TOP"),
                    ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
                    ("LEFTPADDING",(0,0),(-1,-1),5),
                    ("GRID",(0,0),(-1,-1),0.3,HexColor("#C5D8EC")),
                    ("LINEABOVE",(0,0),(-1,0),1.2,BLUE_MED),
                ]
                for i, r in enumerate(rows_data):
                    cmds.append(("BACKGROUND",(0,i),(-1,i), r[3]))
                tbl.setStyle(TableStyle(cmds))
                story.append(tbl)

            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph(
                "Document generat automat — IDBDC UPT  ·  Uz intern",
                ParagraphStyle("F", parent=styles["Normal"],
                    fontName="Helvetica", fontSize=7,
                    textColor=HexColor("#8AADCC"), alignment=1)
            ))
            doc.build(story)
            pdf_buf.seek(0)
            st.download_button(
                "⬇️ Download fișă (PDF)", data=pdf_buf,
                file_name=f"fisa_{cod}.pdf", mime="application/pdf",
                key="fisa_pdf", use_container_width=True,
            )
        except ImportError:
            st.caption("PDF indisponibil (reportlab lipsă)")

    with ea4:
        if st.button("🖨️ Print fișă (PDF / Excel / Word)", key="fisa_print", use_container_width=True):
            html_sections = []
            for section_label, df_sec in export_frames.items():
                html_sections.append(f"<h3>{_html.escape(section_label)}</h3>")
                html_sections.append(df_sec.to_html(index=False, escape=True))
            full_html = f"""
            <html><head><meta charset="utf-8"/>
            <style>body{{font-family:Arial;padding:20px;}}
            h2{{color:#003366;}} h3{{color:#0b2a52;margin-top:20px;}}
            table{{border-collapse:collapse;width:100%;margin-bottom:16px;}}
            th,td{{border:1px solid #ccc;padding:5px;font-size:11px;}}
            th{{background:#e8f0f8;}}
            @media print{{button{{display:none;}}}}
            </style></head><body>
            <button onclick="window.print()">🖨️ Print</button>
            <h2>Fișă — {_html.escape(cod)}</h2>
            {"".join(html_sections)}
            </body></html>
            """
            components.html(full_html, height=700, scrolling=True)
