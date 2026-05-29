# =========================================================
# IDBDC/domenii/_baza/echipa.py
# v.modul.1.0 - Secțiune Echipă (cu tabel)
# =========================================================

import streamlit as st
import pandas as pd


def render(supabase, cod_introdus, is_new, date_existente):
    try:
        res = supabase.table("det_resurse_umane").select(
            "nume_prenume,email,telefon_mobil,telefon_fix,acronim_departament"
        ).order("nume_prenume").execute()
        persoane_data = res.data or []
    except Exception as e:
        st.error(f"❌ Eroare citire persoane: {e}")
        persoane_data = []

    try:
        res2 = supabase.table("nom_departament").select(
            "acronim_departament,denumire_departament"
        ).execute()
        dep_map = {r["acronim_departament"]: r["denumire_departament"]
                   for r in (res2.data or []) if r.get("acronim_departament")}
    except Exception as e:
        st.error(f"❌ Eroare citire departamente: {e}")
        dep_map = {}

    if not persoane_data:
        st.warning("⚠️ Nu s-au găsit persoane în tabela det_resurse_umane.")
    persoane_list = [""] + [p["nume_prenume"] for p in persoane_data if p.get("nume_prenume")]

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

    NR_RANDURI_INIT = 5
    key_rows = f"echipa_rows_{cod_introdus}"
    
    if key_rows not in st.session_state:
        if is_new or not date_existente:
            st.session_state[key_rows] = [
                {"nume": "", "rol": "", "contact": False, "departament": "", "email": "", "mob": "", "fix": ""}
                for _ in range(NR_RANDURI_INIT)
            ]
        else:
            st.session_state[key_rows] = []
            for r in date_existente:
                nume = r.get("nume_prenume", "")
                info = info_map.get(nume, {})
                st.session_state[key_rows].append({
                    "nume": nume,
                    "rol": r.get("rol", ""),
                    "contact": bool(r.get("persoana_contact", False)),
                    "departament": info.get("dep", ""),
                    "email": info.get("email", ""),
                    "mob": info.get("mob", ""),
                    "fix": info.get("fix", ""),
                })
            while len(st.session_state[key_rows]) < NR_RANDURI_INIT:
                st.session_state[key_rows].append(
                    {"nume": "", "rol": "", "contact": False, "departament": "", "email": "", "mob": "", "fix": ""}
                )

    df = pd.DataFrame(st.session_state[key_rows])
    df = df.rename(columns={
        "nume": "👤 NUME ȘI PRENUME",
        "rol": "📌 ROLUL ÎN CONTRACT",
        "contact": "⭐ PERSOANĂ DE CONTACT",
        "departament": "🏛️ DEPARTAMENT",
        "email": "✉️ EMAIL",
        "mob": "📱 TELEFON MOBIL",
        "fix": "☎️ TELEFON FIX",
    })

    col_cfg = {
        "👤 NUME ȘI PRENUME": st.column_config.SelectboxColumn(
            "👤 NUME ȘI PRENUME", options=persoane_list, required=False
        ),
        "📌 ROLUL ÎN CONTRACT": st.column_config.TextColumn("📌 ROLUL ÎN CONTRACT"),
        "⭐ PERSOANĂ DE CONTACT": st.column_config.CheckboxColumn("⭐ PERSOANĂ DE CONTACT"),
        "🏛️ DEPARTAMENT": st.column_config.TextColumn("🏛️ DEPARTAMENT", disabled=True),
        "✉️ EMAIL": st.column_config.TextColumn("✉️ EMAIL", disabled=True),
        "📱 TELEFON MOBIL": st.column_config.TextColumn("📱 TELEFON MOBIL", disabled=True),
        "☎️ TELEFON FIX": st.column_config.TextColumn("☎️ TELEFON FIX", disabled=True),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"echipa_editor_{cod_introdus}",
    )

    # Actualizare session_state
    for idx, row in df_edit.iterrows():
        nume = str(row.get("👤 NUME ȘI PRENUME", "")).strip()
        if idx < len(st.session_state[key_rows]):
            st.session_state[key_rows][idx]["nume"] = nume
            st.session_state[key_rows][idx]["rol"] = str(row.get("📌 ROLUL ÎN CONTRACT", "")).strip()
            st.session_state[key_rows][idx]["contact"] = bool(row.get("⭐ PERSOANĂ DE CONTACT", False))
            
            if nume:
                info = info_map.get(nume, {})
                st.session_state[key_rows][idx]["departament"] = info.get("dep", "")
                st.session_state[key_rows][idx]["email"] = info.get("email", "")
                st.session_state[key_rows][idx]["mob"] = info.get("mob", "")
                st.session_state[key_rows][idx]["fix"] = info.get("fix", "")
            else:
                st.session_state[key_rows][idx]["departament"] = ""
                st.session_state[key_rows][idx]["email"] = ""
                st.session_state[key_rows][idx]["mob"] = ""
                st.session_state[key_rows][idx]["fix"] = ""

    if st.button("➕ Adaugă membru", key=f"add_membru_{cod_introdus}"):
        st.session_state[key_rows].append(
            {"nume": "", "rol": "", "contact": False, "departament": "", "email": "", "mob": "", "fix": ""}
        )
        st.rerun()

    rezultat = []
    for item in st.session_state[key_rows]:
        nume = item.get("nume", "").strip()
        if not nume:
            continue
        rezultat.append({
            "cod_identificare": cod_introdus,
            "nume_prenume": nume,
            "rol": item.get("rol", ""),
            "persoana_contact": item.get("contact", False),
            "functie_upt": "",
        })
    return rezultat
