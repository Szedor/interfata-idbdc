# =========================================================
# IDBDC - FIȘA CEP - Logică specifică contracte CEP
# Versiune: 1.0
# Acoperă: Date de bază, Date financiare, Echipă
# Fișa "Aspecte tehnice" NU se afișează pentru CEP (conform cerințe)
# =========================================================

import streamlit as st
import pandas as pd
from datetime import date, timedelta
import math


# =========================================================
# HELPERS DATE
# =========================================================

def _calc_durata(data_inceput, data_sfarsit) -> int:
    """Calculează durata în luni întregi între două date."""
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
    """Calculează data de sfârșit din data de început + durată luni."""
    try:
        d1 = pd.to_datetime(data_inceput).date()
        luna_noua = d1.month - 1 + int(durata_luni)
        an_nou = d1.year + luna_noua // 12
        luna_noua = luna_noua % 12 + 1
        import calendar
        zi = min(d1.day, calendar.monthrange(an_nou, luna_noua)[1])
        return date(an_nou, luna_noua, zi)
    except Exception:
        return None


def _calc_data_inceput(data_sfarsit, durata_luni) -> date:
    """Calculează data de început din data de sfârșit - durată luni."""
    try:
        d2 = pd.to_datetime(data_sfarsit).date()
        luna_noua = d2.month - 1 - int(durata_luni)
        an_nou = d2.year + luna_noua // 12
        luna_noua = luna_noua % 12 + 1
        import calendar
        zi = min(d2.day, calendar.monthrange(an_nou, luna_noua)[1])
        return date(an_nou, luna_noua, zi)
    except Exception:
        return None


# =========================================================
# FIȘA 1 — DATE DE BAZĂ
# =========================================================

def render_date_de_baza(supabase, cod_introdus: str, cat_sel: str,
                         tip_sel: str, is_new: bool, date_existente: dict):
    """
    Randează fișa Date de bază pentru contracte CEP.
    Returnează dict cu valorile completate de operator.
    """

    # ---- Nomenclatoare ----
    @st.cache_data(show_spinner=False, ttl=600)
    def get_status_list(_sb):
        try:
            res = _sb.table("nom_status_proiect").select("status_contract_proiect").execute()
            return [r["status_contract_proiect"] for r in (res.data or []) if r.get("status_contract_proiect")]
        except Exception:
            return []

    status_list = get_status_list(supabase)

    # ---- Valori existente (modificare) sau goale (fișă nouă) ----
    ex = date_existente  # shortcut

    # ---- Layout ----
    st.markdown("### 📋 DATE DE BAZĂ")

    c1, c2 = st.columns(2)

    with c1:
        # CATEGORIE — automat, blocat
        st.text_input("CATEGORIE", value=cat_sel, disabled=True, key="cep_categorie")

        # NR. CONTRACT
        nr_contract = st.text_input(
            "NR. CONTRACT",
            value=ex.get("cod_identificare", cod_introdus),
            disabled=True,
            key="cep_nr_contract"
        )

        # DATA CONTRACTULUI
        dc_val = None
        if ex.get("data_contract"):
            try:
                dc_val = pd.to_datetime(ex["data_contract"]).date()
            except Exception:
                dc_val = None
        data_contract = st.date_input(
            "DATA CONTRACTULUI",
            value=dc_val,
            format="YYYY-MM-DD",
            key="cep_data_contract"
        )

        # DATA DE INCEPUT
        di_val = None
        if ex.get("data_inceput"):
            try:
                di_val = pd.to_datetime(ex["data_inceput"]).date()
            except Exception:
                di_val = None
        data_inceput = st.date_input(
            "DATA DE INCEPUT",
            value=di_val,
            format="YYYY-MM-DD",
            key="cep_data_inceput"
        )

        # DATA DE SFARSIT
        ds_val = None
        if ex.get("data_sfarsit"):
            try:
                ds_val = pd.to_datetime(ex["data_sfarsit"]).date()
            except Exception:
                ds_val = None
        data_sfarsit = st.date_input(
            "DATA DE SFARSIT",
            value=ds_val,
            format="YYYY-MM-DD",
            key="cep_data_sfarsit"
        )

        # DURATA — calculată automat dacă lipsește
        durata_ex = ex.get("durata", None)
        if data_inceput and data_sfarsit:
            durata_calc = _calc_durata(data_inceput, data_sfarsit)
        elif durata_ex:
            durata_calc = durata_ex
        else:
            durata_calc = 0
        durata = st.number_input(
            "DURATA (luni)",
            min_value=0,
            value=int(durata_calc) if durata_calc else 0,
            step=1,
            key="cep_durata"
        )

    with c2:
        # TIPUL DE CONTRACT — automat, blocat
        st.text_input("TIPUL DE CONTRACT", value=tip_sel, disabled=True, key="cep_tip")

        # DATA CONTRACTULUI placeholder (aliniere vizuală)
        st.write("")

        # OBIECTUL CONTRACTULUI
        obiect = st.text_area(
            "OBIECTUL CONTRACTULUI",
            value=ex.get("obiectul_contractului", ""),
            height=100,
            key="cep_obiect"
        )

        # BENEFICIAR
        beneficiar = st.text_input(
            "BENEFICIAR",
            value=ex.get("denumire_beneficiar", ""),
            key="cep_beneficiar"
        )

        # STATUS CONTRACT
        status_idx = 0
        if ex.get("status_contract_proiect") and ex["status_contract_proiect"] in status_list:
            status_idx = status_list.index(ex["status_contract_proiect"])
        status = st.selectbox(
            "STATUS CONTRACT",
            options=[""] + status_list,
            index=status_idx + 1 if status_idx >= 0 and status_list else 0,
            key="cep_status"
        )

    # ---- Calcule automate dată ----
    if data_inceput and not data_sfarsit and durata:
        ds_calculat = _calc_data_sfarsit(data_inceput, durata)
        if ds_calculat:
            st.info(f"📅 DATA DE SFARSIT calculată automat: {ds_calculat.strftime('%Y-%m-%d')}")
            data_sfarsit = ds_calculat

    if data_sfarsit and not data_inceput and durata:
        di_calculat = _calc_data_inceput(data_sfarsit, durata)
        if di_calculat:
            st.info(f"📅 DATA DE INCEPUT calculată automat: {di_calculat.strftime('%Y-%m-%d')}")
            data_inceput = di_calculat

    # ---- Returnează valorile pentru salvare ----
    return {
        "cod_identificare":       cod_introdus,
        "denumire_categorie":     cat_sel,
        "acronim_tip_contract":   tip_sel,
        "data_contract":          data_contract.isoformat() if data_contract else None,
        "obiectul_contractului":  obiect,
        "denumire_beneficiar":    beneficiar,
        "data_inceput":           data_inceput.isoformat() if data_inceput else None,
        "data_sfarsit":           data_sfarsit.isoformat() if data_sfarsit else None,
        "durata":                 durata if durata else None,
        "status_contract_proiect": status if status else None,
    }


