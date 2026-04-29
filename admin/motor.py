# =========================================================
# admin/motor.py
# vers.modul.3.0
# 2026.04.29
# Tab activ retinut in session_state — nu mai revine la Date de baza
# =========================================================

import streamlit as st
import admin.config as cfg
import admin.data_ops as ops
import admin.ui as ui

from admin.fise import contracte_cep, contracte_terti, contracte_speciale


# Stiluri pentru navigarea tip tab (radio orizontal)
_TAB_CSS = """
<style>
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

    date_baza_ex   = (_fetch(base_table, cod_introdus)[0]
                      if not is_new and _fetch(base_table, cod_introdus) else {})
    date_fin_ex    = _fetch("com_date_financiare", cod_introdus) if not is_new else []
    date_echipa_ex = _fetch("com_echipe_proiect",  cod_introdus) if not is_new else []

    rezultate = {}

    # =========================================================
    # Modulul de fișă
    # =========================================================
    if cat_sel == "Contracte" and tip_sel == "CEP":
        modul = contracte_cep
    elif cat_sel == "Contracte" and tip_sel == "TERTI":
        modul = contracte_terti
    elif cat_sel == "Contracte" and tip_sel == "SPECIALE":
        modul = contracte_speciale
    else:
        st.info(f"Fișele pentru categoria «{cat_sel}» / tipul «{tip_sel}» sunt în curs de configurare.")
        return

    # =========================================================
    # Navigare tab-uri cu reținere în session_state
    # Folosim st.radio orizontal în loc de st.tabs,
    # astfel tab-ul activ supraviețuiește reruns.
    # =========================================================
    TAB_LABELS = ["📋 Date de bază", "💰 Date financiare", "👥 Echipă"]
    key_tab = f"tab_activ_{cod_introdus}"

    # Inițializare tab activ (prima dată sau cod nou)
    if key_tab not in st.session_state:
        st.session_state[key_tab] = TAB_LABELS[0]

    # Dacă după salvare vrem să rămânem pe același tab
    # (session_state[key_tab] este deja setat corect)

    st.markdown(_TAB_CSS, unsafe_allow_html=True)
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

    # Salvăm tab-ul selectat de utilizator
    st.session_state[key_tab] = tab_activ

    st.markdown(
        "<div style='border-top: 2px solid rgba(255,255,255,0.30); margin-bottom: 16px;'></div>",
        unsafe_allow_html=True,
    )

    # =========================================================
    # Conținut tab activ
    # =========================================================
    if tab_activ == "📋 Date de bază":
        rezultate["baza"] = modul.render_date_de_baza(
            supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex
        )

    elif tab_activ == "💰 Date financiare":
        rezultate["financiar"] = modul.render_date_financiare(
            supabase, cod_introdus, is_new, date_fin_ex
        )

    elif tab_activ == "👥 Echipă":
        rezultate["echipa"] = modul.render_echipa(
            supabase, cod_introdus, is_new, date_echipa_ex
        )

    # =========================================================
    # Salvare — colectăm datele din toate secțiunile
    # prin fetch din session_state unde sunt disponibile
    # =========================================================
    if btn_save:
        with st.spinner("Se salvează datele..."):
            erori = []

            # Date de bază — dacă nu sunt în rezultate (alt tab activ),
            # le luăm din ce există deja în baza de date
            if "baza" in rezultate and rezultate["baza"]:
                row = {**rezultate["baza"], "cod_identificare": cod_introdus}
                ok, msg = ops.direct_upsert_single_row(supabase, base_table, row)
                if not ok:
                    erori.append(f"Date de bază: {msg}")
            elif not is_new:
                # Nu s-a modificat Date de bază în acest rerun — lăsăm ce e în DB
                pass

            # Date financiare
            if "financiar" in rezultate:
                try:
                    supabase.table("com_date_financiare").delete().eq("cod_identificare", cod_introdus).execute()
                except Exception:
                    pass
                for row in rezultate["financiar"]:
                    ok, msg = ops.direct_upsert_single_row(
                        supabase, "com_date_financiare", row, match_col="cod_identificare"
                    )
                    if not ok:
                        erori.append(f"Date financiare: {msg}")

            # Echipă
            if "echipa" in rezultate:
                try:
                    supabase.table("com_echipe_proiect").delete().eq("cod_identificare", cod_introdus).execute()
                except Exception:
                    pass
                randuri_echipa = [r for r in rezultate["echipa"] if r.get("nume_prenume")]
                if randuri_echipa:
                    try:
                        supabase.table("com_echipe_proiect").insert(randuri_echipa).execute()
                    except Exception as e:
                        erori.append(f"Echipă: {e}")

            if erori:
                st.session_state["admin_msg"] = ("error", " | ".join(erori))
            else:
                st.session_state["admin_msg"] = ("success", "Toate datele au fost salvate cu succes.")

            st.rerun()

    # =========================================================
    # Ștergere
    # =========================================================
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
                st.session_state["admin_msg"] = ("success", "Înregistrarea a fost eliminată.")
                st.rerun()
            else:
                st.error(msg)
