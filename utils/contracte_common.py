# =========================================================
# IDBDC/utils/contracte_common.py
# VERSIUNE: 7.0
# STATUS: STABIL - Complet și funcțional
# DATA: 2026.05.08
# =========================================================
# CONȚINUT:
#   Logica comună pentru toate tipurile de contracte
#   (CEP, TERȚI, SPECIALE). Conține cele 3 funcții:
#     - render_date_de_baza
#     - render_date_financiare
#     - render_echipa
#
# MODIFICĂRI VERSIUNEA 7.0:
#   - Adăugat _fmt_date() — lipsea din v6.1, cauza erorii
#     AttributeError la import.
#   - render_echipa: implementare completă (nu mai este
#     placeholder/pass) — copiată din utils/sectiuni/echipa.py
#     v7.0, identică și funcțională pentru toate contractele.
#   - Docstring actualizat complet.
# =========================================================

import streamlit as st
import pandas as pd
from utils.date_helpers import to_date, calc_durata, add_months, sub_months


# =========================================================
# HELPERS
# =========================================================
def _fmt_date(val):
    """Convertește orice valoare dată în string ISO (YYYY-MM-DD) sau None."""
    if not val:
        return None
    if hasattr(val, "isoformat"):
        return val.isoformat()
    s = str(val).strip()
    return s if s not in ("", "None", "nan") else None


def _get_status_list(supabase):
    @st.cache_data(show_spinner=False, ttl=600)
    def _fetch(_sb):
        try:
            res = _sb.table("nom_status_proiect").select("status_contract_proiect").execute()
            return [r["status_contract_proiect"] for r in (res.data or []) if r.get("status_contract_proiect")]
        except Exception:
            return []
    return _fetch(supabase)


# =========================================================
# FIȘA 1 — DATE DE BAZĂ
# =========================================================
def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_label, tabela_nume, is_new, date_existente):
    """
    Randează secțiunea Date de bază pentru contracte.
    Parametri:
        supabase    : clientul Supabase
        cod_introdus: codul identificator
        cat_sel     : categoria (ex: "Contracte")
        tip_label   : eticheta tipului (ex: "CEP", "TERȚI", "SPECIALE")
        tabela_nume : tabela SQL (ex: "base_contracte_cep")
        is_new      : True dacă este înregistrare nouă
        date_existente: dict cu datele existente
    """
    status_list = _get_status_list(supabase)

    di     = to_date(date_existente.get("data_inceput"))
    ds     = to_date(date_existente.get("data_sfarsit"))
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
        "CATEGORIE":             cat_sel,
        "TIPUL DE CONTRACT":     tip_label,
        "NR.CONTRACT":           cod_introdus,
        "DATA CONTRACTULUI":     to_date(date_existente.get("data_contract")),
        "OBIECTUL CONTRACTULUI": date_existente.get("obiectul_contractului", ""),
        "BENEFICIAR":            date_existente.get("denumire_beneficiar", ""),
        "DATA DE INCEPUT":       di,
        "DATA DE SFARSIT":       ds,
        "DURATA":                int(dur_ex) if dur_ex else 0,
        "STATUS CONTRACT":       date_existente.get("status_contract_proiect", ""),
    }
    df = pd.DataFrame([row_init])

    col_cfg = {
        "CATEGORIE":             st.column_config.TextColumn("CATEGORIE", disabled=True),
        "TIPUL DE CONTRACT":     st.column_config.TextColumn("TIPUL DE CONTRACT", disabled=True),
        "NR.CONTRACT":           st.column_config.TextColumn("NR.CONTRACT", disabled=True),
        "DATA CONTRACTULUI":     st.column_config.DateColumn("📅 DATA CONTRACTULUI", format="DD-MM-YYYY"),
        "OBIECTUL CONTRACTULUI": st.column_config.TextColumn("OBIECTUL CONTRACTULUI", width="large"),
        "BENEFICIAR":            st.column_config.TextColumn("BENEFICIAR"),
        "DATA DE INCEPUT":       st.column_config.DateColumn("📅 DATA DE INCEPUT", format="DD-MM-YYYY"),
        "DATA DE SFARSIT":       st.column_config.DateColumn("📅 DATA DE SFARSIT", format="DD-MM-YYYY"),
        "DURATA":                st.column_config.NumberColumn("DURATA", format="%d", min_value=0),
        "STATUS CONTRACT":       st.column_config.SelectboxColumn("🔖 STATUS CONTRACT", options=status_list),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"{tabela_nume}_baza_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    di_e  = row["DATA DE INCEPUT"]
    ds_e  = row["DATA DE SFARSIT"]
    dur_e = int(row["DURATA"]) if row["DURATA"] else 0

    if di_e and ds_e:
        dur_e = calc_durata(di_e, ds_e)
        st.caption(f"📅 Durată calculată automat: {dur_e} luni")
    elif di_e and dur_e and not ds_e:
        ds_e = add_months(di_e, dur_e)
        st.caption(f"📅 Data de sfârsit calculată automat: {ds_e}")
    elif ds_e and dur_e and not di_e:
        di_e = sub_months(ds_e, dur_e)
        st.caption(f"📅 Data de început calculată automat: {di_e}")

    return {
        "cod_identificare":        cod_introdus,
        "denumire_categorie":      cat_sel,
        "acronim_tip_contract":    tip_label,
        "data_contract":           _fmt_date(row["DATA CONTRACTULUI"]),
        "obiectul_contractului":   str(row["OBIECTUL CONTRACTULUI"]).strip() if row["OBIECTUL CONTRACTULUI"] else None,
        "denumire_beneficiar":     str(row["BENEFICIAR"]).strip()            if row["BENEFICIAR"]            else None,
        "data_inceput":            _fmt_date(di_e),
        "data_sfarsit":            _fmt_date(ds_e),
        "durata":                  dur_e if dur_e else None,
        "status_contract_proiect": row["STATUS CONTRACT"] if row["STATUS CONTRACT"] else None,
    }


# =========================================================
# FIȘA 2 — DATE FINANCIARE
# =========================================================
def render_date_financiare(supabase, cod_introdus, is_new, date_existente):
    """Randează secțiunea Date financiare pentru contracte."""
    VALUTE = ["LEI", "EUR", "USD"]

    if is_new or not date_existente:
        row_ex = {"valuta": "LEI", "valoare_contract_cep_terti_speciale": 0.0}
    else:
        row_ex = date_existente[0] if isinstance(date_existente, list) else date_existente

    try:
        val_ex = float(row_ex.get("valoare_contract_cep_terti_speciale") or 0)
    except (TypeError, ValueError):
        val_ex = 0.0

    valuta_ex = row_ex.get("valuta", "LEI") or "LEI"
    if valuta_ex not in VALUTE:
        valuta_ex = "LEI"

    df = pd.DataFrame([{
        "VALUTA":           valuta_ex,
        "VALOARE CONTRACT": val_ex,
    }])

    col_cfg = {
        "VALUTA":           st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
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
        "cod_identificare":                   cod_introdus,
        "valuta":                             row["VALUTA"],
        "valoare_contract_cep_terti_speciale": float(row["VALOARE CONTRACT"] or 0),
    }]


