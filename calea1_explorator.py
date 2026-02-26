import streamlit as st
from supabase import create_client, Client


# ----------------------------
# Helpers
# ----------------------------
def norm_text(x) -> str:
    if x is None:
        return ""
    s = str(x).strip()
    s = " ".join(s.split())
    return s.casefold()


@st.cache_data(show_spinner=False, ttl=600)
def get_table_columns(supabase: Client, table_name: str) -> list[str]:
    """
    Folosește aceeași funcție RPC ca în Admin: idbdc_get_columns(p_table).
    Dacă RPC nu există / nu e disponibil, întoarce [] și lucrăm în mod fallback.
    """
    try:
        res = supabase.rpc("idbdc_get_columns", {"p_table": table_name}).execute()
        return [r["column_name"] for r in (res.data or []) if r.get("column_name")]
    except Exception:
        return []


def safe_apply_filters(q, cols: set, filters: dict):
    """
    Aplică filtre Supabase doar dacă coloana există.
    filters = {
      "eq": [(col, value), ...],
      "ilike": [(col, pattern), ...],
      "gte": [(col, value), ...],
      "lte": [(col, value), ...],
      "in": [(col, list_values), ...],
    }
    """
    for col, val in filters.get("eq", []):
        if col in cols and val not in (None, "", []):
            q = q.eq(col, val)

    for col, pat in filters.get("ilike", []):
        if col in cols and pat not in (None, "", []):
            q = q.ilike(col, pat)

    for col, val in filters.get("gte", []):
        if col in cols and val not in (None, "", []):
            q = q.gte(col, val)

    for col, val in filters.get("lte", []):
        if col in cols and val not in (None, "", []):
            q = q.lte(col, val)

    for col, vals in filters.get("in", []):
        if col in cols and isinstance(vals, list) and len(vals) > 0:
            q = q.in_(col, vals)

    return q


def try_fetch_related_table(supabase: Client, table_name: str, cod_identificare: str):
    """
    Încearcă să încarce atașamentele dintr-o tabelă “related”, filtrat după cod_identificare.
    Dacă tabela nu există / nu ai drepturi / altă problemă, returnează (None, mesaj).
    """
    try:
        res = supabase.table(table_name).select("*").eq("cod_identificare", cod_identificare).execute()
        data = res.data or []
        return data, None
    except Exception as e:
        return None, str(e)


