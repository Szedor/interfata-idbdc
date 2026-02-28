import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURARE STIL VIZUAL ---
def apply_card_style():
    st.markdown("""
        <style>
            .stApp {
                background-color: #f0f2f6;
            }
            
            /* Stil pentru expandere (carduri) */
            .stExpander {
                border: none !important;
                background-color: white !important;
                border-radius: 12px !important;
                margin-bottom: 15px !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
                transition: transform 0.2s ease;
            }
            .stExpander:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 15px rgba(0,0,0,0.1) !important;
            }

            /* Badge-uri colorate pentru tipul de proiect */
            .badge {
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                color: white;
                margin-left: 10px;
            }
            .bg-fdi { background-color: #e67e22; }
            .bg-pnrr { background-color: #9b59b6; }
            .bg-cep { background-color: #3498db; }
            .bg-default { background-color: #7f8c8d; }

            /* Titluri secțiuni */
            h1, h2 { color: #2c3e50 !important; }
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

def get_badge_class(tip):
    mapping = {"FDI": "bg-fdi", "PNRR": "bg-pnrr", "CEP": "bg-cep"}
    return mapping.get(tip, "bg-default")

def gate():
    if "auth_explorator" not in st.session_state:
        st.session_state.auth_explorator = False
    if not st.session_state.auth_explorator:
        _, col_mid, _ = st.columns([1, 1.5, 1])
        with col_mid:
            st.markdown("<h2 style='text-align: center;'>🗂️ Arhivă Proiecte IDBDC</h2>", unsafe_allow_html=True)
            p = st.text_input("Parola de acces:", type="password")
            if st.button("Accesează Cardurile"):
                if p == PASSWORD:
                    st.session_state.auth_explorator = True
                    st.rerun()
                else:
                    st.error("Acces neautorizat.")
        st.stop()

def run():
    apply_card_style()
    gate()

    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.title("🗂️ Explorator tip Carduri (Varianta C)")

    # --- FILTRARE RAPIDĂ ---
    col1, col2 = st.columns([2, 1])
    with col1:
        q_text = st.text_input("Caută după acronim, titlu sau cod:", placeholder="Ex: UPT-2024...")
    with col2:
        selected_types = st.multiselect("Filtru Tip:", list(BASE_TABLES.keys()), default=["FDI", "PNRR", "CEP"])

    # --- FETCH ȘI AFIȘARE ---
    rows_all = []
    for t_key in selected_types:
        try:
            res = supabase.table(BASE_TABLES[t_key]).select("*").execute()
            for r in (res.data or []):
                r["_tip"] = t_key
                rows_all.append(r)
        except: continue

    if q_text:
        rows_all = [r for r in rows_all if q_text.lower() in str(list(r.values())).lower()]

    st.write(f"S-au găsit **{len(rows_all)}** înregistrări.")

    for r in rows_all:
        cod = r.get("cod_identificare", "N/A")
        tip = r.get("_tip", "ALT")
        # Alegem un titlu reprezentativ
        titlu = r.get("acronim_proiect") or r.get("titlu_proiect") or r.get("obiect_contract") or "Fără titlu"
        
        badge_cls = get_badge_class(tip)
        
        # Header personalizat pentru fiecare card
        header_html = f"🆔 {cod} | {titlu}"
        
        with st.expander(header_html):
            st.markdown(f"**Tip Proiect:** <span class='badge {badge_cls}'>{tip}</span>", unsafe_allow_html=True)
            st.markdown("---")
            
            # Afișare date în coloane pentru claritate
            c1, c2 = st.columns(2)
            cols = [k for k in r.keys() if not k.startswith("_")]
            mid = len(cols) // 2
            
            with c1:
                for k in cols[:mid]:
                    if r[k]: st.write(f"**{k}:** {r[k]}")
            with c2:
                for k in cols[mid:]:
                    if r[k]: st.write(f"**{k}:** {r[k]}")

if __name__ == "__main__":
    run()
