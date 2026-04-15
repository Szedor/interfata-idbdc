import streamlit as st
from admin_data_ops import ORDINE_CAMPURI_CEP, genereaza_pdf_cu_diacritice, export_excel_special

def afisare_fisa_completa_cep(df):
    st.subheader("Tab1 - Fisa Completa")
    
    if df.empty:
        st.info("Incarcati datele pentru a vizualiza fisa.")
        return

    # Selectie multipla pentru a permite exportul mai multor fise odata
    selectate = st.multiselect("Selectati contractele (Cod Inregistrare):", df["cod_inregistrare"].unique())
    
    if selectate:
        date_selectate = df[df["cod_inregistrare"].isin(selectate)]
        
        # [Punctul 2] Afisarea respecta strict ordinea campurilor
        for _, fisa in date_selectate.iterrows():
            with st.expander(f"Detalii Contract: {fisa['cod_inregistrare']}"):
                for camp in ORDINE_CAMPURI_CEP:
                    st.write(f"**{camp.replace('_', ' ').upper()}:** {fisa[camp]}")
        
        col1, col2 = st.columns(2)
        with col1:
            # Luam prima fisa selectata pentru PDF (de regula PDF-ul este per unitate)
            pdf_bytes = genereaza_pdf_cu_diacritice(date_selectate.iloc[0])
            st.download_button("Export PDF (Diacritice)", data=pdf_bytes, file_name="fisa_cep.pdf")
            
        with col2:
            # Exportul Excel conform regulii celor 2 randuri si coloana goala
            excel_bytes = export_excel_special(date_selectate)
            st.download_button("Export Excel (Special)", data=excel_bytes, file_name="export_fise_cep.xlsx")