# ----------------------------
# Main
# ----------------------------
def run():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    # --- Stil (păstrăm look-ul tău) ---
    st.markdown("""
    <style>
    .stApp { background-color: #003366; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { color: white !important; }
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #ddd; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #003366 !important; }
    [data-testid="stSidebar"] input { color: #31333F !important; background-color: white !important; }

    div.stButton > button {
        border: 1px solid white !important; color: white !important;
        background-color: rgba(255,255,255,0.1) !important;
        width: 100%; font-size: 14px !important; font-weight: bold !important; height: 42px !important;
    }
    div.stButton > button:hover { background-color: white !important; color: #003366 !important; }

    label { font-size: 14px !important; font-weight: 400 !important; }
    .stMultiSelect [data-baseweb="select"] div[aria-live="polite"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    # ----------------------------
    # 0) Poartă acces (parolă)
    # ----------------------------
    if "autorizat_consultare" not in st.session_state:
        st.session_state.autorizat_consultare = False

    if not st.session_state.autorizat_consultare:
        st.markdown("<h2 style='text-align: center;'> 🛡️ Acces Securizat – Consultare IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola:", type="password", key="p_cons_pass")
            if st.button("Autorizare acces"):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_consultare = True
                    st.rerun()
        st.stop()

    # ----------------------------
    # Header
    # ----------------------------
    st.markdown("<h1 style='text-align: center;'> 🔎 Consultare / Explorator IDBDC</h1>", unsafe_allow_html=True)
    st.caption("Căutare pe baza indiciilor introduse, apoi deschizi fiecare rezultat pentru detalii + atașamente.")
    st.write("---")

    # ----------------------------
    # 1) Selectoare principale
    # ----------------------------
    c1, c2 = st.columns(2)

    with c1:
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
            list_cat = sorted(list({i["denumire_categorie"] for i in (res_cat.data or []) if i.get("denumire_categorie")}))
        except Exception:
            list_cat = ["Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"]

        categorii_sel = st.multiselect(
            "1. Categoria de informații:",
            list_cat,
            placeholder="",
            key="c_cons_cat"
        )

    with c2:
        tipuri_sel = []
        if "Contracte & Proiecte" in categorii_sel:
            try:
                res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                list_tip = sorted(list({i["acronim_contracte_proiecte"] for i in (res_tip.data or []) if i.get("acronim_contracte_proiecte")}))
            except Exception:
                # fallback util (poți ajusta)
                list_tip = ["CEP", "TERTI", "FDI", "PNRR", "INTERNATIONALE", "INTERREG", "NONEU", "PNCDI"]

            tipuri_sel = st.multiselect(
                "2. Tipul de contract / proiect:",
                list_tip,
                placeholder="",
                key="c_cons_tip"
            )

    # ----------------------------
    # 2) Filtre (Contracte & Proiecte)
    # ----------------------------
    f_id = f_acro = f_titlu = ""
    f_an = None
    f_rol = []
    f_status = []
    f_dep = []
    f_dir = []

    if "Contracte & Proiecte" in categorii_sel and tipuri_sel:
        st.write("---")
        st.markdown("#####  📂  Contracte & Proiecte – Indicii de căutare")

        st.text_input("Titlul proiectului / Obiectul contractului (conține):", key="c_f_titlu")
        f1, f2, f3 = st.columns(3)

        with f1:
            st.text_input("ID proiect / Nr. contract (exact sau conține):", key="c_f_id")
            st.text_input("Acronim proiect (exact sau conține):", key="c_f_acro")

        with f2:
            st.number_input("Anul de implementare (>=):", 2010, 2035, 2024, key="c_f_an_min")
            st.number_input("Anul de implementare (<=):", 2010, 2035, 2024, key="c_f_an_max")
            st.multiselect("Director / Responsabil (text – fallback conține):", [], placeholder="", key="c_f_dir")

        with f3:
            st.multiselect("Rol UPT:", ["Lider", "Coordonator", "Partener"], placeholder="", key="c_f_rol")
            st.multiselect("Status proiect (select – dacă există):", [], placeholder="", key="c_f_status")
            st.multiselect("Departament (select – dacă există):", [], placeholder="", key="c_f_dep")

        f_id = st.session_state.get("c_f_id", "")
        f_acro = st.session_state.get("c_f_acro", "")
        f_titlu = st.session_state.get("c_f_titlu", "")
        an_min = st.session_state.get("c_f_an_min", None)
        an_max = st.session_state.get("c_f_an_max", None)
        f_rol = st.session_state.get("c_f_rol", [])
        f_status = st.session_state.get("c_f_status", [])
        f_dep = st.session_state.get("c_f_dep", [])
        f_dir = st.session_state.get("c_f_dir", [])

        st.write("---")
        colb1, colb2, colb3 = st.columns([1, 1, 1])
        with colb1:
            do_search = st.button("🔎 CĂUTARE")
        with colb2:
            if st.button("🧹 Reset filtre"):
                for k in [
                    "c_cons_cat", "c_cons_tip",
                    "c_f_titlu", "c_f_id", "c_f_acro",
                    "c_f_an_min", "c_f_an_max",
                    "c_f_rol", "c_f_status", "c_f_dep", "c_f_dir"
                ]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()
        with colb3:
            st.caption("Rezultatele apar mai jos (deschizi fiecare ID).")

    else:
        st.info("Selectează cel puțin o categorie. Pentru Contracte & Proiecte alege și Tipul, apoi folosește CĂUTARE.")
        return

    # ----------------------------
    # 3) Execuție căutare (doar la click)
    # ----------------------------
    if not do_search:
        st.stop()

    # Mapare tabele (ca în Admin)
    map_baze_contracte_proiecte = {
        "CEP": "base_contracte_cep",
        "TERTI": "base_contracte_terti",
        "FDI": "base_proiecte_fdi",
        "PNRR": "base_proiecte_pnrr",
        "INTERNATIONALE": "base_proiecte_internationale",
        "INTERREG": "base_proiecte_interreg",
        "NONEU": "base_proiecte_noneu",
        "PNCDI": "base_proiecte_pncdi",
    }

    # tabele “atașamente” (poți ajusta ulterior – acum e robust: dacă nu există, nu crapă)
    related_tables_guess = {
        "Financiar": [
            "comp_financiar", "comp_date_financiare", "base_financiar", "base_date_financiare"
        ],
        "Resurse umane": [
            "comp_resurse_umane", "comp_ru", "base_resurse_umane", "base_ru"
        ],
        "Tehnic": [
            "comp_aspecte_tehnice", "comp_tehnic", "base_aspecte_tehnice", "base_tehnic"
        ],
    }

    # Căutăm în toate tabelele tipurilor selectate și concatenăm rezultatele
    all_rows = []

    for tip in tipuri_sel:
        table_name = map_baze_contracte_proiecte.get(tip)
        if not table_name:
            continue

        cols = set(get_table_columns(supabase, table_name))

        q = supabase.table(table_name).select("*")

        # Filtre “safe” (doar dacă există coloanele)
        filters = {"eq": [], "ilike": [], "gte": [], "lte": [], "in": []}

        # ID / cod_identificare
        # (în Admin e clar că există cod_identificare)
        if f_id and str(f_id).strip():
            fid = str(f_id).strip()
            if "cod_identificare" in cols:
                # dacă pare exact, eq; altfel ilike
                if len(fid) <= 25 and (" " not in fid):
                    filters["ilike"].append(("cod_identificare", f"%{fid}%"))
                else:
                    filters["ilike"].append(("cod_identificare", f"%{fid}%"))

        # acronim
        if f_acro and str(f_acro).strip():
            fac = str(f_acro).strip()
            for cand in ["acronim_proiect", "acronim", "acronim_contract", "acronim_contract_proiect"]:
                if cand in cols:
                    filters["ilike"].append((cand, f"%{fac}%"))
                    break

        # titlu
        if f_titlu and str(f_titlu).strip():
            ft = str(f_titlu).strip()
            for cand in ["titlu_proiect", "titlu", "obiect_contract", "denumire_proiect"]:
                if cand in cols:
                    filters["ilike"].append((cand, f"%{ft}%"))
                    break

        # an implementare
        an_min = st.session_state.get("c_f_an_min", None)
        an_max = st.session_state.get("c_f_an_max", None)
        for cand in ["an_implementare", "an", "an_derulare", "an_inceput"]:
            if cand in cols:
                if an_min:
                    filters["gte"].append((cand, int(an_min)))
                if an_max:
                    filters["lte"].append((cand, int(an_max)))
                break

        # rol
        if f_rol:
            for cand in ["rol_upt", "rol", "rol_in_proiect"]:
                if cand in cols:
                    # dacă e text simplu, facem fallback ilike pe fiecare
                    # (dacă e enum, merge și eq/in_)
                    # încercăm in_ întâi (safe)
                    filters["in"].append((cand, list(f_rol)))
                    break

        # status (dacă există)
        if f_status:
            for cand in ["status_contract_proiect", "status_proiect", "status"]:
                if cand in cols:
                    filters["in"].append((cand, list(f_status)))
                    break

        # departament (dacă există)
        if f_dep:
            for cand in ["departament", "departament_upt", "departament_coord", "dep"]:
                if cand in cols:
                    filters["in"].append((cand, list(f_dep)))
                    break

        # director/responsabil (fallback text contains)
        # (că momentan lista e goală – deci lăsăm “conține” dacă userul introduce manual text)
        # NOTĂ: multiselect-ul tău e gol -> dacă vrei, îl schimbăm ulterior în text_input.
        # Pentru compatibilitate, dacă f_dir e listă cu 1 element, folosim acel text.
        dir_text = ""
        if isinstance(f_dir, list) and len(f_dir) == 1:
            dir_text = str(f_dir[0]).strip()
        if dir_text:
            for cand in ["director", "responsabil", "director_proiect", "responsabil_proiect", "nume_responsabil"]:
                if cand in cols:
                    filters["ilike"].append((cand, f"%{dir_text}%"))
                    break

        q = safe_apply_filters(q, cols, filters)

        try:
            res = q.execute()
            rows = res.data or []
            # marcăm tipul pentru claritate
            for r in rows:
                r["_tip"] = tip
                r["_tabela"] = table_name
            all_rows.extend(rows)
        except Exception as e:
            st.warning(f"Nu am putut interoga {table_name} ({tip}): {e}")

    # ----------------------------
    # 4) Afișare rezultate + expandere “derulator”
    # ----------------------------
    st.write("---")
    st.markdown("### ✅ Rezultate căutare")

    if not all_rows:
        st.info("Nu există rezultate pentru criteriile selectate.")
        return

    st.caption(f"Total rezultate: {len(all_rows)} (din tipurile: {', '.join(tipuri_sel)})")

    # Sortare simplă (după cod_identificare dacă există)
    def sort_key(r):
        return str(r.get("cod_identificare", "")).strip()

    all_rows = sorted(all_rows, key=sort_key)

    # “Rezumat” per rând + expander pentru detalii
    for r in all_rows:
        cod = str(r.get("cod_identificare", "")).strip() or "(fără cod_identificare)"
        tip = r.get("_tip", "")
        tabela = r.get("_tabela", "")

        # titlu – încercăm câteva chei uzuale
        titlu = ""
        for cand in ["titlu_proiect", "titlu", "obiect_contract", "denumire_proiect"]:
            if r.get(cand):
                titlu = str(r.get(cand)).strip()
                break

        header = f"🆔 {cod}  |  {titlu if titlu else '—'}  ({tip})"

        with st.expander(header, expanded=False):
            st.caption(f"Sursă: {tabela}")

            # 4.1 Detalii complete (toate câmpurile)
            st.markdown("#### 📌 Detalii (toate câmpurile)")
            # afișare “key: value”
            # (păstrăm lizibil, fără tabel imens dacă sunt multe coloane)
            for k in sorted([k for k in r.keys() if not k.startswith("_")]):
                v = r.get(k)
                if v is None or str(v).strip() == "":
                    continue
                st.write(f"**{k}**: {v}")

            st.write("---")

            # 4.2 Atașamente (tabele relaționate)
            st.markdown("#### 📎 Atașamente")
            tabs = st.tabs(list(related_tables_guess.keys()))

            for tab, (comp_name, candidates) in zip(tabs, related_tables_guess.items()):
                with tab:
                    found_any = False
                    for tname in candidates:
                        data, err = try_fetch_related_table(supabase, tname, cod)
                        if data is None:
                            # tabelă inexistentă / permisiuni / etc. -> încercăm următoarea
                            continue
                        # dacă tabela există dar n-are rânduri -> tot o considerăm găsită
                        found_any = True
                        st.markdown(f"**Tabel:** `{tname}`")
                        if len(data) == 0:
                            st.info("Nu există înregistrări atașate pentru acest ID.")
                        else:
                            st.dataframe(data, use_container_width=True, height=260)
                        st.write("---")
                        # dacă vrei să afișezi doar prima tabelă găsită, comentează linia de mai jos:
                        # break

                    if not found_any:
                        st.warning(
                            "Nu am găsit încă o tabelă de atașamente disponibilă pentru această componentă "
                            "(sau nu există permisiuni / nu e creată). "
                            "După ce îmi spui exact numele tabelelor de componente, le fixăm în 2 minute."
                        )


if __name__ == "__main__":
    run()
