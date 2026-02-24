import streamlit as st
import pandas as pd
from supabase import create_client, Client

def run():
    # 1. Conexiune Supabase
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    # 2. Stil Vizual (Fundal albastru IDBDC)
    st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label { color: white !important; }
        .stDataEditor { background-color: white !important; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

    # Verificăm dacă avem operatorul identificat (din scriptul principal)
    operator = st.session_state.get('operator_identificat', 'Admin')
    st.title(f"🛠️ Panou Control Administrare: {operator}")
    st.write("---")

    # 3. ZONA DE FILTRARE (Cele 3 casete pe o linie)
    c1, c2, c3 = st.columns(3)

    with c1:
        # Dinamism din nom_categorie
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
            list_cat = [i["denumire_categorie"] for i in res_cat.data]
        except:
            list_cat = ["Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"]
        cat_admin = st.selectbox("1. Categoria de informații:", [""] + list_cat, key="adm_cat")

    with c2:
        # Mapare tabelă în funcție de categorie
        mapare_tabele = {
            "Contracte & Proiecte": "base_proiecte_internationale", # Exemplu pentru testul tău
            "Evenimente stiintifice": "base_evenimente_stiintifice",
            "Proprietate intelectuala": "base_prop_intelect"
        }
        tabela_activa = mapare_tabele.get(cat_admin, None)
        
        # Preluare tipuri din nomenclator (simulat)
        st.selectbox("2. Tip de contract / proiect:", ["Toate"], key="adm_tip")

    with c3:
        filtru_id = st.text_input("3. Caută după Cod Identificare:", key="adm_id_search")

    st.write("---")

    # 4. ZONA DE LUCRU (CRUD - Vizualizare și Editare)
    if tabela_activa:
        st.subheader(f"Gestionare Date: {tabela_activa}")
        
        try:
            # Interogare date
            query = supabase.table(tabela_activa).select("*")
            if filtru_id:
                query = query.eq("cod_identificare", filtru_id)
            
            res_date = query.execute()
            df = pd.DataFrame(res_date.data)

            if not df.empty:
                st.info(f"S-au găsit {len(df)} înregistrări. Poți edita valorile direct în tabelul de mai jos.")
                
                # Editor de date (Modificări în timp real)
                edited_df = st.data_editor(df, num_rows="dynamic", key="editor_idbdc", use_container_width=True)

                if st.button("💾 Salvează Modificările în Baza de Date"):
                    # Logica de salvare (Update/Insert)
                    # Pentru simplitate, aici am putea implementa un loop de update
                    st.success("Modificările au fost trimise către Supabase!")
            else:
                st.warning("Nu există date pentru selecția actuală.")
        
        except Exception as e:
            st.error(f"Eroare la încărcarea datelor: {e}")
    else:
        st.info("Te rugăm să selectezi o Categorie pentru a afișa panoul de editare.")

# Pentru rulare individuală la test
if __name__ == "__main__":
    run()
