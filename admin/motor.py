# =========================================================
# IDBDC/admin/motor.py
# VERSIUNE: 6.0
# STATUS: STABIL - Dispatch complet pentru toate categoriile/tipurile
# DATA: 2026.05.05
# =========================================================
# CONȚINUT:
#   Motorul principal al modulului Admin. Gestionează
#   navigarea între categorii/tipuri, afișarea tab-urilor
#   și salvarea datelor în PostgreSQL prin Supabase.
#
# MODIFICĂRI VERSIUNEA 6.0:
#   - Adăugat import și dispatch pentru toate tipurile de
#     Proiecte: FDI, PNCDI, PNRR, INTERNATIONALE, INTERREG,
#     NONEU, SEE, STRUCTURALE.
#   - Adăugat import și dispatch pentru Evenimente stiintifice
#     și Proprietate industriala (2 tab-uri fiecare).
#   - Tab-urile sunt acum citite din TABS_MAP (admin/config.py)
#     în loc să fie hardcodate — elimină mesajul
#     «în curs de configurare» pentru categoriile/tipurile noi.
#   - Logica de salvare pentru Aspecte tehnice adăugată.
#   - Tot ce era valid în v5.0 este păstrat neatins.
# =========================================================

import streamlit as st
import admin.config as cfg
import admin.data_ops as ops
import admin.ui as ui

# ── Contracte ──────────────────────────────────────────────
from admin.fise import contracte_cep, contracte_terti, contracte_speciale

# ── Proiecte ───────────────────────────────────────────────
from admin.fise import (
    proiecte_fdi,
    proiecte_pncdi,
    proiecte_pnrr,
    proiecte_internationale,
    proiecte_interreg,
    proiecte_noneu,
    proiecte_see,
    proiecte_structurale,
)

# ── Evenimente și Proprietate ──────────────────────────────
from admin.fise import evenimente_stiintifice, proprietate_industriala


# ── Mapare categorie/tip → modul ───────────────────────────
_MODUL_MAP = {
    ("Contracte", "CEP"):           contracte_cep,
    ("Contracte", "TERTI"):         contracte_terti,
    ("Contracte", "SPECIALE"):      contracte_speciale,
    ("Proiecte", "FDI"):            proiecte_fdi,
    ("Proiecte", "PNCDI"):          proiecte_pncdi,
    ("Proiecte", "PNRR"):           proiecte_pnrr,
    ("Proiecte", "INTERNATIONALE"): proiecte_internationale,
    ("Proiecte", "INTERREG"):       proiecte_interreg,
    ("Proiecte", "NONEU"):          proiecte_noneu,
    ("Proiecte", "SEE"):            proiecte_see,
    ("Proiecte", "STRUCTURALE"):    proiecte_structurale,
    ("Evenimente stiintifice", "CONFERINTE"): evenimente_stiintifice,
    ("Proprietate industriala", "BREVETE"):   proprietate_industriala,
}


