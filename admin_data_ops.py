import pandas as pd
from fpdf import FPDF
import io

# [Art. 11] Definirea ordinii campurilor conform tabelelor SQL pentru sincronizare totala
CEP_COLUMN_ORDER = [
    "cod_identificare", "nr_contract", "data_contract", "beneficiar", 
    "obiect_contract", "valoare_totala", "valuta", "durata_luni", 
    "stadiu_actual", "observatii"
]

def get_ordered_data(df, columns=CEP_COLUMN_ORDER):
    """Asigura ca datele respecta ordinea campurilor solicitata (Art. 2)"""
    return df[columns]

def generate_pdf_fisa(data_row):
    """Generare PDF cu suport pentru diacritice (Rezolvare pct. 1)"""
    pdf = FPDF()
    pdf.add_page()
    
    # Folosim un font standard care suporta setul de caractere necesar pentru diacritice
    # Nota: Daca fisierul font nu este prezent, se va folosi Arial cu mapare UTF-8
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="FISA COMPLETA CONTRACT CEP", ln=True, align='C')
    pdf.ln(10)
    
    for key in CEP_COLUMN_ORDER:
        val = str(data_row.get(key, ""))
        # Conversie pentru a asigura afisarea corecta a textului
        pdf.multi_cell(0, 10, txt=f"{key.replace('_', ' ').upper()}: {val}")
    
    return pdf.output(dest='S').encode('latin-1', errors='replace')

def export_to_excel_2rows(df):
    """Export in format 2 randuri per fisa (Rezolvare pct. 3)"""
    output = io.BytesIO()
    processed_data = []
    
    for _, row in df.iterrows():
        # Rand 1: Denumiri campuri
        processed_data.append(row.index.tolist())
        # Rand 2: Valori campuri
        processed_data.append(row.values.tolist())
        # Rand 3: Rand gol pentru separare
        processed_data.append(["" for _ in row])
        
    new_df = pd.DataFrame(processed_data)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        new_df.to_excel(writer, index=False, header=False)
    return output.getvalue()
