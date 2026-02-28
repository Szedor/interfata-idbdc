import streamlit as st
import pandas as pd
from supabase import create_client, Client
import io

# --- STIL VIZUAL REVITALIZAT ---
def apply_custom_style():
    st.markdown("""
        <style>
            .stApp { background-color: #f4f7f9; }
            .export-container {
                background-color: #ffffff;
                padding: 20px;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                margin-bottom: 20px;
            }
            .stButton>button { border-radius: 8px; }
            @media print {
                .no-print { display: none !important; }
                .stApp { background-color: white !important; }
            }
        </style>
    """, unsafe_allow_html=True)

PASSWORD = "EverDream2SZ"

BASE_TABLES = {
    "CEP": "base_contracte_cep", "TERTI": "base_contracte_terti",
    "FDI": "base_proiecte_fdi", "PNRR": "base_proiecte_pnrr",
    "INTERNATIONALE": "base_proiecte_internationale",
    "INTERREG": "base_proiecte_interreg", "PNCDI": "base_proiecte_pncdi"
}

def gate():
    if "auth_explorator" not in st.session_state:
        st.session_state.auth_explorator = False
    if not st.session_state.auth_explorator:
        _, col_mid, _ = st.columns([1, 1.2, 1])
        with col_mid:
            st.markdown("<h2 style='text-align:center;'>🔐 Acces IDBDC</h2>", unsafe_allow_html=True)
            p = st.text_input("Parola de acces:", type="password")
            if st.button("Deblochează Sistemul"):
                if p == PASSWORD:
                    st.session_state.auth_explorator = True
                    st.rerun()
        st.stop()

def run():
    apply_custom_style()
    gate()

    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.title("📊 Centru de Consultare și Raportare")

    # --- 1. FILTRARE (Într-un container expandabil pentru a economisi spațiu) ---
    with st.expander("🔍 Filtrează datele pentru raport", expanded=True):
        col_t, col_q = st.columns([1, 2])
        with col_t:
            selected_types = st.multiselect("Categorii:", list(BASE_TABLES.keys()), default=["FDI", "PNRR"])
        with col_q:
            q_text = st.text_input("Căutare rapidă (orice câmp):", placeholder="Ex: titlu, nume, cod...")

    # --- 2. COLECTARE DATE ---
    all_rows = []
    for t_key in selected_types:
        try:
            res = supabase.table(BASE_TABLES[t_key]).select("*").execute()
            for r in (res.data or []):
                r["_sursa"] = t_key
                all_rows.append(r)
        except: continue

    if not all_rows:
        st.info("Aștept selectarea categoriilor pentru a genera datele...")
        return

    df_full = pd.DataFrame(all_rows)
    if q_text:
        df_full = df_full[df_full.apply(lambda row: q_text.lower() in str(row.values).lower(), axis=1)]

    # --- 3. SELECȚIE COLOANE (LIBERTATEA DE BIFRE) ---
    st.markdown("### 🛠️ Personalizare Raport")
    all_cols = list(df_full.columns)
    
    # Pre-selectăm câteva coloane esențiale ca să nu fie tabelul gol la început
    default_cols = [c for c in ["cod_identificare", "acronim_proiect", "titlu_proiect", "valoare_totala", "_sursa"] if c in all_cols]
    
    selected_cols = st.multiselect("Bifează coloanele pe care le dorești în extras/print:", all_cols, default=default_cols)

    if not selected_cols:
        st.warning("Te rog selectează cel puțin o coloană pentru a genera raportul.")
        return

    df_final = df_full[selected_cols]

    # --- 4. ZONA DE EXPORT ȘI PRINT ---
    st.markdown('<div class="export-container no-print">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1,1,1,1])
    
    with c1:
        # Export Excel
        output_xlsx = io.BytesIO()
        with pd.ExcelWriter(output_xlsx, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, index=False, sheet_name='Raport_IDBDC')
        st.download_button("📥 Excel (.xlsx)", data=output_xlsx.getvalue(), file_name="raport_idbdc.xlsx")

    with c2:
        # Export CSV
        csv_data = df_final.to_csv(index=False).encode('utf-8')
        st.download_button("📄 CSV (.csv)", data=csv_data, file_name="raport_idbdc.csv")

    with c3:
        # Buton de Print (Trigger browser print)
        if st.button("🖨️ Printează / PDF"):
            st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
            st.info("Folosește funcția 'Save as PDF' din fereastra de print pentru varianta PDF.")

    with c4:
        st.write(f"Total: **{len(df_final)}** rânduri")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 5. AFIȘARE REZULTAT ---
    st.subheader("📋 Previzualizare Date")
    st.dataframe(df_final, use_container_width=True)

if __name__ == "__main__":
    run()
