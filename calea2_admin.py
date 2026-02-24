import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    # 1. CONEXIUNE
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    # 2. STILIZARE (Iconițe mari și culori IDBDC)
    st.markdown("""
    <style>
        .stApp { background-color: #003366 !important; }
        .stDataEditor { background-color: white !important; border-radius: 5px; }
        /* Simboluri mari și expresive */
        div.stButton > button {
            border: none !important;
            font-size: 30px !important; 
            background-color: transparent !important;
        }
        div.stButton > button:hover { transform: scale(1.3); }
    </style>
    """, unsafe_allow_html=True)

    # 3. GESTIUNE SESIUNE
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    # --- POARTA 1: PAROLA ---
    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center; color: white;'>🛡️ Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1, 1, 1])
        with col_ce:
            parola_m = st.text_input("Introdu Parola Generală:", type="password")
            if st.button("AUTORIZARE"):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
        st.stop()

    # --- POARTA 2: OPERATOR (În Sidebar) ---
    if not st.session_state.operator_identificat:
        st.sidebar.markdown("### 👤 Identificare Operator")
        cod_in = st.sidebar.text_input("Cod Operator:", type="password")
        if cod_in:
            res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_in).execute()
            if res_op.data:
                st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                st.rerun()
        st.stop()

    # --- ZONA DE LUCRU ---
    st.markdown(f"#### 🛠️ Consola Admin: {st.session_state.operator_identificat}", unsafe_allow_html=True)
    
    # Filtre orizontale
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
        tip_admin = st.selectbox("Tip:", [""] + list_tip)
    with c3:
        id_admin = st.text_input("Căutare ID/Contract:")

    # --- CRUD CU SIMBOLURI MARI ---
    if cat_admin != "":
        tabel_map = {"Contracte & Proiecte": "base_proiecte_internationale", "Evenimente stiintifice": "base_evenimente_stiintifice", "Proprietate intelectuala": "base_prop_intelect"}
        nume_tabela = tabel_map.get(cat_admin)
        
        query = supabase.table(nume_tabela).select("*")
        if tip_admin: query = query.eq("acronim_contracte_proiecte", tip_admin)
        if id_admin: query = query.eq("cod_identificare", id_admin)
        res = query.execute()

        if res.data:
            df = pd.DataFrame(res.data)
            
            # TOOLBAR SUPERIOR CU SIMBOLURI
            col_nou, col_spatiu, col_save, col_val, col_del = st.columns([1, 4, 1, 1, 1])
            
            with col_nou:
                if st.button("➕", help="NOU - Adaugă rând gol"):
                    st.toast("Funcția NOU va fi activată la următorul pas.")

            # Tabelul editabil
            edited_df = st.data_editor(df, use_container_width=True, hide_index=True, key="ed_final")

            # Detectare modificări pentru afișarea iconițelor în dreapta
            if not df.equals(edited_df):
                with col_save:
                    if st.button("💾", help="ACTUALIZARE (Salvează în DB)"):
                        st.success("Salvat!")
                with col_val:
                    if st.button("🛡️", help="VALIDARE (Confirmă datele)"):
                        st.balloons()
                with col_del:
                    if st.button("🗑️", help="ȘTERGERE (Elimină definitiv)"):
                        st.warning("Sigur ștergeți?")

if __name__ == "__main__":
    run()
