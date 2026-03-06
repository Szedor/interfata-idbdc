import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime as dt
import html as _html
import streamlit.components.v1 as components
import io

# =========================================================
# CONFIG
# =========================================================

GATE_ENABLED = bool(st.secrets.get("GATE_ENABLED", True))
PASSWORD_CONSULTARE = st.secrets.get("PASSWORD_CONSULTARE", "")

TITLE_LINE_1 = "🔎 Baze de date - Interogare | Cautare | Consultare avansata"
TITLE_LINE_2 = "Departamentul Cercetare Dezvoltare Inovare"

ACADEMIC_BLUE = "#0b2a52"

# =========================================================
# TABLE MAP — CATEGORII SPLIT
# =========================================================

CATEGORII = {
    "Contracte": {
        "tipuri": {
            "TERTI": "base_contracte_terti",
            "CEP":   "base_contracte_cep",
        }
    },
    "Proiecte": {
        "tipuri": {
            "FDI":             "base_proiecte_fdi",
            "PNCDI":           "base_proiecte_pncdi",
            "PNRR":            "base_proiecte_pnrr",
            "INTERNATIONALE":  "base_proiecte_internationale",
            "INTERREG":        "base_proiecte_interreg",
            "NONEU":           "base_proiecte_noneu",
        }
    },
    "Evenimente stiintifice": {
        "base_table": "base_evenimente_stiintifice",
        "tipuri": None,
    },
    "Proprietate intelectuala": {
        "base_table": "base_prop_intelect",
        "tipuri": None,
    },
}

# Coloane text candidate pentru keyword search
TEXT_COL_CANDIDATES = [
    "cod_identificare",
    "titlu", "titlul_proiect", "titlu_proiect", "titlu_eveniment", "titlu_lucrare",
    "denumire", "denumire_proiect", "denumire_eveniment",
    "acronim", "acronim_proiect",
    "obiect_contract",
    "descriere", "observatii", "cuvinte_cheie",
]

YEAR_COL_CANDIDATES_CP  = ["an_referinta", "an_derulare", "data_incepere", "data_start", "data_inceput"]
YEAR_COL_CANDIDATES_EV  = ["data_inceput", "data_eveniment", "data_start", "data"]
YEAR_COL_CANDIDATES_PI  = ["data_oficiala_acordare", "data_acordare", "data"]

# Toate tabelele base_*
ALL_BASE_TABLES = [
    "base_contracte_terti",
    "base_contracte_cep",
    "base_proiecte_fdi",
    "base_proiecte_pncdi",
    "base_proiecte_pnrr",
    "base_proiecte_internationale",
    "base_proiecte_interreg",
    "base_proiecte_noneu",
    "base_evenimente_stiintifice",
    "base_prop_intelect",
]

COM_TABLES = {
    "💰 Financiar":  "com_date_financiare",
    "🧪 Tehnic":     "com_aspecte_tehnice",
    "👥 Echipă":     "com_echipe_proiect",
}


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


def _safe_select_eq(supabase: Client, table: str, col: str, value: str, limit: int = 2000) -> list[dict]:
    try:
        res = supabase.table(table).select("*").eq(col, value).limit(limit).execute()
        return res.data or []
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
        end   = dt.datetime(int(y_to) + 1, 1, 1) - dt.timedelta(seconds=1)
        return q.gte(col, start.isoformat()).lte(col, end.isoformat())
    return q.gte(col, int(y_from)).lte(col, int(y_to))


def apply_year_range_best_effort(q, cols: set, candidates: list[str], y_from: int, y_to: int):
    for c in candidates:
        if c in cols:
            return apply_year_range_filter(q, c, y_from, y_to)
    return q


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
            cid  = str(r.get("cod_identificare", "")).strip()
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
            .select("cod_identificare")
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


def _get_year_candidates(categorie: str) -> list[str]:
    if categorie == "Evenimente stiintifice":
        return YEAR_COL_CANDIDATES_EV
    elif categorie == "Proprietate intelectuala":
        return YEAR_COL_CANDIDATES_PI
    else:
        return YEAR_COL_CANDIDATES_CP


def _resolve_base_table(categorie: str, tip: str) -> str | None:
    cat = CATEGORII.get(categorie, {})
    if cat.get("tipuri"):
        return cat["tipuri"].get(tip)
    return cat.get("base_table")


