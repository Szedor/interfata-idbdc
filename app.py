import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 1. CONFIGURARE & STIL (ÎNGHEȚAT CONFORM CERINȚEI)
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="centered")

# Stil special pentru bannerul de eroare roșu și textul centrat
st.markdown("""
<style>
    .eroare-idbdc {
        color: white; 
        background-color: #FF4B4B; 
        padding: 12px; 
        border-radius: 8px;
        text-align: center; 
        font-weight: bold; 
        width: 100%; 
        display: block; 
        margin-top: 10px;
    }
    .text-centrat {
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Gestionarea stării sesiunii
if 'autorizat_p1' not in st.session_state:
    st.session_state.autorizat_p1 = False

# ==========================================
# 2. ANTET (PROTOCOL IDBDC)
# ==========================================
st.markdown("<h1 style='text-align: center;'>🛡️</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Sistemul de Gestiune IDBDC</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Universitatea Politehnica Timișoara</p>", unsafe_allow_html=True)
st.write("---")

# ==========================================
# 3. LOGICA DE AUTORIZARE ȘI CONECTARE
# ==========================================
if not st.session_state.autorizat_p1:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        # Eticheta deasupra casetei
        st.write("Parola pentru autorizare acces")
        
        # Caseta de introducere (fără sugestii browser)
        parola_introdusa = st.text_input(
            "Parola", 
            type="password", 
            label_visibility="collapsed",
            autocomplete="new-password",
            key="p1_pass"
        )
        
        # Butonul de validare
        if st.button("Autorizare acces", use_container_width=True):
            if parola_introdusa == "EverDream2SZ":
                st.session_state.autorizat_p1 = True
                st.rerun()
            else:
                # Mesaj de eroare roșu, vizual puternic
                st.markdown(
                    "<div class='eroare-idbdc'>"
                    "⚠️ Acces Neautorizat: Parola nu corespunde sistemului IDBDC."
                    "</div>", 
                    unsafe_allow_html=True
                )
else:
    # --- INTERFAȚA DUPĂ AUTORIZARE ---
    st.success("✅ Acces Autorizat. Bun venit în sistemul IDBDC.")
    
    # Conectare la Supabase prin API (Port 443)
    try:
        url: str = st.secrets["SUPABASE_URL"]
        key: str = st.secrets["SUPABASE_KEY"]
        supabase: Client = create_client(url, key)
        
        # Interogare tabel base_proiecte_fdi
        response = supabase.table("base_proiecte_fdi").select("*").execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            st.write("### 📂 Date Proiecte FDI")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Conexiunea a reușit, dar tabelul nu conține date.")
            
    except Exception as e:
        st.error(f"Eroare tehnică la conectare: {e}")

    # Buton resetare la final
    st.write("---")
    if st.button("Resetare Sesiune"):
        st.session_state.autorizat_p1 = False
        st.rerun()
