import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime as dt
import html as _html
import streamlit.components.v1 as components


# =========================================================
# CONFIG
# =========================================================

# Gate config din Secrets (Streamlit Cloud)
GATE_ENABLED = bool(st.secrets.get("GATE_ENABLED", True))
PASSWORD_CONSULTARE = st.secrets.get("PASSWORD_CONSULTARE", "")

# Titluri (cum ai cerut)
TITLE_LINE_1 = "🔎 Baze de date - Interogare  | Cautare | Consultare avansata"
TITLE_LINE_2 = "Departamentul Cercetare Dezvoltare Inovare"

ACADEMIC_BLUE = "#0b2a52"


# =========================================================
# STYLE
# =========================================================

def hide_streamlit_chrome():
    """
    Ascunde elementele standard Streamlit (toolbar, meniu, footer).
    Asta elimină și iconițele de tip GitHub/share din UI-ul standard.
    """
    st.markdown(
        """
        <style>
          /* Ascunde bara de sus (unde apar iconițe/meniuri) */
          header { visibility: hidden; height: 0px; }
          /* Ascunde meniul din dreapta sus */
          #MainMenu { visibility: hidden; }
          /* Ascunde footer */
          footer { visibility: hidden; height: 0px; }
          /* Unele versiuni au și aceste elemente */
          [data-testid="stToolbar"] { display: none !important; }
          [data-testid="stDecoration"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_style_gate():
    """Ecranul de acces: fundal albastru + text alb (vizibil)."""
    st.markdown(
        f"""
        <style>
          .stApp {{
            background: {ACADEMIC_BLUE};
          }}

          div.block-container {{
            padding-top: 4.0rem;
            padding-bottom: 2.0rem;
          }}

          /* Card central (semi-transparent) */
          .gate-box {{
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.25);
            border-radius: 18px;
            padding: 26px 22px 18px 22px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.28);
          }}

          .gate-title {{
            text-align: center;
            font-size: 1.45rem;
            font-weight: 900;
            color: #ffffff;
            margin: 0 0 0.35rem 0;
          }}

          .gate-subtitle {{
            text-align: center;
            color: rgba(255,255,255,0.92);
            font-size: 1.02rem;
            font-weight: 600;
            margin: 0 0 1.1rem 0;
          }}

          /* Etichete albe (cerința ta) */
          .stTextInput label {{
            color: #ffffff !important;
            font-weight: 800 !important;
          }}

          /* Input lizibil */
          .stTextInput input {{
            background: rgba(255,255,255,0.96) !important;
            color: #0b1f3a !important;
            border-radius: 12px !important;
          }}

          .stButton > button {{
            width: 100%;
            border-radius: 12px;
            font-weight: 900;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_style_app():
    """Explorator: fundal albastru academic + conținut pe card alb (nu obosește)."""
    st.markdown(
        f"""
        <style>
          .stApp {{
            background: {ACADEMIC_BLUE};
          }}

          /* Card alb pentru toată zona de conținut */
          div.block-container {{
            background: rgba(255,255,255,0.97);
            border-radius: 18px;
            padding: 1.2rem 1.2rem 1.0rem 1.2rem;
            margin-top: 1.0rem;
            margin-bottom: 1.2rem;
            max-width: 1550px;
          }}

          /* Header custom */
          .idbdc-header {{
            text-align: center;
            margin-top: 0.2rem;
            margin-bottom: 0.9rem;
          }}

          .idbdc-title-1 {{
            font-size: 2.05rem;
            font-weight: 900;
            line-height: 1.15;
            color: #0b1f3a;
            margin: 0;
          }}

          /* Cerință: rândul 2 mărit (dar puțin sub rândul 1) */
          .idbdc-title-2 {{
            font-size: 1.78rem;
            font-weight: 800;
            line-height: 1.2;
            color: #0b1f3a;
            margin: 0.35rem 0 0 0;
            opacity: 0.95;
          }}

          /* Mică armonizare vizuală */
          .stButton > button {{
            border-radius: 10px;
            font-weight: 800;
          }}
          .stTextInput input {{
            border-radius: 10px;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        f"""
        <div class="idbdc-header">
          <div class="idbdc-title-1">{_html.escape(TITLE_LINE_1)}</div>
          <div class="idbdc-title-2">{_html.escape(TITLE_LINE_2)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# TABLE MAP
# =========================================================

CATEGORII = {
    "Evenimente stiintifice": {
        "base_table": "base_evenimente_stiintifice",
        "tipuri": None,
    },
    "Proprietate intelectuala": {
        "base_table": "base_prop_intelect",
        "tipuri": None,
    },
    "Contracte & Proiecte": {
        "tipuri": {
            "TERTI": "base_contracte_terti",
            "CEP": "base_contracte_cep",
            "PNCDI": "base_proiecte_pncdi",
            "PNRR": "base_proiecte_pnrr",
            "FDI": "base_proiecte_fdi",
            "INTERNATIONALE": "base_proiecte_internationale",
            "INTERREG": "base_proiecte_interreg",
            "NONEU": "base_proiecte_noneu",
        }
    }
}

TEXT_COL_CANDIDATES = [
    "cod_identificare",
    "titlu", "titlu_proiect", "titlu_eveniment", "titlu_lucrare",
    "denumire", "denumire_proiect", "denumire_eveniment",
    "acronim", "acronim_proiect",
    "obiect_contract",
    "descriere", "observatii", "cuvinte_cheie"
]

YEAR_COL_CANDIDATES_CP = ["an_referinta", "an_derulare", "data_incepere", "data_start"]


# =========================================================
# HELPERS
# =========================================================

@st.cache_data(show_spinner=False, ttl=600)
def get_table_columns(_supabase: Client, table_name: str) -> list[str]:
    try:
        res = _supabase.rpc("idbdc_get_columns", {"p_table": table_name}).execute()
        return [r["column_name"] for r in (res.data or []) if r.get("column_name")]
    except Exception:
        return []


@st.cache_data(show_spinner=False, ttl=600)
def fetch_distinct_values(_supabase: Client, table: str, column: str, limit: int = 2000) -> list[str]:
    try:
        res = _supabase.table(table).select(column).limit(limit).execute()
        vals = []
        for r in (res.data or []):
            v = r.get(column)
            if v is None:
                continue
            s = str(v).strip()
            if s and s not in vals:
                vals.append(s)
        return sorted(vals)
    except Exception:
        return []


@st.cache_data(show_spinner=False, ttl=600)
def fetch_idbdc_people(_supabase: Client, limit: int = 2000) -> list[str]:
    try:
        res = (
            _supabase.table("com_echipe_proiect")
            .select("nume_prenume")
            .eq("reprezinta_idbdc", True)
            .limit(limit)
            .execute()
        )
        vals = []
        for r in (res.data or []):
            v = r.get("nume_prenume")
            if v is None:
                continue
            s = str(v).strip()
            if s and s not in vals:
                vals.append(s)
        return sorted(vals)
    except Exception:
        return []


def apply_keyword_filter(q, cols: set, keyword: str):
    if not keyword:
        return q
    for c in TEXT_COL_CANDIDATES:
        if c in cols:
            return q.ilike(c, f"%{keyword}%")
    if "cod_identificare" in cols:
        return q.ilike("cod_identificare", f"%{keyword}%")
    return q


def apply_date_equals_filter(q, col: str, date_value: dt.date):
    start = dt.datetime.combine(date_value, dt.time.min)
    end = start + dt.timedelta(days=1)
    end_adj = end - dt.timedelta(seconds=1)
    return q.gte(col, start.isoformat()).lte(col, end_adj.isoformat())


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
            @media print {{ button {{ display:none; }} }}
        </style>
    </head>
    <body>
        <button onclick="window.print()">Print</button>
        <h2>{safe_title}</h2>
        {table_html}
    </body>
    </html>
    """


def enrich_reprezentant_idbdc(supabase: Client, df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["reprezentant_idbdc"] = ""

    if "cod_identificare" not in df.columns:
        return df

    ids = sorted({str(x).strip() for x in df["cod_identificare"].dropna().astype(str).tolist() if str(x).strip()})
    if not ids:
        return df

    try:
        res_team = (
            supabase.table("com_echipe_proiect")
            .select("cod_identificare,nume_prenume,reprezinta_idbdc")
            .eq("reprezinta_idbdc", True)
            .in_("cod_identificare", ids)
            .execute()
        )
        rep: dict[str, list[str]] = {}
        for r in (res_team.data or []):
            cid = str(r.get("cod_identificare", "")).strip()
            nume = str(r.get("nume_prenume", "")).strip()
            if not cid or not nume:
                continue
            rep.setdefault(cid, [])
            if nume not in rep[cid]:
                rep[cid].append(nume)

        df["reprezentant_idbdc"] = df["cod_identificare"].astype(str).map(
            lambda x: ", ".join(rep.get(str(x).strip(), []))
        )
    except Exception:
        pass

    return df


def ids_for_person(supabase: Client, person_name: str) -> list[str]:
    if not person_name:
        return []
    try:
        res = (
            supabase.table("com_echipe_proiect")
            .select("cod_identificare,nume_prenume,reprezinta_idbdc")
            .eq("reprezinta_idbdc", True)
            .eq("nume_prenume", person_name)
            .execute()
        )
        return sorted({
            str(r.get("cod_identificare", "")).strip()
            for r in (res.data or [])
            if str(r.get("cod_identificare", "")).strip()
        })
    except Exception:
        return []


# =========================================================
# GATE
# =========================================================

def gate():
    if not GATE_ENABLED:
        st.session_state.autorizat_consultare = True
        return

    if not PASSWORD_CONSULTARE:
        hide_streamlit_chrome()
        apply_style_gate()
        st.error("Config lipsă: setează PASSWORD_CONSULTARE în Streamlit Cloud → Settings → Secrets.")
        st.stop()

    if "autorizat_consultare" not in st.session_state:
        st.session_state.autorizat_consultare = False

    if not st.session_state.autorizat_consultare:
        hide_streamlit_chrome()
        apply_style_gate()

        left, mid, right = st.columns([1.8, 1.0, 1.8])
        with mid:
            st.markdown('<div class="gate-box">', unsafe_allow_html=True)
            st.markdown('<div class="gate-title">🛡️ Acces securizat</div>', unsafe_allow_html=True)
            st.markdown('<div class="gate-subtitle">Interogare baze de date – DCDI</div>', unsafe_allow_html=True)

            parola = st.text_input("Parola acces:", type="password")

            if st.button("Autorizare acces"):
                if parola == PASSWORD_CONSULTARE:
                    st.session_state.autorizat_consultare = True
                    st.rerun()
                else:
                    st.error("Parolă greșită.")

            st.markdown("</div>", unsafe_allow_html=True)

        st.stop()


# =========================================================
# MAIN
# =========================================================

def run():
    st.set_page_config(page_title="IDBDC – Calea 1", layout="wide")

    # 1) Gate (dacă oprește aici, folosește stilul lui)
    gate()

    # 2) Explorator (stil + ascundere iconițe)
    hide_streamlit_chrome()
    apply_style_app()

    # Supabase din Secrets
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        st.error("Config lipsă: setează SUPABASE_URL și SUPABASE_KEY în Streamlit Cloud → Settings → Secrets.")
        st.stop()

    supabase: Client = create_client(url, key)

    # Header (cerințele tale)
    render_header()
    st.divider()

    # ----------------------------
    # SELECTOARE NAVIGARE
    # ----------------------------
    nav1, nav2 = st.columns([1.2, 2.0])

    with nav1:
        categorie = st.selectbox("Alege categorie documente", list(CATEGORII.keys()))

    tip = None
    base_table = None

    if categorie == "Contracte & Proiecte":
        with nav2:
            tip = st.selectbox("Alege tipul de Contracte & Proiecte", list(CATEGORII[categorie]["tipuri"].keys()))
        base_table = CATEGORII[categorie]["tipuri"][tip]
    else:
        base_table = CATEGORII[categorie]["base_table"]

    st.divider()

    # ----------------------------
    # Persoane
    # ----------------------------
    persoane = fetch_idbdc_people(supabase)

    # ----------------------------
    # CRITERII
    # ----------------------------
    if categorie == "Evenimente stiintifice":
        natura_list = fetch_distinct_values(supabase, "nom_evenimente_stiintifice", "natura_eveniment")
        format_list = fetch_distinct_values(supabase, "nom_format_evenimente", "format_eveniment")

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            keyword = st.text_input("Cuvant cheie", value="").strip()
        with c2:
            natura = st.selectbox("Natura evenimentului", [""] + natura_list)
        with c3:
            fmt = st.selectbox("Formatul evenimentului", [""] + format_list)
        with c4:
            data_ev = st.date_input("Data evenimentului", value=None)
        with c5:
            persoana = st.selectbox("Persoana de contact", [""] + persoane, help="Lista include doar persoanele cu reprezinta_idbdc = true.")

    elif categorie == "Proprietate intelectuala":
        tip_pi_list = fetch_distinct_values(supabase, "nom_prop_intelect", "acronym_prop_intelect")
        dep_list = fetch_distinct_values(supabase, "nom_departament", "acronym_departament")

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            keyword = st.text_input("Cuvant cheie", value="").strip()
        with c2:
            tip_pi = st.selectbox("Tip proprietate intelectuala", [""] + tip_pi_list)
        with c3:
            an_acord = st.number_input("Anul acordarii", min_value=1900, max_value=2100, value=2024, step=1)
        with c4:
            dep = st.selectbox("Departament", [""] + dep_list)
        with c5:
            persoana = st.selectbox("Persoana de contact", [""] + persoane, help="Lista include doar persoanele cu reprezinta_idbdc = true.")

    else:
        status_list = fetch_distinct_values(supabase, "nom_status_proiect", "status_contract_proiect")
        dep_list = fetch_distinct_values(supabase, "nom_departament", "acronym_departament")

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            keyword = st.text_input("Cuvant cheie", value="").strip()
        with c2:
            an_impl = st.number_input("An implementare", min_value=1900, max_value=2100, value=2024, step=1)
        with c3:
            status = st.selectbox("Status proiect", [""] + status_list)
        with c4:
            dep = st.selectbox("Departament", [""] + dep_list)
        with c5:
            persoana = st.selectbox("Responsabil contract / Director proiect", [""] + persoane, help="Lista include doar persoanele cu reprezinta_idbdc = true.")

    if not st.button("🔎 Caută"):
        st.info("Completează criteriile și apasă Caută.")
        return

    # ----------------------------
    # QUERY
    # ----------------------------
    cols = set(get_table_columns(supabase, base_table))
    q = supabase.table(base_table).select("*")

    q = apply_keyword_filter(q, cols, keyword if "keyword" in locals() else "")

    if categorie == "Evenimente stiintifice":
        if natura and "natura_eveniment" in cols:
            q = q.eq("natura_eveniment", natura)
        if fmt and "format_eveniment" in cols:
            q = q.eq("format_eveniment", fmt)
        if data_ev and "data_inceput" in cols:
            q = apply_date_equals_filter(q, "data_inceput", data_ev)

        if persoana:
            ids = ids_for_person(supabase, persoana)
            if not ids:
                st.info("Niciun rezultat (nu există coduri asociate persoanei selectate).")
                return
            if "cod_identificare" in cols:
                q = q.in_("cod_identificare", ids)

    elif categorie == "Proprietate intelectuala":
        if "tip_pi" in locals() and tip_pi:
            if "acronym_prop_intelect" in cols:
                q = q.eq("acronym_prop_intelect", tip_pi)

        if "data_oficiala_acordare" in cols and "an_acord" in locals() and an_acord:
            start = dt.datetime(int(an_acord), 1, 1)
            end = dt.datetime(int(an_acord) + 1, 1, 1) - dt.timedelta(seconds=1)
            q = q.gte("data_oficiala_acordare", start.isoformat()).lte("data_oficiala_acordare", end.isoformat())

        if "dep" in locals() and dep:
            if "acronym_departament" in cols:
                q = q.eq("acronym_departament", dep)

        if persoana:
            ids = ids_for_person(supabase, persoana)
            if not ids:
                st.info("Niciun rezultat (nu există coduri asociate persoanei selectate).")
                return
            if "cod_identificare" in cols:
                q = q.in_("cod_identificare", ids)

    else:
        if "an_impl" in locals() and an_impl:
            for c in YEAR_COL_CANDIDATES_CP:
                if c in cols:
                    if c.startswith("data_"):
                        start = dt.datetime(int(an_impl), 1, 1)
                        end = dt.datetime(int(an_impl) + 1, 1, 1) - dt.timedelta(seconds=1)
                        q = q.gte(c, start.isoformat()).lte(c, end.isoformat())
                    else:
                        q = q.eq(c, int(an_impl))
                    break

        if "status" in locals() and status:
            for c in ["status_contract_proiect", "status_proiect", "status"]:
                if c in cols:
                    q = q.eq(c, status)
                    break

        if "dep" in locals() and dep:
            for c in ["acronym_departament", "departament", "departament_upt"]:
                if c in cols:
                    q = q.eq(c, dep)
                    break

        if persoana:
            ids = ids_for_person(supabase, persoana)
            if not ids:
                st.info("Niciun rezultat (nu există coduri asociate persoanei selectate).")
                return
            if "cod_identificare" in cols:
                q = q.in_("cod_identificare", ids)

    q = q.limit(800)

    try:
        res = q.execute()
        rows = res.data or []
    except Exception as e:
        st.error(f"Eroare interogare: {e}")
        return

    if not rows:
        st.info("Niciun rezultat.")
        return

    df = pd.DataFrame(rows)
    df = enrich_reprezentant_idbdc(supabase, df)

    st.divider()
    st.subheader("Rezultate (tabel)")

    available_cols = list(df.columns)

    defaults = [c for c in ["cod_identificare", "reprezentant_idbdc"] if c in available_cols]
    for c in ["titlu", "titlu_proiect", "titlu_eveniment", "denumire", "denumire_proiect", "denumire_eveniment"]:
        if c in available_cols:
            defaults.append(c)
            break

    sel_cols = st.multiselect(
        "Selectează câmpurile pentru tabelul final:",
        options=available_cols,
        default=defaults if defaults else available_cols[:6]
    )

    if not sel_cols:
        st.warning("Selectează cel puțin o coloană.")
        return

    df_final = df[sel_cols].copy()
    st.dataframe(df_final, use_container_width=True, height=560)
    st.caption(f"Total rezultate: {len(df_final)}")

    st.divider()
    st.subheader("Export")

    cA, cB, cC = st.columns(3)

    with cA:
        csv_bytes = df_final.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ Download CSV", data=csv_bytes, file_name="idbdc_rezultate.csv", mime="text/csv")

    with cB:
        import io
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df_final.to_excel(writer, index=False, sheet_name="Rezultate")
        buf.seek(0)
        st.download_button(
            "⬇️ Download Excel",
            data=buf,
            file_name="idbdc_rezultate.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with cC:
        if st.button("🖨️ Print (previzualizare)"):
            html_doc = make_printable_html(df_final, "IDBDC – Rezultate")
            components.html(html_doc, height=700, scrolling=True)


if __name__ == "__main__":
    run()
