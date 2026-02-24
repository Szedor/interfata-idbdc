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
        .stDataEditor { background-color: white !important; border-radius: 5px; }
        div.stButton > button { height: 35px; font-size: 12px !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    # --- ACCES ---
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
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    if not st.session_state.operator_identificat:
        st.sidebar.markdown("### 👤 Autentificare")
        cod_in = st.sidebar.text_input("Cod Operator", type="password", key="p2_cod")
        if cod_in:
            res_op = supabase.table("com_operatori").select("nume_prenume").eq("cod_operatori", cod_in).execute()
            if res_op.data:
                st.session_state.operator_identificat = res_op.data[0]['nume_prenume']
                st.rerun()
        st.stop()

    # --- FILTRE ---
    st.markdown(f"<h4> 🛠️ Administrare: {st.session_state.operator_identificat}</h4>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        list_cat = [i["denumire_categorie"] for i in res_cat.data]
        cat_admin = st.selectbox("Categoria:", [""] + list_cat, key="admin_cat")
    with c2:
        list_tip = []
        if cat_admin == "Contracte & Proiecte":
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            list_tip = [i["acronim_contracte_proiecte"] for i in res_tip.data]
        tip_admin = st.selectbox("Tip:", [""] + list_tip, key="admin_tip")
    with c3:
        id_admin = st.text_input("ID / Contract:", key="admin_id")

    # --- TABEL EDITABIL SI LOGICA UPDATE ---
    if cat_admin != "":
        tabel_map = {"Contracte & Proiecte": "base_proiecte_internationale", "Evenimente stiintifice": "base_evenimente_stiintifice", "Proprietate intelectuala": "base_prop_intelect"}
        nume_tabela = tabel_map.get(cat_admin)
        
        if nume_tabela:
            query = supabase.table(nume_tabela).select("*")
            if tip_admin: query = query.eq("acronim_contracte_proiecte", tip_admin)
            if id_admin: query = query.eq("cod_identificare", id_admin)
            res = query.execute()
            
            if res.data:
                df = pd.DataFrame(res.data)
                
                # Configurare coloane (ID blocat pentru siguranta)
                config = {"cod_identificare": st.column_config.TextColumn("ID", disabled=True)}
                
                st.write("")
                col_txt, b1, b2, b3 = st.columns([6, 1.2, 1.2, 1.2])
                with col_txt: st.markdown(f"📊 **{nume_tabela}**")

                edited_df = st.data_editor(df, use_container_width=True, hide_index=True, column_config=config, key="ed_v4")

                # VERIFICARE SCHIMBARI
                if not df.equals(edited_df):
                    with b1:
                        if st.button("🔄 ACTUALIZARE", use_container_width=True):
                            # LOGICA UPDATE: Identificăm rândul modificat
                            diff = edited_df[df != edited_df].dropna(how='all')
                            for idx in diff.index:
                                row_data = edited_df.loc[idx].to_dict()
                                # Trimitem în DB folosind cod_identificare ca ancoră
                                supabase.table(nume_tabela).update(row_data).eq("cod_identificare", row_data["cod_identificare"]).execute()
                            st.success("Modificările au fost salvate în Supabase!")
                            st.rerun()
                    with b2:
                        if st.button("✅ VALIDARE", use_container_width=True):
                            st.toast("Înregistrare validată conform protocolului.")
                    with b3:
                        if st.button("🗑️ ȘTERGERE", use_container_width=True):
                            st.warning("Confirmarea ștergerii este necesară.")
            else:
                st.info("Niciun rezultat.")

if __name__ == "__main__":
    run()
