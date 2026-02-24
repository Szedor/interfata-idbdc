# LOGICA DE AFIȘARE TABELĂ (După cele 3 casete)
    if cat_admin != "":
        st.write("---")
        st.subheader(f"📊 Rezultate pentru: {cat_admin}")
        
        # Mapare: Categorie -> Nume Tabelă în Supabase
        # Folosim 'base_proiecte_internationale' pentru cele 381 de înregistrări menționate
        tabel_map = {
            "Contracte & Proiecte": "base_proiecte_internationale",
            "Evenimente stiintifice": "base_evenimente_stiintifice",
            "Proprietate intelectuala": "base_prop_intelect"
        }
        
        nume_tabela = tabel_map.get(cat_admin)
        
        if nume_tabela:
            try:
                # 1. Preluăm datele
                query = supabase.table(nume_tabela).select("*")
                
                # 2. Aplicăm filtrul de ID dacă operatorul a introdus ceva în caseta 3
                id_cautat = st.session_state.get("admin_id", "")
                if id_cautat:
                    # Folosim 'cod_identificare' conform protocolului IDBDC
                    query = query.eq("cod_identificare", id_cautat)
                
                res = query.execute()
                
                if res.data:
                    import pandas as pd
                    df = pd.DataFrame(res.data)
                    
                    # Afișăm tabelul
                    # Am adăugat un stil pentru tabelă să fie lizibilă (albă) pe fundalul albastru
                    st.markdown("""
                        <style>
                            .stDataFrame { background-color: white; border-radius: 5px; }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.caption(f"S-au găsit {len(df)} înregistrări.")
                else:
                    st.warning("Nu s-au găsit date pentru criteriile selectate.")
                    
            except Exception as e:
                st.error(f"Eroare la interogarea bazei de date: {e}")
        else:
            st.info("Această categorie nu are încă o tabelă alocată în baza de date.")
