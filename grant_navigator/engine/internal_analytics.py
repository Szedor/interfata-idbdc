import streamlit as st
import pandas as pd
import re
from supabase import Client


# -------------------------
# DB helpers
# -------------------------
def _safe_select_all(supabase: Client, table: str, limit: int = 800):
    try:
        res = supabase.table(table).select("*").limit(limit).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Eroare la citirea din baza de date ({table}): {e}")
        return []


def _safe_select_eq(supabase: Client, table: str, col: str, value: str, limit: int = 2000):
    """
    Citire cu filtru = value (server-side).
    Mult mai eficient decât select("*") + filtrare în pandas.
    """
    try:
        res = supabase.table(table).select("*").eq(col, value).limit(limit).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Eroare la citirea din baza de date ({table}): {e}")
        return []


# -------------------------
# Text helpers
# -------------------------
def _filter_anywhere(df: pd.DataFrame, keyword: str) -> pd.DataFrame:
    k = (keyword or "").strip().lower()
    if not k:
        return df
    try:
        row_text = df.astype(str).fillna("").agg(" | ".join, axis=1).str.lower()
        return df[row_text.str.contains(k, na=False)]
    except Exception:
        return df


def _extract_quoted_text(q: str) -> str:
    if not q:
        return ""
    m = re.findall(r'"([^"]+)"', q)
    if m:
        return " ".join([x.strip() for x in m if x.strip()]).strip()
    return ""


def _ro_normalize(text: str) -> str:
    t = (text or "").strip().lower()
    t = (
        t.replace("ă", "a")
        .replace("â", "a")
        .replace("î", "i")
        .replace("ș", "s")
        .replace("ş", "s")
        .replace("ț", "t")
        .replace("ţ", "t")
    )
    t = re.sub(r"\s+", " ", t)
    return t


# -------------------------
# NLQ router (beta)
# -------------------------
def _nlq_guess_table_and_keyword(question: str):
    q_raw = (question or "").strip()
    q = _ro_normalize(q_raw)

    map_baze = {
        "CEP": "base_contracte_cep",
        "TERTI": "base_contracte_terti",
        "PNCDI": "base_proiecte_pncdi",
        "PNRR": "base_proiecte_pnrr",
        "FDI": "base_proiecte_fdi",
        "INTERNATIONALE": "base_proiecte_internationale",
        "INTERREG": "base_proiecte_interreg",
        "NONEU": "base_proiecte_noneu",
    }

    if any(x in q for x in ["eveniment", "conferin", "workshop", "simpozion", "manifestare"]):
        table = "base_evenimente_stiintifice"
        tip = "Evenimente stiintifice"
    elif any(x in q for x in ["proprietate", "brevet", "patent", "marca", "inventie"]):
        table = "base_prop_intelect"
        tip = "Proprietate intelectuala"
    else:
        detected = None
        if "pnrr" in q:
            detected = "PNRR"
        elif "pncdi" in q:
            detected = "PNCDI"
        elif "interreg" in q:
            detected = "INTERREG"
        elif any(x in q for x in ["international", "internationale"]):
            detected = "INTERNATIONALE"
        elif "noneu" in q or "non-eu" in q or "non eu" in q:
            detected = "NONEU"
        elif "fdi" in q:
            detected = "FDI"
        elif "terti" in q:
            detected = "TERTI"
        elif "cep" in q:
            detected = "CEP"
        else:
            detected = "INTERNATIONALE"

        table = map_baze.get(detected, "base_proiecte_internationale")
        tip = detected

    show_all_patterns = [
        r"\barata\b.*\bproiecte\b.*\binternationale\b",
        r"\barata\b.*\bproiectele\b.*\binternationale\b",
        r"\barata\b.*\bproiectul\b.*\binternational\b",
        r"\blisteaza\b.*\bproiecte\b.*\binternationale\b",
        r"\blisteaza\b.*\bproiectele\b.*\binternationale\b",
    ]
    for p in show_all_patterns:
        if re.search(p, q):
            return table, tip, ""

    kw = _extract_quoted_text(q_raw)
    kw = _ro_normalize(kw)

    if not kw:
        stop = {
            "arata", "listeaza", "care", "ce", "cate", "avem", "dupa",
            "in", "din", "pe", "cu", "fara",
            "proiect", "proiecte", "proiectele", "proiectul",
            "contract", "contracte", "contractele", "contractul",
            "eveniment", "evenimente",
            "stiintifice", "proprietate", "intelectuala",
            "pnrr", "pncdi", "cep", "terti", "fdi", "interreg", "noneu",
            "international", "internationale", "domeniu", "domeniul",
            "partener", "parteneri", "finantare", "finantari"
        }
        words = re.findall(r"[a-z0-9\-]+", q)
        words = [w for w in words if w not in stop and len(w) >= 3]
        kw = " ".join(words[:6]).strip()

    generic = {"proiect", "proiecte", "proiectele", "contract", "contracte", "contractele", "eveniment", "evenimente"}
    if kw in generic:
        kw = ""

    return table, tip, kw


