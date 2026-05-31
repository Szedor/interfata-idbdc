# =========================================================
# IDBDC/calea2_admin/motor.py
# v.modul.2.2 - Complet, corect, gata de utilizare
# =========================================================

import sys
import os
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domenii._baza.upsert import upsert_row, delete_all_for_project, insert_rows
import calea2_admin.ui as ui
from domenii.contracte_cep import admin as cep, definitie as cep_def
from domenii.contracte_terti import admin as terti, definitie as terti_def
from domenii.contracte_speciale import admin as speciale, definitie as speciale_def
from domenii.proiecte_fdi import admin as fdi, definitie as fdi_def

_DOMENII = {
    ("Contracte", "CEP"): (cep, cep_def),
    ("Contracte", "TERTI"): (terti, terti_def),
    ("Contracte", "SPECIALE"): (speciale, speciale_def),
    ("Proiecte", "FDI"): (fdi, fdi_def),
}

_TAB_CSS = """
<style>
[data-testid="stSidebar"] {
    min-width: 320px !important;
    max-width: 320px !important;
    width: 320px !important;
    overflow: hidden !important;
}
[data-testid="stSidebar"] > div:first-child {
    min-width: 320px !important;
    max-width: 320px !important;
    width: 320px !important;
}
</style>
"""


def _fetch(supabase, table, cod):
    try:
        res = supabase.table(table).select("*").eq("cod_identificare", cod).execute()
        return res.data or []
    except Exception:
        return []