# =========================================================
# TAB 1 — FIȘA COMPLETĂ (după cod)
# =========================================================

def render_fisa_completa(supabase: Client):
    st.markdown("## 📄 Fișa completă a unui proiect")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.88);font-size:1.02rem;font-weight:600;"
        "margin-bottom:0.85rem;'>Introduceți cod_identificare și vedeți toate datele "
        "asociate: bază + completări financiare, tehnice și echipă.</div>",
        unsafe_allow_html=True,
    )

    c1, _ = st.columns([1.2, 3.8])
    with c1:
        cod = st.text_input("Cod identificare", value="", key="fisa_cod").strip()

    st.info("Introduceți codul și apăsați «Afișează fișa».", icon="ℹ️")
    go = st.button("📄 Afișează fișa", key="fisa_go")

    if not go:
        return
    if not cod:
        st.warning("Cod identificare este obligatoriu.")
        return

    found_any = False
    st.divider()
    st.markdown("### 📌 Date de bază")

    for t in ALL_BASE_TABLES:
        rows = _safe_select_eq(supabase, t, "cod_identificare", cod, limit=50)
        if rows:
            found_any = True
            st.markdown(f"#### {t}")
            st.dataframe(pd.DataFrame(rows), use_container_width=True, height=260)

    if not found_any:
        st.warning("Nu am găsit acest cod_identificare în tabelele de bază.")
        return

    st.divider()
    st.markdown("### 🧩 Completări")

    tab_fin, tab_teh, tab_ech = st.tabs(list(COM_TABLES.keys()))

    with tab_fin:
        rows = _safe_select_eq(supabase, "com_date_financiare", "cod_identificare", cod, limit=50)
        if not rows:
            st.info("Nu există date financiare pentru acest cod.")
        else:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, height=260)

    with tab_teh:
        rows = _safe_select_eq(supabase, "com_aspecte_tehnice", "cod_identificare", cod, limit=50)
        if not rows:
            st.info("Nu există aspecte tehnice pentru acest cod.")
        else:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, height=260)

    with tab_ech:
        rows = _safe_select_eq(supabase, "com_echipe_proiect", "cod_identificare", cod, limit=2000)
        if not rows:
            st.info("Nu există echipă pentru acest cod.")
        else:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, height=360)


# =========================================================
# TAB 2 — VEDERE RAPIDĂ (doar base_*)
# =========================================================

def render_vedere_rapida(supabase: Client):
    st.markdown("## 🗂️ Vedere rapidă — date de identificare")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.88);font-size:1.02rem;font-weight:600;"
        "margin-bottom:0.85rem;'>Afișare exclusiv din tabelele base_*. "
        "Cuvântul cheie caută și în echipă / departament.</div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1.2, 1.4, 2.0])

    with c1:
        categorie = st.selectbox("Categorie", list(CATEGORII.keys()), key="vr_cat")

    tip = None
    cat_data = CATEGORII[categorie]
    if cat_data.get("tipuri"):
        with c2:
            tip = st.selectbox("Tip", list(cat_data["tipuri"].keys()), key="vr_tip")
    else:
        with c2:
            st.write("")

    with c3:
        keyword = st.text_input("Cuvânt cheie (opțional)", value="", key="vr_kw").strip()

    st.info("Selectați categoria și apăsați «Afișează».", icon="ℹ️")
    if not st.button("🗂️ Afișează", key="vr_go"):
        return

    base_table = _resolve_base_table(categorie, tip)
    if not base_table:
        st.warning("Selectați un tip valid.")
        return

    cols_list = get_table_columns(supabase, base_table)
    cols = set(cols_list)

    q = supabase.table(base_table).select("*")

    # Keyword în tabelul base
    if keyword:
        q = apply_keyword_filter(q, cols, keyword)

    q = q.limit(800)

    try:
        res   = q.execute()
        rows  = res.data or []
    except Exception as e:
        st.error(f"Eroare interogare: {e}")
        return

    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=cols_list)

    # Dacă keyword nu a găsit nimic în base, căutăm și în com_echipe_proiect
    if keyword and df.empty:
        try:
            res_ech = (
                supabase.table("com_echipe_proiect")
                .select("cod_identificare,nume_prenume")
                .ilike("nume_prenume", f"%{keyword}%")
                .limit(500)
                .execute()
            )
            ids_from_echipa = list({
                str(r["cod_identificare"]).strip()
                for r in (res_ech.data or [])
                if r.get("cod_identificare")
            })
            if ids_from_echipa and "cod_identificare" in cols:
                res2 = (
                    supabase.table(base_table)
                    .select("*")
                    .in_("cod_identificare", ids_from_echipa)
                    .limit(800)
                    .execute()
                )
                rows = res2.data or []
                df   = pd.DataFrame(rows) if rows else pd.DataFrame(columns=cols_list)
                if not df.empty:
                    st.caption("Rezultate găsite prin echipă/responsabil.")
        except Exception:
            pass

    # Dacă tot e gol, caută în det_resurse_umane după departament
    if keyword and df.empty and "acronim_departament" in cols:
        try:
            res_dep = (
                supabase.table("det_resurse_umane")
                .select("acronim_departament")
                .ilike("acronim_departament", f"%{keyword}%")
                .limit(10)
                .execute()
            )
            deps = list({r["acronim_departament"] for r in (res_dep.data or []) if r.get("acronim_departament")})
            if deps:
                res3 = (
                    supabase.table(base_table)
                    .select("*")
                    .in_("acronim_departament", deps)
                    .limit(800)
                    .execute()
                )
                rows = res3.data or []
                df   = pd.DataFrame(rows) if rows else pd.DataFrame(columns=cols_list)
                if not df.empty:
                    st.caption("Rezultate găsite prin departament.")
        except Exception:
            pass

    if df.empty:
        st.info("Niciun rezultat.")
        return

    st.divider()
    st.subheader(f"Rezultate — {base_table}")
    st.dataframe(df, use_container_width=True, height=560)
    st.caption(f"Total: {len(df)} înregistrări")