# -------------------------
# UI helpers
# -------------------------
def _render_results(df: pd.DataFrame, table: str):
    st.success(f"Total rezultate: {len(df)}")
    st.subheader("Tabel (primele 200 randuri)")
    st.dataframe(df.head(200), use_container_width=True, height=560)

    st.divider()
    st.subheader("Export")

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "⬇️ Download CSV",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"analiza_{table}.csv",
            mime="text/csv",
        )

    with c2:
        import io
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Rezultate")
        buf.seek(0)
        st.download_button(
            "⬇️ Download Excel",
            data=buf,
            file_name=f"analiza_{table}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def _render_single_table(title: str, rows: list, empty_msg: str):
    st.markdown(f"#### {title}")
    if not rows:
        st.info(empty_msg)
        return
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=240)


def _render_team_table(rows: list):
    st.markdown("#### 👥 Echipa proiect")
    if not rows:
        st.warning("Nu există încă echipă pentru acest proiect.")
        return
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=360)


# -------------------------
# PROFIL PROIECT (determinist)
# -------------------------
def _render_profil_proiect(supabase: Client):
    """
    Profil proiect = un 'hub' determinist, ca în Administrare:
    - folosește cod_identificare
    - arată base + com_* (financiar/tehnic/echipă)
    """
    st.markdown("### 🧾 Profil proiect (rapid)")
    st.caption("Introdu cod_identificare și vezi baza + completările (financiar / tehnic / echipă).")

    # map pentru tabele base (le ai deja)
    map_baze = {
        "CEP": "base_contracte_cep",
        "TERTI": "base_contracte_terti",
        "PNCDI": "base_proiecte_pncdi",
        "PNRR": "base_proiecte_pnrr",
        "FDI": "base_proiecte_fdi",
        "INTERNATIONALE": "base_proiecte_internationale",
        "INTERREG": "base_proiecte_interreg",
        "NONEU": "base_proiecte_noneu",
    }
    base_tables = list(map_baze.values())

    # tabele com (numele astea le ajustăm doar dacă în DB sunt diferite)
    COM_FIN = "com_date_financiare"
    COM_TEH = "com_aspecte_tehnice"
    COM_ECH = "com_echipe_proiect"

    cod = st.text_input("cod_identificare", value="", key="profil_cod").strip()
    run = st.button("Afișează profil", key="profil_run")

    if not run:
        return

    if not cod:
        st.warning("Completează cod_identificare.")
        return

    # 1) căutăm în toate base_* (ca să nu ratezi proiectul dacă e în alt tip)
    base_rows_all = []
    for t in base_tables:
        base_rows_all.extend(_safe_select_eq(supabase, t, "cod_identificare", cod, limit=50))

    st.markdown("#### 📌 Date de bază")
    if not base_rows_all:
        st.warning("Nu am găsit proiectul în tabelele base_* după acest cod_identificare.")
    else:
        st.dataframe(pd.DataFrame(base_rows_all), use_container_width=True, height=260)

    st.divider()

    # 2) com_* (server-side filter)
    fin_rows = _safe_select_eq(supabase, COM_FIN, "cod_identificare", cod, limit=10)
    teh_rows = _safe_select_eq(supabase, COM_TEH, "cod_identificare", cod, limit=10)
    ech_rows = _safe_select_eq(supabase, COM_ECH, "cod_identificare", cod, limit=2000)

    tabs = st.tabs(["💰 Financiar", "🧪 Tehnic", "👥 Echipă"])
    with tabs[0]:
        _render_single_table("💰 Date financiare", fin_rows, "Nu există încă date financiare pentru acest proiect.")
    with tabs[1]:
        _render_single_table("🧪 Aspecte tehnice", teh_rows, "Nu există încă aspecte tehnice pentru acest proiect.")
    with tabs[2]:
        _render_team_table(ech_rows)


