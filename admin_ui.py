import streamlit as st

# [Art. 11] Importam ordinea oficiala din modulul de operatii date
from admin_data_ops import CEP_COLUMN_ORDER

def display_fisa_completa(selected_row):
    """Afisarea campurilor in Tab1 conform ordinii SQL (Rezolvare pct. 2)"""
    st.subheader("📄 Fisa Completa Contract CEP")
    
    # Afisare organizata pe randuri (Art. 10 - Vizibilitate clara pentru economist)
    for col in CEP_COLUMN_ORDER:
        label = col.replace("_", " ").title()
        value = selected_row.get(col, "N/A")
        st.write(f"**{label}:** {value}")
        
    st.divider()
    
    # Butonul de export va folosi acum logica din admin_data_ops
    if st.button("Export PDF (cu diacritice)"):
        # Logica apelare generare PDF
        pass
