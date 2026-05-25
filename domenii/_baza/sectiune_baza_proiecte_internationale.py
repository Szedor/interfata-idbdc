# =========================================================
# IDBDC/domenii/_baza/sectiune_baza_proiecte_internationale.py
# VERSIUNE: 1.3
# STATUS: CORECTAT - eroare StreamlitAPIException + dropdown ROL UPT
# DATA: 2026.05.26
# =========================================================
# MODIFICARI VERSIUNEA 1.3:
#   - Eliminat DateColumn din col_cfg pentru a evita eroarea de compatibilitate
#   - Datele sunt afisate ca text (TextColumn) pentru stabilitate
#   - Adaugat dropdown pentru ROL UPT cu optiunile specificate
#   - Pastrat toate functiile de calcul (durata, date) existente
# =========================================================

import streamlit as st
import pandas as pd
from datetime import date as _date
from utils.date_helpers import to_date, calc_durata, add_months, sub_months

# =========================================================
# OPTIUNI DROPDOWN PENTRU ROL UPT
# =========================================================
ROL_UPT_OPTIONS = [
    "Coordonator",
    "Coordonator asociat",
    "Partener",
    "Partener principal",
    "Partener asociat",
    "Beneficiar",
    "Beneficiar asociat",
    "Subcontractor",
    "Terț afiliat"
]

@st.cache_data(show_spinner=False, ttl=600)
def _get_status_list(_supabase):
    try:
        res = _supabase.table("nom_status_proiect").select("status_contract_proiect").execute()
        return [r["status_contract_proiect"] for r in (res.data or []) if r.get("status_contract_proiect")]
    except Exception:
        return []


def _fmt_date(v):
    if v is None:
        return None
    if hasattr(v, 'strftime'):
        return v.strftime("%Y-%m-%d")
    if hasattr(v, 'isoformat'):
        return v.isoformat()
    s = str(v).strip()
    return s if s not in ("", "None", "nan") else None


def _safe_date(v):
    """Returneaza obiect date Python sau None — niciodata string."""
    if v is None:
        return None
    if isinstance(v, _date):
        return v
    try:
        result = to_date(v)
        return result
    except Exception:
        return None


def _safe_int(v):
    """Conversie robusta la int pentru NumberColumn."""
    if v is None:
        return 0
    try:
        f = float(str(v).replace(",", ".").strip())
        return int(f)
    except (ValueError, TypeError):
        return 0


def _safe_str(v):
    """Returneaza string gol daca None, altfel string."""
    if v is None:
        return ""
    return str(v).strip()


