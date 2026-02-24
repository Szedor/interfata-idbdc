import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
        input { color: #000000 !important; background-color: #ffffff !important; }
        .stDataFrame { background-color: white !important; border-radius: 5px; }
        /* Culori butoane conform protocolului tau */
        div.stButton > button:first-child { border-radius: 8px; font-weight: bold; }
        .st-emotion-cache-v3d49u { background-color: #28a745 !important; color: white !important; } /* NOU - Verde */
        .st-emotion-cache-17l7p0x { background-color: #fd7e14 !important; color: white !important; } /* EDIT - Portocaliu */
    </style>
    """, unsafe_allow_html=True)

    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None
    if 'edit_mode' not in st.session_state: st.session_state.edit_mode = False

    if not st.session_state.autorizat_p1:
        st.markdown('<div style="background-color: #1a4a7a; padding: 40px; border-radius: 15px;">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'> 🛡️ Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola:", type="password", key="p1_pass")
            if st.button("Autorizare acces", use_container_width=True):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
                else:
                    st.error("Parolă incorectă.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    st.sidebar.markdown("### 👤 Autentificare")
    if not st.session_state.operator_identificat:
        cod_in = st.sidebar.text_input("Cod Identificare", type="password", key="p2_cod_input")
        if cod_in:
            res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_in).execute()
            if res_op.data:
                st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                st.rerun()
        st.stop()
    else:
        st.sidebar.success(f"Operator: {st.session_state.operator_identificat}")
        if st.sidebar.button("Ieșire / Resetare"):
            st.session_state.clear()
            st.rerun()

    st.markdown(f"<h3 style='text-align: center;'> 🛠️ Administrare: {st.session_state.operator_identificat}</h3>", unsafe_allow_html=True)
    st.write("---")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        try:
            res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
            list_cat = [i["denumire_categorie"] for i in res_cat.data]
        except:
            list_cat = ["Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"]
        cat_admin = st.selectbox("Categoria de informatii:", [""] + list_cat, key="admin_cat")
    with c2:
        list_tip = []
        if cat_admin == "Contracte & Proiecte":
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
        tip_admin = st.selectbox("Tip de contract / proiect:", [""] + list_tip, key="admin_tip")
    with c3:
        id_admin = st.text_input("ID proiect / Numar de contract:", key="admin_id")

    if cat_admin != "":
        st.write("---")
        
        # 1. TOOLBAR CU 2 ICONITE
        col_t1, col_t2, _ = st.columns([1, 1, 5])
        with col_t1:
            st.button("➕ NOU", use_container_width=True, help="Adaugă înregistrare nouă")
        
        with col_t2:
            # Editarea se activează DOAR dacă există selecție în tabel sau în Caseta 3
            edit_disabled = True
            if 'proiect_selectat' in st.session_state and st.session_state.proiect_selectat is not None:
                edit_disabled = False
            
            if st.button("📝 EDITARE", use_container_width=True, disabled=edit_disabled, help="Modifică proiectul selectat"):
                st.session_state.edit_mode = True

        # 2. TABELA SI SELECTIE
        tabel_map = {"Contracte & Proiecte": "base_proiecte_internationale", "Evenimente stiintifice": "base_evenimente_stiintifice", "Proprietate intelectuala": "base_prop_intelect"}
        nume_tabela = tabel_map.get(cat_admin)
        
        if nume_tabela:
            query = supabase.table(nume_tabela).select("*")
            if tip_admin: query = query.eq("acronim_contracte_proiecte", tip_admin)
            if id_admin: query = query.eq("cod_identificare", id_admin)
            
            res = query.execute()
            if res.data:
                df = pd.DataFrame(res.data)
                
                # Interfață de selecție
                select_event = st.dataframe(
                    df, 
                    use_container_width=True, 
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row"
                )

                # Procesare selecție
