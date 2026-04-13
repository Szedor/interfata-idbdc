# =========================================================
# IDBDC - MOTOR ADMIN - ORCHESTRATOR PRINCIPAL
# Versiune: 2.2 - Mesaje contextuale + corecții aspect
# =========================================================

import streamlit as st
import pandas as pd
import admin_config as cfg
import admin_rules as rules
import admin_data_ops as ops
import admin_ui as ui

def porneste_motorul(supabase):
    # 1. Inițializare Stil și Mesaje
    ui.apply_admin_styles()
    ui.display_admin_message()

    is_admin = st.session_state.get("operator_rol") == "ADMIN"
    filtru_cat = st.session_state.get("operator_filtru_categorie", [])
    filtru_tip = st.session_state.get("operator_filtru_tipuri", [])

    # 2. Sidebar - Selecție Categorie
    with st.sidebar:
        st.header("📂 Selecție Date")

        lista_categorii = (
            [c for c in cfg.BASE_TABLE_MAP.keys() if c in filtru_cat]
            if not is_admin else list(cfg.BASE_TABLE_MAP.keys())
        )
        cat_sel = st.selectbox("Categorie", ["- Alege -"] + lista_categorii)

    # [i] Doar categoria selectată — afișăm mesaj și oprim
    if cat_sel == "- Alege -":
        st.info("Selectați categoria din meniul lateral.")
        return

    # 3. Sidebar - Selecție Tip
    with st.sidebar:
        optiuni_tip = list(cfg.BASE_TABLE_MAP[cat_sel].keys())
        if not is_admin:
            optiuni_tip = [t for t in optiuni_tip if t in filtru_tip]
        tip_sel = st.selectbox("Tip", ["- Alege -"] + optiuni_tip)

    # [ii] Categoria aleasă, tipul nu — afișăm mesaj și oprim
    if tip_sel == "- Alege -":
        st.info("Selectați tipul de contract din meniul lateral.")
        return

    base_table = cfg.get_base_table(cat_sel, tip_sel)

    # 4. Sidebar - Selecție Cod Identificare
    with st.sidebar:
        try:
            res_coduri = supabase.table(base_table).select("cod_identificare").execute()
            list_coduri = sorted(
                [r["cod_identificare"] for r in res_coduri.data]
            ) if res_coduri.data else []
        except Exception:
            list_coduri = []

        cod_id = st.selectbox("Cod Identificare", ["- Alege -", "- NOU -"] + list_coduri)

        st.divider()
        btn_save = st.button("💾 SALVEAZĂ TOATE DATELE", use_container_width=True, type="primary")

        btn_delete = False
        if is_admin and cod_id not in ("- Alege -", "- NOU -"):
            btn_delete = st.button("🗑️ ȘTERGE FIȘA", use_container_width=True)

    # [iii] Tipul ales, codul nu — afișăm mesaj și oprim
    if cod_id == "- Alege -":
        st.info("Selectați «- NOU -» sau introduceți numărul contractului din meniul lateral.")
        return

    # [iv] De aici înainte — cod ales sau NOU — se deschid cele 4 taburi

    # 5. Încărcare Date
    data_dict = {}

    if cod_id == "- NOU -":
        df_base = pd.DataFrame([{"cod_identificare": "", "validat_idbdc": False}])
    else:
        res_b = supabase.table(base_table).select("*").eq("cod_identificare", cod_id).execute()
        df_base = pd.DataFrame(res_b.data)
    data_dict[base_table] = df_base

    for label, t_name in cfg.COMPLEMENTARY_TABLES:
        if cod_id == "- NOU -":
            df_temp = pd.DataFrame([{"cod_identificare": ""}])
        else:
            res_temp = supabase.table(t_name).select("*").eq("cod_identificare", cod_id).execute()
            df_temp = pd.DataFrame(res_temp.data)
        data_dict[t_name] = df_temp

    # 6. Valoare totală din tabelul com_date_financiare (coloana valoare_totala_contract)
    df_fin = data_dict.get("com_date_financiare", pd.DataFrame())

    # 7. Randare Tab-uri
    list_tabs = cfg.get_tabs_for_category(cat_sel)
    st_tabs = st.tabs(list_tabs)

    for i, tab_name in enumerate(list_tabs):
        with st_tabs[i]:
            if tab_name == "Date de bază":
                ui.render_base_info_box()
                col_cfg = rules.get_column_config(data_dict[base_table], is_new=(cod_id == "- NOU -"))
                data_dict[base_table] = st.data_editor(
                    data_dict[base_table],
                    column_config=col_cfg,
                    hide_index=True,
                    use_container_width=True,
                    num_rows="fixed" if cod_id != "- NOU -" else "dynamic",
                    key=f"editor_{base_table}"
                )

            elif tab_name == "Date financiare":
                ui.render_financial_info_box(df_fin)
                t_fin = "com_date_financiare"
                col_cfg = rules.get_column_config(data_dict[t_fin])
                data_dict[t_fin] = st.data_editor(
                    data_dict[t_fin],
                    column_config=col_cfg,
                    hide_index=True,
                    use_container_width=True,
                    num_rows="dynamic",
                    key=f"editor_{t_fin}"
                )

            elif tab_name == "Echipă":
                ui.render_team_info_box(len(data_dict["com_echipe_proiect"]))
                t_ech = "com_echipe_proiect"
                col_cfg = rules.get_column_config(data_dict[t_ech])
                data_dict[t_ech] = st.data_editor(
                    data_dict[t_ech],
                    column_config=col_cfg,
                    hide_index=True,
                    use_container_width=True,
                    num_rows="dynamic",
                    key=f"editor_{t_ech}"
                )

            elif tab_name == "Aspecte tehnice":
                ui.render_technical_info_box()
                t_teh = "com_aspecte_tehnice"
                col_cfg = rules.get_column_config(data_dict[t_teh])
                data_dict[t_teh] = st.data_editor(
                    data_dict[t_teh],
                    column_config=col_cfg,
                    hide_index=True,
                    use_container_width=True,
                    num_rows="dynamic",
                    key=f"editor_{t_teh}"
                )

    # 8. Salvare
    if btn_save:
        with st.spinner("Se salvează datele..."):
            df_b = data_dict[base_table]
            raw_id = df_b.iloc[0].get("cod_identificare", "") if not df_b.empty else ""
            final_cod = str(raw_id).strip()

            if not final_cod or final_cod == "nan":
                st.error("Eroare: Specificați un Cod Identificare valid.")
            else:
                ok, msg = ops.direct_save_all_tables(supabase, final_cod, data_dict, base_table)
                st.session_state["admin_msg"] = ("success" if ok else "error", msg)
                st.rerun()

    # 9. Ștergere
    if btn_delete:
        st.warning(f"Atenție: Ștergeți definitiv fișa {cod_id}!")
        if st.checkbox("Confirm eliminarea din toate tabelele"):
            tabele_curatare = [base_table] + [t[1] for t in cfg.COMPLEMENTARY_TABLES]
            ok, msg = ops.direct_delete_all_tables(supabase, cod_id, tabele_curatare)
            if ok:
                st.session_state["admin_msg"] = ("success", "Înregistrarea a fost eliminată.")
                st.rerun()
            else:
                st.error(msg)
