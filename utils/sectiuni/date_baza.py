# =========================================================
# IDBDC/utils/sectiuni/date_baza.py
# VERSIUNE: 2.0
# STATUS: CORECTAT - cache_data cu hash corect pentru supabase
# DATA: 2026.05.02
# =========================================================

import streamlit as st
import pandas as pd
from utils.date_helpers import to_date, calc_durata, add_months, sub_months
from utils.supabase_helpers import safe_select_eq

# CORECȚIE [4A]: Funcția _get_status_list avea un defect subtil:
# funcția internă _fetch() era decorată cu @st.cache_data, dar
# primea obiectul supabase din closure (din exterior), nu ca
# parametru explicit. Streamlit nu putea "vedea" că supabase
# s-a schimbat între sesiuni și returna uneori date din cache
# incorect. Mai grav: în unele versiuni Streamlit, un obiect
# de conexiune capturat în closure poate cauza erori de
# serializare care forțează reîncărcarea completă a paginii
# — contribuind la "licarire".
#
# SOLUȚIA: Supabase este transmis ca parametru explicit cu
# prefix underscore (_supabase), care instruiește Streamlit
# să NU îl includă în cheia de cache (obiectele de conexiune
# nu sunt serializabile). Cache-ul funcționează corect pe
# conținutul interogării, nu pe obiectul conexiunii.

@st.cache_data(show_spinner=False, ttl=600)
def _get_status_list(_supabase):
    """
    Preia lista de statusuri din nomenclator.
    Prefixul _ la parametru îi spune lui Streamlit să nu
    încerce să serializeze obiectul de conexiune pentru cache.
    """
    try:
        res = _supabase.table("nom_status_proiect").select(
            "status_contract_proiect"
        ).execute()
        return [
            r["status_contract_proiect"]
            for r in (res.data or [])
            if r.get("status_contract_proiect")
        ]
    except Exception:
        return []


def _fmt_date(date_val):
    if date_val is None:
        return None
    if pd.isna(date_val):
        return None
    if hasattr(date_val, 'strftime'):
        return date_val.strftime("%Y-%m-%d")
    if hasattr(date_val, 'isoformat'):
        return date_val.isoformat()
    return str(date_val)


def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_label, tabela_nume, is_new, date_existente):
    """
    Randare și salvare date de bază pentru orice tip de entitate.
    Parametri:
        supabase: clientul Supabase
        cod_introdus: codul identificator
        cat_sel: categoria selectată (ex: "Contracte")
        tip_label: eticheta vizuală a tipului (ex: "CEP", "TERȚI", "SPECIALE")
        tabela_nume: numele tabelei SQL (ex: "base_contracte_cep")
        is_new: boolean - dacă este înregistrare nouă
        date_existente: dict cu datele existente (pentru editare)
    """
    # CORECȚIE [4B]: Apelul corect — supabase transmis ca argument,
    # nu capturat în closure. Efectul imediat: lista de statusuri
    # se încarcă o singură dată la 10 minute, nu la fiecare
    # reîncărcare de pagină. Aceasta reduce semnificativ
    # "licarirea" în secțiunile Date de Bază.
    status_list = _get_status_list(supabase)

    di = to_date(date_existente.get("data_inceput"))
    ds = to_date(date_existente.get("data_sfarsit"))
    dur_ex = date_existente.get("durata")

    # Calcule automate
    if di and ds and (dur_ex is None or dur_ex == 0):
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
        "DURATA": st.column_config.NumberColumn("DURATA (luni)", format="%d", min_value=0),
        "STATUS CONTRACT": st.column_config.SelectboxColumn("🔖 STATUS CONTRACT", options=status_list),
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
        "data_contract": _fmt_date(row["DATA CONTRACTULUI"]),
        "obiectul_contractului": row["OBIECTUL CONTRACTULUI"],
        "denumire_beneficiar": row["BENEFICIAR"],
        "data_inceput": _fmt_date(di_e),
        "data_sfarsit": _fmt_date(ds_e),
        "durata": dur_e if dur_e else None,
        "status_contract_proiect": row["STATUS CONTRACT"] if row["STATUS CONTRACT"] else None,
    }
