# AFIȘARE TABELĂ CONFORM SELECȚIEI DINAMICE
    if cat_admin != "":
        st.write("---")
        tabel_map = {
            "Contracte & Proiecte": "base_proiecte_internationale",
            "Evenimente stiintifice": "base_evenimente_stiintifice",
            "Proprietate intelectuala": "base_prop_intelect"
        }
        nume_tabela = tabel_map.get(cat_admin)
        
        if nume_tabela:
            try:
                # Inițiem interogarea
                query = supabase.table(nume_tabela).select("*")
                
                # FILTRUL 2: Tip de proiect (din a doua casetă)
                # Presupunem că în baza de date coloana se numește 'tip_proiect' sau similar
                # Dacă ai un acronim selectat în caseta 2, filtrăm după el
                tip_sel = st.session_state.get("admin_tip")
                if tip_sel and tip_sel != "":
                    # Aici filtrăm coloana corespunzătoare tipului (ex: 'acronim_tip')
                    query = query.eq("acronim_contracte_proiecte", tip_sel)

                # FILTRUL 3: ID Proiect (din a treia casetă)
                if id_cautat:
                    query = query.eq("cod_identificare", id_cautat)
                
                res = query.execute()
                
                if res.data:
                    df = pd.DataFrame(res.data)
                    st.success(f"🔍 Rezultate: {len(df)} înregistrări găsite.")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.warning("Nu s-au găsit date care să respecte TOATE filtrele selectate.")
            
            except Exception as e:
                st.error(f"Eroare la filtrare: {e}")
