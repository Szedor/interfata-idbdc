import streamlit as st
import pandas as pd
import re
from supabase import Client


def _safe_select_all(supabase: Client, table: str, limit: int = 800):
    try:
        res = supabase.table(table).select("*").limit(limit).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Eroare la citirea din baza de date ({table}): {e}")
        return []


def _filter_anywhere(df: pd.DataFrame, keyword: str) -> pd.DataFrame:
    """
    Filtrare robusta: cauta keyword-ul in ORICE coloana (convertit la text).
    """
    k = (keyword or "").strip().lower()
    if not k:
        return df

    try:
        row_text = df.astype(str).fillna("").agg(" | ".join, axis=1).str.lower()
        return df[row_text.str.contains(k, na=False)]
    except Exception:
        return df


def _extract_quoted_text(q: str) -> str:
    """
    Daca utilizatorul scrie ceva intre ghilimele, luam acel text ca keyword principal.
    Ex: proiecte cu "energie" -> energie
    """
    if not q:
        return ""
    m = re.findall(r'"([^"]+)"', q)
    if m:
        return " ".join([x.strip() for x in m if x.strip()]).strip()
    return ""


def _nlq_guess_table_and_keyword(question: str):
    """
    Interpreteaza o intrebare simpla (beta):
    - alege tabela (CEP/PNRR/PNCDI/... sau Evenimente / Prop. Intelectuala)
    - extrage un keyword (optional)
    """
    q = (question or "").strip()
    q_low = q.lower()

    # harti tabele (aceleasi ca in analiza ghidata)
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

    # 1) Detectie categorie (evenimente / proprietate)
    if any(x in q_low for x in ["eveniment", "conferin", "workshop", "simpozion", "manifestare"]):
        table = "base_evenimente_stiintifice"
        tip = "Evenimente stiintifice"
    elif any(x in q_low for x in ["proprietate", "brevet", "patent", "marca", "inventie"]):
        table = "base_prop_intelect"
        tip = "Proprietate intelectuala"
    else:
        # 2) Detectie tip proiect/contract
        detected = None
        if "pnrr" in q_low:
            detected = "PNRR"
        elif "pncdi" in q_low:
            detected = "PNCDI"
        elif "interreg" in q_low:
            detected = "INTERREG"
        elif any(x in q_low for x in ["international", "internațional", "internationale", "internaționale"]):
            detected = "INTERNATIONALE"
        elif "noneu" in q_low or "non-eu" in q_low or "non eu" in q_low:
            detected = "NONEU"
        elif "fdi" in q_low:
            detected = "FDI"
        elif "terti" in q_low or "terți" in q_low:
            detected = "TERTI"
        elif "cep" in q_low:
            detected = "CEP"
        else:
            detected = "INTERNATIONALE"  # default (beta) - pentru baza ta curenta

        table = map_baze.get(detected, "base_proiecte_internationale")
        tip = detected

    # 3) Keyword: prioritar text intre ghilimele
    kw = _extract_quoted_text(q)

    # daca nu avem ghilimele, incercam sa luam restul "relevant" (foarte simplu)
    if not kw:
        # scoatem cuvintele de tip/categorie, ca sa ramana un posibil keyword
        stop = [
            "arata", "arată", "listeaza", "listează", "care", "ce", "cate", "câte",
            "avem", "dupa", "după", "in", "în", "din", "pe", "cu", "fara", "fără",
            "proiecte", "proiect", "proiectele",
            "contracte", "contract", "contractele",
            "evenimente", "eveniment",
            "stiintifice", "științifice", "proprietate", "intelectuala", "intelectuală",
            "pnrr", "pncdi", "cep", "terti", "terți", "fdi", "interreg", "noneu",
            "international", "internațional", "internationale", "internaționale",
            "domeniul", "domeniu", "parteneri", "partener", "finantare", "finanțare"
        ]
        words = re.findall(r"[A-Za-zĂÂÎȘȚăâîșț0-9\-]+", q_low)
        words = [w for w in words if w not in stop and len(w) >= 3]
        # luam maximum 6 cuvinte ca keyword (beta)
        kw = " ".join(words[:6]).strip()

    return table, tip, kw


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


def render(supabase: Client):
    st.subheader("📊 Analiza interna IDBDC")
    st.caption("Ai două moduri: (1) Întrebări în limbaj normal (beta) și (2) Analiză ghidată (tabel + export).")

    # =========================================================
    # 1) ÎNTREABĂ BAZA IDBDC (BETA)
    # =========================================================
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

    # =========================================================
    # 2) ANALIZA GHIDATĂ (CEA EXISTENTĂ)
    # =========================================================
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
                index=5,  # INTERNATIONALE implicit
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