# =========================================================
# FIȘA 2 — DATE FINANCIARE
# =========================================================

def render_date_financiare(supabase, cod_introdus: str, is_new: bool, date_existente: list):
    """
    Randează fișa Date financiare pentru CEP.
    date_existente: listă de dict (rânduri existente din com_date_financiare)
    Returnează lista de dict pentru salvare.
    """
    st.markdown("### 💰 DATE FINANCIARE")

    VALUTE = ["LEI", "EURO", "USD"]

    # Inițializăm rândurile
    if is_new or not date_existente:
        rows = [{"cod_identificare": cod_introdus, "valuta": "LEI",
                 "valoare_contract_cep_terti_speciale": 0.0}]
    else:
        rows = date_existente

    rezultat = []
    for idx, row in enumerate(rows):
        st.markdown(f"**Înregistrare {idx + 1}**")
        c1, c2 = st.columns(2)

        with c1:
            valuta_idx = VALUTE.index(row.get("valuta", "LEI")) if row.get("valuta") in VALUTE else 0
            valuta = st.selectbox(
                "VALUTA",
                options=VALUTE,
                index=valuta_idx,
                key=f"cep_fin_valuta_{idx}"
            )

        with c2:
            try:
                val_ex = float(row.get("valoare_contract_cep_terti_speciale") or 0)
            except (ValueError, TypeError):
                val_ex = 0.0
            valoare = st.number_input(
                "VALOARE CONTRACT",
                min_value=0.0,
                value=val_ex,
                step=0.01,
                format="%.2f",
                key=f"cep_fin_valoare_{idx}"
            )

        rezultat.append({
            "cod_identificare":                   cod_introdus,
            "valuta":                             valuta,
            "valoare_contract_cep_terti_speciale": valoare,
        })

    return rezultat


# =========================================================
# FIȘA 3 — ECHIPĂ
# =========================================================