# =========================================================
# TAB 3 — CĂUTARE APROFUNDATĂ + EXPORT
# =========================================================

def _build_filters(supabase: Client, categorie: str, prefix: str):
    """Construiește rândul de filtre specific categoriei. Returnează dict cu valorile."""
    persoane     = fetch_idbdc_people(supabase)
    current_year = dt.datetime.now().year
    result       = {}

    if categorie == "Evenimente stiintifice":
        natura_list = fetch_distinct_values(supabase, "nom_evenimente_stiintifice", "natura_eveniment")
        format_list = fetch_distinct_values(supabase, "nom_format_evenimente", "format_eveniment")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1: result["keyword"]  = st.text_input("Cuvânt cheie", value="", key=f"{prefix}_kw").strip()
        with c2: result["an_from"]  = st.number_input("Anul de la", min_value=1900, max_value=2100, value=current_year-2, step=1, key=f"{prefix}_y1")
        with c3: result["an_to"]    = st.number_input("Până la", min_value=1900, max_value=2100, value=current_year, step=1, key=f"{prefix}_y2")
        with c4: result["natura"]   = st.selectbox("Natura evenimentului", [""]+natura_list, key=f"{prefix}_nat")
        with c5: result["fmt"]      = st.selectbox("Format", [""]+format_list, key=f"{prefix}_fmt")
        with c6: result["persoana"] = st.selectbox("Persoana contact", [""]+persoane, key=f"{prefix}_p")

    elif categorie == "Proprietate intelectuala":
        tip_pi_list = fetch_distinct_values(supabase, "nom_prop_intelect", "acronim_prop_intelect")
        dep_list    = fetch_distinct_values(supabase, "nom_departament", "acronim_departament")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1: result["keyword"]  = st.text_input("Cuvânt cheie", value="", key=f"{prefix}_kw").strip()
        with c2: result["an_from"]  = st.number_input("Anul de la", min_value=1900, max_value=2100, value=current_year-5, step=1, key=f"{prefix}_y1")
        with c3: result["an_to"]    = st.number_input("Până la", min_value=1900, max_value=2100, value=current_year, step=1, key=f"{prefix}_y2")
        with c4: result["tip_pi"]   = st.selectbox("Tip proprietate", [""]+tip_pi_list, key=f"{prefix}_tpi")
        with c5: result["dep"]      = st.selectbox("Departament", [""]+dep_list, key=f"{prefix}_dep")
        with c6: result["persoana"] = st.selectbox("Persoana contact", [""]+persoane, key=f"{prefix}_p")

    else:  # Contracte sau Proiecte
        status_list = fetch_distinct_values(supabase, "nom_status_proiect", "status_contract_proiect")
        dep_list    = fetch_distinct_values(supabase, "nom_departament", "acronim_departament")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1: result["keyword"]  = st.text_input("Cuvânt cheie", value="", key=f"{prefix}_kw").strip()
        with c2: result["an_from"]  = st.number_input("Anul de la", min_value=1900, max_value=2100, value=current_year-2, step=1, key=f"{prefix}_y1")
        with c3: result["an_to"]    = st.number_input("Până la", min_value=1900, max_value=2100, value=current_year, step=1, key=f"{prefix}_y2")
        with c4: result["status"]   = st.selectbox("Status", [""]+status_list, key=f"{prefix}_st")
        with c5: result["dep"]      = st.selectbox("Departament", [""]+dep_list, key=f"{prefix}_dep")
        with c6: result["persoana"] = st.selectbox("Responsabil / Director", [""]+persoane, key=f"{prefix}_p")

    return result


