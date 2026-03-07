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

          /* ---- CASETE TEXT — același stil ca selectbox ---- */
          .stTextInput > div > div,
          .stTextInput > div > div > input,
          .stTextInput input {{
            background: #1a3a5c !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            border: 1px solid rgba(255,255,255,0.30) !important;
          }}

          .stTextInput input::placeholder {{
            color: rgba(255,255,255,0.50) !important;
            -webkit-text-fill-color: rgba(255,255,255,0.50) !important;
            opacity: 1 !important;
          }}

          /* NumberInput */
          .stNumberInput > div > div,
          .stNumberInput > div > div > input,
          .stNumberInput input {{
            background: #1a3a5c !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
          }}

          /* Selectbox — același stil */
          .stSelectbox > div > div,
          .stSelectbox [data-baseweb="select"],
          .stSelectbox [data-baseweb="select"] > div,
          .stSelectbox [data-baseweb="select"] > div > div,
          .stSelectbox [data-baseweb="select"] > div > div > div,
          .stSelectbox [data-baseweb="select"] span,
          .stSelectbox [data-baseweb="select"] input,
          .stSelectbox [data-baseweb="select"] svg {{
            background: #1a3a5c !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
          }}

          /* Multiselect */
          .stMultiSelect > div > div,
          .stMultiSelect [data-baseweb="select"] > div,
          .stMultiSelect [data-baseweb="select"] span,
          .stMultiSelect [data-baseweb="select"] input {{
            background: #1a3a5c !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            border-radius: 10px !important;
          }}

          /* Lista derulantă deschisă — alb cu text închis */
          [data-baseweb="popover"],
          [data-baseweb="popover"] *,
          [data-baseweb="menu"],
          [data-baseweb="menu"] *,
          [role="listbox"],
          [role="listbox"] *,
          [role="option"] {{
            background-color: #ffffff !important;
            color: #0b1f3a !important;
            -webkit-text-fill-color: #0b1f3a !important;
          }}
          [role="option"]:hover,
          [role="option"][aria-selected="true"] {{
            background-color: #dce6f5 !important;
          }}

          .stButton > button {{
            border-radius: 10px !important;
            font-weight: 900 !important;
            background: rgba(255,255,255,0.96) !important;
            color: #0b1f3a !important;
            -webkit-text-fill-color: #0b1f3a !important;
            border: 1px solid rgba(255,255,255,0.55) !important;
            opacity: 1 !important;
          }}
          .stButton > button p {{
            color: #0b1f3a !important;
            -webkit-text-fill-color: #0b1f3a !important;
          }}
          .stButton > button:hover {{
            border: 1px solid rgba(255,255,255,0.90) !important;
            color: #0b1f3a !important;
            -webkit-text-fill-color: #0b1f3a !important;
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
        "asociate: informații generale + completări financiare, tehnice și echipă.</div>",
        unsafe_allow_html=True,
    )

    c1, _ = st.columns([1.2, 3.8])
    with c1:
        cod = st.text_input("Cod identificare", value="", key="fisa_cod").strip()

    st.markdown(
        "<style>.fisa-go-btn > button { color: #0b1f3a !important; background: rgba(255,255,255,0.96) !important; }</style>",
        unsafe_allow_html=True,
    )
    st.info("Introduceți codul și apăsați «Afișează fișa».", icon="ℹ️")
    go = st.button("📄 Afișează fișa", key="fisa_go")

    if not go:
        return
    if not cod:
        st.warning("Cod identificare este obligatoriu.")
        return

    # Coloane interne care nu se afișează
    COLS_HIDDEN = {
        "responsabil_idbdc", "observatii_idbdc",
        "status_confirmare", "data_ultimei_modificari", "validat_idbdc",
    }

    found_any = False
    st.divider()
    st.markdown("### 📌 Informații generale")

    for t in ALL_BASE_TABLES:
        rows = _safe_select_eq(supabase, t, "cod_identificare", cod, limit=50)
        if rows:
            found_any = True
            st.markdown(f"#### {t}")
            df_row = pd.DataFrame(rows)
            # Elimină coloanele interne
            df_row = df_row[[c for c in df_row.columns if c not in COLS_HIDDEN]]
            # Un singur rând → afișare orizontală ca listă cheie-valoare
            if len(df_row) == 1:
                st.dataframe(df_row, use_container_width=True, hide_index=True, height=60)
            else:
                st.dataframe(df_row, use_container_width=True, hide_index=True, height=min(260, 40 + len(df_row) * 35))

    if not found_any:
        st.warning("Nu am găsit acest cod_identificare în tabelele de bază.")
        return

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
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
# AUTENTIFICARE EXPORT — funcție comună Tab 2 și Tab 3
# =========================================================

def render_export_auth(supabase: Client, tab_key: str = "tab") -> bool:
    """
    Afișează bara de autentificare pentru export/print.
    tab_key: cheie unică per tab ('ec' pentru Tab2, 'ca' pentru Tab3).
    Autentificările sunt independente per tab.
    """
    import re as _re
    auth_key = f"export_auth_{tab_key}"
    pattern  = _re.compile(r"^[a-z]+(?:\.[a-z]+)+@upt\.ro$", _re.IGNORECASE)

    # Autentificat prin Modul 3 SAU prin bara acestui tab
    if st.session_state.get("auth_ai", False) or st.session_state.get(auth_key, False):
        nume = st.session_state.get("user_name") or st.session_state.get("user_email", "")
        st.markdown(
            f"<div style='background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.25);"
            f"border-radius:10px;padding:8px 16px;color:#ffffff;font-weight:700;font-size:0.95rem;"
            f"margin-bottom:0.5rem;'>✅ Export autorizat — {nume}</div>",
            unsafe_allow_html=True,
        )
        return True

    # Bara de autentificare
    st.markdown(
        "<div style='background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.22);"
        "border-radius:12px;padding:12px 18px;margin-bottom:0.6rem;'>"
        "<span style='color:#ffffff;font-weight:800;font-size:0.97rem;'>"
        "🔐 Pentru Export sau Print — autentificare cu email UPT</span></div>",
        unsafe_allow_html=True,
    )

    ea1, ea2, _ = st.columns([2.0, 1.0, 3.0])
    with ea1:
        email_exp = st.text_input(
            "Email",
            value="",
            key=f"export_email_input_{tab_key}",
            label_visibility="collapsed",
            placeholder="prenume.nume@upt.ro",
        ).strip().lower()
    with ea2:
        auth_clicked = st.button("✅ Autorizare", key=f"export_auth_btn_{tab_key}")

    if auth_clicked:
        if not pattern.match(email_exp):
            st.error("Email invalid. Format: prenume.nume@upt.ro")
        else:
            try:
                res = supabase.table("det_resurse_umane") \
                    .select("nume_prenume,email") \
                    .eq("email", email_exp) \
                    .limit(1).execute()
                if res.data:
                    user = res.data[0]
                    st.session_state[auth_key] = True
                    st.session_state.user_email = email_exp
                    st.session_state.user_name  = (user.get("nume_prenume") or "").strip() or email_exp
                    nume = st.session_state.user_name
                    st.markdown(
                        f"<div style='background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.25);"
                        f"border-radius:10px;padding:8px 16px;color:#ffffff;font-weight:700;font-size:0.95rem;"
                        f"margin-bottom:0.5rem;'>✅ Export autorizat — {nume}</div>",
                        unsafe_allow_html=True,
                    )
                    return True
                else:
                    st.error("Emailul nu există în baza de date IDBDC.")
            except Exception as e:
                st.error(f"Eroare verificare: {e}")

    return False


# =========================================================
# TAB 2 — EXPLORARE DUPĂ CRITERIU
# =========================================================

def _get_tables_for_selection(categorie: str, tip: str, cat_data: dict) -> list[str]:
    """Returnează lista de tabele în funcție de Categorie și Tip selectate."""
    if not categorie:
        return ALL_BASE_TABLES
    if cat_data.get("tipuri") and tip:
        t = _resolve_base_table(categorie, tip)
        return [t] if t else []
    elif cat_data.get("tipuri") and not tip:
        return list(cat_data["tipuri"].values())
    else:
        t = cat_data.get("base_table")
        return [t] if t else []


def _query_tables(supabase: Client, tables: list[str], col: str, value: str,
                  use_ilike: bool = False, limit: int = 800) -> pd.DataFrame:
    """Interogare pe o listă de tabele după o coloană și valoare. Returnează DataFrame unificat."""
    dfs = []
    for t in tables:
        cols_t = set(get_table_columns(supabase, t))
        if col not in cols_t:
            continue
        try:
            q = supabase.table(t).select("*")
            if use_ilike:
                q = q.ilike(col, f"%{value}%")
            else:
                q = q.eq(col, value)
            res = q.limit(limit).execute()
            rows = res.data or []
            if rows:
                df_t = pd.DataFrame(rows)
                df_t["_sursa"] = t
                dfs.append(df_t)
        except Exception:
            pass
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def render_explorare_criteriu(supabase: Client):
    st.markdown("## 🔎 Explorare după criteriu")
    st.markdown(
        "<div style='color:rgba(255,255,255,0.88);font-size:1.02rem;font-weight:600;"
        "margin-bottom:0.85rem;'>Selectați un singur criteriu de căutare și obțineți toate "
        "înregistrările corespunzătoare, transversal prin toate categoriile.</div>",
        unsafe_allow_html=True,
    )

    # ---- Filtre opționale: Categorie și Tip ----
    fc1, fc2, fc3 = st.columns([1.2, 1.4, 2.4])
    with fc1:
        categorie = st.selectbox("Categorie (opțional)", [""] + list(CATEGORII.keys()), key="ec_cat")
    cat_data = CATEGORII.get(categorie, {}) if categorie else {}
    tip = None
    if cat_data.get("tipuri"):
        with fc2:
            tip = st.selectbox("Tip (opțional)", [""] + list(cat_data["tipuri"].keys()), key="ec_tip")
    else:
        with fc2:
            st.write("")

    tables_to_query = _get_tables_for_selection(categorie, tip, cat_data)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ---- Criteriu unic ----
    st.markdown(
        "<div style='color:rgba(255,255,255,0.88);font-size:0.97rem;font-weight:700;"
        "margin-bottom:0.4rem;'>Criteriu de căutare</div>",
        unsafe_allow_html=True,
    )

    # Încărcăm listele pentru dropdown-uri
    status_list   = fetch_distinct_values(supabase, "nom_status_proiect", "status_contract_proiect")
    dep_list      = fetch_distinct_values(supabase, "nom_departament", "acronim_departament")
    persoane_list = fetch_idbdc_people(supabase)
    current_year  = dt.datetime.now().year
    ani_list      = [str(a) for a in range(current_year, 1999, -1)]

    cc1, cc2, cc3 = st.columns([1.2, 1.8, 2.0])
    with cc1:
        criteriu = st.selectbox(
            "Alege criteriul",
            [
                "Status",
                "Departament",
                "Director / Responsabil",
                "An de referință",
                "Cuvânt cheie (titlu / acronim)",
            ],
            key="ec_criteriu",
        )

    with cc2:
        if criteriu == "Status":
            valoare = st.selectbox("Status", [""] + status_list, key="ec_val_st")
        elif criteriu == "Departament":
            valoare = st.selectbox("Departament", [""] + dep_list, key="ec_val_dep")
        elif criteriu == "Director / Responsabil":
            valoare = st.selectbox("Director / Responsabil", [""] + persoane_list, key="ec_val_p")
        elif criteriu == "An de referință":
            valoare = st.selectbox("An de referință", [""] + ani_list, key="ec_val_an")
        else:  # Cuvânt cheie
            valoare = st.text_input("Cuvânt cheie (titlu sau acronim)", value="", key="ec_val_kw", label_visibility="visible").strip()

    st.info("Selectați criteriul și valoarea, apoi apăsați «Explorează».", icon="ℹ️")
    if not st.button("🔎 Explorează", key="ec_go"):
        if "ec_rezultate_df" in st.session_state:
            _render_ec_rezultate(supabase)
        return

    if not valoare:
        st.warning("Introduceți sau selectați o valoare pentru criteriul ales.")
        return

    # ---- Interogare ----
    df = pd.DataFrame()

    if criteriu == "Status":
        # Căutăm în coloanele posibile de status
        for col_st in ["status_contract_proiect", "status_proiect", "status"]:
            df_t = _query_tables(supabase, tables_to_query, col_st, valoare)
            if not df_t.empty:
                df = pd.concat([df, df_t], ignore_index=True) if not df.empty else df_t

    elif criteriu == "Departament":
        for col_dep in ["acronim_departament", "departament", "departament_upt"]:
            df_t = _query_tables(supabase, tables_to_query, col_dep, valoare)
            if not df_t.empty:
                df = pd.concat([df, df_t], ignore_index=True) if not df.empty else df_t

    elif criteriu == "Director / Responsabil":
        # Găsim cod_identificare din echipă
        ids = ids_for_person(supabase, valoare)
        if not ids:
            st.info("Nu s-au găsit înregistrări pentru persoana selectată.")
            return
        for t in tables_to_query:
            cols_t = set(get_table_columns(supabase, t))
            if "cod_identificare" not in cols_t:
                continue
            try:
                res = supabase.table(t).select("*").in_("cod_identificare", ids).limit(800).execute()
                rows = res.data or []
                if rows:
                    df_t = pd.DataFrame(rows)
                    df_t["_sursa"] = t
                    df = pd.concat([df, df_t], ignore_index=True) if not df.empty else df_t
            except Exception:
                pass

    elif criteriu == "An de referință":
        for col_an in YEAR_COL_CANDIDATES_CP + YEAR_COL_CANDIDATES_EV + YEAR_COL_CANDIDATES_PI:
            df_t = _query_tables(supabase, tables_to_query, col_an, valoare)
            if not df_t.empty:
                df = pd.concat([df, df_t], ignore_index=True) if not df.empty else df_t

    else:  # Cuvânt cheie titlu / acronim
        kw_cols = ["titlu", "titlul_proiect", "titlu_proiect", "titlu_eveniment",
                   "titlu_lucrare", "denumire", "denumire_proiect", "acronim", "acronim_proiect"]
        for col_kw in kw_cols:
            df_t = _query_tables(supabase, tables_to_query, col_kw, valoare, use_ilike=True)
            if not df_t.empty:
                df = pd.concat([df, df_t], ignore_index=True) if not df.empty else df_t
        # Deduplicare după cod_identificare dacă există
        if not df.empty and "cod_identificare" in df.columns:
            df = df.drop_duplicates(subset=["cod_identificare", "_sursa"])

    if df.empty:
        st.info("Niciun rezultat pentru criteriul selectat.")
        return

    # Salvăm rezultatele în session_state — supraviețuiesc oricărei interacțiuni
    st.session_state["ec_rezultate_df"] = df
    st.session_state["ec_rezultate_label"] = ", ".join(df["_sursa"].unique()) if "_sursa" in df.columns else "toate categoriile"

    # Afișare rezultate
    _render_ec_rezultate(supabase)


def _render_ec_rezultate(supabase: Client):
    """Afișează tabelul și secțiunea de export pentru Tab 2. Separat pentru a putea fi reapelat."""
    df = st.session_state.get("ec_rezultate_df", pd.DataFrame())
    sursa_label = st.session_state.get("ec_rezultate_label", "")
    if df.empty:
        return

    st.divider()
    st.subheader(f"Rezultate — {sursa_label}")
    st.dataframe(df, use_container_width=True, height=560)
    st.caption(f"Total: {len(df)} înregistrări")

    # ---- EXPORT — doar utilizatori autentificați cu @upt.ro ----
    st.divider()
    if render_export_auth(supabase, tab_key="ec"):
        st.subheader("📤 Export")
        cA, cB, cC, cD = st.columns(4)

        with cA:
            csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button("⬇️ CSV", data=csv_bytes,
                               file_name="idbdc_explorare.csv", mime="text/csv", key="ec_csv")

        with cB:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Rezultate")
            buf.seek(0)
            st.download_button("⬇️ Excel", data=buf,
                               file_name="idbdc_explorare.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               key="ec_xlsx")

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
                styles = getSampleStyleSheet()
                elements = [Paragraph("IDBDC – Explorare după criteriu", styles["Title"])]
                data_rows = [list(df.columns)]
                for _, row in df.iterrows():
                    data_rows.append([str(v) if v is not None else "" for v in row])
                t_pdf = Table(data_rows, repeatRows=1)
                t_pdf.setStyle(TableStyle([
                    ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#0b2a52")),
                    ("TEXTCOLOR",      (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE",       (0, 0), (-1, -1), 7),
                    ("GRID",           (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
                    ("VALIGN",         (0, 0), (-1, -1), "TOP"),
                ]))
                elements.append(t_pdf)
                doc.build(elements)
                pdf_buf.seek(0)
                st.download_button("⬇️ PDF", data=pdf_buf,
                                   file_name="idbdc_explorare.pdf",
                                   mime="application/pdf", key="ec_pdf")
            except ImportError:
                st.caption("PDF indisponibil (reportlab lipsă)")

        with cD:
            if st.button("🖨️ Print", key="ec_print"):
                html_doc = make_printable_html(df, "IDBDC – Explorare după criteriu")
                import streamlit.components.v1 as components
                components.html(html_doc, height=700, scrolling=True)


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

    nav1, nav2, nav3 = st.columns([1.2, 1.4, 1.4])
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

    # Dacă există rezultate salvate din căutarea anterioară, le afișăm
    if not st.button("🔎 Caută", key="ca_go"):
        if "ca_rezultate_df" in st.session_state:
            _render_ca_rezultate(supabase)
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

    # Salvăm în session_state
    st.session_state["ca_rezultate_df"] = df

    # Afișare
    _render_ca_rezultate(supabase)


def _render_ca_rezultate(supabase: Client):
    """Afișează tabelul și exportul pentru Tab 3. Separat pentru a rezista la interacțiuni."""
    df = st.session_state.get("ca_rezultate_df", pd.DataFrame())
    if df.empty:
        return

    st.divider()
    st.subheader("Rezultate")

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
    if render_export_auth(supabase, tab_key="ca"):
        st.subheader("📤 Export")

        cA, cB, cC, cD = st.columns(4)

        with cA:
            csv_bytes = df_final.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "⬇️ CSV", data=csv_bytes,
                file_name="idbdc_rezultate.csv", mime="text/csv", key="exp_csv",
            )

        with cB:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df_final.to_excel(writer, index=False, sheet_name="Rezultate")
            buf.seek(0)
            st.download_button(
                "⬇️ Excel", data=buf,
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
                elements = [Paragraph("IDBDC – Rezultate căutare", styles["Title"])]
                data_rows = [list(df_final.columns)]
                for _, row in df_final.iterrows():
                    data_rows.append([str(v) if v is not None else "" for v in row])
                t = Table(data_rows, repeatRows=1)
                t.setStyle(TableStyle([
                    ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#0b2a52")),
                    ("TEXTCOLOR",      (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE",       (0, 0), (-1, -1), 7),
                    ("GRID",           (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
                    ("VALIGN",         (0, 0), (-1, -1), "TOP"),
                ]))
                elements.append(t)
                doc.build(elements)
                pdf_buf.seek(0)
                st.download_button(
                    "⬇️ PDF", data=pdf_buf,
                    file_name="idbdc_rezultate.pdf",
                    mime="application/pdf", key="exp_pdf",
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
        "🔎 Explorare după criteriu",
        "🔍 Căutare aprofundată + Export",
    ])

    with tab1:
        render_fisa_completa(supabase)

    with tab2:
        render_explorare_criteriu(supabase)

    with tab3:
        render_cautare_aprofundata(supabase)


if __name__ == "__main__":
    run()
