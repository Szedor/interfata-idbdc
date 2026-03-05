import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime as dt
import html as _html
import streamlit.components.v1 as components


# =========================================================
# CONFIG
# =========================================================

GATE_ENABLED = bool(st.secrets.get("GATE_ENABLED", True))
PASSWORD_CONSULTARE = st.secrets.get("PASSWORD_CONSULTARE", "")

TITLE_LINE_1 = "🔎 Baze de date - Interogare | Cautare | Consultare avansata"
TITLE_LINE_2 = "Departamentul Cercetare Dezvoltare Inovare"

ACADEMIC_BLUE = "#0b2a52"


# =========================================================
# UI / STYLE
# =========================================================

def hide_streamlit_chrome():
    st.markdown(
        """
        <style>
          header { visibility: hidden; height: 0px; }
          #MainMenu { visibility: hidden; }
          footer { visibility: hidden; height: 0px; }
          [data-testid="stToolbar"] { display: none !important; }
          [data-testid="stDecoration"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_style_full_blue():
    st.markdown(
        f"""
        <style>
          .stApp {{
            background: {ACADEMIC_BLUE} !important;
          }}

          div.block-container {{
            padding-top: 1.1rem;
            padding-bottom: 1.0rem;
            max-width: 1550px;
          }}

          .idbdc-header {{
            text-align: center;
            margin-top: 0.2rem;
            margin-bottom: 0.9rem;
          }}
          .idbdc-title-1 {{
            font-size: 2.05rem;
            font-weight: 900;
            line-height: 1.15;
            color: #ffffff;
            margin: 0;
          }}
          .idbdc-title-2 {{
            font-size: 1.86rem;
            font-weight: 800;
            line-height: 1.2;
            color: rgba(255,255,255,0.95);
            margin: 0.35rem 0 0 0;
          }}

          label, .stMarkdown, .stCaption, .stText {{
            color: #ffffff !important;
          }}
          [data-testid="stMarkdownContainer"] p {{
            color: #ffffff !important;
          }}
          [data-testid="stCaptionContainer"] {{
            color: rgba(255,255,255,0.88) !important;
          }}

          .stTextInput input,
          .stSelectbox [data-baseweb="select"] > div,
          .stNumberInput input,
          .stDateInput input {{
            background: rgba(255,255,255,0.96) !important;
            color: #0b1f3a !important;
            border-radius: 10px !important;
          }}

          /* IMPORTANT: butoane - lizibile (nu alb pe alb) */
          .stButton > button {{
            border-radius: 10px !important;
            font-weight: 900 !important;
            background: rgba(255,255,255,0.96) !important;
            color: #0b1f3a !important;
            border: 1px solid rgba(255,255,255,0.55) !important;
            opacity: 1 !important;
          }}
          .stButton > button:hover {{
            border: 1px solid rgba(255,255,255,0.90) !important;
            color: #0b1f3a !important;
            opacity: 1 !important;
          }}
          .stButton > button:disabled,
          .stButton > button[disabled] {{
            background: rgba(255,255,255,0.70) !important;
            color: rgba(11,31,58,0.90) !important;
            border: 1px solid rgba(255,255,255,0.40) !important;
            opacity: 1 !important;
          }}

          /* Tabs: spațiere mai strânsă */
          [data-testid="stTabs"] {{
            margin-top: 0.15rem;
          }}

          h1, h2, h3 {{
            color: #ffffff !important;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_style_gate():
    st.markdown(
        f"""
        <style>
          .stApp {{
            background: {ACADEMIC_BLUE} !important;
          }}
          div.block-container {{
            padding-top: 4.0rem;
            padding-bottom: 2.0rem;
          }}

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

          .stTextInput label {{
            color: #ffffff !important;
            font-weight: 800 !important;
          }}

          .stTextInput input {{
            background: rgba(255,255,255,0.96) !important;
            color: #0b1f3a !important;
            border-radius: 12px !important;
          }}

          .stButton > button {{
            width: 100%;
            border-radius: 12px;
            font-weight: 900;
            background: rgba(255,255,255,0.96) !important;
            color: #0b1f3a !important;
            opacity: 1 !important;
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
    "Evenimente stiintifice": {"base_table": "base_evenimente_stiintifice", "tipuri": None},
    "Proprietate intelectuala": {"base_table": "base_prop_intelect", "tipuri": None},
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
    },
}

TEXT_COL_CANDIDATES = [
    "cod_identificare",
    "titlu", "titlu_proiect", "titlu_eveniment", "titlu_lucrare",
    "denumire", "denumire_proiect", "denumire_eveniment",
    "acronim", "acronim_proiect",
    "obiect_contract",
    "descriere", "observatii", "cuvinte_cheie",
]

YEAR_COL_CANDIDATES_CP = ["an_referinta", "an_derulare", "data_incepere", "data_start"]
YEAR_COL_CANDIDATES_EV = ["data_inceput", "data_eveniment", "data_start", "data"]
YEAR_COL_CANDIDATES_PI = ["data_oficiala_acordare", "data_acordare", "data"]


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


def apply_year_range_filter(q, col: str, y_from: int, y_to: int):
    c = (col or "").lower()
    if c.startswith("data_") or c.startswith("dt_") or c.endswith("_data") or c in ("data",):
        start = dt.datetime(int(y_from), 1, 1)
        end = dt.datetime(int(y_to) + 1, 1, 1) - dt.timedelta(seconds=1)
        return q.gte(col, start.isoformat()).lte(col, end.isoformat())
    return q.gte(col, int(y_from)).lte(col, int(y_to))


def apply_year_range_best_effort(q, cols: set, candidates: list[str], y_from: int, y_to: int):
    for c in candidates:
        if c in cols:
            return apply_year_range_filter(q, c, y_from, y_to)
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


def _safe_select_eq(supabase: Client, table: str, col: str, value: str, limit: int = 2000) -> list[dict]:
    try:
        res = supabase.table(table).select("*").eq(col, value).limit(limit).execute()
        return res.data or []
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
# TAB 1 – FISA COMPLETA (DUPA COD)
# =========================================================

def render_fisa_completa(supabase: Client):
    st.markdown("## Fișa completă (după cod)")

    # Text explicit (NU caption) ca să nu "dispară"
    st.markdown(
        "<div style='color: rgba(255,255,255,0.88); font-size: 1.02rem; font-weight: 600; margin-top: 0.1rem; margin-bottom: 0.85rem;'>"
        "Introduceți cod_identificare și vedeți toate înregistrările asociate (bază + completări, dacă există)."
        "</div>",
        unsafe_allow_html=True,
    )

    # 1) input pe rândul lui (scurt)
    c1, c2 = st.columns([1.2, 3.8])
    with c1:
        cod = st.text_input("Cod identificare", value="", key="fisa_cod").strip()
    with c2:
        st.write("")

    # 2) mesaj pe rând separat
    st.info("Introduceți codul și apăsați «Afișează fișa».", icon="ℹ️")

    # 3) buton pe rând separat (lizibil)
    go = st.button("📄 Afișează fișa", key="fisa_go")

    if not go:
        return

    if not cod:
        st.warning("Cod identificare este obligatoriu.")
        return

    base_tables = []
    for k, v in CATEGORII.items():
        if k == "Contracte & Proiecte":
            base_tables.extend(list(v["tipuri"].values()))
        else:
            base_tables.append(v["base_table"])

    found_any = False
    st.divider()
    st.markdown("### 📌 Date de bază")

    for t in base_tables:
        rows = _safe_select_eq(supabase, t, "cod_identificare", cod, limit=50)
        if rows:
            found_any = True
            st.markdown(f"#### {t}")
            st.dataframe(pd.DataFrame(rows), use_container_width=True, height=260)

    if not found_any:
        st.warning("Nu am găsit acest cod_identificare în tabelele de bază.")
        return

    st.divider()
    st.markdown("### 🧩 Completări (dacă există)")

    tab_fin, tab_teh, tab_ech = st.tabs(["💰 Financiar", "🧪 Tehnic", "👥 Echipă"])

    with tab_fin:
        rows = _safe_select_eq(supabase, "com_date_financiare", "cod_identificare", cod, limit=50)
        if not rows:
            st.info("Nu există încă date financiare pentru acest cod.")
        else:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, height=260)

    with tab_teh:
        rows = _safe_select_eq(supabase, "com_aspecte_tehnice", "cod_identificare", cod, limit=50)
        if not rows:
            st.info("Nu există încă aspecte tehnice pentru acest cod.")
        else:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, height=260)

    with tab_ech:
        rows = _safe_select_eq(supabase, "com_echipe_proiect", "cod_identificare", cod, limit=2000)
        if not rows:
            st.info("Nu există încă echipă pentru acest cod.")
        else:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, height=360)


# =========================================================
# TAB 2 – CAUTARE & FILTRARE
# =========================================================

def render_cautare_filtrare(supabase: Client):
    st.markdown("## Căutare & filtrare")
    st.caption("Căutare rapidă în baza IDBDC (fără export/print; exportul este în tabul 3).")

    nav1, nav2 = st.columns([1.2, 2.8])
    with nav1:
        categorie = st.selectbox("Alege categorie documente", list(CATEGORII.keys()), key="cf_cat")

    tip = None
    if categorie == "Contracte & Proiecte":
        with nav2:
            tip = st.selectbox("Alege tipul de Contracte & Proiecte", list(CATEGORII[categorie]["tipuri"].keys()), key="cf_tip")
        base_table = CATEGORII[categorie]["tipuri"][tip]
    else:
        base_table = CATEGORII[categorie]["base_table"]

    persoane = fetch_idbdc_people(supabase)
    current_year = dt.datetime.now().year

    if categorie == "Evenimente stiintifice":
        natura_list = fetch_distinct_values(supabase, "nom_evenimente_stiintifice", "natura_eveniment")
        format_list = fetch_distinct_values(supabase, "nom_format_evenimente", "format_eveniment")

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            keyword = st.text_input("Cuvant cheie", value="", key="cf_kw").strip()
        with c2:
            an_from = st.number_input("Anul de la", min_value=1900, max_value=2100, value=current_year - 2, step=1, key="cf_y1")
        with c3:
            an_to = st.number_input("Anul pana la", min_value=1900, max_value=2100, value=current_year, step=1, key="cf_y2")
        with c4:
            natura = st.selectbox("Natura evenimentului", [""] + natura_list, key="cf_nat")
        with c5:
            fmt = st.selectbox("Formatul evenimentului", [""] + format_list, key="cf_fmt")
        with c6:
            persoana = st.selectbox("Persoana de contact", [""] + persoane, key="cf_p",
                                  help="Lista include doar persoanele cu reprezinta_idbdc = true.")

    elif categorie == "Proprietate intelectuala":
        tip_pi_list = fetch_distinct_values(supabase, "nom_prop_intelect", "acronym_prop_intelect")
        dep_list = fetch_distinct_values(supabase, "nom_departament", "acronym_departament")

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            keyword = st.text_input("Cuvant cheie", value="", key="cf_kw2").strip()
        with c2:
            an_from = st.number_input("Anul de la", min_value=1900, max_value=2100, value=current_year - 5, step=1, key="cf_y3")
        with c3:
            an_to = st.number_input("Anul pana la", min_value=1900, max_value=2100, value=current_year, step=1, key="cf_y4")
        with c4:
            tip_pi = st.selectbox("Tip proprietate intelectuala", [""] + tip_pi_list, key="cf_tpi")
        with c5:
            dep = st.selectbox("Departament", [""] + dep_list, key="cf_dep")
        with c6:
            persoana = st.selectbox("Persoana de contact", [""] + persoane, key="cf_p2",
                                  help="Lista include doar persoanele cu reprezinta_idbdc = true.")

    else:
        status_list = fetch_distinct_values(supabase, "nom_status_proiect", "status_contract_proiect")
        dep_list = fetch_distinct_values(supabase, "nom_departament", "acronym_departament")

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            keyword = st.text_input("Cuvant cheie", value="", key="cf_kw3").strip()
        with c2:
            an_from = st.number_input("Anul de la", min_value=1900, max_value=2100, value=current_year - 2, step=1, key="cf_y5")
        with c3:
            an_to = st.number_input("Anul pana la", min_value=1900, max_value=2100, value=current_year, step=1, key="cf_y6")
        with c4:
            status = st.selectbox("Status proiect", [""] + status_list, key="cf_st")
        with c5:
            dep = st.selectbox("Departament", [""] + dep_list, key="cf_dep2")
        with c6:
            persoana = st.selectbox("Responsabil contract / Director proiect", [""] + persoane, key="cf_p3",
                                  help="Lista include doar persoanele cu reprezinta_idbdc = true.")

    if int(an_to) < int(an_from):
        st.error("Interval invalid: «Anul pana la» trebuie să fie >= «Anul de la».")
        return

    st.info("Completați criteriile și apăsați «Caută».", icon="ℹ️")
    if not st.button("🔎 Caută", key="cf_go"):
        return

    cols = set(get_table_columns(supabase, base_table))
    q = supabase.table(base_table).select("*")
    q = apply_keyword_filter(q, cols, keyword if "keyword" in locals() else "")

    if categorie == "Evenimente stiintifice":
        q = apply_year_range_best_effort(q, cols, YEAR_COL_CANDIDATES_EV, int(an_from), int(an_to))
    elif categorie == "Proprietate intelectuala":
        q = apply_year_range_best_effort(q, cols, YEAR_COL_CANDIDATES_PI, int(an_from), int(an_to))
    else:
        q = apply_year_range_best_effort(q, cols, YEAR_COL_CANDIDATES_CP, int(an_from), int(an_to))

    if categorie == "Evenimente stiintifice":
        if natura and "natura_eveniment" in cols:
            q = q.eq("natura_eveniment", natura)
        if fmt and "format_eveniment" in cols:
            q = q.eq("format_eveniment", fmt)
        if persoana:
            ids = ids_for_person(supabase, persoana)
            if not ids:
                st.info("Niciun rezultat (nu există coduri asociate persoanei).")
                return
            if "cod_identificare" in cols:
                q = q.in_("cod_identificare", ids)

    elif categorie == "Proprietate intelectuala":
        if "tip_pi" in locals() and tip_pi and "acronym_prop_intelect" in cols:
            q = q.eq("acronym_prop_intelect", tip_pi)
        if "dep" in locals() and dep and "acronym_departament" in cols:
            q = q.eq("acronym_departament", dep)
        if persoana:
            ids = ids_for_person(supabase, persoana)
            if not ids:
                st.info("Niciun rezultat (nu există coduri asociate persoanei).")
                return
            if "cod_identificare" in cols:
                q = q.in_("cod_identificare", ids)

    else:
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
                st.info("Niciun rezultat (nu există coduri asociate persoanei).")
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
    st.dataframe(df, use_container_width=True, height=560)
    st.caption(f"Total rezultate: {len(df)}")


# =========================================================
# TAB 3 – CERCETARE BD + EXPORT/PRINT
# =========================================================

def render_cercetare_export_print(supabase: Client):
    st.markdown("## Cercetare BD + Export/Print")

    # categorie (fără divider mare după)
    nav1, nav2 = st.columns([1.2, 2.8])
    with nav1:
        categorie = st.selectbox("Alege categorie documente", list(CATEGORII.keys()), key="ex_cat")

    tip = None
    if categorie == "Contracte & Proiecte":
        with nav2:
            tip = st.selectbox("Alege tipul de Contracte & Proiecte", list(CATEGORII[categorie]["tipuri"].keys()), key="ex_tip")
        base_table = CATEGORII[categorie]["tipuri"][tip]
    else:
        base_table = CATEGORII[categorie]["base_table"]

    # spațiu mic, nu divider
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    persoane = fetch_idbdc_people(supabase)
    current_year = dt.datetime.now().year

    if categorie == "Evenimente stiintifice":
        natura_list = fetch_distinct_values(supabase, "nom_evenimente_stiintifice", "natura_eveniment")
        format_list = fetch_distinct_values(supabase, "nom_format_evenimente", "format_eveniment")

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            keyword = st.text_input("Cuvant cheie", value="", key="ex_kw").strip()
        with c2:
            an_from = st.number_input("Anul de la", min_value=1900, max_value=2100, value=current_year - 2, step=1, key="ex_y1")
        with c3:
            an_to = st.number_input("Anul pana la", min_value=1900, max_value=2100, value=current_year, step=1, key="ex_y2")
        with c4:
            natura = st.selectbox("Natura evenimentului", [""] + natura_list, key="ex_nat")
        with c5:
            fmt = st.selectbox("Formatul evenimentului", [""] + format_list, key="ex_fmt")
        with c6:
            persoana = st.selectbox("Persoana de contact", [""] + persoane, key="ex_p",
                                  help="Lista include doar persoanele cu reprezinta_idbdc = true.")

    elif categorie == "Proprietate intelectuala":
        tip_pi_list = fetch_distinct_values(supabase, "nom_prop_intelect", "acronym_prop_intelect")
        dep_list = fetch_distinct_values(supabase, "nom_departament", "acronym_departament")

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            keyword = st.text_input("Cuvant cheie", value="", key="ex_kw2").strip()
        with c2:
            an_from = st.number_input("Anul de la", min_value=1900, max_value=2100, value=current_year - 5, step=1, key="ex_y3")
        with c3:
            an_to = st.number_input("Anul pana la", min_value=1900, max_value=2100, value=current_year, step=1, key="ex_y4")
        with c4:
            tip_pi = st.selectbox("Tip proprietate intelectuala", [""] + tip_pi_list, key="ex_tpi")
        with c5:
            dep = st.selectbox("Departament", [""] + dep_list, key="ex_dep")
        with c6:
            persoana = st.selectbox("Persoana de contact", [""] + persoane, key="ex_p2",
                                  help="Lista include doar persoanele cu reprezinta_idbdc = true.")

    else:
        status_list = fetch_distinct_values(supabase, "nom_status_proiect", "status_contract_proiect")
        dep_list = fetch_distinct_values(supabase, "nom_departament", "acronym_departament")

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            keyword = st.text_input("Cuvant cheie", value="", key="ex_kw3").strip()
        with c2:
            an_from = st.number_input("Anul de la", min_value=1900, max_value=2100, value=current_year - 2, step=1, key="ex_y5")
        with c3:
            an_to = st.number_input("Anul pana la", min_value=1900, max_value=2100, value=current_year, step=1, key="ex_y6")
        with c4:
            status = st.selectbox("Status proiect", [""] + status_list, key="ex_st")
        with c5:
            dep = st.selectbox("Departament", [""] + dep_list, key="ex_dep2")
        with c6:
            persoana = st.selectbox("Responsabil contract / Director proiect", [""] + persoane, key="ex_p3",
                                  help="Lista include doar persoanele cu reprezinta_idbdc = true.")

    if int(an_to) < int(an_from):
        st.error("Interval invalid: «Anul pana la» trebuie să fie >= «Anul de la».")
        return

    st.info("Completați criteriile și apăsați «Caută».", icon="ℹ️")
    if not st.button("🔎 Caută", key="ex_go"):
        return

    cols = set(get_table_columns(supabase, base_table))
    q = supabase.table(base_table).select("*")
    q = apply_keyword_filter(q, cols, keyword if "keyword" in locals() else "")

    if categorie == "Evenimente stiintifice":
        q = apply_year_range_best_effort(q, cols, YEAR_COL_CANDIDATES_EV, int(an_from), int(an_to))
    elif categorie == "Proprietate intelectuala":
        q = apply_year_range_best_effort(q, cols, YEAR_COL_CANDIDATES_PI, int(an_from), int(an_to))
    else:
        q = apply_year_range_best_effort(q, cols, YEAR_COL_CANDIDATES_CP, int(an_from), int(an_to))

    if categorie == "Evenimente stiintifice":
        if natura and "natura_eveniment" in cols:
            q = q.eq("natura_eveniment", natura)
        if fmt and "format_eveniment" in cols:
            q = q.eq("format_eveniment", fmt)
        if persoana:
            ids = ids_for_person(supabase, persoana)
            if not ids:
                st.info("Niciun rezultat (nu există coduri asociate persoanei).")
                return
            if "cod_identificare" in cols:
                q = q.in_("cod_identificare", ids)

    elif categorie == "Proprietate intelectuala":
        if "tip_pi" in locals() and tip_pi and "acronym_prop_intelect" in cols:
            q = q.eq("acronym_prop_intelect", tip_pi)
        if "dep" in locals() and dep and "acronym_departament" in cols:
            q = q.eq("acronym_departament", dep)
        if persoana:
            ids = ids_for_person(supabase, persoana)
            if not ids:
                st.info("Niciun rezultat (nu există coduri asociate persoanei).")
                return
            if "cod_identificare" in cols:
                q = q.in_("cod_identificare", ids)

    else:
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
                st.info("Niciun rezultat (nu există coduri asociate persoanei).")
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
        default=defaults if defaults else available_cols[:6],
        key="ex_cols"
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
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    with cC:
        if st.button("🖨️ Print (previzualizare)", key="ex_print"):
            html_doc = make_printable_html(df_final, "IDBDC – Rezultate")
            components.html(html_doc, height=700, scrolling=True)


# =========================================================
# MAIN
# =========================================================

def run():
    st.set_page_config(page_title="IDBDC – Calea 1", layout="wide")

    gate()
    hide_streamlit_chrome()
    apply_style_full_blue()

    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        st.error("Config lipsă: setează SUPABASE_URL și SUPABASE_KEY în Streamlit Cloud → Settings → Secrets.")
        st.stop()

    supabase: Client = create_client(url, key)

    render_header()
    st.divider()

    tab1, tab2, tab3 = st.tabs([
        "📄 Fișa completă (după cod)",
        "🔍 Căutare & filtrare",
        "📊 Cercetare BD + Export/Print"
    ])

    with tab1:
        render_fisa_completa(supabase)

    with tab2:
        render_cautare_filtrare(supabase)

    with tab3:
        render_cercetare_export_print(supabase)


if __name__ == "__main__":
    run()
