if nume_operator:
    st.title("🛠️ Editare și Validare Proiecte")
    
    # Selectăm un proiect din baza de date
    cur.execute("SELECT cod_inregistrare, titlu_proiect FROM base_proiecte_fdi")
    proiecte = cur.fetchall()
    optiuni = {f"{p[0]} - {p[1][:50]}...": p[0] for p in proiecte}
    
    selectie = st.selectbox("Selectează proiectul pentru validare:", list(optiuni.keys()))
    cod_proiect = optiuni[selectie]

    # Formularul de "Luptă"
    with st.form("form_editare"):
        st.info(f"Editezi proiectul: {cod_proiect}")
        
        # Aici adăugăm câmpurile CRUD
        validat = st.checkbox("Confirm validare IDBDC")
        observatii = st.text_area("Observații")
        
        buton_salvare = st.form_submit_button("💾 Salvează în Baza de Date")
        
        if buton_salvare:
            # Executăm UPDATE-ul care "ștampilează" rândul cu numele operatorului
            query_update = """
                UPDATE base_proiecte_fdi 
                SET responsabil_idbdc = %s, 
                    data_ultimei_actualizari = CURRENT_TIMESTAMP
                WHERE cod_inregistrare = %s
            """
            cur.execute(query_update, (nume_operator, cod_proiect))
            conn.commit()
            st.success(f"Proiect validat cu succes de către {nume_operator}!")
