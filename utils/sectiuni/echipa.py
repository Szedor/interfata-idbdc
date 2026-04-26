# =========================================================
# utils/sectiuni/echipa.py
# vers.modul.2.0
# 2026.04.27
# Fix pierdere date la editare câmpuri
# =========================================================

import streamlit as st
import pandas as pd


def render_echipa(supabase, cod_introdus, is_new, date_existente):
    """
    Randare și salvare echipă.
    Fix: datele introduse nu se mai pierd la trecerea între câmpuri.
    """

    # ----------------------------------------------------------
    # 1. Citire date de referință (persoane + departamente)
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
    # 2. Construire date inițiale pentru session_state
    #    IMPORTANT: inițializăm session_state O SINGURĂ DATĂ,
    #    la prima afișare a fișei pentru acest cod.
    #    Cheia include codul pentru a separa fișe diferite.
    # ----------------------------------------------------------
    NR_RANDURI_INIT = 5
    key_rows = f"echipa_rows_{cod_introdus}"
    key_init = f"echipa_init_{cod_introdus}"  # flag "am inițializat deja?"

    if key_init not in st.session_state:
        # Prima afișare — construim datele inițiale
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

        st.session_state[key_rows] = rows_init
        st.session_state[key_init] = True

    # ----------------------------------------------------------
    # 3. Afișare data_editor cu datele din session_state
    # ----------------------------------------------------------
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
        key=f"echipa_editor_{cod_introdus}",
    )

    # ----------------------------------------------------------
    # 4. Actualizare câmpuri automate (departament, email, tel)
    #    și salvare înapoi în session_state.
    #    IMPORTANT: actualizăm DOAR câmpurile automate, păstrând
    #    tot ce a tastat utilizatorul (rol, persoana_contact).
    # ----------------------------------------------------------
    df_updated = df_edit.copy()
    for i, row in df_edit.iterrows():
        n = row.get("NUME ȘI PRENUME", "")
        if n and n in info_map:
            info = info_map[n]
            df_updated.at[i, "DEPARTAMENT"]   = info["dep"]
            df_updated.at[i, "EMAIL"]         = info["email"]
            df_updated.at[i, "TELEFON MOBIL"] = info["mob"]
            df_updated.at[i, "TELEFON FIX"]   = info["fix"]
        elif not n:
            df_updated.at[i, "DEPARTAMENT"]   = ""
            df_updated.at[i, "EMAIL"]         = ""
            df_updated.at[i, "TELEFON MOBIL"] = ""
            df_updated.at[i, "TELEFON FIX"]   = ""

    # Salvăm starea curentă (inclusiv tot ce a tastat utilizatorul)
    st.session_state[key_rows] = df_updated.to_dict("records")

    # ----------------------------------------------------------
    # 5. Buton adăugare rând nou
    # ----------------------------------------------------------
    if st.button("➕ Adaugă membru", key=f"add_membru_{cod_introdus}"):
        st.session_state[key_rows].append({
            "NUME ȘI PRENUME": "",
            "ROLUL ÎN CONTRACT": "",
            "PERSOANĂ DE CONTACT": False,
            "DEPARTAMENT": "",
            "EMAIL": "",
            "TELEFON MOBIL": "",
            "TELEFON FIX": "",
        })
        st.rerun()

    # ----------------------------------------------------------
    # 6. Returnare date pentru salvare
    # ----------------------------------------------------------
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
