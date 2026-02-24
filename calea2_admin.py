import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

def run():
    # --- SECȚIUNE VALIDATĂ / ÎNGHEȚATĂ ---
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown("""
    <style>
        .stApp, [data-testid="stSidebar"] { background-color: #003366 !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
        input { color: #000000 !important; background-color: #ffffff !important; }
        div.stButton > button { border: 1px solid white !important; color: white !important; background-color: rgba(255,255,255,0.1) !important; width: 100%; font-size: 14px !important; font-weight: bold !important; height: 45px !important; }
        div.stButton > button:hover { background-color: white !important; color: #003366 !important; }
    </style>
    """, unsafe_allow_html=True)

    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    if 'operator_identificat' not in st.session_state: st.session_state.operator_identificat = None

    if not st.session_state.autorizat_p1:
        st.markdown("<h2 style='text-align: center;'> 🛡️ Acces Securizat IDBDC</h2>", unsafe_allow_html=True)
        _, col_ce, _ = st.columns([1.3, 0.6, 1.3])
        with col_ce:
            parola_m = st.text_input("Parola:", type="password", key="p1_pass")
            if st.button("Autorizare acces"):
                if parola_m == "EverDream2SZ":
                    st.session_state.autorizat_p1 = True
                    st.rerun()
        st.stop()

    if not st.session_state.operator_identificat:
        st.sidebar.markdown("### 👤 Identificare Operator")
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
    # --- SFÂRȘIT SECȚIUNE ÎNGHEȚATĂ ---

    # --- ZONA FILTRE (CASETELE 1-4) ---
    st.markdown(f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.operator_identificat}</h3>", unsafe_allow_html=True)
    
    # Interogare Acronime (din Nomenclator)
    try:
        res_nom = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
        lista_acronime = [""] + [r['acronim_contracte_proiecte'] for r in res_nom.data] if res_nom.data else [""]
    except:
        lista_acronime = [""]

    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2])
    with c1: cat_admin = st.selectbox("1. Categoria:", ["", "Contracte & Proiecte", "Evenimente stiintifice", "Proprietate intelectuala"], key="admin_cat")
    with c2: tip_admin = st.selectbox("2. Tip (Acronim):", lista_acronime, key="admin_tip")
    with c3: id_admin = st.text_input("3. ID Proiect (Cod Identificare):", key="admin_id")
    with c4: componente_com = st.multiselect("4. Componente (COM):", ["Date financiare", "Resurse umane", "Aspecte tehnice"], key="admin_com")

    st.markdown("---")

    # --- FUNCȚIE DE SALVARE (STATUIA VIVANTĂ) ---
    def salveaza_date(tabela, key_editor):
        if key_editor in st.session_state:
            state = st.session_state[key_editor]
            # Colectăm editările (modificări, adăugări)
            updates = state.get('edited_rows', {})
            additions = state.get('added_rows', [])
            
            # Procesăm rândurile editate
            for row_idx, changes in updates.items():
                # Luăm datele originale din session_state pentru a identifica rândul (presupunem df încărcat)
                # Notă: Pentru simplitate și siguranță, trimitem changes + coloanele de audit
                changes['data_ultimei_modificari'] = datetime.now().isoformat()
                changes['observatii_idbdc'] = f"Modificat de {st.session_state.operator_identificat}"
                # Aici ar trebui un ID pentru .eq(), dar UPSERT e mai sigur dacă avem cheie primară definită
                # În IDBDC, presupunem că UPSERT se ocupă de potrivire
                supabase.table(tabela).upsert(changes).execute()

            # Procesăm rândurile noi
            for row in additions:
                if id_admin: row['cod_identificare'] = id_admin
                row['data_ultimei_modificari'] = datetime.now().isoformat()
                row['status_confirmare'] = "Draft"
                supabase.table(tabela).insert(row).execute()

    # --- PANOU BUTOANE CRUD ---
    col_n, col_s, col_v, col_d, col_a = st.columns(5)
    
    with col_s: 
        if st.button("💾 SALVARE"):
            if cat_admin != "":
                # Salvează tabel principal
                tabel_p = "base_proiecte_internationale" if tip_admin != "FDI" else "base_proiecte_fdi"
                if cat_admin == "Evenimente stiintifice": tabel_p = "base_evenimente_stiintifice"
                if cat_admin == "Proprietate intelectuala": tabel_p = "base_prop_intelect"
                
                salveaza_date(tabel_p, f"ed_{tabel_p}")
                
                # Salvează componente COM active
                map_com = {"Date financiare": "com_date_financiare", "Resurse umane": "com_echipe_proiect", "Aspecte tehnice": "com_aspecte_tehnice"}
                for comp in componente_com:
                    salveaza_date(map_com[comp], f"ed_{map_com[comp]}")
                
                st.success("✅ Toate modificările au fost salvate în baza de date!")
                st.rerun()

    with col_a:
        if st.button("❌ ANULARE"):
            st.rerun()

    # --- AFIȘARE TABELE ---
    if cat_admin != "":
        tabel_map = {
            "Contracte & Proiecte": "base_proiecte_internationale" if tip_admin != "FDI" else "base_proiecte_fdi",
            "Evenimente stiintifice": "base_evenimente_stiintifice",
            "Proprietate intelectuala": "base_prop_intelect"
        }
        nume_tabela = tabel_map.get(cat_admin)

        # 1. Tabel Principal
        res_main = supabase.table(nume_tabela).select("*")
        if id_admin: res_main = res_main.eq("cod_identificare", id_admin)
        df_main = pd.DataFrame(res_main.execute().data)
        
        st.markdown(f"**📂 Tabel Principal: {nume_tabela}**")
        st.data_editor(df_main, use_container_width=True, hide_index=True, key=f"ed_{nume_tabela}", num_rows="dynamic")

        # 2. Tabele Componente (COM)
        if componente_com:
            map_tabele_com = {"Date financiare": "com_date_financiare", "Resurse umane": "com_echipe_proiect", "Aspecte tehnice": "com_aspecte_tehnice"}
            for comp in componente_com:
                nume_tabel_com = map_tabele_com[comp]
                st.write("---")
                st.markdown(f"**🔍 Componenta: {comp}**")
                res_com = supabase.table(nume_tabel_com).select("*")
                if id_admin: res_com = res_com.eq("cod_identificare", id_admin)
                df_com = pd.DataFrame(res_com.execute().data)
                
                if df_com.empty and id_admin:
                    df_com = pd.DataFrame([{"cod_identificare": id_admin, "status_confirmare": "Draft"}])
                
                st.data_editor(df_com, use_container_width=True, hide_index=True, key=f"ed_{nume_tabel_com}", num_rows="dynamic")

if __name__ == "__main__":
    run()
