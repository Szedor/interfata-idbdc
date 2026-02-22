# ==========================================
# 4. ZONA CENTRALĂ: LOGICĂ CATEGORII (7/8)
# ==========================================
if st.session_state.operator_identificat:
    st.markdown(f"### Panou de Lucru: {st.session_state.operator_identificat}")
    st.write("---")
    
    col_a, col_b = st.columns([1, 1])
    
    cat_selectata = "---"

    with col_a:
        try:
            # Încercăm să luăm datele din nom_categorii
            res_cat = supabase.table("nom_categorii").select("*").execute()
            if res_cat.data:
                # Extragem prima coloană disponibilă dacă "nume_categorie" nu e găsit
                cols = list(res_cat.data[0].keys())
                nume_col_cat = "nume_categorie" if "nume_categorie" in cols else cols[0]
                
                liste_categorii = [item[nume_col_cat] for item in res_cat.data]
                cat_selectata = st.selectbox("Selectați Categoria:", ["---"] + liste_categorii)
            else:
                st.warning("Tabela 'nom_categorii' este goală.")
        except Exception as e:
            st.error(f"Eroare la nom_categorii: Verifică dacă tabelul sau coloana există.")

    with col_b:
        if cat_selectata == "Contracte & Proiecte":
            try:
                res_sub = supabase.table("nom_contracte_proiecte").select("*").execute()
                if res_sub.data:
                    cols_sub = list(res_sub.data[0].keys())
                    nume_col_sub = "nume_optiune" if "nume_optiune" in cols_sub else cols_sub[0]
                    
                    liste_sub = [item[nume_col_sub] for item in res_sub.data]
                    opt_selectata = st.selectbox("Selectați Tipul:", ["---"] + liste_sub)
                else:
                    st.warning("Tabela 'nom_contracte_proiecte' este goală.")
            except Exception as e:
                st.error("Eroare la nom_contracte_proiecte.")
        else:
            st.selectbox("Selectați Tipul:", ["---"], disabled=True)

    if cat_selectata != "---":
        st.write(f"Secțiunea curentă: **{cat_selectata}**")
