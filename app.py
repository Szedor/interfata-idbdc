# ==========================================
# CALEA 1: EXPLORATOR DE DATE (Public)
# ==========================================
if calea_activa == "explorator":
    # i) Titlul centrat
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de Date IDBDC</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Sistem de interogare rapidă a informațiilor de cercetare</p>", unsafe_allow_html=True)
    st.write("---")

    # i) Alege categoria de informații
    st.markdown("### i) Alege categoria de informații")
    try:
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        categorii = [item["denumire_categorie"] for item in res_cat.data]
        cat_selectata = st.selectbox("Selectați categoria:", ["---"] + categorii, label_visibility="collapsed", key="exp_cat")

        # i1) Dacă alege Contracte & Proiecte
        if cat_selectata == "Contracte & Proiecte":
            st.write("")
            st.markdown("### i1.1) Alege tipul de contract sau proiect")
            
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            tipuri = [item["acronim_contracte_proiecte"] for item in res_tip.data]
            tip_ales = st.selectbox("Selectați tipul (FDI, PNRR etc.):", ["---"] + tipuri, label_visibility="collapsed", key="exp_tip")

            if tip_ales != "---":
                # Determinăm tabelul bază conform Protocolului (ex: base_proiecte_fdi)
                tabel_tinta = f"base_proiecte_{tip_ales.lower()}"
                
                # Preluăm datele pentru filtrare
                res_date = supabase.table(tabel_tinta).select("*").execute()
                df = pd.DataFrame(res_date.data)

                if not df.empty:
                    st.write("---")
                    st.markdown("#### Filtre de rafinare situație:")
                    
                    # Cele 3 coloane pentru interogare
                    f1, f2, f3 = st.columns(3)
                    
                    with f1:
                        # An Referință (din tabelul curent)
                        ani = sorted(df['an_referinta'].unique().tolist()) if 'an_referinta' in df.columns else []
                        an_selectat = st.multiselect("An referință:", ani)
                        
                        # Cod Identificare / Nr. Contract
                        id_cautat = st.text_input("Cod Identificare / Nr. Contract:")

                    with f2:
                        # Director de Proiect (Legătură cu com_echipe_proiecte, doar cei cu DA)
                        try:
                            res_dir = supabase.table("com_echipe_proiecte").select("nume_prenume_membru").eq("reprezinta_idbdc", "DA").execute()
                            directori = sorted(list(set([d['nume_prenume_membru'] for d in res_dir.data])))
                            director_ales = st.multiselect("Director Proiect (IDBDC):", directori)
                        except:
                            director_ales = []

                    with f3:
                        # Departament
                        depts = sorted(df['departament'].unique().tolist()) if 'departament' in df.columns else []
                        dept_ales = st.multiselect("Departament:", depts)

                    # --- LOGICA DE FILTRARE ---
                    if an_selectat:
                        df = df[df['an_referinta'].isin(an_selectat)]
                    if id_cautat:
                        df = df[df['cod_identificare'].str.contains(id_cautat, case=False, na=False)]
                    if director_ales:
                        # Aici presupunem că în tabelul base_proiecte există coloana director_proiect
                        if 'director_proiect' in df.columns:
                            df = df[df['director_proiect'].isin(director_ales)]
                    if dept_ales:
                        df = df[df['departament'].isin(dept_ales)]

                    # --- AFIȘARE REZULTATE ---
                    st.write("---")
                    st.markdown(f"**Rezultate găsite: {len(df)}**")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Export CSV pentru vizitatori
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Descarcă Raportul", csv, f"raport_{tip_ales.lower()}.csv", "text/csv")
                else:
                    st.warning(f"Tabelul {tabel_tinta} nu conține date.")
    except Exception as e:
        st.error(f"Eroare la interogare: {e}")
