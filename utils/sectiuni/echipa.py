# =========================================================
# IDBDC/utils/sectiuni/echipa.py
# VERSIUNE: 7.0
# STATUS: CORECTAT - ROL sincronizat corect la prima tastare
# DATA: 2026.05.03
# =========================================================
# CONȚINUT:
#   Secțiunea ECHIPĂ comună pentru toate tipurile de contracte
#   și proiecte. Randează tabelul editabil cu membrii echipei,
#   completează automat departament/email/telefon la selectarea
#   numelui, gestionează adăugarea de membri noi și returnează
#   datele pentru salvare în PostgreSQL (tabela com_echipe_proiect).
#
# MODIFICĂRI VERSIUNEA 7.0:
#   - Corectat comportamentul câmpului ROLUL ÎN CONTRACT care
#     se pierdea la prima tastare când se trecea la alt câmp.
#     CAUZA: la prima tastare într-un câmp ROL, Streamlit nu
#     declanșează un rerun imediat — valoarea din df_edit era
#     corectă pe ecran dar nu ajungea în session_state înainte
#     ca utilizatorul să treacă la câmpul următor.
#     SOLUȚIA: citim valorile ROL direct din
#     st.session_state[key_editor] (starea internă a editorului
#     Streamlit) când este disponibil, ca sursă prioritară față
#     de df_edit. Aceasta garantează că orice valoare tastată,
#     chiar și la prima interacțiune, este capturată corect.
# =========================================================

import streamlit as st
import pandas as pd


def render_echipa(supabase, cod_introdus, is_new, date_existente):

    # ----------------------------------------------------------
    # 1. Citire date de referință (cu cache 10 minute)
    # ----------------------------------------------------------
    @st.cache_data(show_spinner=False, ttl=600)
    def _fetch_persoane(_supabase):
        try:
            res = _supabase.table("det_resurse_umane").select(
                "nume_prenume,email,telefon_mobil,telefon_fix,acronim_departament"
            ).order("nume_prenume").execute()
            return res.data or []
        except Exception:
            return []

    @st.cache_data(show_spinner=False, ttl=600)
    def _fetch_departamente(_supabase):
        try:
            res2 = _supabase.table("nom_departament").select(
                "acronim_departament,denumire_departament"
            ).execute()
            return {
                r["acronim_departament"]: r["denumire_departament"]
                for r in (res2.data or []) if r.get("acronim_departament")
            }
        except Exception:
            return {}

    persoane_data = _fetch_persoane(supabase)
    dep_map = _fetch_departamente(supabase)

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
    # 5. Detectare schimbări + sincronizare completă session_state
    #
    # CORECȚIE [v7.0]: Citim valorile ROL direct din starea
    # internă a editorului (st.session_state[key_editor])
    # când este disponibilă, ca sursă prioritară.
    #
    # DE CE: Streamlit's data_editor stochează starea editată
    # în st.session_state[key_editor] sub cheia "edited_rows"
    # imediat la orice modificare, ÎNAINTE de rerun. Astfel,
    # chiar dacă utilizatorul tastează ROL și trece rapid la
    # alt câmp (fără rerun intermediar), valoarea este deja
    # în session_state[key_editor]["edited_rows"] și o putem
    # citi de acolo. df_edit reflectă starea DUPĂ rerun —
    # dacă reruns-ul nu s-a produs încă, df_edit poate conține
    # valoarea veche (goală) pentru ROL.
    # ----------------------------------------------------------
    rows_curente = st.session_state[key_data_init]
    needs_rerun = False

    # Extragem edited_rows din starea internă a editorului
    editor_state = st.session_state.get(key_editor, {})
    edited_rows = editor_state.get("edited_rows", {}) if isinstance(editor_state, dict) else {}

    for i, row in df_edit.iterrows():
        if i >= len(rows_curente):
            break

        nume_nou   = row.get("NUME ȘI PRENUME", "") or ""
        nume_vechi = rows_curente[i].get("NUME ȘI PRENUME", "") or ""

        # CORECȚIE [v7.0]: Pentru ROL, verificăm mai întâi în
        # edited_rows (starea internă a editorului) — aceasta
        # conține valoarea tastată chiar dacă reruns-ul nu s-a
        # produs încă. Fallback pe df_edit dacă nu există în
        # edited_rows.
        rol_din_editor = (
            edited_rows.get(i, {}).get("ROLUL ÎN CONTRACT")
            if i in edited_rows else None
        )
        rol_final = rol_din_editor if rol_din_editor is not None \
            else (row.get("ROLUL ÎN CONTRACT", "") or "")

        rows_curente[i]["ROLUL ÎN CONTRACT"]   = str(rol_final).strip()
        rows_curente[i]["PERSOANĂ DE CONTACT"] = bool(
            edited_rows.get(i, {}).get("PERSOANĂ DE CONTACT",
                row.get("PERSOANĂ DE CONTACT", False))
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
        if key_editor in st.session_state:
            del st.session_state[key_editor]
        st.rerun()

    # ----------------------------------------------------------
    # 6. Buton Adaugă membru
    # ----------------------------------------------------------
    if st.button("➕ Adaugă membru", key=f"add_membru_{cod_introdus}"):
        rows_sync = st.session_state[key_data_init]
        for i, row in df_edit.iterrows():
            if i < len(rows_sync):
                rol_din_editor = (
                    edited_rows.get(i, {}).get("ROLUL ÎN CONTRACT")
                    if i in edited_rows else None
                )
                rows_sync[i]["NUME ȘI PRENUME"]     = row.get("NUME ȘI PRENUME", "") or ""
                rows_sync[i]["ROLUL ÎN CONTRACT"]   = str(rol_din_editor).strip() \
                    if rol_din_editor is not None \
                    else (row.get("ROLUL ÎN CONTRACT", "") or "")
                rows_sync[i]["PERSOANĂ DE CONTACT"] = bool(row.get("PERSOANĂ DE CONTACT", False))
                n = rows_sync[i]["NUME ȘI PRENUME"]
                if n and n in info_map:
                    info = info_map[n]
                    rows_sync[i]["DEPARTAMENT"]   = info["dep"]
                    rows_sync[i]["EMAIL"]         = info["email"]
                    rows_sync[i]["TELEFON MOBIL"] = info["mob"]
                    rows_sync[i]["TELEFON FIX"]   = info["fix"]

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

        if key_editor in st.session_state:
            del st.session_state[key_editor]
        st.rerun()

    # ----------------------------------------------------------
    # 7. Returnare date pentru salvare
    # CORECȚIE [v7.0]: ROL citit prioritar din edited_rows
    # pentru a garanta că ultima valoare tastată este salvată.
    # ----------------------------------------------------------
    rezultat = []
    for i, row in df_edit.iterrows():
        n = str(row.get("NUME ȘI PRENUME", "") or "").strip()
        if not n:
            continue
        rol_din_editor = (
            edited_rows.get(i, {}).get("ROLUL ÎN CONTRACT")
            if i in edited_rows else None
        )
        rol = str(rol_din_editor).strip() if rol_din_editor is not None \
            else str(row.get("ROLUL ÎN CONTRACT", "") or "").strip()
        contact = bool(
            edited_rows.get(i, {}).get("PERSOANĂ DE CONTACT",
                row.get("PERSOANĂ DE CONTACT", False))
        )
        rezultat.append({
            "cod_identificare": cod_introdus,
            "nume_prenume":     n,
            "rol":              rol,
            "persoana_contact": contact,
            "functie_upt":      "",
        })
    return rezultat
