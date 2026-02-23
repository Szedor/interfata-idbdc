# ==========================================
# CALEA 1: EXPLORATOR DE DATE (Public)
# ==========================================
if calea_activa == "explorator":
    # i) Titlu centrat și curat
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de date</h1>", unsafe_allow_html=True)
    st.write("---")

    # ii) SELECTII DE BAZĂ (Punctele 1 și 2)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # 1. Categoria de informatii
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        cat_selectata = st.selectbox("Alege categoria de informații:", ["---"] + [i["denumire_categorie"] for i in res_cat.data], key="f_cat")

    with c2:
        # 2. Tipul de contract / proiect
        tip_ales = "---"
        if cat_selectata == "Contracte & Proiecte":
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            tip_ales = st.selectbox("Tipul de contract / proiect:", ["---"] + [i["acronim_contracte_proiecte"] for i in res_tip.data], key="f_tip")

    # iii) FILTRE DE RAFINARE (Punctele 3 - 9)
    # Apar doar după ce am ales tipul (ex: FDI, PNRR)
    if tip_ales != "---":
        st.markdown("#### Rafinare interogare:")
        
        # Împărțim celelalte 7 puncte în 3 coloane (3 + 2 + 2)
        f1, f2, f3 = st.columns(3)
        
        # Încărcăm datele din tabelul specific (ex: base_proiecte_fdi)
        tabel_tinta = f"base_proiecte_{tip_ales.lower()}"
        res_data = supabase.table(tabel_tinta).select("*").execute()
        df = pd.DataFrame(res_data.data)

        if not df.empty:
            with f1:
                # 3. ID-ul proiect / Numar contract
                id_sel = st.text_input("ID Proiect / Nr. Contract:", key="f_id")
                # 4. Acronim proiect / contract
                acro_sel = st.text_input("Acronim proiect:", key="f_acro")
                # 5. Titlul proiect / Obiectul contractului
                titlu_sel = st.text_input("Titlu / Obiect contract:", key="f_titlu")

            with f2:
                # 6. Director de proiect / Responsabil contract (Doar cei cu bifa DA)
                res_dir = supabase.table("com_echipe_proiecte").select("nume_prenume_membru").eq("reprezinta_idbdc", "DA").execute()
                directori = sorted(list(set([d['nume_prenume_membru'] for d in res_dir.data])))
                dir_sel = st.multiselect("Director / Responsabil:", directori, key="f_dir")
                
                # 7. Anul de implementare
                ani = sorted(df['an_implementare'].unique().tolist()) if 'an_implementare' in df.columns else []
                an_sel = st.multiselect("Anul de implementare:", ani, key="f_an")

            with f3:
                # 8. Rolul UPT (Coordonator / Partener)
                roluri = sorted(df['rol_upt'].unique().tolist()) if 'rol_upt' in df.columns else ["Coordonator", "Partener"]
                rol_sel = st.multiselect("Rolul UPT:", roluri, key="f_rol")
                
                # 9. Statusul proiectului / contractului
                statusuri = sorted(df['status'].unique().tolist()) if 'status' in df.columns else ["În derulare", "Finalizat"]
                status_sel = st.multiselect("Status proiect:", statusuri, key="f_status")

            # --- LOGICA DE FILTRARE (Rupere legături între filtre) ---
            if id_sel: df = df[df['cod_identificare'].astype(str).str.contains(id_sel, case=False, na=False)]
            if acro_sel: df = df[df['acronim'].str.contains(acro_sel, case=False, na=False)]
            if titlu_sel: df = df[df['titlu'].str.contains(titlu_sel, case=False, na=False)]
            if dir_sel: df = df[df['director_proiect'].isin(dir_sel)]
            if an_sel: df = df[df['an_implementare'].isin(an_sel)]
            if rol_sel: df = df[df['rol_upt'].isin(rol_sel)]
            if status_sel: df = df[df['status'].isin(status_sel)]

            # iv) Rezultate
            st.write("---")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button("📥 Descarcă Selecția", df.to_csv(index=False), f"export_{tip_ales.lower()}.csv")
