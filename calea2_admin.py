import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    # CSS pentru simboluri mari, expresive și aliniere precisă
    st.markdown("""
    <style>
        .stApp { background-color: #003366 !important; }
        .stDataEditor { background-color: white !important; border-radius: 5px; }
        /* Butoane tip simboluri universale mari */
        div.stButton > button {
            border: none !important;
            font-size: 35px !important; 
            background-color: transparent !important;
            padding: 0px !important;
            line-height: 1 !important;
        }
        div.stButton > button:hover { transform: scale(1.2); color: #ffaa00 !important; }
    </style>
    """, unsafe_allow_html=True)

    # --- LOGICA DE ACCES (Sesiune) ---
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    # POARTA 1 & 2 (Păstrate pentru securitate conform IDBDC)
    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center; color: white;'>🛡️ Acces Securizat</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1, 1, 1])
        with col_ce:
            p_in = st.text_input("Parola:", type="password")
            if st.button("OK"):
                if p_in == "EverDream2SZ": 
                    st.session_state.autorizat_p1 = True
                    st.rerun()
        st.stop()

    if not st.session_state.operator_identificat:
        cod_op = st.sidebar.text_input("Cod Operator:", type="password")
        if cod_op:
            res = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_op).execute()
            if res.data:
                st.session_state.operator_identificat = res.data[0]['nume_prenume']
                st.rerun()
        st.stop()

    # --- INTERFAȚA DE LUCRU ---
    st.markdown(f"#### 🛠️ {st.session_state.operator_identificat}")
    
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
        id_admin = st.text_input("ID Căutat:")

    if cat_admin != "":
        tabel_map = {"Contracte & Proiecte": "base_proiecte_internationale", "Evenimente stiintifice": "base_evenimente_stiintifice", "Proprietate intelectuala": "base_prop_intelect"}
        nume_tabela = tabel_map.get(cat_admin)
        
        # Preluare date
        res = supabase.table(nume_tabela).select("*").execute()
        df = pd.DataFrame(res.data)

        # ---------------------------------------------------------
        # ZONA CRUD (NOU în stânga, RESTUL în dreapta)
        # ---------------------------------------------------------
        col_stanga, col_spatiu, col_d1, col_d2, col_d3 = st.columns([1, 6, 1, 1, 1])
        
        with col_stanga:
            if st.button("➕", help="Adaugă înregistrare nouă"):
                st.toast("Se generează un rând gol...")

        # TABELUL (Data Editor)
        # Folosim selectia de rand pentru a activa instantaneu butoanele din dreapta
        edit_event = st.data_editor(
            df, 
            use_container_width=True, 
            hide_index=True, 
            key="idbdc_editor",
            on_select="rerun", # Aceasta este cheia: la orice click, reincarcam pentru butoane
            selection_mode="single-row"
        )

        # ACTIVARE BUTOANE DREAPTA
        # Apar dacă un rând este selectat SAU dacă tabelul a fost modificat
        este_selectat = len(edit_event.selection.rows) > 0
        este_modificat = not df.equals(edit_event)

        if este_selectat or este_modificat:
            with col_d1:
                if st.button("💾", help="ACTUALIZARE"):
                    st.success("Salvat!")
            with col_d2:
                if st.button("🛡️", help="VALIDARE"):
                    st.info("Validat!")
            with col_d3:
                if st.button("🗑️", help="ȘTERGERE"):
                    st.error("Eliminat!")

if __name__ == "__main__":
    run()
