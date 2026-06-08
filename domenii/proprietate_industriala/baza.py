# =========================================================
# IDBDC/domenii/proprietate_industriala/baza.py
# VERSIUNE: 2.2 - Corectare completă erori și mapare nomenclator în timp real
# DATA: 2026.06.09
# =========================================================

import streamlit as st
import datetime

def _incarca_nomenclator_pi(supabase):
    """Încarcă datele brute din nom_prop_industr pentru mapare în timp real."""
    try:
        res = supabase.table("nom_prop_industr").select("acronim_prop_industr, denumire_prop_industr, ani_de_valabilitate").execute()
        return res.data or []
    except Exception:
        return []

def render_generale(supabase, cod_introdus, cat_sel, tabela_nume, is_new, date_existente):
    st.markdown(
        "<div style='background-color:#0b2a52; padding:8px 15px; border-radius:6px; margin-bottom:15px.'>"
        "<h3 style='margin:0; color:#ffffff; font-size:1.2rem;'>📋 DATE DE BAZĂ GENERALE</h3>"
        "</div>",
        unsafe_allow_html=True
    )

    # Încărcare nomenclator din SQL
    nom_data = _incarca_nomenclator_pi(supabase)
    liste_acronime = [r["acronim_prop_industr"] for r in nom_data]
    map_denumiri = {r["acronim_prop_industr"]: r["denumire_prop_industr"] for r in nom_data}
    map_ani = {r["acronim_prop_industr"]: r["ani_de_valabilitate"] for r in nom_data}

    if not liste_acronime:
        liste_acronime = [""]

    # R1 -> ACRONIM (25%), DENUMIRE PROPRIETATE (50%), NR. INREGISTRARE CERERE (25%)
    r1_c1, r1_c2, r1_c3 = st.columns([25, 50, 25])
    with r1_c1:
        saved_acr = date_existente.get("acronim_prop_industr", "") if date_existente else ""
        idx_acr = 0
        if saved_acr in liste_acronime:
            idx_acr = liste_acronime.index(saved_acr)
        acronim = st.selectbox("ACRONIM TIP PROPRIETATE", options=liste_acronime, index=idx_acr, key=f"pi_acr_{cod_introdus}")
    
    with r1_c2:
        # Corelare automată directă pe baza selecției de mai sus
        denumire_nom = map_denumiri.get(acronim, "")
        st.text_input("DENUMIRE PROPRIETATE INDUSTRIALA", value=denumire_nom, disabled=True, key=f"pi_den_nom_{cod_introdus}")
    
    with r1_c3:
        st.text_input("NR. INREGISTRARE CERERE", value=cod_introdus, disabled=True, key=f"pi_cod_{cod_introdus}")

    # R2 -> TITLUL PROPRIETATII - 100%
    saved_titlu = date_existente.get("titlul_proprietatii", "") if date_existente else ""
    titlul_prop = st.text_area("TITLUL PROPRIETATII", value=saved_titlu or "", height=65, key=f"pi_titlu_{cod_introdus}")

    # R3 -> DATA DEPOZIT CERERE (25%), NR. PUBLICARE CERERE (25%), DATA OFICIALA DE ACORDARE (25%), NR. OFICIAL DE ACORDARE (25%)
    r3_c1, r3_c2, r3_c3, r3_c4 = st.columns([25, 25, 25, 25])
    with r3_c1:
        val_dep = date_existente.get("data_depozit_cerere") if date_existente else None
        dt_dep = datetime.date.fromisoformat(val_dep) if val_dep else None
        data_depozit = st.date_input("DATA DEPOZIT CERERE", value=dt_dep, key=f"pi_dt_dep_{cod_introdus}")
    with r3_c2:
        saved_pub = date_existente.get("numar_publicare_cerere", "") if date_existente else ""
        nr_pub = st.text_input("NR. PUBLICARE CERERE", value=saved_pub or "", key=f"pi_nr_pub_{cod_introdus}")
    with r3_c3:
        val_ac = date_existente.get("data_oficiala_de_acordare") if date_existente else None
        dt_ac = datetime.date.fromisoformat(val_ac) if val_ac else None
        data_oficiala = st.date_input("DATA OFICIALA DE ACORDARE", value=dt_ac, key=f"pi_dt_ac_{cod_introdus}")
    with r3_c4:
        saved_of = date_existente.get("numar_oficial_acordare", "") if date_existente else ""
        nr_oficial = st.text_input("NR. OFICIAL DE ACORDARE", value=saved_of or "", key=f"pi_nr_of_{cod_introdus}")

    # R4 -> DATA INCEPUT VALABILITATE (25%), DURATA (25%), DATA SFARSIT (25%), ID PROIECT SURSA (25%)
    r4_c1, r4_c2, r4_c3, r4_c4 = st.columns([25, 25, 25, 25])
    with r4_c1:
        val_inc = date_existente.get("data_inceput_valabilitate") if date_existente else None
        dt_inc = datetime.date.fromisoformat(val_inc) if val_inc else None
        data_inc = st.date_input("DATA INCEPUT VALABILITATE", value=dt_inc, key=f"pi_dt_inc_{cod_introdus}")
    
    with r4_c2:
        durata_ani = int(map_ani.get(acronim, 0))
        st.number_input("DURATA DE VALABILITATE (ani)", value=durata_ani, disabled=True, key=f"pi_durata_{cod_introdus}")
    
    with r4_c3:
        if data_inc and durata_ani > 0:
            try:
                dt_sfarsit = data_inc.replace(year=data_inc.year + durata_ani)
            except ValueError:
                dt_sfarsit = data_inc + datetime.timedelta(days=durata_ani * 365)
        else:
            dt_sfarsit = None
        st.date_input("DATA SFARSIT VALABILITATE", value=dt_sfarsit, disabled=True, key=f"pi_dt_sf_{cod_introdus}")
    
    with r4_c4:
        saved_id = date_existente.get("id_proiect_contract_sursa", "") if date_existente else ""
        id_proiect = st.text_input("ID PROIECT SURSA/CONTRACT", value=saved_id or "", key=f"pi_id_pr_{cod_introdus}")

    # R5 -> DENUMIRE TITULAR (33%), DENUMIRE SOLICITANT (33%), LINK ESPACENET (33%)
    r5_c1, r5_c2, r5_c3 = st.columns([33, 33, 34])
    with r5_c1:
        saved_tit = date_existente.get("denumire_titular", "") if date_existente else ""
        titular = st.text_input("DENUMIRE TITULAR", value=saved_tit or "", key=f"pi_titular_{cod_introdus}")
    with r5_c2:
        saved_sol = date_existente.get("denumire_solicitant", "") if date_existente else ""
        solicitant = st.text_input("DENUMIRE SOLICITANT", value=saved_sol or "", key=f"pi_solic_{cod_introdus}")
    with r5_c3:
        saved_lnk = date_existente.get("link_espacenet", "") if date_existente else ""
        link_espa = st.text_input("LINK ESPACENET", value=saved_lnk or "", key=f"pi_link_{cod_introdus}")

    # R6 -> TITLU ENGLEZA DIPLOMA - 100%
    saved_dip = date_existente.get("titlu_engleza_diploma", "") if date_existente else ""
    titlu_en_dip = st.text_input("TITLU ENGLEZA DIPLOMA", value=saved_dip or "", key=f"pi_en_dip_{cod_introdus}")

    return {
        "cod_identificare": cod_introdus,
        "denumire_categorie": cat_sel,
        "acronim_prop_industr": acronim,
        "denumire_prop_industr": denumire_nom,
        "titlul_proprietatii": titlul_prop.strip() if titlul_prop else None,
        "data_depozit_cerere": data_depozit.isoformat() if data_depozit else None,
        "numar_publicare_cerere": nr_pub.strip() if nr_pub else None,
        "data_oficiala_de_acordare": data_oficiala.isoformat() if data_oficiala else None,
        "numar_oficial_acordare": nr_oficial.strip() if nr_oficial else None,
        "data_inceput_valabilitate": data_inc.isoformat() if data_inc else None,
        "ani_de_valabilitate": durata_ani,
        "data_sfarsit_valabilitate": dt_sfarsit.isoformat() if dt_sfarsit else None,
        "id_proiect_contract_sursa": id_proiect.strip() if id_proiect else None,
        "denumire_titular": titular.strip() if titular else None,
        "denumire_solicitant": solicitant.strip() if solicitant else None,
        "link_espacenet": link_espa.strip() if link_espa else None,
        "titlu_engleza_diploma": titlu_en_dip.strip() if titlu_en_dip else None,
    }

