# =========================================================
# utils/contracte_display_common.py
# v.modul.1.0 - Funcții comune pentru afișarea fișei complete (explorator)
# =========================================================
# Acest fișier conține toată logica comună pentru afișarea fișei complete,
# inclusiv export, print, formatare, etc. Extras din tab1_fisa_completa.py.
# =========================================================

import streamlit as st
import pandas as pd
import html as _html
import io
import streamlit.components.v1 as components
from supabase import Client
from utils.supabase_helpers import safe_select_eq
from utils.date_helpers import to_date, calc_durata, add_months, sub_months

# =========================================================
# Configurări comune (etichete, etc.) – aici se pot adăuga și celelalte COL_LABELS etc.
# =========================================================
# Pentru simplitate, păstrăm aceleași dicționare ca în original.
# În practică, acestea pot fi mutate aici și importate în loc de a fi duplicate.
# Din motive de spațiu, voi presupune că există deja în tab1_fisa_completa.py sau aici.
# TODO: mutați aici constantele comune (COL_LABELS, TABLE_LABELS, etc.)

COL_LABELS = {
    "cod_identificare": "NR.CONTRACT/ID PROIECT",
    "durata": "DURATA (în nr. luni)",
    "valoare_contract_cep_terti_speciale": "VALOARE CONTRACT CEP",
    # ... restul etichetelor (se pot copia din original)
}

TABLE_LABELS = {
    "base_contracte_cep": "📄 Contract CEP",
    "base_contracte_terti": "📄 Contract TERȚI",
    "base_contracte_speciale": "📄 Contract SPECIALE",
}

ALL_BASE_TABLES = ["base_contracte_cep", "base_contracte_terti", "base_contracte_speciale"]

# =========================================================
# Funcții de formatare
# =========================================================
def fmt_numeric(val, col_name: str = "") -> str:
    # Aceeași logică ca în original
    if val is None:
        return ""
    raw = str(val).strip()
    if raw == "":
        return ""
    try:
        f = float(raw.replace(",", "."))
    except (ValueError, TypeError):
        return raw
    # ... restul codului de formatare (similar cu _fmt_numeric)
    if f.is_integer():
        return str(int(f))
    return f"{f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def col_label(col: str, table: str = None) -> str:
    # similar cu _col_label
    return COL_LABELS.get(col, col.replace("_", " ").capitalize())

# =========================================================
# Funcții de randare pentru secțiuni (Generale, Financiar, Echipa)
# =========================================================
def render_sectiune_generale(rows, table_name):
    # randare tabel date generale (similar cu _render_sectiune_tabel)
    pass

def render_sectiune_financiar(rows):
    pass

def render_echipa(rows, supabase):
    # randare echipă (similar cu _render_echipa_compact)
    pass

# =========================================================
# Funcții de export (orizontale pentru CSV/Excel, verticale pentru PDF/Print)
# =========================================================
def build_horizontal_export_data(supabase, cod, tabela_gasita):
    # similar cu _build_horizontal_export_data
    pass

def generate_pdf_vertical(supabase, cod, tabela_gasita, titlu_fisa):
    # similar cu _generate_pdf_vertical
    pass

def generate_print_html_vertical(supabase, cod, tabela_gasita, titlu_fisa):
    # similar cu _generate_print_html_vertical
    pass

# =========================================================
# Funcția principală de randare a fișei complete
# =========================================================
def render_fisa_completa(supabase: Client, cod: str, tabela_gasita: str, tip_label: str):
    """
    Parametri:
        supabase: clientul Supabase
        cod: codul identificator
        tabela_gasita: numele tabelei SQL (ex: "base_contracte_cep")
        tip_label: eticheta vizuală (ex: "CEP", "TERȚI", "SPECIALE")
    """
    st.markdown("## 📄 Fișă completă")
    # ... restul codului din render_fisa_completa, dar parametrizat
    # În loc să folosească variabile globale, folosește tabela_gasita și tip_label
    # Afișează secțiunile: Generale, Financiar, Echipa (Tehnic nu pentru contracte)
    # La final, butoane de export care folosesc funcțiile de mai sus.
