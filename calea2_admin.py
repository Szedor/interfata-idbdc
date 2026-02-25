import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime


def run():
    # ---------------------------
    # Conectare Supabase
    # ---------------------------
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    # ---------------------------
    # Stil (păstrat din varianta ta)
    # ---------------------------
    st.markdown(
        """
        <style>
            .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
            .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown,
            [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
            input { color: #000000 !important; background-color: #ffffff !important; }
            div.stButton > button {
                border: 1px solid white !important;
                color: white !important;
                background-color: rgba(255,255,255,0.1) !important;
                width: 100%;
                font-size: 14px !important;
                font-weight: bold !important;
                height: 45px !important;
            }
            div.stButton > button:hover { background-color: white !important; color: #003366 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------
    # Sesiune (păstrat)
    # ---------------------------
    if "autorizat_p1" not in st.session_state:
        st.session_state.autorizat_p1 = False
    if "operator_identificat" not in st.session_state:
        st.session_state.operator_identificat = None

    # ---------------------------
    # Acces securizat (parola)
    #   Notă: păstrez exact cum ai acum.
    #   (Mai târziu o mutăm în secrets, ca să fie "mai safe".)
    # ---------------------------
    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'> 🛡️ Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola:", type="password", key="p1_pass")
            if st.button("Autorizare acces"):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
        st.stop()

    # ---------------------------
    # Identificare operator (păstrat)
    # ---------------------------
    if not st.session_state.operator_identificat:
        st.sidebar.markdown("### 👤 Identificare Operator")
        cod_in = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod_input")
        if cod_in:
            res_op = (
                supabase.table("com_operatori")
                .select("nume_prenume")
                .eq("cod_operatori", cod_in)
                .execute()
            )
            if res_op.data:
                st.session_state.operator_identificat = res_op.data[0]["nume_prenume"]
                st.rerun()
        st.stop()
    else:
        st.sidebar.success(f"Operator: {st.session_state.operator_identificat}")
        if st.sidebar.button("Ieșire / Resetare"):
            st.session_state.clear()
            st.rerun()

    # ---------------------------
    # Titlu
    # ---------------------------
    st.markdown(
        f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.operator_identificat}</h3>",
        unsafe_allow_html=True,
    )

    # ---------------------------
    # Utilitare: preluare liste pt dropdown
    # ---------------------------
    def fetch_list(table_name: str, col_name: str) -> list[str]:
        try:
            res = supabase.table(table_name).select(col_name).execute()
            vals = [r[col_name] for r in (res.data or []) if r.get(col_name)]
            vals = sorted(list(set(vals)))
            return vals
        except Exception:
            return []

    # liste dropdown cerute în docul tău
    opt_categorii = [""] + fetch_list("nom_categorie", "denumire_categorie")
    opt_acronime = [""] + fetch_list("nom_contracte_proiecte", "acronim_contracte_proiecte")
    opt_status_proiect = [""] + fetch_list("nom_status_proiect", "status_contract_proiect")
    opt_status_confirmare = ["Draft", "Validat"]

    # ---------------------------
    # Filtre (simplificat pt azi: doar baza internațională)
    # ---------------------------
    c1, c2, c3 = st.columns([1, 1, 1.2])
    with c1:
        _cat_admin = st.selectbox("1. Categoria:", ["Contracte & Proiecte"], index=0)
    with c2:
        _tip_admin = st.selectbox("2. Tip (Acronim):", ["INTERNATIONALE"], index=0)
    with c3:
        id_admin = st.text_input("3. Filtru (Cod Identificare):", key="admin_id")

    st.markdown("---")

    # ---------------------------
    # Butoane
    # ---------------------------
    col_s, col_a = st.columns([1, 1])
    with col_s:
        btn_salvare = st.button("💾 SALVARE")
    with col_a:
        if st.button("❌ ANULARE / REÎNCĂRCARE"):
            st.rerun()

    st.write("")

    # ---------------------------
    # Tabel: base_proiecte_internationale
    # ---------------------------
    nume_tabela = "base_proiecte_internationale"

    res_main = supabase.table(nume_tabela).select("*")
    if id_admin:
        res_main = res_main.eq("cod_identificare", id_admin)

    df_main = pd.DataFrame(res_main.execute().data or [])
    if df_main.empty:
        # ca să “existe” coloanele și să se vadă dropdown-urile chiar dacă nu găsește nimic
        df_main = pd.DataFrame([{}])

    st.markdown(f"**📂 Tabel Principal: {nume_tabela}**")

    # IMPORTANT: aici “aprindem” dropdown-urile în tabel
    column_config = {
        "denumire_categorie": st.column_config.SelectboxColumn(
            "denumire_categorie (dropdown)",
            options=opt_categorii,
            help="Vine din nom_categorie.denumire_categorie",
        ),
        "acronim_contracte_proiecte": st.column_config.SelectboxColumn(
            "acronim_contracte_proiecte (dropdown)",
            options=opt_acronime,
            help="Vine din nom_contracte_proiecte.acronim_contracte_proiecte",
        ),
        "status_contract_proiect": st.column_config.SelectboxColumn(
            "status_contract_proiect (dropdown)",
            options=opt_status_proiect,
            help="Vine din nom_status_proiect.status_contract_proiect",
        ),
        "status_confirmare": st.column_config.SelectboxColumn(
            "status_confirmare (dropdown)",
            options=opt_status_confirmare,
            help="Draft = în lucru; Validat = confirmat",
        ),
    }

    ed_df = st.data_editor(
        df_main,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key=f"ed_{nume_tabela}",
        column_config=column_config,
    )

    # ---------------------------
    # Salvare (ștergere + upsert)
    # ---------------------------
    if btn_salvare:
        df_old = pd.DataFrame(res_main.execute().data or [])

        # 1) Ștergere: rânduri eliminate
        if not df_old.empty and "cod_identificare" in df_old.columns and "cod_identificare" in ed_df.columns:
            old_ids = set(df_old["cod_identificare"].dropna().astype(str))
            new_ids = set(ed_df["cod_identificare"].dropna().astype(str))
            to_delete = old_ids - new_ids
            for cid in to_delete:
                supabase.table(nume_tabela).delete().eq("cod_identificare", cid).execute()

        # 2) Upsert: rânduri editate/adăugate
        for _, r in ed_df.iterrows():
            v = r.to_dict()

            # curățare NaN -> None
            for k in list(v.keys()):
                if pd.isna(v[k]):
                    v[k] = None

            # completări audit (cine/când)
            v["data_ultimei_modificari"] = datetime.now().isoformat()
            v["observatii_idbdc"] = f"Editat de {st.session_state.operator_identificat}"

            # status default
            if not v.get("status_confirmare"):
                v["status_confirmare"] = "Draft"

            # protecție minimă: dacă nu există cod_identificare, nu salvăm rândul
            if not v.get("cod_identificare"):
                continue

            supabase.table(nume_tabela).upsert(v).execute()

        st.success("✅ Salvare OK. Tabel sincronizat.")
        st.rerun()


if __name__ == "__main__":
    run()
