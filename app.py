Python
# Funcție pentru a verifica dacă utilizatorul este unul dintre cei 9
def verifica_specialist(cod_introdus):
    # Interogăm tabelul tău de specialiști (ajustează numele tabelului dacă e diferit)
    query = f"SELECT cod_identificare FROM nom_specialisti WHERE cod_identificare = '{cod_introdus}'"
    rezultat = conexiune_supabase.query(query) # Folosește metoda ta de conectare
    return len(rezultat) > 0

# Funcție pentru încărcarea datelor reale (Fără LIMIT 2)
def incarca_date_idbdc(nume_tabel):
    # Aici aducem TOATE rândurile (cele 381 sau miile care vor veni)
    query = f"SELECT * FROM {nume_tabel} ORDER BY cod_identificare DESC"
    return conexiune_supabase.query(query)

# --- ÎN CONSOLĂ ---
if user_id != "":
    if verifica_specialist(user_id):
        st.sidebar.success("Autoritate Confirmată")
        
        # Încărcăm datele din tabelul ales în Sidebar
        date_proiecte = incarca_date_idbdc(baza_selectata)
        
        st.write(f"### Gestionare {baza_selectata}")
        st.write(f"Sunt încărcate **{len(date_proiecte)}** înregistrări.")
        
        # AFIȘAREA TABELULUI MASTER
        # Folosim st.dataframe pentru vizualizare sau st.data_editor pentru editare rapidă
        proiect_selectat = st.dataframe(date_proiecte, use_container_width=True)
    else:
        st.sidebar.error("Codul nu figurează în lista celor 9 autorități.")
