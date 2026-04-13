# =========================================================
# IDBDC - FIȘA CEP - Logică specifică contracte CEP
# Versiune: 1.1 - Corecție coloane com_echipe_proiect
# Acoperă: Date de bază, Date financiare, Echipă
# Fișa "Aspecte tehnice" NU se afișează pentru CEP
# =========================================================

import streamlit as st
import pandas as pd
from datetime import date
import calendar as cal_lib


# =========================================================
# HELPERS DATE
# =========================================================

def _calc_durata(data_inceput, data_sfarsit) -> int:
    try:
        d1 = pd.to_datetime(data_inceput).date()
        d2 = pd.to_datetime(data_sfarsit).date()
        luni = (d2.year - d1.year) * 12 + (d2.month - d1.month)
        if d2.day >= d1.day:
            luni += 1
        return max(0, luni)
    except Exception:
        return 0


def _calc_data_sfarsit(data_inceput, durata_luni) -> date:
    try:
        d1 = pd.to_datetime(data_inceput).date()
        luna_noua = d1.month - 1 + int(durata_luni)
        an_nou = d1.year + luna_noua // 12
        luna_noua = luna_noua % 12 + 1
        zi = min(d1.day, cal_lib.monthrange(an_nou, luna_noua)[1])
        return date(an_nou, luna_noua, zi)
    except Exception:
        return None


def _calc_data_inceput(data_sfarsit, durata_luni) -> date:
    try:
        d2 = pd.to_datetime(data_sfarsit).date()
        luna_noua = d2.month - 1 - int(durata_luni)
        an_nou = d2.year + luna_noua // 12
        luna_noua = luna_noua % 12 + 1
        zi = min(d2.day, cal_lib.monthrange(an_nou, luna_noua)[1])
        return date(an_nou, luna_noua, zi)
    except Exception:
        return None


# =========================================================
# FIȘA 1 — DATE DE BAZĂ
# =========================================================

def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_sel, is_new, date_existente):

    @st.cache_data(show_spinner=False, ttl=600)
    def get_status_list(_sb):
        try:
            res = _sb.table("nom_status_proiect").select("status_contract_proiect").execute()
            return [r["status_contract_proiect"] for r in (res.data or [])
                    if r.get("status_contract_proiect")]
        except Exception:
            return []

    status_list = get_status_list(supabase)
    ex = date_existente

    c1, c2 = st.columns(2)

    with c1:
        st.text_input("CATEGORIE", value=cat_sel, disabled=True, key="cep_categorie")

        st.text_input("NR. CONTRACT", value=cod_introdus, disabled=True, key="cep_nr_contract")

        dc_val = None
        if ex.get("data_contract"):
            try:
                dc_val = pd.to_datetime(ex["data_contract"]).date()
            except Exception:
                pass
        data_contract = st.date_input("DATA CONTRACTULUI", value=dc_val,
                                      format="YYYY-MM-DD", key="cep_data_contract")

        di_val = None
        if ex.get("data_inceput"):
            try:
                di_val = pd.to_datetime(ex["data_inceput"]).date()
            except Exception:
                pass
        data_inceput = st.date_input("DATA DE INCEPUT", value=di_val,
                                     format="YYYY-MM-DD", key="cep_data_inceput")

        ds_val = None
        if ex.get("data_sfarsit"):
            try:
                ds_val = pd.to_datetime(ex["data_sfarsit"]).date()
            except Exception:
                pass
        data_sfarsit = st.date_input("DATA DE SFARSIT", value=ds_val,
                                     format="YYYY-MM-DD", key="cep_data_sfarsit")

        # Durata — calculată automat dacă lipsește
        if data_inceput and data_sfarsit:
            durata_calc = _calc_durata(data_inceput, data_sfarsit)
        else:
            try:
                durata_calc = int(ex.get("durata") or 0)
            except Exception:
                durata_calc = 0

        durata = st.number_input("DURATA (luni)", min_value=0, value=durata_calc,
                                 step=1, key="cep_durata")

    with c2:
        st.text_input("TIPUL DE CONTRACT", value=tip_sel, disabled=True, key="cep_tip")

        obiect = st.text_area("OBIECTUL CONTRACTULUI",
                              value=ex.get("obiectul_contractului", ""),
                              height=120, key="cep_obiect")

        beneficiar = st.text_input("BENEFICIAR",
                                   value=ex.get("denumire_beneficiar", ""),
                                   key="cep_beneficiar")

        status_curent = ex.get("status_contract_proiect", "")
        optiuni_status = [""] + status_list
        idx_status = optiuni_status.index(status_curent) if status_curent in optiuni_status else 0
        status = st.selectbox("STATUS CONTRACT", options=optiuni_status,
                              index=idx_status, key="cep_status")

    # Calcule automate dată
    if data_inceput and not data_sfarsit and durata:
        ds_calc = _calc_data_sfarsit(data_inceput, durata)
        if ds_calc:
            st.info(f"📅 DATA DE SFARSIT calculată automat: {ds_calc.strftime('%Y-%m-%d')}")
            data_sfarsit = ds_calc

    if data_sfarsit and not data_inceput and durata:
        di_calc = _calc_data_inceput(data_sfarsit, durata)
        if di_calc:
            st.info(f"📅 DATA DE INCEPUT calculată automat: {di_calc.strftime('%Y-%m-%d')}")
            data_inceput = di_calc

    return {
        "cod_identificare":        cod_introdus,
        "denumire_categorie":      cat_sel,
        "acronim_tip_contract":    tip_sel,
        "data_contract":           data_contract.isoformat() if data_contract else None,
        "obiectul_contractului":   obiect,
        "denumire_beneficiar":     beneficiar,
        "data_inceput":            data_inceput.isoformat() if data_inceput else None,
        "data_sfarsit":            data_sfarsit.isoformat() if data_sfarsit else None,
        "durata":                  durata if durata else None,
        "status_contract_proiect": status if status else None,
    }