def render(supabase, cod_introdus, cat_sel, tip_label, tabela_nume, is_new, date_existente):
    status_list = _get_status_list(supabase)

    di     = _safe_date(date_existente.get("data_inceput"))
    ds     = _safe_date(date_existente.get("data_sfarsit"))
    dur_ex = _safe_int(date_existente.get("durata"))

    if di and ds and not dur_ex:
        dur_ex = calc_durata(di, ds)
    elif di and dur_ex and not ds:
        ds = add_months(di, dur_ex)
    elif ds and dur_ex and not di:
        di = sub_months(ds, dur_ex)
    if di and ds:
        dur_ex = calc_durata(di, ds)

    # Valoare initiala pentru ROL UPT dropdown
    rol_upt_initial = _safe_str(date_existente.get("rol_upt"))
    if rol_upt_initial not in ROL_UPT_OPTIONS:
        rol_upt_initial = ROL_UPT_OPTIONS[0]  # default "Coordonator"

    row_init = {
        "CATEGORIE":             cat_sel,
        "TIPUL DE PROIECT":      tip_label,
        "ID PROIECT":            cod_introdus,
        "TITLUL PROIECTULUI":    _safe_str(date_existente.get("titlul_proiect")),
        "ACRONIMUL PROIECTULUI": _safe_str(date_existente.get("acronim_proiect")),
        "DATA DE INCEPUT":       di,
        "DATA DE SFARSIT":       ds,
        "DURATA (luni)":         dur_ex,
        "STATUS PROIECT":        _safe_str(date_existente.get("status_contract_proiect")),
        "SCOR EVALUARE":         _safe_str(date_existente.get("scor_evaluare")),
        "NR.PARTICIPANTI":       _safe_str(date_existente.get("numar_participanti")),
        "DENUMIRE PARTICIPANTI": _safe_str(date_existente.get("denumire_participanti")),
        "ROL UPT":               rol_upt_initial,
        "APELUL":                _safe_str(date_existente.get("identificare_apel")),
        "DATA LIMITA DEPUNERE":  _safe_date(date_existente.get("data_inchidere_apel")),
        "PROGRAM DE FINANTARE":  _safe_str(date_existente.get("program_finantare")),
        "TEMA / TOPIC":          _safe_str(date_existente.get("tema_topic")),
        "SCHEMA DE FINANTARE":   _safe_str(date_existente.get("schema_de_finantare")),
        "WEBSITE":               _safe_str(date_existente.get("website")),
        "OBSERVATII":            _safe_str(date_existente.get("observatii")),
    }
    df = pd.DataFrame([row_init])

    # =========================================================
    # CONFIGURARE COLOANE - FARA DateColumn pentru stabilitate
    # =========================================================
    col_cfg = {
        "CATEGORIE":             st.column_config.TextColumn("CATEGORIE", disabled=True),
        "TIPUL DE PROIECT":      st.column_config.TextColumn("TIPUL DE PROIECT", disabled=True),
        "ID PROIECT":            st.column_config.TextColumn("ID PROIECT", disabled=True),
        "TITLUL PROIECTULUI":    st.column_config.TextColumn("TITLUL PROIECTULUI", width="large"),
        "ACRONIMUL PROIECTULUI": st.column_config.TextColumn("ACRONIMUL PROIECTULUI"),
        "DATA DE INCEPUT":       st.column_config.TextColumn("📅 DATA DE INCEPUT (AAAA-LL-ZZ)"),
        "DATA DE SFARSIT":       st.column_config.TextColumn("📅 DATA DE SFARSIT (AAAA-LL-ZZ)"),
        "DURATA (luni)":         st.column_config.NumberColumn("DURATA (luni)", format="%d", min_value=0),
        "STATUS PROIECT":        st.column_config.SelectboxColumn("🔖 STATUS PROIECT", options=status_list),
        "SCOR EVALUARE":         st.column_config.TextColumn("SCOR EVALUARE"),
        "NR.PARTICIPANTI":       st.column_config.TextColumn("NR.PARTICIPANTI"),
        "DENUMIRE PARTICIPANTI": st.column_config.TextColumn("DENUMIRE PARTICIPANTI", width="large"),
        "ROL UPT":               st.column_config.SelectboxColumn("ROL UPT", options=ROL_UPT_OPTIONS),
        "APELUL":                st.column_config.TextColumn("APELUL"),
        "DATA LIMITA DEPUNERE":  st.column_config.TextColumn("📅 DATA LIMITA DEPUNERE (AAAA-LL-ZZ)"),
        "PROGRAM DE FINANTARE":  st.column_config.TextColumn("PROGRAM DE FINANTARE"),
        "TEMA / TOPIC":          st.column_config.TextColumn("TEMA / TOPIC", width="large"),
        "SCHEMA DE FINANTARE":   st.column_config.TextColumn("SCHEMA DE FINANTARE"),
        "WEBSITE":               st.column_config.TextColumn("WEBSITE"),
        "OBSERVATII":            st.column_config.TextColumn("📝 OBSERVATII", width="large"),
    }

    df_edit = st.data_editor(
        df, column_config=col_cfg, hide_index=True,
        use_container_width=True, num_rows="fixed",
        key=f"{tabela_nume}_baza_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]
    st.caption("ℹ️ Durata se calculează automat după salvarea fișei.")

    # Preluare valori din editor
    di_e_str  = _safe_str(row["DATA DE INCEPUT"])
    ds_e_str  = _safe_str(row["DATA DE SFARSIT"])
    dur_e     = _safe_int(row["DURATA (luni)"])

    # Conversie date din string
    di_e = _safe_date(di_e_str) if di_e_str else None
    ds_e = _safe_date(ds_e_str) if ds_e_str else None

    # Calcul automat durata / date
    if di_e and ds_e:
        dur_e = calc_durata(di_e, ds_e)
    elif di_e and dur_e and not ds_e:
        ds_e = add_months(di_e, dur_e)
    elif ds_e and dur_e and not di_e:
        di_e = sub_months(ds_e, dur_e)

    def _s(v):
        return str(v).strip() if v else None

    return {
        "cod_identificare":        cod_introdus,
        "denumire_categorie":      cat_sel,
        "acronim_tip_proiecte":    tip_label,
        "titlul_proiect":          _s(row["TITLUL PROIECTULUI"]),
        "acronim_proiect":         _s(row["ACRONIMUL PROIECTULUI"]),
        "data_inceput":            _fmt_date(di_e),
        "data_sfarsit":            _fmt_date(ds_e),
        "durata":                  dur_e if dur_e else None,
        "status_contract_proiect": _s(row["STATUS PROIECT"]),
        "scor_evaluare":           _s(row["SCOR EVALUARE"]),
        "numar_participanti":      _s(row["NR.PARTICIPANTI"]),
        "denumire_participanti":   _s(row["DENUMIRE PARTICIPANTI"]),
        "rol_upt":                 _s(row["ROL UPT"]),
        "identificare_apel":       _s(row["APELUL"]),
        "data_inchidere_apel":     _fmt_date(_safe_date(row["DATA LIMITA DEPUNERE"])),
        "program_finantare":       _s(row["PROGRAM DE FINANTARE"]),
        "tema_topic":              _s(row["TEMA / TOPIC"]),
        "schema_de_finantare":     _s(row["SCHEMA DE FINANTARE"]),
        "website":                 _s(row["WEBSITE"]),
        "observatii":              _s(row["OBSERVATII"]),
    }
