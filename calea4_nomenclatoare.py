import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime


def _check_gate_password(supabase: Client, gate: str, password: str) -> bool:
    try:
        res = supabase.rpc(
            "idbdc_check_gate_password",
            {"p_gate": gate, "p_password": password},
        ).execute()
        return bool(res.data)
    except Exception:
        return False


def run():
    st.set_page_config(page_title="IDBDC - Nomenclatoare & Detalii", layout="wide")

    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown(
        """
        <style>
          [data-testid="stSidebar"] {
            background: #0b2a52 !important;
            border-right: 2px solid rgba(255,255,255,0.20);
          }
          [data-testid="stSidebar"] .stMarkdown,
          [data-testid="stSidebar"] label,
          [data-testid="stSidebar"] p,
          [data-testid="stSidebar"] h1,
          [data-testid="stSidebar"] h2,
          [data-testid="stSidebar"] h3 {
            color: #ffffff !important;
          }
          div.block-container { padding-top: 1.0rem; padding-bottom: 1.0rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ============================
    # SESSION
    # ============================
    if "autorizat_nom" not in st.session_state:
        st.session_state.autorizat_nom = False
    if "operator_identificat" not in st.session_state:
        st.session_state.operator_identificat = None
    if "operator_rol" not in st.session_state:
        st.session_state.operator_rol = None

    # ============================
    # GATE (parola)
    # ============================
    if not st.session_state.autorizat_nom:
        st.markdown("<h2 style='text-align: center;'> 🛡️ Acces Securizat – Nomenclatoare & Detalii</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola:", type="password", key="nom_pass")
            if st.button("Autorizare acces"):
                if _check_gate_password(supabase, "admin", parola_m):
                    st.session_state.autorizat_nom = True
                    st.rerun()
                else:
                    st.error("Parolă greșită sau poarta este dezactivată.")
        st.stop()

    # ============================
    # OPERATOR (cu rol)
    # ============================
    if not st.session_state.operator_identificat:
        st.sidebar.markdown("### 👤 Identificare Operator")
        cod_in = st.sidebar.text_input("Cod Identificare", type="password", key="nom_cod_input")
        if cod_in:
            try:
                res_op = (
                    supabase.table("com_operatori")
                    .select("nume_prenume, rol")
                    .eq("cod_operatori", cod_in)
                    .execute()
                )
                if res_op.data:
                    st.session_state.operator_identificat = res_op.data[0].get("nume_prenume")
                    st.session_state.operator_rol = res_op.data[0].get("rol") or "OPERATOR"
                    st.rerun()
                else:
                    st.sidebar.error("Cod operator invalid.")
            except Exception as e:
                st.sidebar.error(f"Eroare la verificarea operatorului: {e}")
        st.stop()
    else:
        st.sidebar.success(f"Operator: {st.session_state.operator_identificat} ({st.session_state.operator_rol})")
        if st.sidebar.button("Ieșire / Resetare"):
            st.session_state.clear()
            st.rerun()

    # ============================
    # ROLE CHECK
    # ============================
    if (st.session_state.operator_rol or "").upper() != "ADMIN":
        st.error("Acces interzis. Modulul este disponibil doar pentru rolul ADMIN.")
        st.stop()

    # ============================
    # WHITELIST
    # ============================
    WHITELIST = [
        "nom_categorie",
        "nom_status_proiect",
        "nom_contracte_proiecte",
        "nom_departament",
        "nom_functie_upt",
        "nom_domenii_fdi",
        "nom_universitati",
        "det_resurse_umane",
    ]

    DROPDOWN_MAP = {
        "det_resurse_umane": {
            "acronim_functie_upt": ("nom_functie_upt", "acronim_functie_upt"),
            "acronim_departament": ("nom_departament", "acronim_departament"),
        }
    }

    # ============================
    # HELPERS
    # ============================
    def get_columns(table_name: str):
        try:
            res = supabase.rpc("idbdc_get_columns", {"p_table": table_name}).execute()
            return [r["column_name"] for r in (res.data or []) if r.get("column_name")]
        except Exception:
            return []

    @st.cache_data(show_spinner=False, ttl=300)
    def load_dropdown_options(source_table: str, source_col: str):
        try:
            res = supabase.table(source_table).select(source_col).execute()
            rows = res.data or []
            vals = []
            for r in rows:
                v = r.get(source_col)
                if v is None:
                    continue
                s = str(v).strip()
                if s:
                    vals.append(s)
            return sorted(list(set(vals)))
        except Exception:
            return []

    def build_column_config(table_name: str, df: pd.DataFrame):
        cfg = {}

        rel = DROPDOWN_MAP.get(table_name, {})
        for target_col, (src_table, src_col) in rel.items():
            if target_col not in df.columns:
                continue
            options = load_dropdown_options(src_table, src_col)
            if not options:
                continue
            cfg[target_col] = st.column_config.SelectboxColumn(
                label=target_col,
                options=options,
                required=False,
            )

        if "__STERGE__" in df.columns:
            cfg["__STERGE__"] = st.column_config.CheckboxColumn(
                label="Șterge",
                default=False,
                help="Bifează rândul pentru ștergere, apoi apasă SALVARE.",
            )

        return cfg

    def detect_pk(cols: list[str]) -> str:
        if "id_tehnic" in cols:
            return "id_tehnic"
        if cols:
            return cols[0]
        return ""

    def clean_payload(d: dict):
        out = {}
        for k, v in (d or {}).items():
            if k == "__STERGE__":
                continue
            if v is None:
                continue
            if isinstance(v, str) and v.strip() == "":
                continue
            out[k] = v
        return out

    # ============================
    # UI
    # ============================
    st.markdown(f"<h3 style='text-align: center;'>🧩 Nomenclatoare & Detalii (ADMIN)</h3>", unsafe_allow_html=True)

    st.sidebar.markdown("### 🗂️ Alege tabela")
    tabela = st.sidebar.selectbox("Tabelă", WHITELIST, index=0)

    cols = get_columns(tabela)
    if not cols:
        st.error("Nu pot citi coloanele tablei (idbdc_get_columns nu a returnat nimic).")
        st.stop()

    pk = detect_pk(cols)

    st.caption(f"Tabelă: {tabela} | Cheie: {pk}")

    # încărcare date
    try:
        res = supabase.table(tabela).select("*").execute()
        data = res.data or []
        df = pd.DataFrame(data)
    except Exception as e:
        st.error(f"Eroare la încărcarea datelor: {e}")
        st.stop()

    if df.empty:
        df = pd.DataFrame(columns=cols)

    # asigurare coloană __STERGE__
    if "__STERGE__" not in df.columns:
        df["__STERGE__"] = False

    # ordonare coloane (datele + ștergere la final)
    show_cols = [c for c in cols if c in df.columns] + ["__STERGE__"]
    df = df[show_cols]

    cfg = build_column_config(tabela, df)

    edited = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config=cfg,
    )

    colb1, colb2 = st.columns([1, 3])
    with colb1:
        btn_save = st.button("💾 SALVARE", use_container_width=True)

    if btn_save:
        try:
            # ștergeri
            to_delete = edited[edited["__STERGE__"] == True]  # noqa: E712
            for _, row in to_delete.iterrows():
                key_val = row.get(pk)
                if key_val is None or str(key_val).strip() == "":
                    continue
                supabase.table(tabela).delete().eq(pk, key_val).execute()

            # upsert pentru restul (nebifate)
            to_upsert = edited[edited["__STERGE__"] != True].copy()  # noqa: E712
            payloads = []
            for _, row in to_upsert.iterrows():
                d = row.to_dict()
                d = clean_payload(d)

                # trebuie să existe cheia
                key_val = d.get(pk)
                if key_val is None or str(key_val).strip() == "":
                    continue

                payloads.append(d)

            if payloads:
                supabase.table(tabela).upsert(payloads, on_conflict=pk).execute()

            st.success("Salvare realizată.")
            st.rerun()

        except Exception as e:
            st.error(f"Eroare la salvare: {e}")
