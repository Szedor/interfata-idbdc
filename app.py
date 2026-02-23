# ==========================================
# CALEA 1: EXPLORATOR DE DATE (Public)
# ==========================================
if calea_activa == "explorator":
    # i) Titlul centrat (fără IDBDC, conform cerinței)
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de date</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Sistem de interogare rapidă a informațiilor de cercetare</p>", unsafe_allow_html=True)
    st.write("---")

    # Structură pe 3 coloane pentru Selecția Principală
    c1, c2, c3 = st.columns(3)

    with c1:
        # ii) Prima casetă fără "i)" la început
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
            categorii = [item["denumire_categorie"] for item in res_cat.data]
            cat_selectata = st.selectbox("Alege categoria de informații:", ["---"] + categorii, key="exp_cat")
        except:
            st.error("Eroare nomenclator categorii.")
            cat_selectata = "---"

    with c2:
        # Apare doar dacă s-a selectat categoria
        tip_ales = "---"
        if cat_selectata == "Contracte & Proiecte":
            try:
                res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
                tipuri = [item["acronim_contracte_proiecte"] for item in res_tip.data]
                tip_ales = st.selectbox("Alege tipul de proiect:", ["---"] + tipuri, key="exp_tip")
            except:
                st.error("Eroare nomenclator tipuri.")

    # Dacă avem tipul selectat, afișăm filtrele de rafinare dedesubt, tot pe coloane
    if tip_ales != "---":
        st.write("---")
        st.markdown("#### Rafinare interogare:")
        
        # Grid de filtre (3 coloane)
        f1, f2, f3 = st.columns(3)
        
        tabel_tinta = f"base_proiecte_{tip_ales.lower()}"
        res_date = supabase.table(tabel_tinta).select("*").execute()
        df = pd.DataFrame(res_date.data)

        if not df.empty:
            with f1:
                # Filtru An și ID
                ani = sorted(df['an_referinta'].unique().tolist()) if 'an_referinta' in df.columns else []
                an_sel = st.multiselect("An referință:", ani)
                id_sel = st.text_input("Cod / Nr. Contract:")

            with f2:
                # Filtru Director (doar cei cu bifa DA)
                try:
                    res_dir = supabase.table("com_echipe_proiecte").select("nume_prenume_membru").eq("reprezinta_idbdc", "DA").execute()
                    directori = sorted(list(set([d['nume_prenume_membru'] for d in res_dir.data])))
                    dir_sel = st.multiselect("Director Proiect:", directori)
                except:
                    dir_sel = []

            with f3:
                # Filtru Departament
                depts = sorted(df['departament'].unique().tolist()) if 'departament' in df.columns else []
                dept_sel = st.multiselect("Departament:", depts)

            # --- LOGICA FILTRARE ---
            if an_sel: df = df[df['an_referinta'].isin(an_sel)]
            if id_sel: df = df[df['cod_identificare'].astype(str).str.contains(id_sel, case=False, na=False)]
            if dir_sel:
                if 'director_proiect' in df.columns:
                    df = df[df['director_proiect'].isin(dir_sel)]
            if dept_sel: df = df[df['departament'].isin(dept_sel)]

            # Afișare tabel
            st.write("---")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button("📥 Descarcă rezultatele", df.to_csv(index=False), f"export_{tip_ales.lower()}.csv")
