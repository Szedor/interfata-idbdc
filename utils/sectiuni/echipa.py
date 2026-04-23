# =========================================================
# utils/sectiuni/echipa.py
# v.modul.2.0 - Rescris complet de la zero, simplu si functional
# =========================================================

import streamlit as st
import pandas as pd

def render_echipa(supabase, cod_introdus, is_new, date_existente):
    # =========================================================
    # INCARCARE DATE PERSOANE SI DEPARTAMENTE
    # =========================================================
    try:
        res = supabase.table("det_resurse_umane").select(
            "nume_prenume,email,telefon_mobil,telefon_fix,acronim_departament"
        ).order("nume_prenume").execute()
        persoane_data = res.data or []
    except Exception as e:
        st.error(f"Eroare citire persoane: {e}")
        persoane_data = []

    try:
        res2 = supabase.table("nom_departament").select(
            "acronim_departament,denumire_departament"
        ).execute()
        dep_map = {r["acronim_departament"]: r["denumire_departament"]
                   for r in (res2.data or []) if r.get("acronim_departament")}
    except Exception as e:
        st.error(f"Eroare citire departamente: {e}")
        dep_map = {}

    # Lista pentru dropdown
    persoane_lista = [""] + [p["nume_prenume"] for p in persoane_data if p.get("nume_prenume")]

    # Mapare informatii persoana
    info_persoana = {}
    for p in persoane_data:
        nume = p.get("nume_prenume", "")
        if not nume:
            continue
        acronim = p.get("acronim_departament", "")
        den = dep_map.get(acronim, "")
        info_persoana[nume] = {
            "departament": f"{acronim} - {den}" if acronim and den else acronim,
            "email": p.get("email", ""),
            "mobil": p.get("telefon_mobil", ""),
            "fix": p.get("telefon_fix", ""),
        }

    # =========================================================
    # INCARCARE DATE EXISTENTE SAU INITIALIZARE
    # =========================================================
    cheie_sesiune = f"echipa_{cod_introdus}"
    
    if cheie_sesiune not in st.session_state:
        if is_new or not date_existente:
            # Initializare cu 5 randuri goale
            st.session_state[cheie_sesiune] = [
                {"nume": "", "rol": "", "contact": False, "departament": "", "email": "", "mobil": "", "fix": ""}
                for _ in range(5)
            ]
        else:
            # Incarcare date existente
            st.session_state[cheie_sesiune] = []
            for r in date_existente:
                nume = r.get("nume_prenume", "")
                info = info_persoana.get(nume, {})
                st.session_state[cheie_sesiune].append({
                    "nume": nume,
                    "rol": r.get("rol", ""),
                    "contact": bool(r.get("persoana_contact", False)),
                    "departament": info.get("departament", ""),
                    "email": info.get("email", ""),
                    "mobil": info.get("mobil", ""),
                    "fix": info.get("fix", ""),
                })
            # Completam pana la 5 randuri daca sunt mai putine
            while len(st.session_state[cheie_sesiune]) < 5:
                st.session_state[cheie_sesiune].append(
                    {"nume": "", "rol": "", "contact": False, "departament": "", "email": "", "mobil": "", "fix": ""}
                )

    # =========================================================
    # AFISARE TABEL EDITABIL
    # =========================================================
    df = pd.DataFrame(st.session_state[cheie_sesiune])
    df = df.rename(columns={
        "nume": "NUME ȘI PRENUME",
        "rol": "ROLUL ÎN CONTRACT",
        "contact": "PERSOANĂ DE CONTACT",
        "departament": "DEPARTAMENT",
        "email": "EMAIL",
        "mobil": "TELEFON MOBIL",
        "fix": "TELEFON FIX",
    })

    col_cfg = {
        "NUME ȘI PRENUME": st.column_config.SelectboxColumn(
            "👤 NUME ȘI PRENUME", options=persoane_lista, required=False
        ),
        "ROLUL ÎN CONTRACT": st.column_config.TextColumn("ROLUL ÎN CONTRACT"),
        "PERSOANĂ DE CONTACT": st.column_config.CheckboxColumn("⭐ PERSOANĂ DE CONTACT"),
        "DEPARTAMENT": st.column_config.TextColumn("DEPARTAMENT", disabled=True),
        "EMAIL": st.column_config.TextColumn("EMAIL", disabled=True),
        "TELEFON MOBIL": st.column_config.TextColumn("TELEFON MOBIL", disabled=True),
        "TELEFON FIX": st.column_config.TextColumn("TELEFON FIX", disabled=True),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"echipa_editor_{cod_introdus}",
    )

    # =========================================================
    # PRELUCRARE DATE DUPA EDITARE
    # =========================================================
    rezultat_nou = []
    for _, row in df_edit.iterrows():
        nume = str(row.get("NUME ȘI PRENUME", "")).strip()
        if not nume:
            continue
        
        # Obtine informatiile complete pentru numele ales
        info = info_persoana.get(nume, {})
        
        rezultat_nou.append({
            "cod_identificare": cod_introdus,
            "nume_prenume": nume,
            "rol": str(row.get("ROLUL ÎN CONTRACT", "")).strip(),
            "persoana_contact": bool(row.get("PERSOANĂ DE CONTACT", False)),
            "functie_upt": "",
        })
        
        # Actualizeaza si session_state cu informatiile complete
        for item in st.session_state[cheie_sesiune]:
            if item["nume"] == nume:
                item["departament"] = info.get("departament", "")
                item["email"] = info.get("email", "")
                item["mobil"] = info.get("mobil", "")
                item["fix"] = info.get("fix", "")
                item["rol"] = str(row.get("ROLUL ÎN CONTRACT", "")).strip()
                item["contact"] = bool(row.get("PERSOANĂ DE CONTACT", False))
                break
    
    # =========================================================
    # BUTON ADAUGARE RAND NOU
    # =========================================================
    if st.button("➕ Adaugă membru", key=f"add_membru_{cod_introdus}"):
        st.session_state[cheie_sesiune].append(
            {"nume": "", "rol": "", "contact": False, "departament": "", "email": "", "mobil": "", "fix": ""}
        )
        st.rerun()

    return rezultat_nou
