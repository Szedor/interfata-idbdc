# =========================================================
# IDBDC - MODUL ADMIN - REGULI ȘI VALIDĂRI (admin_rules.py)
# Versiune: 1.0 - Rezolvare bug persoana_contact & Tipuri Date
# =========================================================

import streamlit as st

def get_column_config(df):
    """
    Definește configurația coloanelor pentru st.data_editor.
    Aici se forțează tipurile de date pentru a evita erorile de compatibilitate.
    """
    config = {}
    
    for col in df.columns:
        # 1. Forțăm TEXT pentru câmpurile problematice
        if col in ["cod_identificare", "telefon", "email"]:
            config[col] = st.column_config.TextColumn(
                col.replace("_", " ").title(),
                help=f"Câmp formatat ca text pentru {col}",
                disabled=(col == "cod_identificare")
            )
        
        # 2. Configurare pentru Booleene (Checkboxes)
        elif col.startswith("is_") or col in ["validat_idbdc", "confirmare", "persoana_contact"]:
            config[col] = st.column_config.CheckboxColumn(
                col.replace("_", " ").title()
            )
            
        # 3. Configurare pentru Ani (fără virgulă la mii, ex: 2.024 -> 2024)
        elif "an_" in col or col == "an":
            config[col] = st.column_config.NumberColumn(
                col.replace("_", " ").title(),
                format="%d"
            )
            
        # 4. Configurare pentru Valori Financiare
        elif any(key in col for key in ["valoare", "buget", "suma"]):
            config[col] = st.column_config.NumberColumn(
                col.replace("_", " ").title(),
                format="%.2f"
            )

    return config

def get_hidden_columns(categorie, tabel_nume):
    """
    Returnează lista coloanelor care nu trebuie să apară în UI.
    Păstrează logica din versiunea stabilă.
    """
    hidden = ["id", "creat_la", "creat_de", "modificat_la", "modificat_de"]
    
    # Reguli specifice per categorie (ex: dacă e Eveniment, ascundem anumite câmpuri)
    if categorie in ["Evenimente stiintifice", "Proprietate industriala"]:
        hidden.extend(["echipa", "aspecte_tehnice"]) # Just in case
        
    return hidden

def get_editor_height(tabel_nume):
    """
    Returnează înălțimea optimă a editorului în funcție de tabel.
    """
    if tabel_nume.startswith("base_"):
        return 250
    return 400 # Pentru tabelele de detaliu (Echipă, Finanțe) care au mai multe rânduri

def is_multiannual(tabel_nume):
    """Regulă pentru PNRR și PNCDI (logică multianuală)."""
    return "pnrr" in tabel_nume or "pncdi" in tabel_nume
