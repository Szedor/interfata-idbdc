# =========================================================
# IDBDC/domenii/_baza/sectiune_baza_prop_industr.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.05.23
# =========================================================
# LOGICA SPECIALA:
#   [1] ACRONIM TIP PROPRIETATE — dropdown din nom_prop_industr.acronim_prop_industr
#   [2] La selectia acronimului se completeaza automat:
#         - DENUMIRE PROPRIETATE INDUSTRIALA (denumire_prop_industr)
#         - DURATA DE VALABILITATE (ani_de_valabilitate)
#   [3] Dupa completarea DATA DE INCEPUT VALABILITATE, sistemul
#       calculeaza automat DATA DE SFARSIT VALABILITATE
#       = DATA INCEPUT + DURATA (ani) * 365 zile
#   [4] Sectiunea SUPLIMENTARA este salvata in acelasi tabel
#       base_prop_industr dar este afisata NUMAI in Calea2 (Admin)
# =========================================================

import streamlit as st
import pandas as pd
from datetime import date, timedelta


# ── Helpers ───────────────────────────────────────────────────────────────────

def _to_date(v):
    if v is None: return None
    if isinstance(v, date): return v
    if isinstance(v, str) and v:
        try: return date.fromisoformat(v[:10])
        except: return None
    return None

def _fmt_date(v):
    if v is None: return None
    if hasattr(v, 'strftime'): return v.strftime("%Y-%m-%d")
    if hasattr(v, 'isoformat'): return v.isoformat()
    return str(v)

def _add_ani(d, ani):
    """Adauga un numar de ani la o data (aproximare: ani * 365 zile)."""
    if d is None or not ani: return None
    try: return d + timedelta(days=int(ani) * 365)
    except: return None

def _s(v): return str(v).strip() if v else None


# ── Cache nomenclator ─────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False, ttl=600)
def _get_nom_prop_industr(_supabase):
    """
    Returneaza lista de dictionare din nom_prop_industr:
    [{"acronim": "...", "denumire": "...", "ani": ...}, ...]
    """
    try:
        res = _supabase.table("nom_prop_industr").select(
            "acronim_prop_industr, denumire_prop_industr, ani_de_valabilitate"
        ).execute()
        return res.data or []
    except Exception:
        return []


# ── Sectiunea GENERALE (Tab 1 — Calea1 + Calea2) ─────────────────────────────

