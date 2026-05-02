# =========================================================
# IDBDC/utils/sectiuni/echipa.py
# VERSIUNE: 6.0
# STATUS: CORECTAT - sincronizare completă session_state
# DATA: 2026.05.02
# =========================================================

import streamlit as st
import pandas as pd


def render_echipa(supabase, cod_introdus, is_new, date_existente):

    # ----------------------------------------------------------
    # 1. Citire date de referință
    # CORECȚIE [1A]: Interogările către baza de date sunt
    # acum protejate cu @st.cache_data, exact ca în date_baza.py.
    # Efectul: datele despre persoane și departamente se citesc
    # O SINGURĂ DATĂ și se păstrează în memorie 10 minute.
    # Anterior, la FIECARE reîncărcare a paginii (inclusiv la
    # fiecare literă tastată), aplicația mergea la baza de date
    # de 2 ori. Acesta era principalul vinovat pentru "licarire"
    # și pentru timpul mare de răspuns.
    # ----------------------------------------------------------

    @st.cache_data(show_spinner=False, ttl=600)
    def _fetch_persoane(_supabase):
        try:
            res = _supabase.table("det_resurse_umane").select(
                "nume_prenume,email,telefon_mobil,telefon_fix,acronim_departament"
            ).order("nume_prenume").execute()
            return res.data or []
        except Exception as e:
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
        except Exception as e:
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
    # 5. Detectare schimbări nume + completare automată
    #
    # CORECȚIE [2A]: Sincronizare COMPLETĂ a tuturor rândurilor
    # înainte de a decide dacă este necesar un rerun.
    #
    # PROBLEMA ORIGINALĂ: Bucla verifica rând cu rând dacă s-a
    # schimbat numele. Când găsea o schimbare, marca needs_rerun=True
    # și continua bucla — dar rândurile URMĂTOARE (care poate aveau
    # deja ROLUL completat de utilizator) erau salvate corect doar
    # dacă utilizatorul nu acționa prea repede. Dacă utilizatorul
    # trecea rapid la alt câmp, Streamlit reîncărca pagina cu starea
    # veche a rândurilor neprocessate încă, ștergând ce se scrisese.
    #
    # SOLUȚIA: Salvăm ÎNTOTDEAUNA toate rândurile (inclusiv ROLUL
    # și PERSOANA DE CONTACT) pentru TOATE rândurile din editor,
    # indiferent dacă s-a schimbat sau nu numele. Abia DUPĂ ce
    # toate datele sunt în siguranță în session_state, facem rerun
    # dacă este nevoie. Astfel, chiar dacă utilizatorul acționează
    # rapid, datele sale sunt deja salvate înainte de reîncărcare.
    # ----------------------------------------------------------
    rows_curente = st.session_state[key_data_init]
    needs_rerun = False

    for i, row in df_edit.iterrows():
        if i >= len(rows_curente):
            break

        nume_nou   = row.get("NUME ȘI PRENUME", "") or ""
        nume_vechi = rows_curente[i].get("NUME ȘI PRENUME", "") or ""

        # CORECȚIE [2B]: Salvăm ROLUL și PERSOANA DE CONTACT
        # pentru ORICE rând, indiferent dacă s-a schimbat numele.
        # Anterior, în ramura "if nume_nou != nume_vechi", se salva
        # rolul corect, dar în anumite condiții de timing rapid,
        # rândurile din afara ramurii if puteau fi suprascrise cu
        # valorile vechi din session_state în loc de cele din editor.
        rows_curente[i]["ROLUL ÎN CONTRACT"]   = row.get("ROLUL ÎN CONTRACT", "") or ""
        rows_curente[i]["PERSOANĂ DE CONTACT"] = bool(row.get("PERSOANĂ DE CONTACT", False))

        if nume_nou != nume_vechi:
            # Completăm automat departament/email/telefon din info_map
            info = info_map.get(nume_nou, {"dep": "", "email": "", "mob": "", "fix": ""})
            rows_curente[i]["NUME ȘI PRENUME"] = nume_nou
            rows_curente[i]["DEPARTAMENT"]     = info["dep"]
            rows_curente[i]["EMAIL"]           = info["email"]
            rows_curente[i]["TELEFON MOBIL"]   = info["mob"]
            rows_curente[i]["TELEFON FIX"]     = info["fix"]
            needs_rerun = True

    # CORECȚIE [2C]: Salvăm session_state ÎNAINTE de orice rerun.
    # Anterior această linie exista, dar ordinea operațiilor putea
    # cauza ca într-un rerun rapid să se folosească starea veche.
    # Acum toate modificările sunt consolidate mai sus înainte de save.
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
    #
    # CORECȚIE [3A]: Datele returnate pentru salvare provin
    # acum din df_edit (ce vede utilizatorul pe ecran în acel
    # moment), NU din session_state[key_data_init].
    #
    # PROBLEMA ORIGINALĂ: Dacă utilizatorul scria ROLUL și apoi
    # apăsa imediat "Salvează toate datele", session_state putea
    # conține versiunea anterioară a rândului (fără ultimul ROL
    # scris), deoarece sincronizarea din secțiunea 5 se bazează
    # pe detectarea schimbărilor de NUME. Modificările doar în
    # câmpul ROL, fără schimbare de NUME, puteau fi pierdute
    # dacă salvarea era apăsată foarte rapid.
    #
    # SOLUȚIA: Citim datele direct din df_edit pentru câmpurile
    # editabile (NUME, ROL, PERSOANA), și din session_state
    # pentru câmpurile completate automat (DEPARTAMENT etc.).
    # Astfel ce vede utilizatorul = ce se salvează în baza de date.
    # ----------------------------------------------------------
    rezultat = []
    rows_ref = st.session_state[key_data_init]

    for i, row in df_edit.iterrows():
        n = str(row.get("NUME ȘI PRENUME", "") or "").strip()
        if not n:
            continue
        # CORECȚIE [3B]: ROL și PERSOANA vin din df_edit (ecran),
        # nu din session_state, pentru a garanta că ultima valoare
        # introdusă de utilizator este cea care se salvează.
        rol = str(row.get("ROLUL ÎN CONTRACT", "") or "").strip()
        contact = bool(row.get("PERSOANĂ DE CONTACT", False))

        rezultat.append({
            "cod_identificare": cod_introdus,
            "nume_prenume":     n,
            "rol":              rol,
            "persoana_contact": contact,
            "functie_upt":      "",
        })
    return rezultat
