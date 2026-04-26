# =========================================================
# admin/motor.py
# vers.modul.2.0
# 2026.04.27
# Fix navigare tab-uri + stabilitate session_state
# =========================================================

import streamlit as st
import admin.config as cfg
import admin.data_ops as ops
import admin.ui as ui

from admin.fise import contracte_cep, contracte_terti, contracte_speciale


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
    # Determinăm modulul de fișă în funcție de selecție
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
    # Tab-uri — fiecare tab randează INDEPENDENT, nu în buclă.
    # Streamlit gestionează intern tab-ul activ; nu folosim
    # query_params pentru asta (cauzau reruns în buclă).
    # =========================================================
    tab_baza, tab_fin, tab_echipa = st.tabs(
        ["📋 Date de bază", "💰 Date financiare", "👥 Echipă"]
    )

    with tab_baza:
        rezultate["baza"] = modul.render_date_de_baza(
            supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex
        )

    with tab_fin:
        rezultate["financiar"] = modul.render_date_financiare(
            supabase, cod_introdus, is_new, date_fin_ex
        )

    with tab_echipa:
        rezultate["echipa"] = modul.render_echipa(
            supabase, cod_introdus, is_new, date_echipa_ex
        )

    # =========================================================
    # Salvare
    # =========================================================
    if btn_save:
        with st.spinner("Se salvează datele..."):
            erori = []

            if "baza" in rezultate and rezultate["baza"]:
                row = {**rezultate["baza"]}
                row["cod_identificare"] = cod_introdus
                ok, msg = ops.direct_upsert_single_row(supabase, base_table, row)
                if not ok:
                    erori.append(f"Date de bază: {msg}")

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
        if st.checkbox("Confirm eliminarea din toate tabelele"):
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
