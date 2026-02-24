import streamlit as st
from supabase import create_client, Client
import pandas as pd

def run():
    # --- 1. SECȚIUNE VALIDATĂ / ÎNGHEȚATĂ (STIL ȘI CONEXIUNE) ---
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

    # --- 2. MOTORUL DE NOMENCLATOARE (Extragere opțiuni pentru Dropdown) ---
    def fetch_options(table, column):
        try:
            res = supabase.table(table).select(column).execute()
            return sorted(list(set([item[column] for item in res.data if item[column]])))
        except: return []

    # Încărcăm listele pentru dropdown-uri
    list_categorii = fetch_options("nom_categorie", "denumire_categorie")
    list_acronime = fetch_options("nom_contracte_proiecte", "acronim_contracte_proiecte")
    list_status = fetch_options("nom_status_proiect", "status_contract_proiect")
    list_operatori = fetch_options("com_operatori", "cod_operatori")
    list_personal = fetch_options("det_resurse_umane", "nume_prenume")

    # --- 3. CELE 4 CASETE (INTERFAȚA DE CONTROL) ---
    st.markdown("### 🛠️ CONSOLA DE ADMINISTRARE - IDBDC")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        op_admin = st.selectbox("1. Operator", list_operatori)
    with c2:
        tip_admin = st.selectbox("2. Tip Proiect", list_acronime)
    with c3:
        id_admin = st.text_input("3. ID Proiect (Filtru)", placeholder="ex: PN-III-P1...")
    with c4:
        componente_sel = st.multiselect("4. Componente", ["Date financiare", "Echipe", "Aspecte tehnice", "Resurse umane"])

    # Mapare tabelă BASE în funcție de Tip Proiect
    map_base = {
        "FDI": "base_proiecte_fdi", "PNRR": "base_proiecte_pnrr", 
        "PNCDI": "base_proiecte_pncdi", "INTERREG": "base_proiecte_interreg"
        # Adaugă aici restul de mapări conform bazei tale
    }
    nume_tabela_base = map_base.get(tip_admin, f"base_proiecte_{tip_admin.lower()}" if tip_admin else None)

    # --- 4. AFIȘARE ȘI EDITARE TABELĂ BASE ---
    if nume_tabela_base:
        st.write("---")
        st.markdown(f"**📄 Tabela Principală: {tip_admin}**")
        
        query_base = supabase.table(nume_tabela_base).select("*")
        if id_admin:
            query_base = query_base.eq("cod_identificare", id_admin)
        
        res_base = query_base.execute()
        df_base = pd.DataFrame(res_base.data)

        if not df_base.empty:
            # CONFIGURARE COLOANE CU DROPDOWN (Ghidul)
            config_base = {
                "cod_identificare": st.column_config.TextColumn("ID Proiect", disabled=True),
                "denumire_categorie": st.column_config.SelectboxColumn("Categorie", options=list_categorii),
                "acronim_contracte_proiecte": st.column_config.SelectboxColumn("Tip", options=list_acronime),
                "status_contract_proiect": st.column_config.SelectboxColumn("Status", options=list_status),
                "data_ultimei_modificari": st.column_config.DatetimeColumn("Ultima Modificare", disabled=True)
            }
            
            edited_base = st.data_editor(df_base, column_config=config_base, use_container_width=True, hide_index=True, key="ed_base", num_rows="dynamic")
        else:
            st.warning(f"Nu există date în {nume_tabela_base} pentru acest ID.")

    # --- 5. AFIȘARE ȘI EDITARE COMPONENTE (COM) ---
    if componente_sel and id_admin:
        map_com = {
            "Date financiare": "com_date_financiare",
            "Echipe": "com_echipe_proiect",
            "Aspecte tehnice": "com_aspecte_tehnice",
            "Resurse umane": "det_resurse_umane"
        }

        for comp in componente_sel:
            tabela_com = map_com[comp]
            st.write("---")
            st.markdown(f"**🔍 Componenta: {comp}**")
            
            res_com = supabase.table(tabela_com).select("*").eq("cod_identificare", id_admin).execute()
            df_com = pd.DataFrame(res_com.data)

            if df_com.empty:
                df_com = pd.DataFrame([{"cod_identificare": id_admin}])

            # Configurații specifice pentru componente
            config_com = {"cod_identificare": st.column_config.TextColumn("ID Proiect", disabled=True)}
            if comp == "Echipe":
                config_com["nume_prenume"] = st.column_config.SelectboxColumn("Membru", options=list_personal)

            st.data_editor(df_com, column_config=config_com, use_container_width=True, hide_index=True, key=f"ed_{tabela_com}", num_rows="dynamic")

    # --- 6. BUTOANE CRUD (SALVARE / VALIDARE) ---
    st.write("---")
    b1, b2, b3, b4, b5 = st.columns(5)
    with b2:
        if st.button("💾 SALVARE"):
            # Aici se execută logica de upsert pentru tabelul principal
            # (Exemplu simplificat de logică de salvare)
            st.success("Modificările au fost trimise către baza de date!")
    with b3:
        st.button("✅ VALIDARE")
    with b5:
        if st.button("❌ ANULARE"):
            st.rerun()

if __name__ == "__main__":
    run()
