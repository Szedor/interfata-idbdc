import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURARE STIL VIZU ---
def apply_wizard_style():
    st.markdown("""
        <style>
            /* Fundal cu gradient de calmare */
            .stApp {
                background: linear-gradient(to right, #ece9e6, #ffffff);
            }
            
            /* Stil pentru pașii procesului */
            .step-header {
                padding: 15px;
                border-radius: 50px;
                text-align: center;
                font-weight: bold;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            .step-1 { background-color: #3498db; color: white; }
            .step-2 { background-color: #f39c12; color: white; }
            .step-3 { background-color: #27ae60; color: white; }

            /* Carduri pentru input */
            .stTextInput, .stMultiSelect, .stSelectbox {
                background-color: white;
                padding: 10px;
                border-radius: 15px;
            }

            /* Butoane de navigare */
            .stButton>button {
                width: 100%;
                border-radius: 12px !important;
                height: 3em;
                font-size: 18px !important;
                text-transform: uppercase;
                letter-spacing: 1px;
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
        _, col_mid, _ = st.columns([1, 1.5, 1])
        with col_mid:
            st.markdown("<h2 style='text-align: center; color: #2c3e50;'>🔑 Autentificare Asistent</h2>", unsafe_allow_html=True)
            p = st.text_input("Parola de acces:", type="password")
            if st.button("Lansează Asistentul"):
                if p == PASSWORD:
                    st.session_state.auth_explorator = True
                    st.rerun()
                else:
                    st.error("Acces refuzat.")
        st.stop()

def run():
    apply_wizard_style()
    gate()

    # Inițializare pas
    if "step" not in st.session_state:
        st.session_state.step = 1

    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.title("🧙‍♂️ Asistent Căutare Proiecte")

    # --- PASUL 1: SELECȚIE CATEGORII ---
    if st.session_state.step == 1:
        st.markdown('<div class="step-header step-1">PASUL 1: Ce tip de proiecte cauți?</div>', unsafe_allow_html=True)
        
        st.info("Alege una sau mai multe categorii de proiecte pentru a începe scanarea bazei de date.")
        selected = st.multiselect("Categorii disponibile:", list(BASE_TABLES.keys()), default=["FDI", "PNRR"])
        
        st.markdown("---")
        if st.button("Continuă spre Filtre ➡️"):
            if not selected:
                st.warning("Te rog selectează cel puțin o categorie.")
            else:
                st.session_state.selected_types = selected
                st.session_state.step = 2
                st.rerun()

    # --- PASUL 2: FILTRE ȘI INDICII ---
    elif st.session_state.step == 2:
        st.markdown('<div class="step-header step-2">PASUL 2: Definește indicii de căutare</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            q_id = st.text_input("Cod Identificare (exact):", help="Ex: UPT-2024-XXX")
            q_acro = st.text_input("Acronim sau Cuvânt cheie titlu:")
        with col2:
            q_an = st.number_input("An implementare (0 pentru toți):", min_value=0, max_value=2030, value=0)
            q_status = st.selectbox("Status proiect:", ["Toate", "In derulare", "Finalizat", "In evaluare"])

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Înapoi la Categorii"):
                st.session_state.step = 1
                st.rerun()
        with c2:
            if st.button("Vezi Rezultatele 🔍"):
                st.session_state.filters = {"id": q_id, "text": q_acro, "an": q_an, "status": q_status}
                st.session_state.step = 3
                st.rerun()

    # --- PASUL 3: REZULTATE ȘI DETALII ---
    elif st.session_state.step == 3:
        st.markdown('<div class="step-header step-3">PASUL 3: Rezultate Găsite</div>', unsafe_allow_html=True)
        
        # Logica de fetch bazată pe pașii anteriori
        all_data = []
        for t_key in st.session_state.selected_types:
            t_name = BASE_TABLES[t_key]
            res = supabase.table(t_name).select("*").execute()
            temp_df = pd.DataFrame(res.data)
            if not temp_df.empty:
                temp_df["_tip"] = t_key
                all_data.append(temp_df)

        if not all_data:
            st.error("Nu am găsit date conform selecției.")
            if st.button("Resetează"): st.session_state.step = 1; st.rerun()
            return

        df = pd.concat(all_data, ignore_index=True)
        
        # Aplicare filtre din pasul 2
        f = st.session_state.filters
        if f["id"]:
            df = df[df["cod_identificare"].astype(str).str.contains(f["id"], case=False)]
        if f["text"]:
            df = df[df.apply(lambda r: f["text"].lower() in str(r.values).lower(), axis=1)]

        st.success(f"Am găsit {len(df)} proiecte care corespund criteriilor tale.")
        
        # Afișare rezultate sub formă de tabel curat
        st.dataframe(df[["cod_identificare", "_tip", "acronim_proiect", "titlu_proiect"]], use_container_width=True)

        if st.button("🔄 Începe o căutare nouă"):
            st.session_state.step = 1
            st.rerun()

if __name__ == "__main__":
    run()
