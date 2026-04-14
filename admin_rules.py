# =========================================================
# IDBDC - MODUL ADMIN - REGULI ȘI VALIDĂRI (admin_rules.py)
# Versiune: 1.1 - cod_identificare editabil doar la înregistrări noi
# =========================================================

import streamlit as st

def get_column_config(df, is_new: bool = False):
    """
    Definește configurația coloanelor pentru st.data_editor.
    is_new=True  -> cod_identificare editabil (înregistrare nouă)
    is_new=False -> cod_identificare blocat  (înregistrare existentă)
    """
    config = {}

    for col in df.columns:
        # 1. TEXT — câmpuri standard
        if col in ["cod_identificare", "telefon", "email"]:
            config[col] = st.column_config.TextColumn(
                col.replace("_", " ").title(),
                help=f"Câmp formatat ca text pentru {col}",
                disabled=(col == "cod_identificare" and not is_new)
            )

        # 2. Booleene (bifă)
        elif col.startswith("is_") or col in ["validat_idbdc", "confirmare", "persoana_contact"]:
            config[col] = st.column_config.CheckboxColumn(
                "✅ " + col.replace("_", " ").title()
            )

        # 3. Ani (fără virgulă la mii: 2.024 -> 2024)
        elif "an_" in col or col == "an":
            config[col] = st.column_config.NumberColumn(
                "📆 " + col.replace("_", " ").title(),
                format="%d"
            )

        # 4. Valori financiare
        elif any(key in col for key in ["valoare", "buget", "suma"]):
            config[col] = st.column_config.NumberColumn(
                "💰 " + col.replace("_", " ").title(),
                format="%,.2f"
            )

    return config

def get_hidden_columns(categorie, tabel_nume):
    hidden = ["id", "creat_la", "creat_de", "modificat_la", "modificat_de"]
    if categorie in ["Evenimente stiintifice", "Proprietate industriala"]:
        hidden.extend(["echipa", "aspecte_tehnice"])
    return hidden

def get_editor_height(tabel_nume):
    if tabel_nume.startswith("base_"):
        return 250
    return 400

def is_multiannual(tabel_nume):
    return "pnrr" in tabel_nume or "pncdi" in tabel_nume
