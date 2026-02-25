import streamlit as st
import pandas as pd
from datetime import datetime

def porneste_motorul(supabase):

    # Preluare opțiuni pentru dropdown-uri
    def fetch_opt(t, c):
        res = supabase.table(t).select(c).execute()
        vals = []
        for r in (res.data or []):
            v = r.get(c)
            if v is None:
                continue
            v = str(v).strip()
            if v:
                vals.append(v)
        return sorted(list(set(vals)))

    # Liste pentru dropdown (nomenclatoare)
    lista_acronime = [""] + fetch_opt("nom_contracte_proiecte", "acronim_contracte_proiecte")
    lista_categorii = [""] + fetch_opt("nom_categorie", "denumire_categorie")
    lista_status_proiect = [""] + fetch_opt("nom_status_proiect", "status_contract_proiect")

    st.markdown(
        f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.operator_identificat}</h3>",
        unsafe_allow_html=True
    )

    # CASETELE 1-4 (păstrate)
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2])
    with c1:
        cat_admin = st.selectbox(
            "1. Categoria:",
            ["", "Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"],
            key="admin_cat"
        )
    with c2:
        tip_admin = st.selectbox("2. Tip (Acronim):", lista_acronime, key="admin_tip")
    with c3:
        id_admin = st.text_input("3. ID Proiect (Cod Identificare):", key="admin_id")
    with c4:
        componente_com = st.multiselect(
            "4. Componente (COM):",
            ["Date financiare", "Resurse umane", "Aspecte tehnice"],
            key="admin_com"
        )

    st.markdown("---")

    # PANOU BUTOANE CRUD (păstrat)
    col_n, col_s, col_v, col_d, col_a = st.columns(5)

    with col_n:
        if st.button("➕ RAND NOU"):
            st.toast("Folosiți '+' din subsolul tabelului.")

    with col_s:
        btn_salvare = st.button("💾 SALVARE")

    with col_v:
        if st.button("✅ VALIDARE"):
            st.success("Date pregătite pentru validare finală. (Etapa următoare)")

    with col_d:
        if st.button("🗑️ ȘTERGERE"):
            st.warning("Ștergeți rândul din editor (tasta Delete) apoi apăsați SALVARE.")

    with col_a:
        if st.button("❌ ANULARE"):
            st.rerun()

    st.write("")

    # Mapare tabel (păstrată)
    map_baze = {
        "FDI": "base_proiecte_fdi",
        "PNRR": "base_proiecte_pnrr",
        "INTERNATIONALE": "base_proiecte_internationale"
    }

    nume_tabela = map_baze.get(tip_admin) if cat_admin == "Contracte & Proiecte" else None

    # --- AFIȘARE TABEL ---
    if nume_tabela:
        res_main = supabase.table(nume_tabela).select("*")
        if id_admin:
            res_main = res_main.eq("cod_identificare", id_admin)

        df_main = pd.DataFrame(res_main.execute().data or [])

        st.markdown(f"**📂 Tabel Principal: {nume_tabela}**")

        # ✅ AICI ESTE CHEIA: dropdown-uri doar pentru base_proiecte_internationale
        column_config = None
        if nume_tabela == "base_proiecte_internationale":
            column_config = {
                "denumire_categorie": st.column_config.SelectboxColumn(
                    "denumire_categorie (dropdown)",
                    options=lista_categorii
                ),
                "acronim_contracte_proiecte": st.column_config.SelectboxColumn(
                    "acronim_contracte_proiecte (dropdown)",
                    options=lista_acronime
                ),
                "status_contract_proiect": st.column_config.SelectboxColumn(
                    "status_contract_proiect (dropdown)",
                    options=lista_status_proiect
                ),
            }

        ed_df = st.data_editor(
            df_main,
            use_container_width=True,
            hide_index=True,
            key=f"ed_{nume_tabela}",
            num_rows="dynamic",
            column_config=column_config
        )

        # --- LOGICA DE SALVARE (păstrată + un pic întărită) ---
        if btn_salvare:
            # 1) ȘTERGERE (dacă un cod_identificare dispare din tabel)
            if not df_main.empty and "cod_identificare" in df_main.columns and "cod_identificare" in ed_df.columns:
                ids_vechi = set(df_main["cod_identificare"].dropna().astype(str))
                ids_noi = set(ed_df["cod_identificare"].dropna().astype(str))
                for s in (ids_vechi - ids_noi):
                    supabase.table(nume_tabela).delete().eq("cod_identificare", s).execute()

            # 2) SALVARE (Update/Insert)
            for _, r in ed_df.iterrows():
                if pd.notna(r.get("cod_identificare")):
                    v = r.to_dict()

                    # curățare NaN -> None
                    for k in list(v.keys()):
                        if pd.isna(v[k]):
                            v[k] = None

                    v["data_ultimei_modificari"] = datetime.now().isoformat()
                    v["observatii_idbdc"] = f"Editat de {st.session_state.operator_identificat}"

                    supabase.table(nume_tabela).upsert(v).execute()

            st.success("✅ Sincronizare reușită!")
            st.rerun()

    else:
        st.info("Alege Categoria + Tip ca să apară tabelul.")
