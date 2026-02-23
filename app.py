# ==========================================
# 4. MODUL INTEROGARE BINE STRUCTURAT (IDBDC)
# ==========================================
if st.session_state.get('operator_identificat'):
    st.markdown("### 🔍 Sistem de Interogare Date")
    
    # i) Alege categoria de informatii
    st.markdown("#### i) Alege categoria de informații")
    try:
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        categorii = [item["denumire_categorie"] for item in res_cat.data]
        cat_selectata = st.selectbox("Categorie:", ["---"] + categorii, label_visibility="collapsed")
    except:
        st.error("Eroare la încărcarea categoriilor.")
        cat_selectata = "---"

    # i1) Dacă alege Contracte & Proiecte
    if cat_selectata == "Contracte & Proiecte":
        st.write("---")
        col_st, col_dr = st.columns(2)

        with col_st:
            # i1.1) Alege tipul de contract sau proiect
            st.markdown("#### i1.1) Alege tipul de contract sau proiect")
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            tipuri = [item["acronim_contracte_proiecte"] for item in res_tip.data]
            tip_ales = st.selectbox("Tip proiect:", ["---"] + tipuri, label_visibility="collapsed")

        if tip_ales != "---":
            tabel_tinta = f"base_proiecte_{tip_ales.lower()}"
            
            try:
                # Interogăm tabelul specificat
                res_date = supabase.table(tabel_tinta).select("*").execute()
                df = pd.DataFrame(res_date.data)

                if not df.empty:
                    st.markdown("#### Filtre de rafinare situație")
                    f1, f2, f3 = st.columns(3)

                    with f1:
                        # An referință și ID (din cod_identificare)
                        ani = sorted(df['an_referinta'].unique().tolist()) if 'an_referinta' in df.columns else []
                        an_selectat = st.multiselect("An referință:", ani)
                        
                        id_cautat = st.text_input("Cod Identificare / Nr. Contract:")

                    with f2:
                        # Director de Proiect (Legătură cu com_echipe_proiecte)
                        # Aici căutăm doar persoanele care au 'DA' pe reprezinta_idbdc
                        try:
                            res_dir = supabase.table("com_echipe_proiecte").select("nume_prenume_membru").eq("reprezinta_idbdc", "DA").execute()
                            directori = sorted(list(set([d['nume_prenume_membru'] for d in res_dir.data])))
                            director_ales = st.multiselect("Director Proiect (IDBDC):", directori)
                        except:
                            st.write("Eroare la încărcare directori.")
                            director_ales = []

                    with f3:
                        # Departament
                        depts = sorted(df['departament'].unique().tolist()) if 'departament' in df.columns else []
                        dept_ales = st.multiselect("Departament:", depts)

                    # --- LOGICA DE FILTRARE TABEL ---
                    if an_selectat:
                        df = df[df['an_referinta'].isin(an_selectat)]
                    if id_cautat:
                        df = df[df['cod_identificare'].str.contains(id_cautat, case=False, na=False)]
                    if director_ales:
                        # Filtrăm în DF principal coloana directorului (dacă există)
                        if 'director_proiect' in df.columns:
                            df = df[df['director_proiect'].isin(director_ales)]
                    if dept_ales:
                        df = df[df['departament'].isin(dept_ales)]

                    # --- AFIȘARE REZULTATE & DOWNLOAD ---
                    st.write("---")
                    st.markdown(f"**Situație generată: {len(df)} înregistrări**")
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    # Export pentru raportare management
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Descarcă Situația (CSV/Excel)", csv, f"raport_{tip_ales.lower()}.csv", "text/csv")

            except Exception as e:
                st.error(f"Tabelul '{tabel_tinta}' nu este încă populat sau lipsește.")
    
    # Restul variantelor (i2, i3) se vor adăuga similar după stabilirea structurii lor
else:
    st.info("Sistemul așteaptă identificarea operatorului pentru interogare.")