# =========================================================
# CSS global pentru tab-uri și sidebar lățime fixă
# ADĂUGAT v5.0: secțiunea [data-testid="stSidebar"] fixează
# lățimea la 320px indiferent de conținut sau etapă.
# =========================================================
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
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    padding: 0 !important;
}
div.tab-nav > div[role="radiogroup"] {
    display: flex; flex-direction: row; gap: 6px;
}
div.tab-nav label {
    background: rgba(255,255,255,0.10) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.30) !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 6px 18px !important;
    font-weight: 700 !important;
    font-size: 0.93rem !important;
    cursor: pointer !important;
}
div.tab-nav label:has(input:checked) {
    background: rgba(255,255,255,0.96) !important;
    color: #0b1f3a !important;
    border-bottom: 2px solid rgba(255,255,255,0.96) !important;
}
div.tab-nav [data-testid="stMarkdownContainer"] { display: none; }
</style>
"""


def porneste_motorul(supabase):
    st.markdown(_TAB_CSS, unsafe_allow_html=True)

    ui.apply_admin_styles()
    ui.display_admin_message()

    is_admin = st.session_state.get("operator_rol") == "ADMIN"
    filtru_cat = st.session_state.get("operator_filtru_categorie", [])
    filtru_tip = st.session_state.get("operator_filtru_tipuri", [])

    with st.sidebar:
        st.header("📂 Selecție Date")
        lista_categorii = (
            [c for c in cfg.BASE_TABLE_MAP.keys() if c in filtru_cat]
            if not is_admin else list(cfg.BASE_TABLE_MAP.keys())
        )
        cat_sel = st.selectbox("Categorie", ["- Alege -"] + lista_categorii)

    if cat_sel == "- Alege -":
        st.info("Selectați categoria din meniul lateral.")
        return

    with st.sidebar:
        optiuni_tip = list(cfg.BASE_TABLE_MAP[cat_sel].keys())
        if not is_admin:
            optiuni_tip = [t for t in optiuni_tip if t in filtru_tip]
        tip_sel = st.selectbox("Tip", ["- Alege -"] + optiuni_tip)

    if tip_sel == "- Alege -":
        st.info("Selectați tipul din meniul lateral.")
        return

    base_table = cfg.get_base_table(cat_sel, tip_sel)
    modul = _MODUL_MAP.get((cat_sel, tip_sel))

    if modul is None:
        st.warning(f"Modulul pentru «{cat_sel}» / «{tip_sel}» nu a fost găsit.")
        return

    with st.sidebar:
        try:
            res_coduri = supabase.table(base_table).select("cod_identificare").execute()
            list_coduri = sorted(
                [r["cod_identificare"] for r in res_coduri.data]
            ) if res_coduri.data else []
        except Exception:
            list_coduri = []

        cod_introdus = st.text_input(
            "Cod identificare",
            placeholder="Introduceți codul...",
            key="input_cod_identificare"
        ).strip()

    if not cod_introdus:
        st.info("Introduceți codul în meniul lateral.")
        return

    este_existent = cod_introdus in list_coduri

    with st.sidebar:
        if este_existent:
            st.success(f"✅ Cod recunoscut: {cod_introdus}")
            st.info("✏️ S-a identificat o fișă existentă, în secțiunile căreia poți modifica/completa datele.")
        else:
            st.warning(f"🆕 Cod nou: {cod_introdus}")
            st.info("🆕 S-a creat o fișă nouă, în secțiunile căreia poți înregistra date.")

        st.divider()
        btn_save = st.button(
            "💾 SALVEAZĂ TOATE DATELE",
            use_container_width=True,
            type="primary"
        )

        btn_delete = False
        if is_admin and este_existent:
            btn_delete = st.button("🗑️ ȘTERGE FIȘA", use_container_width=True)

    is_new = not este_existent

    def _fetch(table, cod):
        try:
            res = supabase.table(table).select("*").eq("cod_identificare", cod).execute()
            return res.data or []
        except Exception:
            return []

    if not is_new:
        _baza_list     = _fetch(base_table, cod_introdus)
        date_baza_ex   = _baza_list[0] if _baza_list else {}
        date_fin_ex    = _fetch("com_date_financiare", cod_introdus)
        date_echipa_ex = _fetch("com_echipe_proiect",  cod_introdus)
        date_teh_ex    = _fetch("com_aspecte_tehnice", cod_introdus)
    else:
        date_baza_ex   = {}
        date_fin_ex    = []
        date_echipa_ex = []
        date_teh_ex    = []

    rezultate  = {}
    TAB_LABELS = cfg.get_tabs_for_category(cat_sel, tip_sel)
    key_tab    = f"tab_activ_{cod_introdus}"

    if key_tab not in st.session_state:
        st.session_state[key_tab] = TAB_LABELS[0]

    # Dacă tab-ul salvat nu mai există în lista curentă, resetăm
    if st.session_state[key_tab] not in TAB_LABELS:
        st.session_state[key_tab] = TAB_LABELS[0]

    st.markdown('<div class="tab-nav">', unsafe_allow_html=True)
    tab_activ = st.radio(
        "Secțiune",
        TAB_LABELS,
        index=TAB_LABELS.index(st.session_state[key_tab]),
        horizontal=True,
        key=f"radio_tab_{cod_introdus}",
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.session_state[key_tab] = tab_activ

    st.markdown(
        "<div style='border-top: 2px solid rgba(255,255,255,0.30); margin-bottom: 16px;'></div>",
        unsafe_allow_html=True,
    )

    key_baza_ss = f"ss_baza_{cod_introdus}"
    key_fin_ss  = f"ss_fin_{cod_introdus}"
    key_teh_ss  = f"ss_teh_{cod_introdus}"

    if tab_activ == "📋 Date de bază":
        rezultat_baza = modul.render_date_de_baza(
            supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex
        )
        if rezultat_baza:
            st.session_state[key_baza_ss] = rezultat_baza
        rezultate["baza"] = rezultat_baza

    elif tab_activ == "💰 Date financiare":
        rezultat_fin = modul.render_date_financiare(
            supabase, cod_introdus, is_new, date_fin_ex
        )
        if rezultat_fin is not None:
            st.session_state[key_fin_ss] = rezultat_fin
        rezultate["financiar"] = rezultat_fin

    elif tab_activ == "👥 Echipă":
        rezultate["echipa"] = modul.render_echipa(
            supabase, cod_introdus, is_new, date_echipa_ex
        )

    elif tab_activ == "🧪 Aspecte tehnice":
        rezultat_teh = modul.render_aspecte_tehnice(
            supabase, cod_introdus, is_new, date_teh_ex
        )
        if rezultat_teh is not None:
            st.session_state[key_teh_ss] = rezultat_teh
        rezultate["tehnice"] = rezultat_teh

    if btn_save:
        with st.spinner("Se salvează datele..."):
            erori = []

            # Date de bază
            baza_de_salvat = rezultate.get("baza") or st.session_state.get(key_baza_ss)
            if baza_de_salvat:
                row = {**baza_de_salvat, "cod_identificare": cod_introdus}
                ok, msg = ops.direct_upsert_single_row(supabase, base_table, row)
                if not ok:
                    erori.append(f"Date de bază: {msg}")

            # Date financiare
            fin_de_salvat = rezultate.get("financiar") or st.session_state.get(key_fin_ss)
            if fin_de_salvat is not None:
                try:
                    supabase.table("com_date_financiare").delete().eq(
                        "cod_identificare", cod_introdus
                    ).execute()
                except Exception:
                    pass
                for row in fin_de_salvat:
                    ok, msg = ops.direct_upsert_single_row(
                        supabase, "com_date_financiare", row, match_col="cod_identificare"
                    )
                    if not ok:
                        erori.append(f"Date financiare: {msg}")

            # Echipă
            if "echipa" in rezultate:
                try:
                    supabase.table("com_echipe_proiect").delete().eq(
                        "cod_identificare", cod_introdus
                    ).execute()
                except Exception:
                    pass
                randuri_echipa = [r for r in rezultate["echipa"] if r.get("nume_prenume")]
                if randuri_echipa:
                    try:
                        supabase.table("com_echipe_proiect").insert(randuri_echipa).execute()
                    except Exception as e:
                        erori.append(f"Echipă: {e}")

            # Aspecte tehnice
            teh_de_salvat = rezultate.get("tehnice") or st.session_state.get(key_teh_ss)
            if teh_de_salvat is not None:
                try:
                    supabase.table("com_aspecte_tehnice").delete().eq(
                        "cod_identificare", cod_introdus
                    ).execute()
                except Exception:
                    pass
                for row in teh_de_salvat:
                    ok, msg = ops.direct_upsert_single_row(
                        supabase, "com_aspecte_tehnice", row, match_col="cod_identificare"
                    )
                    if not ok:
                        erori.append(f"Aspecte tehnice: {msg}")

            if erori:
                st.session_state["admin_msg"] = ("error", " | ".join(erori))
            else:
                st.session_state["admin_msg"] = ("success", "Toate datele au fost salvate cu succes.")

            key_editor_echipa = f"echipa_editor_{cod_introdus}"
            if key_editor_echipa in st.session_state:
                del st.session_state[key_editor_echipa]

            st.rerun()

    if btn_delete:
        st.warning(f"Atenție: Ștergeți definitiv fișa {cod_introdus}!")
        if st.checkbox("Confirm eliminarea din toate tabelelor"):
            tabele_curatare = [
                base_table,
                "com_date_financiare",
                "com_echipe_proiect",
                "com_aspecte_tehnice",
            ]
            ok, msg = ops.direct_delete_all_tables(supabase, cod_introdus, tabele_curatare)
            if ok:
                for k in [key_baza_ss, key_fin_ss, key_teh_ss,
                           f"echipa_data_init_{cod_introdus}",
                           f"echipa_editor_{cod_introdus}",
                           f"tab_activ_{cod_introdus}"]:
                    st.session_state.pop(k, None)
                st.session_state["admin_msg"] = ("success", "Înregistrarea a fost eliminată.")
                st.rerun()
            else:
                st.error(msg)
