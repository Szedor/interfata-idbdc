import streamlit as st
import pandas as pd
from supabase import create_client, Client
import html as _html


# =========================================================
# Helpers
# =========================================================
PASSWORD_CONSULTARE = "EverDream2SZ"

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

# coloane candidate (căutare text best-effort)
TEXT_COL_CANDIDATES = [
    "cod_identificare",
    "acronim_proiect", "acronim", "acronim_contract", "acronim_contract_proiect",
    "titlu_proiect", "titlu", "denumire_proiect", "obiect_contract",
]

# coloane candidate (an)
YEAR_COL_CANDIDATES = ["an_implementare", "an", "an_derulare", "an_inceput"]


def apply_brand_css():
    # Paletă “mai caldă”, inspirată ca vibe de UPT:
    # - fundal foarte deschis
    # - header albastru UPT
    # - accent albastru mai “friendly”
    st.markdown(
        """
        <style>
            .stApp {
                background: #f4f6fb;
                color: #1f2937;
            }

            /* Sidebar discret */
            [data-testid="stSidebar"] {
                background: #ffffff !important;
                border-right: 1px solid #e5e7eb;
            }

            /* Titluri */
            .upt-header {
                background: linear-gradient(90deg, #003366, #0b4b8a);
                padding: 14px 18px;
                border-radius: 14px;
                color: white;
                margin-bottom: 12px;
            }
            .upt-header h1 {
                margin: 0;
                font-size: 26px;
                font-weight: 800;
                letter-spacing: 0.2px;
            }
            .upt-sub {
                margin-top: 6px;
                opacity: 0.92;
                font-size: 13px;
            }

            /* Card */
            .upt-card {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 16px;
                padding: 14px 14px 8px 14px;
                box-shadow: 0 8px 22px rgba(17, 24, 39, 0.06);
            }

            /* Butoane */
            div.stButton > button {
                border-radius: 12px !important;
                border: 1px solid #0b4b8a !important;
                color: white !important;
                background: #0b4b8a !important;
                font-weight: 700 !important;
                height: 44px !important;
            }
            div.stButton > button:hover {
                background: #003366 !important;
                border-color: #003366 !important;
            }

            /* Inputs */
            input, textarea {
                border-radius: 10px !important;
            }
            [data-baseweb="select"] > div {
                border-radius: 10px !important;
            }

            /* Dataframe container */
            .stDataFrame {
                background: #ffffff;
                border-radius: 14px;
                border: 1px solid #e5e7eb;
                overflow: hidden;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def gate():
    if "autorizat_consultare" not in st.session_state:
        st.session_state.autorizat_consultare = False

    if not st.session_state.autorizat_consultare:
        apply_brand_css()
        st.markdown(
            """
            <div class="upt-card" style="max-width:520px;margin: 40px auto;">
              <div class="upt-header">
                <h1>🛡️ Acces securizat</h1>
                <div class="upt-sub">IDBDC – Interogare și Dezvoltare Baze de Date (UPT)</div>
              </div>
            """,
            unsafe_allow_html=True
        )
        p = st.text_input("Parola:", type="password")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Autorizare acces", use_container_width=True):
                if p == PASSWORD_CONSULTARE:
                    st.session_state.autorizat_consultare = True
                    st.rerun()
                else:
                    st.error("Parolă greșită.")
        with col2:
            st.caption("Te rog folosește parola comunicată.")
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()


@st.cache_data(show_spinner=False, ttl=600)
def get_table_columns(supabase: Client, table_name: str) -> list[str]:
    """
    Folosește RPC idbdc_get_columns(p_table) dacă există.
    Fallback: [] (în acest caz aplicăm filtre doar local, minim).
    """
    try:
        res = supabase.rpc("idbdc_get_columns", {"p_table": table_name}).execute()
        return [r["column_name"] for r in (res.data or []) if r.get("column_name")]
    except Exception:
        return []


def safe_apply_filters(q, cols: set, keyword: str, an_min: int | None, an_max: int | None):
    # keyword: aplicăm ILIKE pe prima coloană utilă găsită (sau pe mai multe, dar fără OR nativ e greu)
    # ca să rămânem stabili, aplicăm ILIKE pe cod_identificare dacă există, altfel pe prima coloană text relevantă.
    if keyword:
        chosen = None
        for c in TEXT_COL_CANDIDATES:
            if c in cols:
                chosen = c
                break
        if chosen:
            q = q.ilike(chosen, f"%{keyword}%")

    # an_min/an_max: aplicăm pe prima coloană an găsită
    year_col = None
    for c in YEAR_COL_CANDIDATES:
        if c in cols:
            year_col = c
            break
    if year_col:
        if an_min is not None:
            q = q.gte(year_col, int(an_min))
        if an_max is not None:
            q = q.lte(year_col, int(an_max))

    return q


def pick_title_col(df: pd.DataFrame) -> str | None:
    for c in ["titlu_proiect", "titlu", "denumire_proiect", "obiect_contract"]:
        if c in df.columns:
            return c
    return None


def make_printable_html(df: pd.DataFrame, title: str) -> str:
    # HTML simplu + buton “Print” (deschide dialogul de print)
    # Notă: Streamlit permite HTML via components.
    safe_title = _html.escape(title)

    # Convertim df în tabel HTML (cu escaping)
    table_html = df.to_html(index=False, escape=True)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>{safe_title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 16px; }}
            h2 {{ margin: 0 0 10px 0; }}
            .meta {{ color: #374151; margin-bottom: 12px; font-size: 12px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #d1d5db; padding: 6px 8px; font-size: 12px; }}
            th {{ background: #f3f4f6; text-align: left; }}
            @media print {{
                button {{ display: none; }}
                body {{ padding: 0; }}
            }}
        </style>
    </head>
    <body>
        <button onclick="window.print()">Print</button>
        <h2>{safe_title}</h2>
        <div class="meta">Generat din IDBDC (Calea 1 – Consultare)</div>
        {table_html}
    </body>
    </html>
    """


# =========================================================
# Main
# =========================================================
def run():
    st.set_page_config(page_title="IDBDC – Calea 1 (Consultare)", layout="wide")
    gate()
    apply_brand_css()

    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown(
        """
        <div class="upt-header">
            <h1>🔎 IDBDC – Calea 1 (Consultare)</h1>
            <div class="upt-sub">Maxim 5 criterii • Rezultate doar din base_* + com_echipe_proiect (reprezinta_idbdc)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # 1) Criterii de căutare (MAX 5)
    # -----------------------------------------------------
    st.markdown('<div class="upt-card">', unsafe_allow_html=True)
    st.subheader("Căutare (max 5 criterii)")

    c1, c2, c3, c4, c5 = st.columns([1.1, 1.4, 0.8, 0.8, 1.1])

    with c1:
        # 1) TIP (criteriu 1)
        tipuri = st.multiselect("1) Tip", list(BASE_TABLES.keys()), default=["INTERNATIONALE"])

    with c2:
        # 2) TEXT (criteriu 2)
        keyword = st.text_input("2) Cuvânt cheie (ID / acronim / titlu)", value="").strip()

    with c3:
        # 3) an_min (criteriu 3)
        an_min = st.number_input("3) An minim", min_value=2010, max_value=2035, value=2010, step=1)

    with c4:
        # 4) an_max (criteriu 4)
        an_max = st.number_input("4) An maxim", min_value=2010, max_value=2035, value=2035, step=1)

    with c5:
        # 5) Limită rezultate (criteriu 5) – util ca “control”, fără să încărcăm
        limit = st.number_input("5) Limită rezultate", min_value=10, max_value=2000, value=300, step=10)

    colb1, colb2 = st.columns([1, 2])
    with colb1:
        do_search = st.button("🔎 Caută", use_container_width=True)
    with colb2:
        st.caption("Sugestie: pentru test, lasă Tip=INTERNATIONALE. Date oficiale sunt doar acolo acum (cum ai spus).")

    st.markdown("</div>", unsafe_allow_html=True)

    if not do_search:
        st.info("Setează criteriile și apasă **Caută**.")
        return

    if not tipuri:
        st.warning("Selectează cel puțin un Tip.")
        return

    # -----------------------------------------------------
    # 2) Interogare base_* (doar tabele base)
    # -----------------------------------------------------
    all_rows = []
    for tip in tipuri:
        table_name = BASE_TABLES.get(tip)
        if not table_name:
            continue

        cols = set(get_table_columns(supabase, table_name))
        q = supabase.table(table_name).select("*").limit(int(limit))

        # filtrare best-effort server-side
        q = safe_apply_filters(
            q=q,
            cols=cols,
            keyword=keyword,
            an_min=int(an_min) if an_min else None,
            an_max=int(an_max) if an_max else None
        )

        try:
            res = q.execute()
            rows = res.data or []
            for r in rows:
                r["_tip"] = tip
                r["_tabela"] = table_name
            all_rows.extend(rows)
        except Exception as e:
            st.warning(f"Nu am putut interoga {table_name} ({tip}): {e}")

    if not all_rows:
        st.info("Niciun rezultat.")
        return

    df = pd.DataFrame(all_rows)

    # -----------------------------------------------------
    # 3) com_echipe_proiect: doar nume_prenume cu reprezinta_idbdc = true
    #    (legare după cod_identificare)
    # -----------------------------------------------------
    reprezentanti = {}
    if "cod_identificare" in df.columns:
        ids = sorted({str(x).strip() for x in df["cod_identificare"].dropna().astype(str).tolist() if str(x).strip()})
        if ids:
            try:
                res_team = (
                    supabase.table("com_echipe_proiect")
                    .select("cod_identificare,nume_prenume,reprezinta_idbdc")
                    .eq("reprezinta_idbdc", True)
                    .in_("cod_identificare", ids)
                    .execute()
                )
                team_rows = res_team.data or []
                for r in team_rows:
                    cid = str(r.get("cod_identificare", "")).strip()
                    nume = str(r.get("nume_prenume", "")).strip()
                    if not cid or not nume:
                        continue
                    reprezentanti.setdefault(cid, [])
                    if nume not in reprezentanti[cid]:
                        reprezentanti[cid].append(nume)
            except Exception as e:
                st.warning(f"Nu pot citi com_echipe_proiect (reprezinta_idbdc): {e}")

        df["reprezentant_idbdc"] = df["cod_identificare"].astype(str).map(
            lambda x: ", ".join(reprezentanti.get(str(x).strip(), []))
        )
    else:
        df["reprezentant_idbdc"] = ""

    # curățare coloane interne
    # păstrăm _tip pentru context, dar nu obligăm în tabelul final
    # -----------------------------------------------------
    st.divider()
    st.subheader("Rezultate")

    # -----------------------------------------------------
    # 4) Selector de coloane (bifare câmpuri pentru tabel final)
    # -----------------------------------------------------
    # “toate câmpurile atribuite fiecărui proiect” = toate coloanele din df (minus cele interne)
    internal_cols = {"_tabela"}  # nu vrem sursa în tabelul oficial
    available_cols = [c for c in df.columns if c not in internal_cols]

    # default: cod_identificare + tip + titlu + reprezentant
    defaults = []
    for c in ["cod_identificare", "_tip", "reprezentant_idbdc"]:
        if c in available_cols:
            defaults.append(c)
    title_col = pick_title_col(df)
    if title_col and title_col in available_cols and title_col not in defaults:
        defaults.append(title_col)

    with st.container():
        st.markdown('<div class="upt-card">', unsafe_allow_html=True)
        sel_cols = st.multiselect(
            "Alege câmpurile care apar în tabelul final (bifezi ce vrei):",
            options=available_cols,
            default=defaults
        )
        if not sel_cols:
            st.warning("Bifează cel puțin un câmp.")
            st.stop()

        df_final = df[sel_cols].copy()

        st.dataframe(df_final, use_container_width=True, height=560)
        st.caption(f"Total rezultate: {len(df_final)}")
        st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # 5) Download + Print
    # -----------------------------------------------------
    st.markdown('<div class="upt-card">', unsafe_allow_html=True)
    st.subheader("Export")

    cdl1, cdl2, cdl3 = st.columns([1, 1, 1])

    csv_bytes = df_final.to_csv(index=False).encode("utf-8-sig")
    with cdl1:
        st.download_button(
            "⬇️ Download CSV",
            data=csv_bytes,
            file_name="idbdc_rezultate.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Excel (fără dependințe extra)
    with cdl2:
        xlsx_buffer = None
        try:
            import io
            xlsx_buffer = io.BytesIO()
            with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
                df_final.to_excel(writer, index=False, sheet_name="Rezultate")
            xlsx_buffer.seek(0)
        except Exception as e:
            st.warning(f"Nu pot genera Excel: {e}")

        if xlsx_buffer:
            st.download_button(
                "⬇️ Download Excel",
                data=xlsx_buffer,
                file_name="idbdc_rezultate.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.button("⬇️ Download Excel", disabled=True, use_container_width=True)

    with cdl3:
        # Print: afișăm într-un iframe HTML cu buton Print
        import streamlit.components.v1 as components
        if st.button("🖨️ Print (previzualizare)", use_container_width=True):
            html_doc = make_printable_html(df_final, title="IDBDC – Rezultate (Calea 1)")
            components.html(html_doc, height=720, scrolling=True)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    run()
