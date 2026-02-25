# calea2_admin.py  (versiune finalizare Calea 2 - etapa 1: base_proiecte_internationale)

import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timezone


def run():
    # -----------------------------
    # Conectare Supabase
    # -----------------------------
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    # -----------------------------
    # Stil UI (păstrat)
    # -----------------------------
    st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4,
        .stApp p, .stApp label, .stApp .stMarkdown,
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
    """, unsafe_allow_html=True)

    # -----------------------------
    # Sesiune (păstrat)
    # -----------------------------
    if "autorizat_p1" not in st.session_state:
        st.session_state.autorizat_p1 = False
    if "operator_identificat" not in st.session_state:
        st.session_state.operator_identificat = None

    # -----------------------------
    # 1) Parolă acces
    # -----------------------------
    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'> 🛡️ Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola:", type="password", key="p1_pass")
            if st.button("Autorizare acces"):
                # Notă: mai târziu mutăm parola în st.secrets (mai safe)
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
        st.stop()

    # -----------------------------
    # 2) Identificare operator
    # -----------------------------
    if not st.session_state.operator_identificat:
        st.sidebar.markdown("### 👤 Identificare Operator")
        cod_in = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod_input")

        if cod_in:
            res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_in).execute()
            if res_op.data:
                st.session_state.operator_identificat = res_op.data[0]["nume_prenume"]
                st.rerun()

        st.stop()
    else:
        st.sidebar.success(f"Operator: {st.session_state.operator_identificat}")
        if st.sidebar.button("Ieșire / Resetare"):
            st.session_state.clear()
            st.rerun()

    # -----------------------------
    # Funcții ajutătoare
    # -----------------------------
    def utc_now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @st.cache_data(show_spinner=False, ttl=3600)
    def fetch_options(table: str, column: str):
        """Ia opțiunile pentru dropdown dintr-un tabel nom_."""
        try:
            res = supabase.table(table).select(column).execute()
            if not res.data:
                return [""]
            vals = []
            for r in res.data:
                v = r.get(column)
                if v is None:
                    continue
                v = str(v).strip()
                if v:
                    vals.append(v)
            vals = sorted(list(set(vals)))
            return [""] + vals
        except Exception:
            return [""]

    def normalize_bool(v, default=False):
        """Transformă valori ciudate în True/False (pentru coloane booleene)."""
        if v is None:
            return default
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            s = v.strip().lower()
            if s in ["true", "1", "da", "yes", "validat"]:
                return True
            if s in ["false", "0", "nu", "no", "draft", "nevalidat"]:
                return False
        return default

    # -----------------------------
    # Dropdown-urile (din documentul tău)
    # -----------------------------
    opt_categorii = fetch_options("nom_categorie", "denumire_categorie")
    opt_acronime_cp = fetch_options("nom_contracte_proiecte", "acronim_contracte_proiecte")
    opt_status_proiect = fetch_options("nom_status_proiect", "status_contract_proiect")

    # -----------------------------
    # UI: filtre 1-4
    # -----------------------------
    st.markdown(
        f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.operator_identificat}</h3>",
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2])
    with c1:
        cat_admin = st.selectbox(
            "1. Categoria:",
            ["", "Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"],
            key="admin_cat",
        )
    with c2:
        tip_admin = st.selectbox("2. Tip (Acronim):", opt_acronime_cp, key="admin_tip")
    with c3:
        id_admin = st.text_input("3. ID Proiect (Cod Identificare):", key="admin_id")
    with c4:
        componente_com = st.multiselect(
            "4. Componente (COM):",
            ["Date financiare", "Resurse umane", "Aspecte tehnice"],
            key="admin_com",
        )

    st.markdown("---")

    # -----------------------------
    # Butoane
    # -----------------------------
    col_n, col_s, col_v, col_d, col_a = st.columns(5)

    with col_n:
        st.button("➕ RAND NOU", help="Folosește '+' din tabel pentru rând nou.")
    with col_s:
        btn_salvare = st.button("💾 SALVARE")
    with col_v:
        btn_validare = st.button("✅ VALIDARE")
    with col_d:
        st.button("🗑️ ȘTERGERE", help="Ștergi rândul din tabel (Delete) apoi SALVARE.")
    with col_a:
        if st.button("❌ ANULARE"):
            st.rerun()

    # -----------------------------
    # Azi lucrăm strict pe base_proiecte_internationale
    # -----------------------------
    if cat_admin != "Contracte & Proiecte":
        st.info("Pentru etapa de azi: alege 'Contracte & Proiecte' (lucrăm pe base_proiecte_internationale).")
        return

    tabel_principal = "base_proiecte_internationale"

    # -----------------------------
    # Citire date (doar SELECT)
    # -----------------------------
    q = supabase.table(tabel_principal).select("*")
    if id_admin:
        q = q.eq("cod_identificare", id_admin)

    data = q.execute().data
    df_main = pd.DataFrame(data) if data else pd.DataFrame()

    st.markdown(f"**📂 Tabel Principal: {tabel_principal}**")

    # -----------------------------
    # Editor: dropdown pe coloanele cerute
    # -----------------------------
    edited_df = st.data_editor(
        df_main,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key=f"ed_{tabel_principal}",
        column_config={
            "denumire_categorie": st.column_config.SelectboxColumn(
                "denumire_categorie", options=opt_categorii
            ),
            "acronim_contracte_proiecte": st.column_config.SelectboxColumn(
                "acronim_contracte_proiecte", options=opt_acronime_cp
            ),
            "status_contract_proiect": st.column_config.SelectboxColumn(
                "status_contract_proiect", options=opt_status_proiect
            ),
        },
    )

    # -----------------------------
    # SALVARE (safe) pe cod_identificare (cheia primară)
    # -----------------------------
    if btn_salvare:
        if edited_df is None or edited_df.empty:
            # Dacă era ceva și s-a șters tot, ștergem și din DB (doar dacă era filtrat pe un cod)
            if id_admin:
                supabase.table(tabel_principal).delete().eq("cod_identificare", id_admin).execute()
                st.success("✅ Rândul a fost șters (pentru cod_identificare filtrat).")
                st.rerun()
            else:
                st.warning("Nu sunt date de salvat. (Dacă vrei să ștergi, filtrează întâi pe un cod_identificare.)")
            return

        # 1) Detectăm ștergeri: ce coduri existau și nu mai există
        old_ids = set(df_main["cod_identificare"].dropna().astype(str).tolist()) if "cod_identificare" in df_main.columns else set()
        new_ids = set(edited_df["cod_identificare"].dropna().astype(str).tolist()) if "cod_identificare" in edited_df.columns else set()
        ids_de_sters = list(old_ids - new_ids)

        for cid in ids_de_sters:
            supabase.table(tabel_principal).delete().eq("cod_identificare", cid).execute()

        # 2) Upsert pentru fiecare rând (pe baza PK = cod_identificare)
        salvate = 0
        sarite = 0

        for _, row in edited_df.iterrows():
            v = row.to_dict()

            # Dacă rândul nou nu are cod_identificare, încercăm să-l completăm din filtru
            if (not v.get("cod_identificare")) and id_admin:
                v["cod_identificare"] = id_admin

            # Dacă tot nu are, nu avem cum salva (PK lipsește)
            if not v.get("cod_identificare"):
                sarite += 1
                continue

            # Standardizare câmpuri sistem
            v["data_ultimei_modificari"] = utc_now_iso()
            v["observatii_idbdc"] = f"Editat de {st.session_state.operator_identificat}"

            # IMPORTANT: booleene corecte
            if "status_confirmare" in v:
                v["status_confirmare"] = normalize_bool(v.get("status_confirmare"), default=False)
            if "validat_idbdc" in v:
                v["validat_idbdc"] = normalize_bool(v.get("validat_idbdc"), default=False)

            supabase.table(tabel_principal).upsert(v).execute()
            salvate += 1

        if sarite > 0:
            st.warning(f"⚠️ Am sărit {sarite} rând(uri) fără cod_identificare (cheia primară).")

        st.success(f"✅ Salvare reușită. Rânduri salvate: {salvate}.")
        st.rerun()

    # -----------------------------
    # VALIDARE (marchează validat_idbdc=True)
    # -----------------------------
    if btn_validare:
        if edited_df is None or edited_df.empty:
            st.warning("Nu există rânduri pentru validare.")
            return

        # Validăm doar rândurile vizibile în tabel (respectă filtrul id_admin dacă e setat)
        ids_to_validate = edited_df["cod_identificare"].dropna().astype(str).tolist() if "cod_identificare" in edited_df.columns else []
        for cid in ids_to_validate:
            supabase.table(tabel_principal).update({
                "validat_idbdc": True,
                "data_ultimei_modificari": utc_now_iso(),
                "observatii_idbdc": f"Validat de {st.session_state.operator_identificat}",
            }).eq("cod_identificare", cid).execute()

        st.success("✅ Rândurile afișate au fost marcate ca validate.")
        st.rerun()


if __name__ == "__main__":
    run()
