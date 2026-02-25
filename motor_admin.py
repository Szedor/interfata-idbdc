import streamlit as st
import pandas as pd
from datetime import datetime


def porneste_motorul(supabase):
    """
    Motor Admin (Calea 2) - varianta robusta:
      - dropdown stabil pentru coloanele cerute
      - rand nou inserat SUS (ca sa nu derulezi la final)
      - Draft/Validat pe booleeni (mai safe)
    """

    # ----------------------------
    # Helpers
    # ----------------------------
    def fetch_opt(table_name: str, col_name: str) -> list[str]:
        """Ia optiuni distincte dintr-un tabel (nom_...) pentru dropdown."""
        try:
            res = supabase.table(table_name).select(col_name).execute()
            vals = [r.get(col_name) for r in (res.data or [])]
            vals = [v for v in vals if v is not None and str(v).strip() != ""]
            # unice + sort
            return sorted(list(set([str(v).strip() for v in vals])))
        except Exception:
            return []

    def merge_with_existing(options: list[str], df: pd.DataFrame, col: str) -> list[str]:
        """
        Ca dropdown-ul sa NU dispara:
        adaugam in lista de optiuni si valorile care exista deja in tabel.
        """
        if df is None or df.empty or col not in df.columns:
            return options

        existing = (
            df[col]
            .dropna()
            .astype(str)
            .map(lambda x: x.strip())
            .tolist()
        )
        existing = [x for x in existing if x != ""]
        merged = list(dict.fromkeys([""] + options + sorted(list(set(existing)))))  # pastreaza ordinea
        return merged

    def empty_row_for(df: pd.DataFrame) -> dict:
        """Creeaza un rand gol cu aceleasi coloane ca df (ca sa-l inseram sus)."""
        row = {}
        for c in df.columns:
            row[c] = None
        # daca exista aceste coloane, le setam logic:
        if "status_confirmare" in row:
            row["status_confirmare"] = False  # Draft
        if "validat_idbdc" in row:
            row["validat_idbdc"] = False
        if "data_ultimei_modificari" in row:
            row["data_ultimei_modificari"] = None
        if "observatii_idbdc" in row:
            row["observatii_idbdc"] = None
        return row

    # ----------------------------
    # Dropdown options (nom tables)
    # ----------------------------
    lista_categorii = fetch_opt("nom_categorie", "denumire_categorie")
    lista_acronime = fetch_opt("nom_contracte_proiecte", "acronim_contracte_proiecte")
    lista_status = fetch_opt("nom_status_proiect", "status_contract_proiect")

    # ----------------------------
    # Header
    # ----------------------------
    st.markdown(
        f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.operator_identificat}</h3>",
        unsafe_allow_html=True
    )

    # ----------------------------
    # CASETELE 1-4
    # ----------------------------
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2])

    with c1:
        cat_admin = st.selectbox(
            "1. Categoria:",
            ["", "Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"],
            key="admin_cat"
        )

    with c2:
        tip_admin = st.selectbox(
            "2. Tip (Acronim):",
            [""] + lista_acronime,
            key="admin_tip"
        )

    with c3:
        id_admin = st.text_input(
            "3. ID Proiect (Cod Identificare):",
            key="admin_id"
        )

    with c4:
        componente_com = st.multiselect(
            "4. Componente (COM):",
            ["Date financiare", "Resurse umane", "Aspecte tehnice"],
            key="admin_com"
        )

    st.markdown("---")

    # ----------------------------
    # MAPARE tabele
    # ----------------------------
    map_baze = {
        "FDI": "base_proiecte_fdi",
        "PNRR": "base_proiecte_pnrr",
        "INTERNATIONALE": "base_proiecte_internationale",
    }

    nume_tabela = None
    if cat_admin == "Contracte & Proiecte":
        nume_tabela = map_baze.get(tip_admin)

    if cat_admin == "Evenimente stiintifice":
        nume_tabela = "base_evenimente_stiintifice"

    if cat_admin == "Proprietate intelectuala":
        nume_tabela = "base_prop_intelect"

    # ----------------------------
    # BUTOANE CRUD
    # ----------------------------
    col_n, col_s, col_v, col_d, col_a = st.columns(5)

    with col_n:
        if st.button("➕ RAND NOU"):
            # flag ca sa inseram un rand gol SUS, la urmatorul render
            st.session_state["adauga_rand_sus"] = True
            st.rerun()

    with col_s:
        btn_salvare = st.button("💾 SALVARE")

    with col_v:
        btn_validare = st.button("✅ VALIDARE")

    with col_d:
        st.button("🗑️ ȘTERGERE")  # stergerea reala se face din tabel + SALVARE

    with col_a:
        if st.button("❌ ANULARE"):
            st.rerun()

    st.write("")

    # ----------------------------
    # AFISARE + EDITARE TABEL
    # ----------------------------
    if not nume_tabela:
        st.info("Alege Categoria + Tip ca sa incarcam un tabel.")
        return

    res_main = supabase.table(nume_tabela).select("*")
    if id_admin:
        res_main = res_main.eq("cod_identificare", id_admin)

    df_main = pd.DataFrame(res_main.execute().data or [])

    # daca nu avem inca date, tot vrem coloanele — altfel editorul e “gol” si dificil
    if df_main.empty:
        # incercam sa luam macar 1 rand ca sa stim coloanele
        # (daca nu exista niciun rand, ramanem cu DF gol)
        df_main = pd.DataFrame(df_main)

    # Inserare rand nou SUS (daca s-a apasat butonul)
    if st.session_state.get("adauga_rand_sus") and not df_main.empty:
        top = pd.DataFrame([empty_row_for(df_main)])
        df_main = pd.concat([top, df_main], ignore_index=True)
        st.session_state["adauga_rand_sus"] = False

    # IMPORTANT: refacem listele de dropdown ca sa includa si valorile existente (altfel pot disparea)
    opt_categorii = merge_with_existing(lista_categorii, df_main, "denumire_categorie")
    opt_acronime = merge_with_existing(lista_acronime, df_main, "acronim_contracte_proiecte")
    opt_status = merge_with_existing(lista_status, df_main, "status_contract_proiect")

    # Config dropdown pe coloane (exact cum ai cerut in documentul tau)
    column_config = {
        "denumire_categorie": st.column_config.SelectboxColumn(
            "denumire_categorie",
            options=opt_categorii
        ),
        "acronim_contracte_proiecte": st.column_config.SelectboxColumn(
            "acronim_contracte_proiecte",
            options=opt_acronime
        ),
        "status_contract_proiect": st.column_config.SelectboxColumn(
            "status_contract_proiect",
            options=opt_status
        ),
    }

    st.markdown(f"**📂 Tabel Principal: {nume_tabela}**")

    ed_df = st.data_editor(
        df_main,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key=f"ed_{nume_tabela}",
        column_config=column_config
    )

    # ----------------------------
    # SALVARE (Update/Insert/Delete)
    # ----------------------------
    if btn_salvare:
        # 1) Stergere: daca un cod_identificare a disparut complet din tabelul editat
        # (ATENTIE: asta functioneaza corect daca "cod_identificare" este unic pe rand)
        if not df_main.empty and "cod_identificare" in df_main.columns and "cod_identificare" in ed_df.columns:
            ids_vechi = set(df_main["cod_identificare"].dropna().astype(str))
            ids_noi = set(ed_df["cod_identificare"].dropna().astype(str))
            de_sters = ids_vechi - ids_noi
            for cid in de_sters:
                supabase.table(nume_tabela).delete().eq("cod_identificare", cid).execute()

        # 2) Upsert: bagam/actualizam fiecare rand
        for _, r in ed_df.iterrows():
            v = r.to_dict()

            # nu salvam randuri fara cod_identificare
            if "cod_identificare" not in v or v["cod_identificare"] is None or str(v["cod_identificare"]).strip() == "":
                continue

            # audit simplu
            v["data_ultimei_modificari"] = datetime.now().isoformat()
            v["observatii_idbdc"] = f"Editat de {st.session_state.operator_identificat}"

            # Draft implicit daca nu e setat
            if "status_confirmare" in v and v["status_confirmare"] is None:
                v["status_confirmare"] = False
            if "validat_idbdc" in v and v["validat_idbdc"] is None:
                v["validat_idbdc"] = False

            supabase.table(nume_tabela).upsert(v).execute()

        st.success("✅ Salvare reușită!")
        st.rerun()

    # ----------------------------
    # VALIDARE (marcheaza randurile ca validate)
    # ----------------------------
    if btn_validare:
        # Traducere: "validare" = nu doar salvez, ci marchez oficial ca e “bun / final”
        # Varianta simpla si sigura: valideaza tot ce e in vizualizarea curenta (filtrata pe id_admin daca e completat)
        q = supabase.table(nume_tabela).update({
            "status_confirmare": True,
            "validat_idbdc": True,
            "data_ultimei_modificari": datetime.now().isoformat(),
            "observatii_idbdc": f"Validat de {st.session_state.operator_identificat}"
        })
        if id_admin:
            q = q.eq("cod_identificare", id_admin)

        q.execute()
        st.success("✅ Validare efectuată (în vizualizarea curentă).")
        st.rerun()