# =========================================================
# FIȘA 3 — ECHIPĂ
# =========================================================
def render_echipa(supabase, cod_introdus, is_new, date_existente):
    """
    Randează secțiunea Echipă pentru contracte.
    Identică cu utils/sectiuni/echipa.py v7.0.
    """
    @st.cache_data(show_spinner=False, ttl=600)
    def _fetch_persoane(_sb):
        try:
            res = _sb.table("det_resurse_umane").select(
                "nume_prenume,email,telefon_mobil,telefon_fix,acronim_departament"
            ).order("nume_prenume").execute()
            return res.data or []
        except Exception:
            return []

    @st.cache_data(show_spinner=False, ttl=600)
    def _fetch_departamente(_sb):
        try:
            res2 = _sb.table("nom_departament").select(
                "acronim_departament,denumire_departament"
            ).execute()
            return {
                r["acronim_departament"]: r["denumire_departament"]
                for r in (res2.data or []) if r.get("acronim_departament")
            }
        except Exception:
            return {}

    persoane_data = _fetch_persoane(supabase)
    dep_map       = _fetch_departamente(supabase)

    if not persoane_data:
        st.warning("⚠️ Nu s-au găsit persoane în tabela det_resurse_umane.")

    persoane_list = [""] + [p["nume_prenume"] for p in persoane_data if p.get("nume_prenume")]

    info_map = {}
    for p in persoane_data:
        n = p.get("nume_prenume", "")
        if not n:
            continue
        acronim = p.get("acronim_departament", "")
        den     = dep_map.get(acronim, "")
        info_map[n] = {
            "dep":   f"{acronim} - {den}" if acronim and den else acronim,
            "email": p.get("email", ""),
            "mob":   p.get("telefon_mobil", ""),
            "fix":   p.get("telefon_fix", ""),
        }

    NR_RANDURI_INIT = 5
    key_editor    = f"echipa_editor_{cod_introdus}"
    key_data_init = f"echipa_data_init_{cod_introdus}"

    if key_data_init not in st.session_state:
        if is_new or not date_existente:
            rows_init = [
                {"NUME ȘI PRENUME": "", "ROLUL ÎN CONTRACT": "",
                 "PERSOANĂ DE CONTACT": False, "DEPARTAMENT": "",
                 "EMAIL": "", "TELEFON MOBIL": "", "TELEFON FIX": ""}
                for _ in range(NR_RANDURI_INIT)
            ]
        else:
            rows_init = []
            for r in date_existente:
                n    = r.get("nume_prenume", "")
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
                    "PERSOANĂ DE CONTACT": False, "DEPARTAMENT": "",
                    "EMAIL": "", "TELEFON MOBIL": "", "TELEFON FIX": "",
                })
        st.session_state[key_data_init] = rows_init

    df_init = pd.DataFrame(st.session_state[key_data_init])

    col_cfg = {
        "NUME ȘI PRENUME":     st.column_config.SelectboxColumn("👤 NUME ȘI PRENUME", options=persoane_list, required=False),
        "ROLUL ÎN CONTRACT":   st.column_config.TextColumn("ROLUL ÎN CONTRACT"),
        "PERSOANĂ DE CONTACT": st.column_config.CheckboxColumn("⭐ PERSOANĂ DE CONTACT"),
        "DEPARTAMENT":         st.column_config.TextColumn("DEPARTAMENT", disabled=True),
        "EMAIL":               st.column_config.TextColumn("EMAIL", disabled=True),
        "TELEFON MOBIL":       st.column_config.TextColumn("TELEFON MOBIL", disabled=True),
        "TELEFON FIX":         st.column_config.TextColumn("TELEFON FIX", disabled=True),
    }

    df_edit = st.data_editor(
        df_init,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=key_editor,
    )

    rows_curente = st.session_state[key_data_init]
    needs_rerun  = False
    editor_state = st.session_state.get(key_editor, {})
    edited_rows  = editor_state.get("edited_rows", {}) if isinstance(editor_state, dict) else {}

    for i, row in df_edit.iterrows():
        if i >= len(rows_curente):
            break
        nume_nou   = row.get("NUME ȘI PRENUME", "") or ""
        nume_vechi = rows_curente[i].get("NUME ȘI PRENUME", "") or ""

        rol_din_editor = edited_rows.get(i, {}).get("ROLUL ÎN CONTRACT") if i in edited_rows else None
        rol_final      = rol_din_editor if rol_din_editor is not None else (row.get("ROLUL ÎN CONTRACT", "") or "")

        rows_curente[i]["ROLUL ÎN CONTRACT"]   = str(rol_final).strip()
        rows_curente[i]["PERSOANĂ DE CONTACT"] = bool(
            edited_rows.get(i, {}).get("PERSOANĂ DE CONTACT", row.get("PERSOANĂ DE CONTACT", False))
        )

        if nume_nou != nume_vechi:
            info = info_map.get(nume_nou, {"dep": "", "email": "", "mob": "", "fix": ""})
            rows_curente[i]["NUME ȘI PRENUME"] = nume_nou
            rows_curente[i]["DEPARTAMENT"]     = info["dep"]
            rows_curente[i]["EMAIL"]           = info["email"]
            rows_curente[i]["TELEFON MOBIL"]   = info["mob"]
            rows_curente[i]["TELEFON FIX"]     = info["fix"]
            needs_rerun = True

    st.session_state[key_data_init] = rows_curente

    if needs_rerun:
        st.rerun()

    if st.button("➕ Adaugă membru", key=f"add_membru_{cod_introdus}"):
        rows_sync = st.session_state[key_data_init]
        for i, row in df_edit.iterrows():
            if i < len(rows_sync):
                rol_din_editor = edited_rows.get(i, {}).get("ROLUL ÎN CONTRACT") if i in edited_rows else None
                rows_sync[i]["NUME ȘI PRENUME"]     = row.get("NUME ȘI PRENUME", "") or ""
                rows_sync[i]["ROLUL ÎN CONTRACT"]   = str(rol_din_editor).strip() if rol_din_editor is not None else (row.get("ROLUL ÎN CONTRACT", "") or "")
                rows_sync[i]["PERSOANĂ DE CONTACT"] = bool(row.get("PERSOANĂ DE CONTACT", False))
                n = rows_sync[i]["NUME ȘI PRENUME"]
                if n and n in info_map:
                    info = info_map[n]
                    rows_sync[i]["DEPARTAMENT"]   = info["dep"]
                    rows_sync[i]["EMAIL"]         = info["email"]
                    rows_sync[i]["TELEFON MOBIL"] = info["mob"]
                    rows_sync[i]["TELEFON FIX"]   = info["fix"]
        rows_sync.append({
            "NUME ȘI PRENUME": "", "ROLUL ÎN CONTRACT": "",
            "PERSOANĂ DE CONTACT": False, "DEPARTAMENT": "",
            "EMAIL": "", "TELEFON MOBIL": "", "TELEFON FIX": "",
        })
        st.session_state[key_data_init] = rows_sync
        if key_editor in st.session_state:
            del st.session_state[key_editor]
        st.rerun()

    rezultat = []
    for i, row in df_edit.iterrows():
        n = str(row.get("NUME ȘI PRENUME", "") or "").strip()
        if not n:
            continue
        rol_din_editor = edited_rows.get(i, {}).get("ROLUL ÎN CONTRACT") if i in edited_rows else None
        rol     = str(rol_din_editor).strip() if rol_din_editor is not None else str(row.get("ROLUL ÎN CONTRACT", "") or "").strip()
        contact = bool(edited_rows.get(i, {}).get("PERSOANĂ DE CONTACT", row.get("PERSOANĂ DE CONTACT", False)))
        rezultat.append({
            "cod_identificare": cod_introdus,
            "nume_prenume":     n,
            "rol":              rol,
            "persoana_contact": contact,
            "functie_upt":      "",
        })
    return rezultat