def _apply_filters_to_query(q, cols: set, categorie: str, filters: dict, supabase: Client):
    """Aplică filtrele pe query și returnează query-ul modificat sau None dacă niciun rezultat."""
    keyword  = filters.get("keyword", "")
    an_from  = filters.get("an_from", dt.datetime.now().year - 2)
    an_to    = filters.get("an_to",   dt.datetime.now().year)

    q = apply_keyword_filter(q, cols, keyword)
    q = apply_year_range_best_effort(q, cols, _get_year_candidates(categorie), int(an_from), int(an_to))

    if categorie == "Evenimente stiintifice":
        natura   = filters.get("natura", "")
        fmt      = filters.get("fmt", "")
        persoana = filters.get("persoana", "")
        if natura and "natura_eveniment" in cols:
            q = q.eq("natura_eveniment", natura)
        if fmt and "format_eveniment" in cols:
            q = q.eq("format_eveniment", fmt)
        if persoana:
            ids = ids_for_person(supabase, persoana)
            if not ids:
                return None
            if "cod_identificare" in cols:
                q = q.in_("cod_identificare", ids)

    elif categorie == "Proprietate intelectuala":
        tip_pi   = filters.get("tip_pi", "")
        dep      = filters.get("dep", "")
        persoana = filters.get("persoana", "")
        if tip_pi and "acronim_prop_intelect" in cols:
            q = q.eq("acronim_prop_intelect", tip_pi)
        if dep and "acronim_departament" in cols:
            q = q.eq("acronim_departament", dep)
        if persoana:
            ids = ids_for_person(supabase, persoana)
            if not ids:
                return None
            if "cod_identificare" in cols:
                q = q.in_("cod_identificare", ids)

    else:  # Contracte / Proiecte
        status   = filters.get("status", "")
        dep      = filters.get("dep", "")
        persoana = filters.get("persoana", "")
        if status:
            for c in ["status_contract_proiect", "status_proiect", "status"]:
                if c in cols:
                    q = q.eq(c, status)
                    break
        if dep:
            for c in ["acronim_departament", "departament", "departament_upt"]:
                if c in cols:
                    q = q.eq(c, dep)
                    break
        if persoana:
            ids = ids_for_person(supabase, persoana)
            if not ids:
                return None
            if "cod_identificare" in cols:
                q = q.in_("cod_identificare", ids)

    return q