def render_suplimentare(supabase, cod_introdus, is_new, date_existente):
    st.markdown(
        "<div style='background-color:#0b2a52; padding:8px 15px; border-radius:6px; margin-bottom:15px; margin-top:10px;'> "
        "<h3 style='margin:0; color:#ffffff; font-size:1.2rem;'>🔒 DATE SUPLIMENTARE DE CONTROL</h3>"
        "</div>",
        unsafe_allow_html=True
    )

    if not date_existente:
        date_existente = {}

    # R1 -> NR. SI DATA NOTIFICARE (25%), DOCUMENT OFICIAL (50%), STATUS DOCUMENT (25%)
    r1_c1, r1_c2, r1_c3 = st.columns([25, 50, 25])
    with r1_c1:
        saved_notif = date_existente.get("numar_data_notificare_intern", "")
        nr_notif = st.text_input("NR. SI DATA DE NOTIFICARE INTERNA", value=saved_notif or "", key=f"pi_nr_not_{cod_introdus}")
    with r1_c2:
        saved_doc = date_existente.get("document_oficial_original", "")
        doc_oficial = st.text_input("DOCUMENT OFICIAL ORIGINAL", value=saved_doc or "", key=f"pi_doc_of_{cod_introdus}")
    with r1_c3:
        status_opts = ["", "In curs de examinare", "Acordat", "Respins", "Retras"]
        saved_status = date_existente.get("status_document", "") or ""
        idx_st = status_opts.index(saved_status) if saved_status in status_opts else 0
        status_doc = st.selectbox("STATUS DOCUMENT", options=status_opts, index=idx_st, key=f"pi_stat_doc_{cod_introdus}")

    # R2 -> DOMENIU APLICARE (33%), SPIN OFF (33%), CONTRACT CESIUNE (33%)
    r2_c1, r2_c2, r2_c3 = st.columns([33, 33, 34])
    with r2_c1:
        saved_dom = date_existente.get("domeniu_aplicare_idbdc", "")
        domeniu = st.text_input("DOMENIU APLICARE", value=saved_dom or "", key=f"pi_domeniu_{cod_introdus}")
    with r2_c2:
        saved_spin = date_existente.get("spin_off", "")
        spin_off = st.text_input("SPIN OFF", value=saved_spin or "", key=f"pi_spin_{cod_introdus}")
    with r2_c3:
        saved_ces = date_existente.get("contract_cesiune_externi", "")
        contract_ces = st.text_input("CONTRACT CESIUNE INVENTATORI EXTERNI", value=saved_ces or "", key=f"pi_cesiune_{cod_introdus}")

    # R3 -> NUMAR AUTORI TOTAL (25%), TITLU ENGLEZA EPO (75%)
    r3_c1, r3_c2 = st.columns([25, 75])
    with r3_c1:
        saved_aut_tot = date_existente.get("numar_autori_total", "")
        val_aut_tot = str(saved_aut_tot) if saved_aut_tot is not None else ""
        nr_autori_total = st.text_input("NUMAR AUTORI TOTAL", value=val_aut_tot, key=f"pi_aut_tot_{cod_introdus}")
    with r3_c2:
        saved_epo = date_existente.get("titlu_engleza_epo", "")
        titlu_epo = st.text_input("TITLU ENGLEZA EPO", value=saved_epo or "", key=f"pi_epo_{cod_introdus}")

    # R4 -> NUMAR AUTORI UPT (25%), TITLU ENGLEZA FISA INVENTIEI (75%)
    r4_c1, r4_c2 = st.columns([25, 75])
    with r4_c1:
        saved_aut_upt = date_existente.get("numar_autori_upt", "")
        val_aut_upt = str(saved_aut_upt) if saved_aut_upt is not None else ""
        nr_autori_upt = st.text_input("NUMAR AUTORI UPT", value=val_aut_upt, key=f"pi_aut_upt_{cod_introdus}")
    with r4_c2:
        saved_fisa = date_existente.get("titlu_engleza_fisa_inventiei", "")
        titlu_fisa = st.text_input("TITLU ENGLEZA FISA INVENTIEI", value=saved_fisa or "", key=f"pi_fisa_{cod_introdus}")

    # R5 -> COMENTARII DOCUMENT - 100%
    saved_com_doc = date_existente.get("comentarii_document", "")
    com_doc = st.text_area("COMENTARII DOCUMENT", value=saved_com_doc or "", height=70, key=f"pi_com_doc_{cod_introdus}")
    
    # R6 -> COMENTARII DIVERSE - 100%
    saved_com_div = date_existente.get("comentarii_diverse", "")
    com_div = st.text_area("COMENTARII DIVERSE", value=saved_com_div or "", height=70, key=f"pi_com_div_{cod_introdus}")

    def _str(v):
        return str(v).strip() if v else None

    return {
        "numar_data_notificare_intern": _str(nr_notif),
        "document_oficial_original": _str(doc_oficial),
        "status_document": status_doc if status_doc else None,
        "domeniu_aplicare_idbdc": _str(domeniu),
        "spin_off": _str(spin_off),
        "contract_cesiune_externi": _str(contract_ces),
        "numar_autori_total": int(nr_autori_total) if nr_autori_total.strip().isdigit() else None,
        "numar_autori_upt": int(nr_autori_upt) if nr_autori_upt.strip().isdigit() else None,
        "titlu_engleza_epo": _str(titlu_epo),
        "titlu_engleza_fisa_inventiei": _str(titlu_fisa),
        "comentarii_document": _str(com_doc),
        "comentarii_diverse": _str(com_div),
    }
