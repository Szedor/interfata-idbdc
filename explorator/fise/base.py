# IDBDC - Funcții comune pentru afișarea fișelor în explorator
import re

def fmt_numeric(val, col_name: str = "") -> str:
    if val is None:
        return ""
    raw = str(val).strip()
    if raw == "":
        return ""
    try:
        f = float(raw.replace(",", "."))
    except (ValueError, TypeError):
        return raw
    col_name = (col_name or "").lower().strip()
    no_decimal_fields = {
        "cod_identificare", "numar_contract", "nr_contract", "nr_contract_achizitie",
        "nr_contract_subsecvent", "numar_oficial_acordare", "numar_publicare_cerere",
        "numar_data_notificare_intern", "telefon_mobil", "telefon_upt",
        "cod_depunere", "cod_temporar",
    }
    if col_name in no_decimal_fields:
        return str(int(round(f)))
    financial_keys = ("valoare", "buget", "suma", "cost", "contributie", "cofinantare")
    is_financial = any(k in col_name for k in financial_keys)
    if is_financial:
        return f"{f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if f.is_integer():
        return str(int(f))
    return f"{f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def col_label(col: str, table: str = None, COL_LABELS=None, COL_LABELS_PER_TABLE=None):
    # Funcție care va folosi dicționarele globale – temporar o lăsăm în fisa_completa.py
    pass
