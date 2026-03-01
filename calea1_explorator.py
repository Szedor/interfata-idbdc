import streamlit as st
import pandas as pd
from supabase import create_client, Client
import html as _html
import streamlit.components.v1 as components

# =========================================================
# CONFIGURARE (TEXTE FREEZE)
# =========================================================

PASSWORD_CONSULTARE = "EverDream2SZ"

TITLE_GATE = "🛡️ Acces securizat – Interogare Baze de Date"
SUBTITLE_GATE = "Departamentul Cercetare Dezvoltare Inovare"

TITLE_MAIN = "🔎 Baze de Date – Departamentul Cercetare Dezvoltare Inovare"
SUBTITLE_MAIN = "Interogare | Căutare | Consultare avansată"

BASE_TABLES = {
    "CEP": "base_contracte_cep",
    "TERTI": "base_contracte_terti",
    "FDI": "base_proiecte_fdi",
    "PNRR": "base_proiecte_pnrr",
    "INTERNATIONALE": "base_proiecte_internationale",
    "INTERREG": "base_proiecte_interreg",
    "NONEU": "base_proiecte_noneu",
    "PNCDI": "base_proiecte_pncdi",
}

TEXT_COL_CANDIDATES = [
    "cod_identificare",
    "acronim_proiect", "acronim",
    "titlu_proiect", "titlu",
    "denumire_proiect", "obiect_contract",
]

YEAR_COL_CANDIDATES = [
    "an_implementare", "an",
    "an_derulare", "an_inceput"
]


# =========================================================
# HELPER FUNCTIONS
# =========================================================

@st.cache_data(show_spinner=False, ttl=600)
def get_table_columns(_supabase: Client, table_name: str) -> list[str]:
    try:
        res = supabase.rpc("idbdc_get_columns", {"p_table": table_name}).execute()
        return [r["column_name"] for r in (res.data or []) if r.get("column_name")]
    except Exception:
        return []


def safe_apply_filters(q, cols: set, keyword: str, an_min, an_max):
    if keyword:
        for col in TEXT_COL_CANDIDATES:
            if col in cols:
                q = q.ilike(col, f"%{keyword}%")
                break

    for col in YEAR_COL_CANDIDATES:
        if col in cols:
            if an_min:
                q = q.gte(col, int(an_min))
            if an_max:
                q = q.lte(col, int(an_max))
            break

    return q


def make_printable_html(df: pd.DataFrame, title: str) -> str:
    safe_title = _html.escape(title)
    table_html = df.to_html(index=False, escape=True)

    return f"""
    <html>
    <head>
        <meta charset="utf-8" />
        <title>{safe_title}</title>
        <style>
            body {{ font-family: Arial; padding:20px; }}
            table {{ border-collapse: collapse; width:100%; }}
            th, td {{ border:1px solid #ccc; padding:6px; font-size:12px; }}
            th {{ background:#f0f0f0; }}
            @media print {{
                button {{ display:none; }}
            }}
        </style>
    </head>
    <body>
        <button onclick="window.print()">Print</button>
        <h2>{safe_title}</h2>
        {table_html}
    </body>
    </html>
    """


def gate():
    if "autorizat_consultare" not in st.session_state:
        st.session_state.autorizat_consultare = False

    if not st.session_state.autorizat_consultare:
        st.markdown(f"## {TITLE_GATE}")
        st.caption(SUBTITLE_GATE)

        parola = st.text_input("Parola:", type="password")
        if st.button("Autorizare acces"):
            if parola == PASSWORD_CONSULTARE:
                st.session_state.autorizat_consultare = True
                st.rerun()
            else:
                st.error("Parolă greșită.")
        st.stop()


# =========================================================
# MAIN
# =========================================================

def run():
    st.set_page_config(page_title="IDBDC – Calea 1", layout="wide")
    gate()

    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown(f"# {TITLE_MAIN}")
    st.caption(SUBTITLE_MAIN)
    st.divider()

    # ==============================
    # 5 CRITERII
    # ==============================

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        tipuri = st.multiselect("1) Tip", list(BASE_TABLES.keys()), default=["INTERNATIONALE"])

    with col2:
        keyword = st.text_input("2) Cuvânt cheie")

    with col3:
        an_min = st.number_input("3) An minim", 2010, 2035, 2010)

    with col4:
        an_max = st.number_input("4) An maxim", 2010, 2035, 2035)

    with col5:
        limit = st.number_input("5) Limită rezultate", 10, 2000, 300)

    if not st.button("🔎 Caută"):
        st.info("Setează criteriile și apasă Caută.")
        return

    if not tipuri:
        st.warning("Selectează cel puțin un Tip.")
        return

    # ==============================
    # INTEROGARE BASE_*
    # ==============================

    all_rows = []

    for tip in tipuri:
        table_name = BASE_TABLES.get(tip)
        cols = set(get_table_columns(supabase, table_name))

        q = supabase.table(table_name).select("*").limit(int(limit))
        q = safe_apply_filters(q, cols, keyword, an_min, an_max)

        try:
            res = q.execute()
            rows = res.data or []
            for r in rows:
                r["_tip"] = tip
            all_rows.extend(rows)
        except Exception as e:
            st.warning(f"Eroare interogare {table_name}: {e}")

    if not all_rows:
        st.info("Niciun rezultat.")
        return

    df = pd.DataFrame(all_rows)

    # ==============================
    # com_echipe_proiect
    # ==============================

    df["reprezentant_idbdc"] = ""

    if "cod_identificare" in df.columns:
        ids = df["cod_identificare"].astype(str).unique().tolist()

        try:
            res_team = (
                supabase.table("com_echipe_proiect")
                .select("cod_identificare,nume_prenume")
                .eq("reprezinta_idbdc", True)
                .in_("cod_identificare", ids)
                .execute()
            )

            team_rows = res_team.data or []
            reprezentanti = {}

            for r in team_rows:
                cid = str(r["cod_identificare"])
                nume = r["nume_prenume"]
                reprezentanti.setdefault(cid, []).append(nume)

            df["reprezentant_idbdc"] = df["cod_identificare"].astype(str).map(
                lambda x: ", ".join(reprezentanti.get(str(x), []))
            )

        except Exception as e:
            st.warning(f"Eroare com_echipe_proiect: {e}")

    # ==============================
    # SELECTARE COLOANE
    # ==============================

    st.divider()
    st.subheader("Rezultate")

    available_cols = list(df.columns)
    default_cols = ["cod_identificare", "_tip", "reprezentant_idbdc"]

    sel_cols = st.multiselect(
        "Selectează câmpurile pentru tabelul final:",
        available_cols,
        default=[c for c in default_cols if c in available_cols]
    )

    if not sel_cols:
        st.warning("Selectează cel puțin o coloană.")
        return

    df_final = df[sel_cols]
    st.dataframe(df_final, use_container_width=True)

    # ==============================
    # EXPORT
    # ==============================

    st.divider()
    st.subheader("Export")

    colA, colB, colC = st.columns(3)

    with colA:
        csv_bytes = df_final.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Download CSV",
            data=csv_bytes,
            file_name="idbdc_rezultate.csv",
            mime="text/csv"
        )

    with colB:
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_final.to_excel(writer, index=False)
        buffer.seek(0)

        st.download_button(
            "⬇️ Download Excel",
            data=buffer,
            file_name="idbdc_rezultate.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with colC:
        if st.button("🖨️ Print"):
            html_doc = make_printable_html(df_final, "IDBDC – Rezultate")
            components.html(html_doc, height=700)