def render_generale(supabase, cod_introdus, cat_sel, tabela_nume, is_new, date_existente):
    nom = _get_nom_prop_industr(supabase)

    acronime      = [r["acronim_prop_industr"] for r in nom if r.get("acronim_prop_industr")]
    map_denumire  = {r["acronim_prop_industr"]: r.get("denumire_prop_industr", "") for r in nom}
    map_ani       = {r["acronim_prop_industr"]: r.get("ani_de_valabilitate")        for r in nom}

    # Valori existente
    acronim_ex  = date_existente.get("acronim_prop_industr", "")
    denumire_ex = date_existente.get("denumire_prop_industr", "")
    ani_ex      = date_existente.get("ani_de_valabilitate")
    di_ex       = _to_date(date_existente.get("data_inceput_valabilitate"))
    ds_ex       = _to_date(date_existente.get("data_sfarsit_valabilitate"))

    # ── Dropdown ACRONIM ──────────────────────────────────────────────────────
    st.markdown("##### Tip proprietate")
    idx_acronim = acronime.index(acronim_ex) if acronim_ex in acronime else 0
    acronim_sel = st.selectbox(
        "ACRONIM TIP PROPRIETATE",
        options=acronime,
        index=idx_acronim,
        key=f"acronim_prop_{cod_introdus}",
    )

    # Completare automata denumire si durata din nomenclator
    denumire_auto = map_denumire.get(acronim_sel, denumire_ex or "")
    ani_auto      = map_ani.get(acronim_sel, ani_ex)

    st.info(f"**DENUMIRE PROPRIETATE INDUSTRIALA:** {denumire_auto or '—'}")
    if ani_auto:
        st.info(f"**DURATA DE VALABILITATE:** {ani_auto} ani")

    # ── Restul campurilor ─────────────────────────────────────────────────────
    st.markdown("##### Date generale")

    df = pd.DataFrame([{
        "CATEGORIE":               cat_sel,
        "NR.INREGISTRARE CERERE":  cod_introdus,
        "TITLUL PROPRIETATII":     date_existente.get("titlul_proprietatii", ""),
        "DATA DEPOZIT CERERE":     _to_date(date_existente.get("data_depozit_cerere")),
        "NR.PUBLICARE CERERE":     date_existente.get("numar_publicare_cerere", ""),
        "NR.OFICIAL DE ACORDARE":  date_existente.get("numar_oficial_acordare", ""),
        "DATA OFICIALA DE ACORDARE": _to_date(date_existente.get("data_oficiala_de_acordare")),
        "DATA DE INCEPUT VALABILITATE": di_ex,
        "DURATA DE VALABILITATE (ani)": int(ani_auto) if ani_auto else 0,
        "DATA DE SFARSIT VALABILITATE": ds_ex,
        "ID PROIECT SURSA/CONTRACT": date_existente.get("id_proiect_contract_sursa", ""),
        "DENUMIRE SOLICITANT":     date_existente.get("denumire_solicitant", ""),
        "DENUMIRE TITULAR":        date_existente.get("denumire_titular", ""),
        "LINK ESPACENET":          date_existente.get("link_espacenet", ""),
        "TITLU ENGLEZA DIPLOMA":   date_existente.get("titlu_engleza_diploma", ""),
    }])

    col_cfg = {
        "CATEGORIE":                    st.column_config.TextColumn("CATEGORIE", disabled=True),
        "NR.INREGISTRARE CERERE":       st.column_config.TextColumn("NR.INREGISTRARE CERERE", disabled=True),
        "TITLUL PROPRIETATII":          st.column_config.TextColumn("TITLUL PROPRIETATII", width="large"),
        "DATA DEPOZIT CERERE":          st.column_config.DateColumn("📅 DATA DEPOZIT CERERE", format="YYYY-MM-DD"),
        "NR.PUBLICARE CERERE":          st.column_config.TextColumn("NR.PUBLICARE CERERE"),
        "NR.OFICIAL DE ACORDARE":       st.column_config.TextColumn("NR.OFICIAL DE ACORDARE"),
        "DATA OFICIALA DE ACORDARE":    st.column_config.DateColumn("📅 DATA OFICIALA DE ACORDARE", format="YYYY-MM-DD"),
        "DATA DE INCEPUT VALABILITATE": st.column_config.DateColumn("📅 DATA DE INCEPUT VALABILITATE", format="YYYY-MM-DD"),
        "DURATA DE VALABILITATE (ani)": st.column_config.NumberColumn("DURATA DE VALABILITATE (ani)", format="%d", min_value=0, disabled=True),
        "DATA DE SFARSIT VALABILITATE": st.column_config.DateColumn("📅 DATA DE SFARSIT VALABILITATE", format="YYYY-MM-DD", disabled=True),
        "ID PROIECT SURSA/CONTRACT":    st.column_config.TextColumn("ID PROIECT SURSA/CONTRACT"),
        "DENUMIRE SOLICITANT":          st.column_config.TextColumn("DENUMIRE SOLICITANT", width="large"),
        "DENUMIRE TITULAR":             st.column_config.TextColumn("DENUMIRE TITULAR", width="large"),
        "LINK ESPACENET":               st.column_config.TextColumn("LINK ESPACENET"),
        "TITLU ENGLEZA DIPLOMA":        st.column_config.TextColumn("TITLU ENGLEZA DIPLOMA", width="large"),
    }

    df_edit = st.data_editor(
        df, column_config=col_cfg, hide_index=True,
        use_container_width=True, num_rows="fixed",
        key=f"{tabela_nume}_generale_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    # Calcul automat DATA SFARSIT VALABILITATE
    di_e  = row["DATA DE INCEPUT VALABILITATE"]
    ani_e = int(ani_auto) if ani_auto else 0
    ds_e  = _add_ani(di_e, ani_e) if di_e and ani_e else row["DATA DE SFARSIT VALABILITATE"]

    if di_e and ani_e:
        st.caption(f"📅 Data de sfarsit valabilitate calculata automat: **{_fmt_date(ds_e)}** "
                   f"({ani_e} ani de la {_fmt_date(di_e)})")

    return {
        "cod_identificare":          cod_introdus,
        "denumire_categorie":        cat_sel,
        "acronim_prop_industr":      acronim_sel,
        "denumire_prop_industr":     denumire_auto,
        "titlul_proprietatii":       _s(row["TITLUL PROPRIETATII"]),
        "data_depozit_cerere":       _fmt_date(row["DATA DEPOZIT CERERE"]),
        "numar_publicare_cerere":    _s(row["NR.PUBLICARE CERERE"]),
        "numar_oficial_acordare":    _s(row["NR.OFICIAL DE ACORDARE"]),
        "data_oficiala_de_acordare": _fmt_date(row["DATA OFICIALA DE ACORDARE"]),
        "data_inceput_valabilitate": _fmt_date(di_e),
        "ani_de_valabilitate":       ani_e if ani_e else None,
        "data_sfarsit_valabilitate": _fmt_date(ds_e),
        "id_proiect_contract_sursa": _s(row["ID PROIECT SURSA/CONTRACT"]),
        "denumire_solicitant":       _s(row["DENUMIRE SOLICITANT"]),
        "denumire_titular":          _s(row["DENUMIRE TITULAR"]),
        "link_espacenet":            _s(row["LINK ESPACENET"]),
        "titlu_engleza_diploma":     _s(row["TITLU ENGLEZA DIPLOMA"]),
    }


# ── Sectiunea SUPLIMENTARA (Tab 2 — NUMAI Calea2 / Admin) ────────────────────

def render_suplimentare(supabase, cod_introdus, tabela_nume, is_new, date_existente):
    st.info("🔒 Această secțiune este vizibilă exclusiv operatorului (Calea2 / Admin).")

    df = pd.DataFrame([{
        "NR.SI DATA DE NOTIFICARE INTERNA":   date_existente.get("numar_data_notificare_intern", ""),
        "DOCUMENT OFICIAL ORIGINAL":          date_existente.get("document_oficial_original", ""),
        "STATUS DOCUMENT":                    date_existente.get("status_document", ""),
        "SPIN OFF":                           date_existente.get("spin_off", ""),
        "COMENTARII DOCUMENT":                date_existente.get("comentarii_document", ""),
        "COMENTARII DIVERSE":                 date_existente.get("comentarii_diverse", ""),
        "NUMAR AUTORI TOTAL":                 date_existente.get("numar_autori_total", ""),
        "NUMAR AUTORI UPT":                   date_existente.get("numar_autori_upt", ""),
        "DOMENIU APLICARE":                   date_existente.get("domeniu_aplicare", ""),
        "CONTRACT CESIUNE INVENTATORI EXTERNI": date_existente.get("contract_cesiune_inventatori_externi", ""),
        "TITLU ENGLEZA EPO":                  date_existente.get("titlu_engleza_epo", ""),
        "TITLU ENGLEZA FISA INVENTIEI":       date_existente.get("titlu_engleza_fisa_inventiei", ""),
    }])

    col_cfg = {
        "NR.SI DATA DE NOTIFICARE INTERNA":     st.column_config.TextColumn("NR.SI DATA DE NOTIFICARE INTERNA"),
        "DOCUMENT OFICIAL ORIGINAL":            st.column_config.TextColumn("DOCUMENT OFICIAL ORIGINAL"),
        "STATUS DOCUMENT":                      st.column_config.TextColumn("STATUS DOCUMENT"),
        "SPIN OFF":                             st.column_config.TextColumn("SPIN OFF"),
        "COMENTARII DOCUMENT":                  st.column_config.TextColumn("📝 COMENTARII DOCUMENT", width="large"),
        "COMENTARII DIVERSE":                   st.column_config.TextColumn("📝 COMENTARII DIVERSE",  width="large"),
        "NUMAR AUTORI TOTAL":                   st.column_config.TextColumn("NUMAR AUTORI TOTAL"),
        "NUMAR AUTORI UPT":                     st.column_config.TextColumn("NUMAR AUTORI UPT"),
        "DOMENIU APLICARE":                     st.column_config.TextColumn("DOMENIU APLICARE"),
        "CONTRACT CESIUNE INVENTATORI EXTERNI": st.column_config.TextColumn("CONTRACT CESIUNE INVENTATORI EXTERNI", width="large"),
        "TITLU ENGLEZA EPO":                    st.column_config.TextColumn("TITLU ENGLEZA EPO", width="large"),
        "TITLU ENGLEZA FISA INVENTIEI":         st.column_config.TextColumn("TITLU ENGLEZA FISA INVENTIEI", width="large"),
    }

    df_edit = st.data_editor(
        df, column_config=col_cfg, hide_index=True,
        use_container_width=True, num_rows="fixed",
        key=f"{tabela_nume}_suplimentare_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]

    return {
        "cod_identificare":                       cod_introdus,
        "numar_data_notificare_intern":            _s(row["NR.SI DATA DE NOTIFICARE INTERNA"]),
        "document_oficial_original":              _s(row["DOCUMENT OFICIAL ORIGINAL"]),
        "status_document":                        _s(row["STATUS DOCUMENT"]),
        "spin_off":                               _s(row["SPIN OFF"]),
        "comentarii_document":                    _s(row["COMENTARII DOCUMENT"]),
        "comentarii_diverse":                     _s(row["COMENTARII DIVERSE"]),
        "numar_autori_total":                     _s(row["NUMAR AUTORI TOTAL"]),
        "numar_autori_upt":                       _s(row["NUMAR AUTORI UPT"]),
        "domeniu_aplicare":                       _s(row["DOMENIU APLICARE"]),
        "contract_cesiune_inventatori_externi":   _s(row["CONTRACT CESIUNE INVENTATORI EXTERNI"]),
        "titlu_engleza_epo":                      _s(row["TITLU ENGLEZA EPO"]),
        "titlu_engleza_fisa_inventiei":           _s(row["TITLU ENGLEZA FISA INVENTIEI"]),
    }
