# =========================================================
# utils/contracte_common.py
# v.modul.1.1 - Funcții comune pentru administrare contracte (CEP, TERTI, SPECIALE)
# =========================================================

import streamlit as st
import pandas as pd
from utils.date_helpers import to_date, calc_durata, add_months, sub_months
from utils.supabase_helpers import safe_select_eq

# =========================================================
# Helper pentru status (dropdown)
# =========================================================
def _get_status_list(supabase):
    @st.cache_data(show_spinner=False, ttl=600)
    def _fetch():
        try:
            res = supabase.table("nom_status_proiect").select("status_contract_proiect").execute()
            return [r["status_contract_proiect"] for r in (res.data or []) if r.get("status_contract_proiect")]
        except Exception:
            return []
    return _fetch()

# =========================================================
# FIȘA 1 — DATE DE BAZĂ (comună)
# =========================================================
def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_label, tabela_nume, is_new, date_existente):
    status_list = _get_status_list(supabase)

    di = to_date(date_existente.get("data_inceput"))
    ds = to_date(date_existente.get("data_sfarsit"))
    dur_ex = date_existente.get("durata")

    if di and ds and not dur_ex:
        dur_ex = calc_durata(di, ds)
    elif di and dur_ex and not ds:
        ds = add_months(di, dur_ex)
    elif ds and dur_ex and not di:
        di = sub_months(ds, dur_ex)
    if di and ds:
        dur_ex = calc_durata(di, ds)

    row_init = {
        "CATEGORIE": cat_sel,
        "TIPUL DE CONTRACT": tip_label,
        "NR.CONTRACT": cod_introdus,
        "DATA CONTRACTULUI": to_date(date_existente.get("data_contract")),
        "OBIECTUL CONTRACTULUI": date_existente.get("obiectul_contractului", ""),
        "BENEFICIAR": date_existente.get("denumire_beneficiar", ""),
        "DATA DE INCEPUT": di,
        "DATA DE SFARSIT": ds,
        "DURATA": int(dur_ex) if dur_ex else 0,
        "STATUS CONTRACT": date_existente.get("status_contract_proiect", ""),
    }
    df = pd.DataFrame([row_init])

    col_cfg = {
        "CATEGORIE": st.column_config.TextColumn("CATEGORIE", disabled=True),
        "TIPUL DE CONTRACT": st.column_config.TextColumn("TIPUL DE CONTRACT", disabled=True),
        "NR.CONTRACT": st.column_config.TextColumn("NR.CONTRACT", disabled=True),
        "DATA CONTRACTULUI": st.column_config.DateColumn("📅 DATA CONTRACTULUI", format="DD-MM-YYYY"),
        "OBIECTUL CONTRACTULUI": st.column_config.TextColumn("OBIECTUL CONTRACTULUI", width="large"),
        "BENEFICIAR": st.column_config.TextColumn("BENEFICIAR"),
        "DATA DE INCEPUT": st.column_config.DateColumn("📅 DATA DE INCEPUT", format="DD-MM-YYYY"),
        "DATA DE SFARSIT": st.column_config.DateColumn("📅 DATA DE SFARSIT", format="DD-MM-YYYY"),
        "DURATA": st.column_config.NumberColumn("DURATA", format="%d", min_value=0),
        "STATUS CONTRACT": st.column_config.SelectboxColumn("🔖 STATUS CONTRACT", options=status_list),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"{tabela_nume}_baza_editor",
    )
    row = df_edit.iloc[0]

    di_e = row["DATA DE INCEPUT"]
    ds_e = row["DATA DE SFARSIT"]
    dur_e = int(row["DURATA"]) if row["DURATA"] else 0

    if di_e and ds_e:
        dur_e = calc_durata(di_e, ds_e)
        st.caption(f"📅 Durată calculată automat: {dur_e} luni")
    elif di_e and dur_e and not ds_e:
        ds_e = add_months(di_e, dur_e)
        st.caption(f"📅 Data de sfarsit calculată automat: {ds_e}")
    elif ds_e and dur_e and not di_e:
        di_e = sub_months(ds_e, dur_e)
        st.caption(f"📅 Data de inceput calculată automat: {di_e}")

    return {
        "cod_identificare": cod_introdus,
        "denumire_categorie": cat_sel,
        "acronim_tip_contract": tip_label,
        "data_contract": row["DATA CONTRACTULUI"].isoformat() if row["DATA CONTRACTULUI"] else None,
        "obiectul_contractului": row["OBIECTUL CONTRACTULUI"],
        "denumire_beneficiar": row["BENEFICIAR"],
        "data_inceput": di_e.isoformat() if di_e else None,
        "data_sfarsit": ds_e.isoformat() if ds_e else None,
        "durata": dur_e if dur_e else None,
        "status_contract_proiect": row["STATUS CONTRACT"] if row["STATUS CONTRACT"] else None,
    }

