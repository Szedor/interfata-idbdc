# =========================================================
# IDBDC/utils/sectiuni/echipa.py
# VERSIUNE: 5.0
# STATUS: Adauga membru pastreaza datele existente introduse
# DATA: 2026.05.01
# =========================================================

import streamlit as st
import pandas as pd


def render_echipa(supabase, cod_introdus, is_new, date_existente):

    # ----------------------------------------------------------
    # 1. Citire date de referință
    # ----------------------------------------------------------
    try:
        res = supabase.table("det_resurse_umane").select(
            "nume_prenume,email,telefon_mobil,telefon_fix,acronim_departament"
        ).order("nume_prenume").execute()
        persoane_data = res.data or []
    except Exception as e:
        st.error(f"❌ Eroare citire det_resurse_umane: {e}")
        persoane_data = []

    try:
        res2 = supabase.table("nom_departament").select(
            "acronim_departament,denumire_departament"
        ).execute()
        dep_map = {
            r["acronim_departament"]: r["denumire_departament"]
            for r in (res2.data or []) if r.get("acronim_departament")
        }
    except Exception as e:
        st.error(f"❌ Eroare citire nom_departament: {e}")
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

    # ----------------------------------------------------------
    # 2. Chei session_state
    # ----------------------------------------------------------
    NR_RANDURI_INIT = 5
    key_editor    = f"echipa_editor_{cod_introdus}"
    key_data_init = f"echipa_data_init_{cod_introdus}"

    # ----------------------------------------------------------
    # 3. Inițializare date (o singură dată per cod)
    # ----------------------------------------------------------
    if key_data_init not in st.session_state:
        if is_new or not date_existente:
            rows_init = [
                {
                    "NUME ȘI PRENUME": "",
                    "ROLUL ÎN CONTRACT": "",
                    "PERSOANĂ DE CONTACT": False,
                    "DEPARTAMENT": "",
                    "EMAIL": "",
                    "TELEFON MOBIL": "",
                    "TELEFON FIX": "",
                }
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
                    "NUME ȘI PRENUME": "",
                    "ROLUL ÎN CONTRACT": "",
                    "PERSOANĂ DE CONTACT": False,
                    "DEPARTAMENT": "",
                    "EMAIL": "",
                    "TELEFON MOBIL": "",
                    "TELEFON FIX": "",
                })
        st.session_state[key_data_init] = rows_init

    # ----------------------------------------------------------
    # 4. Afișare data_editor
    # ----------------------------------------------------------
    df_init = pd.DataFrame(st.session_state[key_data_init])

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
        df_init,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=key_editor,
    )

    # ----------------------------------------------------------
    # 5. Detectare schimbări nume + completare automată
    # ----------------------------------------------------------
    rows_curente = st.session_state[key_data_init]
    needs_rerun = False

    for i, row in df_edit.iterrows():
        nume_nou   = row.get("NUME ȘI PRENUME", "") or ""
        nume_vechi = rows_curente[i].get("NUME ȘI PRENUME", "") or "" if i < len(rows_curente) else ""

        if nume_nou != nume_vechi:
            info = info_map.get(nume_nou, {"dep": "", "email": "", "mob": "", "fix": ""})
            rows_curente[i]["NUME ȘI PRENUME"]     = nume_nou
            rows_curente[i]["DEPARTAMENT"]          = info["dep"]
            rows_curente[i]["EMAIL"]               = info["email"]
            rows_curente[i]["TELEFON MOBIL"]       = info["mob"]
            rows_curente[i]["TELEFON FIX"]         = info["fix"]
            rows_curente[i]["ROLUL ÎN CONTRACT"]   = row.get("ROLUL ÎN CONTRACT", "") or ""
            rows_curente[i]["PERSOANĂ DE CONTACT"] = bool(row.get("PERSOANĂ DE CONTACT", False))
            needs_rerun = True
        else:
            rows_curente[i]["ROLUL ÎN CONTRACT"]   = row.get("ROLUL ÎN CONTRACT", "") or ""
            rows_curente[i]["PERSOANĂ DE CONTACT"] = bool(row.get("PERSOANĂ DE CONTACT", False))

    st.session_state[key_data_init] = rows_curente

    if needs_rerun:
        if key_editor in st.session_state:
            del st.session_state[key_editor]
        st.rerun()

    # ----------------------------------------------------------
    # 6. Buton Adaugă membru
    #    IMPORTANT: înainte de rerun, sincronizăm key_data_init
    #    cu editările curente din editor (df_edit), astfel
    #    datele introduse nu se pierd la redesenarea editorului.
    # ----------------------------------------------------------
    if st.button("➕ Adaugă membru", key=f"add_membru_{cod_introdus}"):
        # Sincronizăm mai întâi datele curente din editor în key_data_init
        rows_sync = st.session_state[key_data_init]
        for i, row in df_edit.iterrows():
            if i < len(rows_sync):
                rows_sync[i]["NUME ȘI PRENUME"]     = row.get("NUME ȘI PRENUME", "") or ""
                rows_sync[i]["ROLUL ÎN CONTRACT"]   = row.get("ROLUL ÎN CONTRACT", "") or ""
                rows_sync[i]["PERSOANĂ DE CONTACT"] = bool(row.get("PERSOANĂ DE CONTACT", False))
                n = rows_sync[i]["NUME ȘI PRENUME"]
                if n and n in info_map:
                    info = info_map[n]
                    rows_sync[i]["DEPARTAMENT"]   = info["dep"]
                    rows_sync[i]["EMAIL"]         = info["email"]
                    rows_sync[i]["TELEFON MOBIL"] = info["mob"]
                    rows_sync[i]["TELEFON FIX"]   = info["fix"]

        # Adăugăm rândul nou gol
        rows_sync.append({
            "NUME ȘI PRENUME": "",
            "ROLUL ÎN CONTRACT": "",
            "PERSOANĂ DE CONTACT": False,
            "DEPARTAMENT": "",
            "EMAIL": "",
            "TELEFON MOBIL": "",
            "TELEFON FIX": "",
        })
        st.session_state[key_data_init] = rows_sync

        # Resetăm editorul pentru a prelua noua configurație
        if key_editor in st.session_state:
            del st.session_state[key_editor]
        st.rerun()

    # ----------------------------------------------------------
    # 7. Returnare date pentru salvare
    # ----------------------------------------------------------
    rezultat = []
    for row in st.session_state[key_data_init]:
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