def render_cautare_aprofundata(supabase: Client):
    st.markdown("## 🔍 Căutare aprofundată")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.88);font-size:1.02rem;font-weight:600;"
        "margin-bottom:0.85rem;'>Căutare cu filtre multiple. "
        "Selectați câmpurile dorite și exportați rezultatele.</div>",
        unsafe_allow_html=True,
    )

    nav1, nav2 = st.columns([1.2, 2.8])
    with nav1:
        categorie = st.selectbox("Categorie", list(CATEGORII.keys()), key="ca_cat")

    tip = None
    cat_data = CATEGORII[categorie]
    if cat_data.get("tipuri"):
        with nav2:
            tip = st.selectbox("Tip", list(cat_data["tipuri"].keys()), key="ca_tip")

    base_table = _resolve_base_table(categorie, tip)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    filters = _build_filters(supabase, categorie, "ca")

    an_from = filters.get("an_from", dt.datetime.now().year - 2)
    an_to   = filters.get("an_to",   dt.datetime.now().year)
    if int(an_to) < int(an_from):
        st.error("Interval invalid: «Până la» trebuie să fie >= «De la».")
        return

    st.info("Completați criteriile și apăsați «Caută».", icon="ℹ️")
    if not st.button("🔎 Caută", key="ca_go"):
        return

    if not base_table:
        st.warning("Selectați un tip valid.")
        return

    cols = set(get_table_columns(supabase, base_table))
    q    = supabase.table(base_table).select("*")
    q    = _apply_filters_to_query(q, cols, categorie, filters, supabase)

    if q is None:
        st.info("Niciun rezultat (nicio persoană găsită cu acel cod).")
        return

    q = q.limit(800)

    try:
        res  = q.execute()
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
    st.subheader("Rezultate")

    # Selectare coloane pentru tabelul final
    available_cols = list(df.columns)
    defaults = [c for c in ["cod_identificare", "reprezentant_idbdc"] if c in available_cols]
    for c in ["titlul_proiect", "titlu_proiect", "titlu_eveniment", "denumire", "titlul"]:
        if c in available_cols:
            defaults.append(c)
            break
    for c in ["status_contract_proiect", "an_referinta", "data_incepere", "data_start"]:
        if c in available_cols:
            defaults.append(c)
            break

    sel_cols = st.multiselect(
        "Selectează câmpurile pentru tabelul final:",
        options=available_cols,
        default=defaults if defaults else available_cols[:6],
        key="ca_cols",
    )

    if not sel_cols:
        st.warning("Selectează cel puțin o coloană.")
        return

    df_final = df[sel_cols].copy()
    st.dataframe(df_final, use_container_width=True, height=560)
    st.caption(f"Total rezultate: {len(df_final)}")

    # ---- EXPORT ----
    st.divider()
    st.subheader("📤 Export")

    cA, cB, cC, cD = st.columns(4)

    with cA:
        csv_bytes = df_final.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ CSV",
            data=csv_bytes,
            file_name="idbdc_rezultate.csv",
            mime="text/csv",
            key="exp_csv",
        )

    with cB:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df_final.to_excel(writer, index=False, sheet_name="Rezultate")
        buf.seek(0)
        st.download_button(
            "⬇️ Excel",
            data=buf,
            file_name="idbdc_rezultate.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="exp_xlsx",
        )

    with cC:
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet

            pdf_buf = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buf, pagesize=landscape(A4),
                                    leftMargin=20, rightMargin=20,
                                    topMargin=20, bottomMargin=20)
            styles   = getSampleStyleSheet()
            elements = []

            # Header
            elements.append(Paragraph("IDBDC – Rezultate căutare", styles["Title"]))

            # Tabel
            data_rows = [list(df_final.columns)]
            for _, row in df_final.iterrows():
                data_rows.append([str(v) if v is not None else "" for v in row])

            t = Table(data_rows, repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#0b2a52")),
                ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
                ("FONTSIZE",    (0, 0), (-1, -1), 7),
                ("GRID",        (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
                ("VALIGN",      (0, 0), (-1, -1), "TOP"),
            ]))
            elements.append(t)
            doc.build(elements)
            pdf_buf.seek(0)

            st.download_button(
                "⬇️ PDF",
                data=pdf_buf,
                file_name="idbdc_rezultate.pdf",
                mime="application/pdf",
                key="exp_pdf",
            )
        except ImportError:
            st.caption("PDF indisponibil (reportlab lipsă)")

    with cD:
        if st.button("🖨️ Print", key="ca_print"):
            html_doc = make_printable_html(df_final, "IDBDC – Rezultate")
            components.html(html_doc, height=700, scrolling=True)


# =========================================================
# MAIN
# =========================================================

def run():
    st.set_page_config(page_title="IDBDC – Modul 1", layout="wide")

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
        "🗂️ Vedere rapidă (base_*)",
        "🔍 Căutare aprofundată + Export",
    ])

    with tab1:
        render_fisa_completa(supabase)

    with tab2:
        render_vedere_rapida(supabase)

    with tab3:
        render_cautare_aprofundata(supabase)


if __name__ == "__main__":
    run()
