import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURARE ȘI STIL ---
def apply_custom_style():
    st.markdown("""
        <style>
            /* Fundal general cu un gradient discret */
            .stApp {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            }
            
            /* Stil pentru containerele de rezultate */
            div[data-testid="stExpander"], .stDataFrame {
                background-color: white !important;
                border-radius: 10px !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
            }

            /* Sidebar cu personalitate */
            [data-testid="stSidebar"] {
                background-color: #1e3a5f !important;
                color: white !important;
            }
            [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p {
                color: #ffcc00 !important; /* Accent galben pentru titluri */
            }

            /* Butoane vii */
            .stButton>button {
                background-color: #2ecc71 !important;
                color: white !important;
                border-radius: 20px !important;
                border: none !important;
                transition: all 0.3s ease;
                font-weight: bold;
            }
            .stButton>button:hover {
                background-color: #27ae60 !important;
                transform: scale(1.02);
            }

            /* Carduri de detalii */
            .detail-card {
                background-color: #ffffff;
                padding: 20px;
                border-left: 5px solid #3498db;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

PASSWORD = "EverDream2SZ"

BASE_TABLES = {
    "CEP": "base_contracte_cep",
    "TERTI": "base_contracte_terti",
    "FDI": "base_proiecte_fdi",
    "PNRR": "base_proiecte_pnrr",
    "INTERNATIONALE": "base_proiecte_internationale",
    "INTERREG": "base_proiecte_interreg",
    "NONEU": "base_proiecte_noneu",
    "PNCDI": "base_proiecte_pncdi",
}

def gate():
    if "auth_explorator" not in st.session_state:
        st.session_state.auth_explorator = False
    if not st.session_state.auth_explorator:
        _, col_mid, _ = st.columns([1, 2, 1])
        with col_mid:
            st.markdown("<h2 style='text-align: center; color: #1e3a5f;'>🛡️ Acces Explorator IDBDC</h2>", unsafe_allow_html=True)
            p = st.text_input("Introdu parola de acces:", type="password")
            if st.button("Deblochează"):
                if p == PASSWORD:
                    st.session_state.auth_explorator = True
                    st.rerun()
                else:
                    st.error("Parolă incorectă.")
        st.stop()

def run():
    apply_custom_style()
    gate()

    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.title("🔍 Explorator Date Cercetare (Varianta A)")
    
    # --- SIDEBAR FILTRE ---
    with st.sidebar:
        st.header("⚙️ Filtre Căutare")
        selected_types = st.multiselect("Tip Proiecte:", list(BASE_TABLES.keys()), default=list(BASE_TABLES.keys()))
        q_text = st.text_input("Căutare rapidă (Acronim/Titlu):", "").strip().casefold()
        
        st.markdown("---")
        if st.button("Resetare filtre"):
            st.rerun()

    # --- LOGICA DE FETCH ---
    all_data = []
    for t_key in selected_types:
        t_name = BASE_TABLES[t_key]
        try:
            res = supabase.table(t_name).select("*").execute()
            df_temp = pd.DataFrame(res.data)
            if not df_temp.empty:
                df_temp["_tip"] = t_key
                all_data.append(df_temp)
        except:
            continue

    if not all_data:
        st.warning("Niciun tip de proiect selectat sau date lipsă.")
        return

    df = pd.concat(all_data, ignore_index=True)

    # Filtrare locală rapidă
    if q_text:
        mask = df.apply(lambda row: q_text in str(row.values).lower(), axis=1)
        df = df[mask]

    # --- LAYOUT DOUĂ COLOANE ---
    left, right = st.columns([1.2, 1], gap="large")

    with left:
        st.subheader(f"📊 Rezultate ({len(df)})")
        show_cols = [c for c in ["cod_identificare", "_tip", "acronim_proiect", "titlu_proiect"] if c in df.columns]
        
        # Tabel interactiv
        st.dataframe(df[show_cols], use_container_width=True, height=500)
        
        selected_id = st.selectbox("Selectează un ID pentru detalii complete:", [""] + list(df["cod_identificare"].unique()))

    with right:
        st.subheader("📄 Detalii Înregistrare")
        if not selected_id:
            st.info("Alege un ID din stânga pentru a vedea detaliile.")
        else:
            match = df[df["cod_identificare"] == selected_id].iloc[0]
            
            with st.container():
                st.markdown(f"""
                <div class="detail-card">
                    <h3 style="color: #1e3a5f; margin-top:0;">{match.get('acronim_proiect', 'Fără Acronim')}</h3>
                    <p><b>Tip:</b> {match.get('_tip')}</p>
                    <p><b>ID Identificare:</b> {match.get('cod_identificare')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Afișare restul câmpurilor într-un mod curat
                for k, v in match.items():
                    if k not in ["_tip", "cod_identificare"] and pd.notnull(v):
                        st.write(f"**{k}:** {v}")

if __name__ == "__main__":
    run()
