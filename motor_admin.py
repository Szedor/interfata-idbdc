import streamlit as st
import pandas as pd
from datetime import datetime


def porneste_motorul(supabase):

    # ============================
    # HELPERS
    # ============================

    def now_iso():
        return datetime.now().isoformat()

    def get_table_columns(table_name: str):
        try:
            res = supabase.rpc("idbdc_get_columns", {"p_table": table_name}).execute()
            return [r["column_name"] for r in (res.data or []) if r.get("column_name")]
        except Exception:
            return []

    def empty_row(columns):
        row = {c: None for c in columns}
        if "status_confirmare" in row:
            row["status_confirmare"] = False
        if "validat_idbdc" in row:
            row["validat_idbdc"] = False
        return row

    # ============================
    # HEADER
    # ============================

    st.markdown(
        f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.operator_identificat}</h3>",
        unsafe_allow_html=True
    )

    # ============================
    # SELECTOARE
    # ============================

    c1, c2, c3 = st.columns(3)

    with c1:
        cat_admin = st.selectbox(
            "Categoria:",
            ["", "Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"],
        )

    with c2:
        if cat_admin == "Contracte & Proiecte":
            tip_admin = st.selectbox(
                "Tip:",
                ["", "CEP", "TERTI", "FDI", "PNRR", "INTERNATIONALE", "INTERREG", "NONEU", "PNCDI"],
            )
        else:
            tip_admin = ""

    with c3:
        id_admin = st.text_input("Filtru cod_identificare:")

    st.divider()

    # ============================
    # MAPARE TABELE
    # ============================

    map_baze = {
        "CEP": "base_contracte_cep",
        "TERTI": "base_contracte_terti",
        "FDI": "base_proiecte_fdi",
        "PNRR": "base_proiecte_pnrr",
        "INTERNATIONALE": "base_proiecte_internationale",
        "INTERREG": "base_proiecte_interreg",
        "NONEU": "base_proiecte_noneu",
        "PNCDI": "base_proiecte_pncdi",
    }

    if cat_admin == "Contracte & Proiecte":
        nume_tabela = map_baze.get(tip_admin)
    elif cat_admin == "Evenimente stiintifice":
        nume_tabela = "base_evenimente_stiintifice"
    elif cat_admin == "Proprietate intelectuala":
        nume_tabela = "base_prop_intelect"
    else:
        nume_tabela = None

    if not nume_tabela:
        st.info("Selectează categoria și tipul.")
        return

    # ============================
    # ÎNCĂRCARE DATE
    # ============================

    res = supabase.table(nume_tabela).select("*")
    if id_admin:
        res = res.eq("cod_identificare", id_admin)

    df = pd.DataFrame(res.execute().data or [])

    cols_real = get_table_columns(nume_tabela)

    if df.empty:
        df = pd.DataFrame(columns=cols_real)

    if "df_admin" not in st.session_state:
        st.session_state.df_admin = df.copy()

    # ============================
    # BUTOANE
    # ============================

    b1, b2, b3, b4 = st.columns(4)

    with b1:
        if st.button("➕ RAND NOU"):
            st.session_state.df_admin = pd.concat(
                [pd.DataFrame([empty_row(cols_real)]), st.session_state.df_admin],
                ignore_index=True
            )

    with b2:
        btn_save = st.button("💾 SALVARE")

    with b3:
        btn_validate = st.button("✅ VALIDARE")

    with b4:
        btn_delete = st.button("🗑️ ȘTERGERE SELECTATE")

    # ============================
    # EDITOR
    # ============================

    edited_df = st.data_editor(
        st.session_state.df_admin,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic"
    )

    # ============================
    # SALVARE
    # ============================

    if btn_save:
        saved = 0

        for _, row in edited_df.iterrows():
            data = row.to_dict()
            cod = data.get("cod_identificare")

            if not cod or str(cod).strip() == "":
                continue

            if "data_ultimei_modificari" in cols_real:
                data["data_ultimei_modificari"] = now_iso()

            if "observatii_idbdc" in cols_real:
                data["observatii_idbdc"] = f"Editat de {st.session_state.operator_identificat}"

            supabase.table(nume_tabela).upsert(data).execute()
            saved += 1

        st.session_state.df_admin = edited_df.copy()
        st.success(f"Salvare completă ({saved} rânduri).")
        st.rerun()

    # ============================
    # VALIDARE
    # ============================

    if btn_validate:
        count = 0

        for _, row in edited_df.iterrows():
            cod = row.get("cod_identificare")
            if not cod:
                continue

            payload = {}
            if "status_confirmare" in cols_real:
                payload["status_confirmare"] = True
            if "validat_idbdc" in cols_real:
                payload["validat_idbdc"] = True
            if "data_ultimei_modificari" in cols_real:
                payload["data_ultimei_modificari"] = now_iso()
            if "observatii_idbdc" in cols_real:
                payload["observatii_idbdc"] = f"Validat de {st.session_state.operator_identificat}"

            supabase.table(nume_tabela).update(payload).eq("cod_identificare", cod).execute()
            count += 1

        st.success(f"Validare realizată pentru {count} rânduri.")
        st.rerun()

    # ============================
    # ȘTERGERE
    # ============================

    if btn_delete:
        deleted = 0

        for _, row in edited_df.iterrows():
            if row.get("status_confirmare") is False:
                continue

            cod = row.get("cod_identificare")
            if not cod:
                continue

            supabase.table(nume_tabela).delete().eq("cod_identificare", cod).execute()
            deleted += 1

        st.success(f"Șterse {deleted} rânduri.")
        st.rerun()
