# =========================================================
# IDBDC/calea2_admin/motor.py
# VERSIUNE: 2.0
# STATUS: CORECTAT - salvare corectă date financiare multi-ani
# DATA: 2026.05.28
# =========================================================
# MODIFICĂRI VERSIUNEA 2.0:
#   - CORECȚIE MAJORĂ: Datele financiare se salvează folosind
#     insert_rows_batch() sau upsert_rows_batch() cu cheie compusă
#   - Eliminat delete_all_for_project() înainte de upsert (contraproductiv)
#   - Folosit direct upsert_rows_batch cu match_col compus
# =========================================================

# ... (restul importurilor și codului identic până la secțiunea de salvare)

    if btn_save:
        with st.spinner("Se salvează datele..."):
            erori = []

            baza = rezultate.get("baza") or st.session_state.get(key_baza_ss)
            if baza:
                ok, msg = upsert_row(supabase, defn.BASE_TABLE, {**baza, "cod_identificare": cod_introdus})
                if not ok:
                    erori.append(f"Date de bază: {msg}")

            # Date suplimentare (proprietate industriala) — acelasi tabel ca baza
            supl = rezultate.get("suplimentare") or st.session_state.get(key_baza_ss + "_supl")
            if supl:
                ok, msg = upsert_row(supabase, defn.BASE_TABLE, {**supl, "cod_identificare": cod_introdus})
                if not ok:
                    erori.append(f"Date suplimentare: {msg}")

            # ─────────────────────────────────────────────────────────────────
            # SALVARE DATE FINANCIARE - CORECTATĂ PENTRU MULTI-ANI
            # ─────────────────────────────────────────────────────────────────
            if hasattr(defn, "FIN_TABLE"):
                fin = rezultate.get("financiar") or st.session_state.get(key_fin_ss)
                if fin is not None and isinstance(fin, list) and fin:
                    # Filtrăm doar rândurile valide (care au an_referinta)
                    rows_valide = [row for row in fin if row.get("an_referinta")]
                    
                    if rows_valide:
                        # Metoda 1: Folosim upsert cu cheie compusă (recomandat)
                        # Aceasta va adăuga noi ani și va actualiza anii existenți
                        ok, msg = upsert_rows_batch(
                            supabase, 
                            defn.FIN_TABLE, 
                            rows_valide, 
                            match_col=["cod_identificare", "an_referinta"]  # CHEIE COMPUSĂ
                        )
                        if not ok:
                            erori.append(f"Date financiare: {msg}")
                        
                        # Debug: afișăm în log câte înregistrări s-au salvat
                        st.caption(f"📊 Salvate {len(rows_valide)} înregistrări financiare pentru anii: {', '.join([r['an_referinta'] for r in rows_valide])}")
                    else:
                        # Dacă nu sunt rânduri valide, ștergem toate înregistrările existente
                        delete_all_for_project(supabase, defn.FIN_TABLE, cod_introdus)
                elif fin == []:  # Listă goală - utilizatorul a șters toți anii
                    delete_all_for_project(supabase, defn.FIN_TABLE, cod_introdus)

            # SALVARE ECHIPĂ
            if "echipa" in rezultate:
                delete_all_for_project(supabase, defn.ECHIPA_TABLE, cod_introdus)
                randuri = [r for r in rezultate["echipa"] if r.get("nume_prenume")]
                if randuri:
                    ok, msg = insert_rows(supabase, defn.ECHIPA_TABLE, randuri)
                    if not ok:
                        erori.append(f"Echipă: {msg}")

            # SALVARE ASPECTE TEHNICE
            if hasattr(defn, "TEHNIC_TABLE"):
                teh = rezultate.get("tehnice") or st.session_state.get(key_teh_ss)
                if teh is not None:
                    delete_all_for_project(supabase, defn.TEHNIC_TABLE, cod_introdus)
                    for row in teh:
                        ok, msg = upsert_row(supabase, defn.TEHNIC_TABLE, row)
                        if not ok:
                            erori.append(f"Aspecte tehnice: {msg}")

            st.session_state["admin_msg"] = (
                ("error", " | ".join(erori)) if erori
                else ("success", "Toate datele au fost salvate cu succes.")
            )
            if f"echipa_editor_{cod_introdus}" in st.session_state:
                del st.session_state[f"echipa_editor_{cod_introdus}"]
            st.rerun()

# ... (restul codului identic)
