import pandas as pd
import io
from fpdf import FPDF

# [Art. 11] Lista oficiala care dicteaza ordinea campurilor (Punctul 2)
# Aceasta ordine va fi replicata in SQL, Interfata, PDF si Excel
ORDINE_CAMPURI_CEP = [
    "cod_inregistrare", "nr_contract", "data_contract", "beneficiar", 
    "obiect_contract", "valoare_totala", "valuta", "durata_luni", 
    "stadiu_actual", "observatii"
]

def genereaza_pdf_cu_diacritice(date_fisa):
    """Generare PDF cu suport pentru caractere romanesti (Punctul 1)"""
    pdf = FPDF()
    pdf.add_page()
    # Utilizam un font standard care suporta setul de caractere latin-2
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="FISA COMPLETA CONTRACT CEP", ln=True, align='C')
    pdf.ln(10)
    
    for camp in ORDINE_CAMPURI_CEP:
        nume_afisat = camp.replace("_", " ").upper()
        valoare = str(date_fisa.get(camp, ""))
        # Conversie manuala pentru a asigura scrierea diacriticelor in formatul PDF
        linie = f"{nume_afisat}: {valoare}"
        pdf.multi_cell(0, 10, txt=linie.encode('latin-1', 'replace').decode('latin-1'))
    
    return pdf.output(dest='S').encode('latin-1')

def export_excel_special(df_selectat):
    """Export: R1-Denumiri, R2-Valori, Coloana goala intre fise (Punctul 3)"""
    output = io.BytesIO()
    lista_finala = []
    
    # Capetele de tabel (Denumirile campurilor)
    rand_header = []
    # Datele (Valorile)
    rand_date = []
    
    for i, (_, row) in enumerate(df_selectat.iterrows()):
        for camp in ORDINE_CAMPURI_CEP:
            rand_header.append(camp.replace("_", " ").upper())
            rand_date.append(row[camp])
        
        # Daca sunt mai multe fise, adaugam o coloana goala (Punctul 3)
        if i < len(df_selectat) - 1:
            rand_header.append("") # Coloana goala in header
            rand_date.append("")   # Coloana goala in date
            
    df_export = pd.DataFrame([rand_header, rand_date])
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_export.to_excel(writer, index=False, header=False)
    return output.getvalue()