# =========================================================
# FIȘA 2 — DATE FINANCIARE (comună)
# =========================================================
def render_date_financiare(supabase, cod_introdus, is_new, date_existente):
    VALUTE = ["LEI", "EURO", "USD"]
    if is_new or not date_existente:
        row_ex = {"valuta": "LEI", "valoare_contract_cep_terti_speciale": 0.0}
    else:
        row_ex = date_existente[0]

    try:
        val_ex = float(row_ex.get("valoare_contract_cep_terti_speciale") or 0)
    except:
        val_ex = 0.0
    valuta_ex = row_ex.get("valuta", "LEI")
    if valuta_ex not in VALUTE:
        valuta_ex = "LEI"

    df = pd.DataFrame([{
        "VALUTA": valuta_ex,
        "VALOARE CONTRACT": val_ex,
    }])

    col_cfg = {
        "VALUTA": st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
        "VALOARE CONTRACT": st.column_config.NumberColumn("💰 VALOARE CONTRACT", format="%,.2f", min_value=0.0),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"fin_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]
    return [{
        "cod_identificare": cod_introdus,
        "valuta": row["VALUTA"],
        "valoare_contract_cep_terti_speciale": float(row["VALOARE CONTRACT"] or 0),
    }]

# =========================================================
# FIȘA 3 — ECHIPĂ (comună) – copiată din admin_cep.py original
# =========================================================
def render_echipa(supabase, cod_introdus, is_new, date_existente):
    # =========================================================
    # Acest cod este identic cu funcția render_echipa din admin_cep.py
    # Singura modificare: am înlocuit referințele la _safe_select_eq cu safe_select_eq din helper
    # =========================================================
    
    # Citire persoane din det_resurse_umane
    try:
        res = supabase.table("det_resurse_umane").select(
            "nume_prenume,email,telefon_mobil,telefon_fix,acronim_departament"
        ).order("nume_prenume").execute()
        persoane_data = res.data or []
    except Exception as e:
        st.error(f"❌ Eroare citire det_resurse_umane: {e}")
        persoane_data = []

    # Citire departamente
    try:
        res2 = supabase.table("nom_departament").select(
            "acronim_departament,denumire_departament"
        ).execute()
        dep_map = {r["acronim_departament"]: r["denumire_departament"]
                   for r in (res2.data or []) if r.get("acronim_departament")}
    except Exception as e:
        st.error(f"❌ Eroare citire nom_departament: {e}")
        dep_map = {}

    if not persoane_data:
        st.warning("⚠️ Nu s-au găsit persoane în tabela det_resurse_umane. Verificați conexiunea la baza de date.")
    persoane_list = [""] + [p["nume_prenume"] for p in persoane_data if p.get("nume_prenume")]

    # Indexuri rapide pentru completare automată
    info_map = {}
    for p in persoane_data:
        n = p.get("nume_prenume", "")
        if not n:
            continue
        acronim = p.get("acronim_departament", "")
        den = dep_map.get(acronim, "")
        info_map[n] = {
            "dep":   f"{acronim} - {den}" if acronim and den else acronim,
            "email": p.get("email", ""),
            "mob":   p.get("telefon_mobil", ""),
            "fix":   p.get("telefon_fix", ""),
        }

    # Construire tabel inițial
    NR_RANDURI_INIT = 5

    if is_new or not date_existente:
        rows_init = [
            {"NUME ȘI PRENUME": "", "ROLUL ÎN CONTRACT": "",
             "PERSOANĂ DE CONTACT": False,
             "DEPARTAMENT": "", "EMAIL": "",
             "TELEFON MOBIL": "", "TELEFON FIX": ""}
            for _ in range(NR_RANDURI_INIT)
        ]
    else:
        rows_init = []
        for r in date_existente:
            n = r.get("nume_prenume", "")
            info = info_map.get(n, {"dep": "", "email": "", "mob": "", "fix": ""})
            rows_init.append({
                "NUME ȘI PRENUME":     n,
                "ROLUL ÎN CONTRACT":   r.get("rol", ""),
                "PERSOANĂ DE CONTACT": bool(r.get("persoana_contact", False)),
                "DEPARTAMENT":         info["dep"],
                "EMAIL":               info["email"],
                "TELEFON MOBIL":       info["mob"],
                "TELEFON FIX":         info["fix"],
            })
        while len(rows_init) < NR_RANDURI_INIT:
            rows_init.append({
                "NUME ȘI PRENUME": "", "ROLUL ÎN CONTRACT": "",
                "PERSOANĂ DE CONTACT": False,
                "DEPARTAMENT": "", "EMAIL": "",
                "TELEFON MOBIL": "", "TELEFON FIX": ""
            })

    key_rows = f"echipa_rows_{cod_introdus}"
    if key_rows not in st.session_state:
        st.session_state[key_rows] = rows_init

    df = pd.DataFrame(st.session_state[key_rows])

    col_cfg = {
        "NUME ȘI PRENUME": st.column_config.SelectboxColumn(
            "👤 NUME ȘI PRENUME", options=persoane_list, required=False
        ),
        "ROLUL ÎN CONTRACT":   st.column_config.TextColumn("ROLUL ÎN CONTRACT"),
        "PERSOANĂ DE CONTACT": st.column_config.CheckboxColumn("⭐ PERSOANĂ DE CONTACT"),
        "DEPARTAMENT":         st.column_config.TextColumn("DEPARTAMENT", disabled=True),
        "EMAIL":               st.column_config.TextColumn("EMAIL", disabled=True),
        "TELEFON MOBIL":       st.column_config.TextColumn("TELEFON MOBIL", disabled=True),
        "TELEFON FIX":         st.column_config.TextColumn("TELEFON FIX", disabled=True),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key="echipa_editor",
    )

    # Completare automată
    df_updated = df_edit.copy()
    for i, row in df_edit.iterrows():
        n = row.get("NUME ȘI PRENUME", "")
        info = info_map.get(n, {"dep": "", "email": "", "mob": "", "fix": ""})
        df_updated.at[i, "DEPARTAMENT"]   = info["dep"]
        df_updated.at[i, "EMAIL"]         = info["email"]
        df_updated.at[i, "TELEFON MOBIL"] = info["mob"]
        df_updated.at[i, "TELEFON FIX"]   = info["fix"]

    if not df_updated.equals(df_edit):
        st.session_state[key_rows] = df_updated.to_dict("records")
        st.rerun()

    # Buton adăugare rând
    if st.button("➕ Adaugă membru", key="add_membru"):
        st.session_state[key_rows].append({
            "NUME ȘI PRENUME": "", "ROLUL ÎN CONTRACT": "",
            "PERSOANĂ DE CONTACT": False,
            "DEPARTAMENT": "", "EMAIL": "",
            "TELEFON MOBIL": "", "TELEFON FIX": ""
        })
        st.rerun()

    # Construire listă pentru salvare
    rezultat = []
    for _, row in df_updated.iterrows():
        n = str(row.get("NUME ȘI PRENUME", "")).strip()
        if not n:
            continue
        rezultat.append({
            "cod_identificare": cod_introdus,
            "nume_prenume":     n,
            "rol":              str(row.get("ROLUL ÎN CONTRACT", "")).strip(),
            "persoana_contact": bool(row.get("PERSOANĂ DE CONTACT", False)),
            "functie_upt":      "",
        })
    return rezultat