# -------------------------
# MAIN render
# -------------------------
def render(supabase: Client):
    st.subheader("📊 Analiza interna IDBDC")
    st.caption("Ai două moduri: (1) Profil proiect (rapid) + (2) Întrebări NLQ (beta) și Analiză ghidată.")

    # 0) PROFIL PROIECT (nou)
    _render_profil_proiect(supabase)

    st.divider()

    # 1) NLQ
    st.markdown("### 🧠 Întreabă baza IDBDC (beta)")
    q = st.text_input(
        "Scrie întrebarea (ex: Arată proiectele internaționale / Arată proiecte cu \"energie\")",
        value="",
        key="nlq_question",
    )

    cqa1, _ = st.columns([1, 3])
    with cqa1:
        run_q = st.button("Răspunde", key="nlq_run")

    if run_q:
        if not (q or "").strip():
            st.warning("Scrie o întrebare.")
        else:
            table, tip, kw = _nlq_guess_table_and_keyword(q)

            st.info(
                f"Am interpretat întrebarea ca: **{tip}** → tabela **{table}**"
                + (f" | keyword: **{kw}**" if kw else "")
            )

            rows = _safe_select_all(supabase, table, limit=800)
            if not rows:
                st.info("Nu exista rezultate.")
            else:
                df = pd.DataFrame(rows)

                if kw:
                    df2 = _filter_anywhere(df, kw)
                    if df2.empty:
                        st.warning("Nu am găsit potriviri pentru keyword-ul dedus din întrebare.")
                    else:
                        _render_results(df2, table)
                else:
                    _render_results(df, table)

    st.divider()

    # 2) ANALIZA GHIDATA
    st.markdown("### 🧩 Analiză ghidată (clasic)")
    col1, col2, col3 = st.columns([1.3, 1.3, 1.6])

    with col1:
        categorie = st.selectbox(
            "Categorie",
            ["Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"],
            index=0,
            key="guided_categorie",
        )

    tip = ""
    with col2:
        if categorie == "Contracte & Proiecte":
            tip = st.selectbox(
                "Tip",
                ["CEP", "TERTI", "PNCDI", "PNRR", "FDI", "INTERNATIONALE", "INTERREG", "NONEU"],
                index=5,
                key="guided_tip",
            )
        else:
            st.write("")

    with col3:
        keyword = st.text_input("Cuvant cheie (optional)", value="", key="guided_keyword").strip()

    map_baze = {
        "CEP": "base_contracte_cep",
        "TERTI": "base_contracte_terti",
        "PNCDI": "base_proiecte_pncdi",
        "PNRR": "base_proiecte_pnrr",
        "FDI": "base_proiecte_fdi",
        "INTERNATIONALE": "base_proiecte_internationale",
        "INTERREG": "base_proiecte_interreg",
        "NONEU": "base_proiecte_noneu",
    }

    if categorie == "Contracte & Proiecte":
        table = map_baze.get(tip, "base_proiecte_internationale")
    elif categorie == "Evenimente stiintifice":
        table = "base_evenimente_stiintifice"
    else:
        table = "base_prop_intelect"

    st.divider()

    if not st.button("Ruleaza analiza", key="guided_run"):
        st.info("Apasa «Ruleaza analiza».")
        return

    rows = _safe_select_all(supabase, table, limit=800)
    if not rows:
        st.info("Nu exista rezultate.")
        return

    df = pd.DataFrame(rows)

    if keyword:
        df2 = _filter_anywhere(df, keyword)
        if df2.empty:
            st.warning("Nu am gasit potriviri pentru cuvantul cheie introdus.")
            return
        df = df2

    _render_results(df, table)
