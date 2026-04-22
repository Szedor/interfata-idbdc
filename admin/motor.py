# =========================================================
# admin/motor.py
# v.modul.1.2 - Secțiunea de salvare cu mesaje explicite
# =========================================================

# ... (restul fișierului identic, doar secțiunea btn_save este cea modificată)

    if btn_save:
        with st.spinner("Se salvează datele..."):
            erori = []

            # Tabel bază
            if "baza" in rezultate and rezultate["baza"]:
                row = {**rezultate["baza"]}
                row["cod_identificare"] = cod_introdus
                ok, msg = ops.direct_upsert_single_row(supabase, base_table, row)
                if not ok:
                    erori.append(f"Date de bază: {msg}")
                else:
                    st.success("✅ Datele de bază au fost salvate cu succes!")

            # Date financiare
            if "financiar" in rezultate:
                try:
                    supabase.table("com_date_financiare").delete().eq("cod_identificare", cod_introdus).execute()
                except:
                    pass
                for row in rezultate["financiar"]:
                    ok, msg = ops.direct_upsert_single_row(
                        supabase, "com_date_financiare", row, match_col="cod_identificare"
                    )
                    if not ok:
                        erori.append(f"Date financiare: {msg}")
                    else:
                        st.success("✅ Datele financiare au fost salvate cu succes!")

            # Echipă
            if "echipa" in rezultate:
                try:
                    supabase.table("com_echipe_proiect").delete().eq("cod_identificare", cod_introdus).execute()
                except:
                    pass
                randuri_echipa = [row for row in rezultate["echipa"] if row.get("nume_prenume")]
                if randuri_echipa:
                    try:
                        supabase.table("com_echipe_proiect").insert(randuri_echipa).execute()
                        st.success("✅ Echipa a fost salvată cu succes!")
                    except Exception as e:
                        erori.append(f"Echipă: {e}")

            if erori:
                st.session_state["admin_msg"] = ("error", " | ".join(erori))
            else:
                st.session_state["admin_msg"] = ("success", "Toate datele au fost salvate cu succes.")
            st.rerun()