def render_echipa(supabase, cod_introdus: str, is_new: bool, date_existente: list):
    """
    Randează fișa Echipă pentru CEP.
    date_existente: listă de dict (rânduri existente din com_echipe_proiect)
    Returnează lista de dict pentru salvare.
    """
    st.markdown("### 👥 ECHIPĂ")

    # ---- Nomenclator persoane ----
    @st.cache_data(show_spinner=False, ttl=600)
    def get_persoane(_sb):
        try:
            res = _sb.table("det_resurse_umane").select(
                "nume_prenume,email,telefon_mobil,telefon_fix,acronim_departament"
            ).execute()
            return res.data or []
        except Exception:
            return []

    @st.cache_data(show_spinner=False, ttl=600)
    def get_departamente(_sb):
        try:
            res = _sb.table("nom_departament").select(
                "acronim_departament,denumire_departament"
            ).execute()
            return {r["acronim_departament"]: r["denumire_departament"] for r in (res.data or [])}
        except Exception:
            return {}

    persoane_data = get_persoane(supabase)
    dep_map = get_departamente(supabase)
    persoane_list = [p["nume_prenume"] for p in persoane_data if p.get("nume_prenume")]

    def get_persoana_info(nume):
        for p in persoane_data:
            if p.get("nume_prenume") == nume:
                acronim = p.get("acronim_departament", "")
                den_dep = dep_map.get(acronim, "")
                dep_display = f"{acronim} - {den_dep}" if acronim and den_dep else acronim
                return {
                    "email":             p.get("email", ""),
                    "telefon_mobil":     p.get("telefon_mobil", ""),
                    "telefon_fix":       p.get("telefon_fix", ""),
                    "departament":       dep_display,
                    "acronim_departament": acronim,
                }
        return {}

    # Inițializăm rândurile
    if is_new or not date_existente:
        rows = [{"cod_identificare": cod_introdus}]
    else:
        rows = date_existente

    # Buton adăugare membru nou
    if st.button("➕ Adaugă membru", key="cep_add_membru"):
        rows.append({"cod_identificare": cod_introdus})

    rezultat = []
    for idx, row in enumerate(rows):
        with st.expander(f"Membru {idx + 1}: {row.get('nume_prenume', '— necompletat —')}", expanded=True):
            c1, c2 = st.columns(2)

            with c1:
                # NUME SI PRENUME — dropdown din det_resurse_umane
                nume_curent = row.get("nume_prenume", "")
                optiuni_persoane = [""] + persoane_list
                idx_pers = optiuni_persoane.index(nume_curent) if nume_curent in optiuni_persoane else 0
                nume = st.selectbox(
                    "NUME ȘI PRENUME",
                    options=optiuni_persoane,
                    index=idx_pers,
                    key=f"cep_ech_nume_{idx}"
                )

                # Date automate din det_resurse_umane
                info = get_persoana_info(nume) if nume else {}

                departament = st.text_input(
                    "DEPARTAMENT",
                    value=info.get("departament", row.get("acronim_departament", "")),
                    disabled=True,
                    key=f"cep_ech_dep_{idx}"
                )

                email = st.text_input(
                    "EMAIL",
                    value=info.get("email", row.get("email", "")),
                    disabled=True,
                    key=f"cep_ech_email_{idx}"
                )

            with c2:
                rol = st.text_input(
                    "ROLUL ÎN CONTRACT",
                    value=row.get("rol", ""),
                    key=f"cep_ech_rol_{idx}"
                )

                persoana_contact = st.checkbox(
                    "PERSOANĂ DE CONTACT",
                    value=bool(row.get("persoana_contact", False)),
                    key=f"cep_ech_pc_{idx}"
                )

                tel_mobil = st.text_input(
                    "TELEFON MOBIL",
                    value=info.get("telefon_mobil", row.get("telefon_mobil", "")),
                    disabled=True,
                    key=f"cep_ech_mob_{idx}"
                )

                tel_fix = st.text_input(
                    "TELEFON FIX",
                    value=info.get("telefon_fix", row.get("telefon_fix", "")),
                    disabled=True,
                    key=f"cep_ech_fix_{idx}"
                )

            rezultat.append({
                "cod_identificare":    cod_introdus,
                "nume_prenume":        nume,
                "rol":                 rol,
                "persoana_contact":    persoana_contact,
                "acronim_departament": info.get("acronim_departament", row.get("acronim_departament", "")),
                "email":               info.get("email", row.get("email", "")),
                "telefon_mobil":       info.get("telefon_mobil", row.get("telefon_mobil", "")),
                "telefon_fix":         info.get("telefon_fix", row.get("telefon_fix", "")),
            })

    return rezultat
