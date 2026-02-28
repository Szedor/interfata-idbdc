import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- STILIZARE VIVIDĂ ---
def apply_custom_style():
    st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
            }
            .wizard-container {
                background-color: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            }
            div.stButton > button {
                border-radius: 20px;
                background-color: #4a90e2;
                color: white;
                border: none;
                font-weight: bold;
                padding: 0.5rem 1.5rem;
            }
            div.stButton > button:hover {
                background-color: #357abd;
            }
            h1, h2, h3 { color: #2c3e50 !important; }
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
            st.markdown("<h2 style='text-align: center;'>🛡️ Acces Securizat</h2>", unsafe_allow_html=True)
            p = st.text_input("Parola:", type="password")
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

    if "step" not in st.session_state:
        st.session_state.step = 1

    st.title("🧙‍♂️ Asistent Căutare (Wizard)")

    with st.container():
        # --- PASUL 1: Alegere tip ---
        if st.session_state.step == 1:
            st.subheader("Pasul 1: Ce căutăm?")
            st.info("Selectează categoriile pe care dorești să le explorezi.")
            selected_types = st.multiselect("Categorii:", list(BASE_TABLES.keys()), default=["FDI"])
            
            if st.button("Continuă →"):
                st.session_state.selected_types = selected_types
                st.session_state.step = 2
                st.rerun()

        # --- PASUL 2: Filtrare ---
        elif st.session_state.step == 2:
            st.subheader("Pasul 2: Filtrare")
            q_text = st.text_input("Cuvânt cheie (Acronim/Titlu):")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("← Înapoi"):
                    st.session_state.step = 1
                    st.rerun()
            with c2:
                if st.button("Caută Rezultate →"):
                    st.session_state.q_text = q_text
                    st.session_state.step = 3
                    st.rerun()

        # --- PASUL 3: Rezultate ---
        elif st.session_state.step == 3:
            st.subheader("Pasul 3: Rezultate")
            
            # Fetch date
            all_data = []
            for t_key in st.session_state.selected_types:
                res = supabase.table(BASE_TABLES[t_key]).select("*").execute()
                df_temp = pd.DataFrame(res.data)
                if not df_temp.empty:
                    df_temp["_tip"] = t_key
                    all_data.append(df_temp)
            
            df = pd.concat(all_data, ignore_index=True)
            
            # Filtrare locală
            if st.session_state.get("q_text"):
                t = st.session_state.q_text.casefold()
                mask = df.apply(lambda row: t in str(row.values).lower(), axis=1)
                df = df[mask]

            st.write(f"Am găsit {len(df)} înregistrări.")
            st.dataframe(df, use_container_width=True)

            if st.button("Restart Wizard"):
                st.session_state.step = 1
                st.rerun()

if __name__ == "__main__":
    run()