def porneste_motorul(supabase):
    st.markdown(_TAB_CSS, unsafe_allow_html=True)
    ui.apply_admin_styles()
    ui.display_admin_message()

    is_admin = st.session_state.get("operator_rol") == "ADMIN"
    filtru_cat = st.session_state.get("operator_filtru_categorie", [])
    filtru_tip = st.session_state.get("operator_filtru_tipuri", [])

    categorii_disponibile = sorted({cat for cat, _ in _DOMENII.keys()})
    if not is_admin:
        categorii_disponibile = [c for c in categorii_disponibile if c in filtru_cat]

    with st.sidebar:
        st.header("📂 Selecție Date")
        cat_sel = st.selectbox("Categorie", ["- Alege -"] + categorii_disponibile)

    if cat_sel == "- Alege -":
        st.info("Selectați categoria din meniul lateral.")
        return

    tipuri_disponibile = sorted({tip for cat, tip in _DOMENII.keys() if cat == cat_sel})
    if not is_admin:
        tipuri_disponibile = [t for t in tipuri_disponibile if t in filtru_tip]

    with st.sidebar:
        tip_sel = st.selectbox("Tip", ["- Alege -"] + tipuri_disponibile)

    if tip_sel == "- Alege -":
        st.info("Selectați tipul din meniul lateral.")
        return

    entry = _DOMENII.get((cat_sel, tip_sel))
    if entry is None:
        st.warning(f"Domeniul «{cat_sel}» / «{tip_sel}» nu este configurat.")
        return

    modul, defn = entry

    with st.sidebar:
        try:
            res_coduri = supabase.table(defn.BASE_TABLE).select("cod_identificare").execute()
            list_coduri = sorted([r["cod_identificare"] for r in res_coduri.data]) if res_coduri.data else []
        except Exception:
            list_coduri = []

        cod_introdus = st.text_input(
            "Cod identificare",
            placeholder="Introduceți codul...",
            key="input_cod_identificare",
        ).strip()

    if not cod_introdus:
        st.info("Introduceți codul în meniul lateral.")
        return

    este_existent = cod_introdus in list_coduri

    with st.sidebar:
        if este_existent:
            st.success(f"✅ Cod recunoscut: {cod_introdus}")
            st.info("✏️ Fișă existentă — modificați/completați datele.")
        else:
            st.warning(f"🆕 Cod nou: {cod_introdus}")
            st.info("🆕 Fișă nouă — înregistrați datele.")

        st.divider()
        btn_save = st.button("💾 SALVEAZĂ TOATE DATELE", use_container_width=True, type="primary")
        btn_delete = False
        if is_admin and este_existent:
            btn_delete = st.button("🗑️ ȘTERGE FIȘA", use_container_width=True)

    is_new = not este_existent

    if not is_new:
        date_baza_ex = (_fetch(supabase, defn.BASE_TABLE, cod_introdus) or [{}])[0]
        date_fin_ex = _fetch(supabase, defn.FIN_TABLE, cod_introdus) if hasattr(defn, "FIN_TABLE") else []
        date_echipa_ex = _fetch(supabase, defn.ECHIPA_TABLE, cod_introdus)
        date_teh_ex = _fetch(supabase, defn.TEHNIC_TABLE, cod_introdus) if hasattr(defn, "TEHNIC_TABLE") else []
    else:
        date_baza_ex = {}
        date_fin_ex = date_echipa_ex = date_teh_ex = []

    TAB_LABELS = defn.TAB_LABELS_ADMIN
    key_tab = f"tab_activ_{cod_introdus}"

    if key_tab not in st.session_state or st.session_state[key_tab] not in TAB_LABELS:
        st.session_state[key_tab] = TAB_LABELS[0]

    st.markdown('<div class="tab-nav">', unsafe_allow_html=True)
    tab_activ = st.radio(
        "Secțiune", TAB_LABELS,
        index=TAB_LABELS.index(st.session_state[key_tab]),
        horizontal=True,
        key=f"radio_tab_{cod_introdus}",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.session_state[key_tab] = tab_activ

    st.markdown("<div style='border-top:2px solid rgba(255,255,255,0.30);margin-bottom:16px;'></div>", unsafe_allow_html=True)

    key_baza_ss = f"ss_baza_{cod_introdus}"
    key_fin_ss = f"ss_fin_{cod_introdus}"
    key_teh_ss = f"ss_teh_{cod_introdus}"
    rezultate = {}

    if tab_activ == "📋 Date de bază":
        r = modul.render_date_de_baza(supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex)
        if r:
            st.session_state[key_baza_ss] = r
        rezultate["baza"] = r

    elif tab_activ == "💰 Date financiare" and hasattr(modul, "render_date_financiare"):
        r = modul.render_date_financiare(supabase, cod_introdus, is_new, date_fin_ex)
        if r is not None:
            st.session_state[key_fin_ss] = r
        rezultate["financiar"] = r

    elif tab_activ == "👥 Echipă":
        rezultate["echipa"] = modul.render_echipa(supabase, cod_introdus, is_new, date_echipa_ex)

    elif tab_activ == "🧪 Aspecte tehnice" and hasattr(modul, "render_aspecte_tehnice"):
        r = modul.render_aspecte_tehnice(supabase, cod_introdus, is_new, date_teh_ex)
        if r is not None:
            st.session_state[key_teh_ss] = r
        rezultate["tehnice"] = r

    if btn_save:
        with st.spinner("Se salvează datele..."):
            erori = []

            baza = rezultate.get("baza") or st.session_state.get(key_baza_ss)
            if baza:
                ok, msg = upsert_row(supabase, defn.BASE_TABLE, {**baza, "cod_identificare": cod_introdus})
                if not ok:
                    erori.append(f"Date de bază: {msg}")

            if hasattr(defn, "FIN_TABLE"):
                fin = rezultate.get("financiar") or st.session_state.get(key_fin_ss)
                if fin is not None and isinstance(fin, list):
                    for row in fin:
                        if "an_referinta" in row:
                            del row["an_referinta"]
                        ok, msg = upsert_row(supabase, defn.FIN_TABLE, row)
                        if not ok:
                            erori.append(f"Date financiare: {msg}")

            if "echipa" in rezultate:
                ok_del, msg_del = delete_all_for_project(supabase, defn.ECHIPA_TABLE, cod_introdus)
                if not ok_del:
                    erori.append(f"Echipă — ștergere eșuată: {msg_del}")
                else:
                    randuri = [r for r in rezultate["echipa"] if r.get("nume_prenume")]
                    if randuri:
                        ok, msg = insert_rows(supabase, defn.ECHIPA_TABLE, randuri)
                        if not ok:
                            erori.append(f"Echipă: {msg}")

            if hasattr(defn, "TEHNIC_TABLE"):
                teh = rezultate.get("tehnice") or st.session_state.get(key_teh_ss)
                if teh is not None:
                    ok_del, msg_del = delete_all_for_project(supabase, defn.TEHNIC_TABLE, cod_introdus)
                    if not ok_del:
                        erori.append(f"Aspecte tehnice — ștergere eșuată: {msg_del}")
                    else:
                        for row in teh:
                            ok, msg = upsert_row(supabase, defn.TEHNIC_TABLE, row)
                            if not ok:
                                erori.append(f"Aspecte tehnice: {msg}")

            st.session_state["admin_msg"] = (
                ("error", " | ".join(erori)) if erori
                else ("success", "Toate datele au fost salvate cu succes.")
            )
            if f"echipa_editor_{cod_introdus}" in st.session_state:
                del st.session_state[f"echipa_editor_{cod_introdus}"]
            st.rerun()

    if btn_delete:
        st.warning(f"Atenție: Ștergeți definitiv fișa {cod_introdus}!")
        if st.checkbox("Confirm eliminarea din toate tabelele"):
            for t in defn.SECTIUNI_SALVARE:
                delete_all_for_project(supabase, t, cod_introdus)
            for k in [key_baza_ss, key_fin_ss, key_teh_ss,
                      f"echipa_data_init_{cod_introdus}",
                      f"echipa_editor_{cod_introdus}",
                      key_tab]:
                st.session_state.pop(k, None)
            st.session_state["admin_msg"] = ("success", "Înregistrarea a fost eliminată.")
            st.rerun()
