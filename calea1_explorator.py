import streamlit as st
import pandas as pd
from supabase import create_client, Client
import io

# --- STIL VIZUAL ---
def apply_card_style():
    st.markdown("""
        <style>
            .stApp { background-color: #f8f9fa; }
            .stExpander {
                background-color: white !important;
                border-radius: 10px !important;
                border: 1px solid #dee2e6 !important;
                margin-bottom: 10px;
            }
            .download-section {
                background-color: #ffffff;
                padding: 15px;
                border-radius: 10px;
                border: 1px dashed #28a745;
                margin-bottom: 20px;
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
            st.subheader("🔑 Acces Securizat")
            p = st.text_input("Parola:", type="password")
            if st.button("Intră în Arhivă"):
                if p == PASSWORD:
                    st.session_state.auth_explorator = True
                    st.rerun()
        st.stop()

def run():
    apply_card_style()
    gate()

    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.title("🗂️ Explorator Proiecte cu Export Excel")

    # --- ZONA DE FILTRARE ---
    with st.container():
        col1, col2 = st.columns([2, 1])
        with col1:
            q_text = st.text_input("Căutare (Acronim/Titlu/Cod):", placeholder="Scrie aici pentru filtrare...")
        with col2:
            selected_types = st.multiselect("Tipuri:", list(BASE_TABLES.keys()), default=["FDI", "PNRR"])

    # --- COLECTARE DATE ---
    rows_all = []
    for t_key in selected_types:
        try:
            res = supabase.table(BASE_TABLES[t_key]).select("*").execute()
            for r in (res.data or []):
                r["Sursa_Tabel"] = t_key
                rows_all.append(r)
        except: continue

    if not rows_all:
        st.info("Selectează tipurile de proiecte pentru a afișa datele.")
        return

    # Transformăm în DataFrame pentru filtrare și download
    df_final = pd.DataFrame(rows_all)

    # Filtrare text
    if q_text:
        mask = df_final.apply(lambda row: q_text.lower() in str(row.values).lower(), axis=1)
        df_final = df_final[mask]

    # --- BUTON DOWNLOAD (Apare doar dacă avem rezultate) ---
    if not df_final.empty:
        st.markdown('<div class="download-section">', unsafe_allow_html=True)
        col_txt, col_btn = st.columns([3, 1])
        with col_txt:
            st.write(f"✅ Am găsit **{len(df_final)}** rezultate. Poți descărca tabelul filtrat în format Excel:")
        
        with col_btn:
            # Generare Excel în memorie
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_final.to_excel(writer, index=False, sheet_name='Rezultate_IDBDC')
            
            st.download_button(
                label="📥 Descarcă Excel",
                data=output.getvalue(),
                file_name="extras_proiecte_idbdc.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # --- AFIȘARE CARDURI ---
    for _, r in df_final.iterrows():
        cod = r.get("cod_identificare", "N/A")
        acronim = r.get("acronim_proiect") or r.get("titlu_proiect") or "Proiect"
        sursa = r.get("Sursa_Tabel")
        
        with st.expander(f"🆔 {cod} | {acronim} ({sursa})"):
            # Afișăm toate câmpurile care nu sunt goale
            for col_name, value in r.items():
                if pd.notnull(value) and str(value).strip() != "":
                    st.write(f"**{col_name}:** {value}")

if __name__ == "__main__":
    run()