# =========================================================
# FIȘA 2 — DATE FINANCIARE
# =========================================================

def render_date_financiare(supabase, cod_introdus, is_new, date_existente):

    VALUTE = ["LEI", "EURO", "USD"]

    if is_new or not date_existente:
        rows = [{"cod_identificare": cod_introdus,
                 "valuta": "LEI",
                 "valoare_contract_cep_terti_speciale": 0.0}]
    else:
        rows = date_existente

    rezultat = []
    for idx, row in enumerate(rows):
        c1, c2 = st.columns(2)

        with c1:
            valuta_curent = row.get("valuta", "LEI")
            idx_valuta = VALUTE.index(valuta_curent) if valuta_curent in VALUTE else 0
            valuta = st.selectbox("VALUTA", options=VALUTE,
                                  index=idx_valuta, key=f"cep_fin_valuta_{idx}")

        with c2:
            try:
                val_ex = float(row.get("valoare_contract_cep_terti_speciale") or 0)
            except (ValueError, TypeError):
                val_ex = 0.0
            valoare = st.number_input("VALOARE CONTRACT", min_value=0.0,
                                      value=val_ex, step=0.01, format="%.2f",
                                      key=f"cep_fin_valoare_{idx}")

        rezultat.append({
            "cod_identificare":                    cod_introdus,
            "valuta":                              valuta,
            "valoare_contract_cep_terti_speciale": valoare,
        })

    return rezultat


# =========================================================
# FIȘA 3 — ECHIPĂ
# Coloane salvate în com_echipe_proiect:
#   cod_identificare, nume_prenume, rol, persoana_contact, functie_upt
# Afișate dar nesalvate (vin din det_resurse_umane):
#   departament (acronim + denumire), email, telefon_mobil, telefon_upt
# =========================================================

def render_echipa(supabase, cod_introdus, is_new, date_existente):

    @st.cache_data(show_spinner=False, ttl=600)
    def get_persoane(_sb):
        try:
            res = _sb.table("det_resurse_umane").select(
                "nume_prenume,email,telefon_mobil,telefon_upt,acronim_departament"
            ).execute()
            return res.data or []
        except Exception:
            return []

    @st.cache_data(show_spinner=False, ttl=600)
    def get_dep_map(_sb):
        try:
            res = _sb.table("nom_departament").select(
                "acronim_departament,denumire_departament"
            ).execute()
            return {r["acronim_departament"]: r["denumire_departament"]
                    for r in (res.data or []) if r.get("acronim_departament")}
        except Exception:
            return {}

    persoane_data = get_persoane(supabase)
    dep_map = get_dep_map(supabase)
    persoane_list = [p["nume_prenume"] for p in persoane_data if p.get("nume_prenume")]

    def get_info(nume):
        for p in persoane_data:
            if p.get("nume_prenume") == nume:
                acronim = p.get("acronim_departament", "")
                den = dep_map.get(acronim, "")
                dep_display = f"{acronim} - {den}" if acronim and den else acronim
                return {
                    "departament":   dep_display,
                    "email":         p.get("email", ""),
                    "telefon_mobil": p.get("telefon_mobil", ""),
                    "telefon_upt":   p.get("telefon_upt", ""),
                }
        return {"departament": "", "email": "", "telefon_mobil": "", "telefon_upt": ""}

    if is_new or not date_existente:
        rows = [{"cod_identificare": cod_introdus}]
    else:
        rows = date_existente

    if st.button("➕ Adaugă membru", key="cep_add_membru"):
        rows.append({"cod_identificare": cod_introdus})

    rezultat = []
    for idx, row in enumerate(rows):
        with st.expander(
            f"Membru {idx + 1}: {row.get('nume_prenume', '— necompletat —')}",
            expanded=True
        ):
            c1, c2 = st.columns(2)

            with c1:
                optiuni = [""] + persoane_list
                nume_curent = row.get("nume_prenume", "")
                idx_pers = optiuni.index(nume_curent) if nume_curent in optiuni else 0
                nume = st.selectbox("NUME ȘI PRENUME", options=optiuni,
                                    index=idx_pers, key=f"cep_ech_nume_{idx}")

                info = get_info(nume) if nume else get_info("")

                st.text_input("DEPARTAMENT", value=info["departament"],
                              disabled=True, key=f"cep_ech_dep_{idx}")

                st.text_input("EMAIL", value=info["email"],
                              disabled=True, key=f"cep_ech_email_{idx}")

            with c2:
                rol = st.text_input("ROLUL ÎN CONTRACT",
                                    value=row.get("rol", ""),
                                    key=f"cep_ech_rol_{idx}")

                persoana_contact = st.checkbox("PERSOANĂ DE CONTACT",
                                               value=bool(row.get("persoana_contact", False)),
                                               key=f"cep_ech_pc_{idx}")

                st.text_input("TELEFON MOBIL", value=info["telefon_mobil"],
                              disabled=True, key=f"cep_ech_mob_{idx}")

                st.text_input("TELEFON FIX (UPT)", value=info["telefon_upt"],
                              disabled=True, key=f"cep_ech_fix_{idx}")

            # Salvăm doar coloanele care există în com_echipe_proiect
            rezultat.append({
                "cod_identificare": cod_introdus,
                "nume_prenume":     nume,
                "rol":              rol,
                "persoana_contact": persoana_contact,
                "functie_upt":      row.get("functie_upt", ""),
            })

    return rezultat
