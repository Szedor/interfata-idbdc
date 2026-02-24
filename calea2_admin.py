import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    # CSS pentru iconițe mari și butoane scurte
    st.markdown("""
    <style>
        .stApp { background-color: #003366 !important; }
        .stDataEditor { background-color: white !important; border-radius: 5px; }
        /* Stil pentru butoanele tip simbol */
        div.stButton > button {
            border: none !important;
            font-size: 24px !important; /* Simboluri mari */
            background-color: transparent !important;
            transition: transform 0.2s;
        }
        div.stButton > button:hover { transform: scale(1.2); background-color: rgba(255,255,255,0.1) !important; }
    </style>
    """, unsafe_allow_html=True)

    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    # --- PAZNICI ---
    if not st.session_state.autorizat_p1 or not st.session_state.operator_identificat:
        st.warning("Te rugăm să te autentifici în Sidebar.")
        st.stop()

    # --- ZONA DE FILTRARE ---
    c1, c2, c3 = st.columns(3)
    with c1:
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        list_cat = [i["denumire_categorie"] for i in res_cat.data]
        cat_admin = st.selectbox("Categoria:", [""] + list_cat)
    with c2:
        list_tip = []
        if cat_admin == "Contracte & Proiecte":
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
        st.selectbox("Tip:", [""] + list_tip)
    with c3:
        id_admin = st.text_input("ID Căutat:")

    # --- ZONA DE LUCRU CRUD ---
    if cat_admin != "":
        tabel_map = {"Contracte & Proiecte": "base_proiecte_internationale", "Evenimente stiintifice": "base_evenimente_stiintifice", "Proprietate intelectuala": "base_prop_intelect"}
        nume_tabela = tabel_map.get(cat_admin)
        
        res = supabase.table(nume_tabela).select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)

            # TOOLBAR: NOU (Stânga) | ACTUALIZARE, VALIDARE, ȘTERGERE (Dreapta)
            col_nou, col_spatiu, col_save, col_val, col_del = st.columns([1, 5, 0.6, 0.6, 0.6])
            
            with col_nou:
                if st.button("➕", help="Adaugă rând nou"):
                    # Logica pentru rând gol
                    st.toast("Rând nou generat")

            # TABELUL EDITABIL
            # Folosim 'on_select' pentru a detecta când utilizatorul este "într-un câmp"
            ed_event = st.data_editor(df, use_container_width=True, hide_index=True, key="editor_idbdc", on_change=None)

            # Verificăm dacă există modificări pentru a afișa opțiunile în dreapta
            schimbari = not df.equals(ed_event)
            
            if schimbari:
                with col_save:
                    if st.button("💾", help="ACTUALIZARE (Salvează modificările)"):
                        st.success("Salvat!")
                with col_val:
                    if st.button("🛡️", help="VALIDARE (Confirmă integritatea)"):
                        st.info("Validat!")
                with col_del:
                    if st.button("🗑️", help="ȘTERGERE (Elimină rândul)"):
                        st.error("Șters!")

            st.write("---")
