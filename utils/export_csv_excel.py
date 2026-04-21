# =========================================================
# utils/export_csv_excel.py
# v.modul.1.0 - Generare CSV și Excel (orizontal)
# =========================================================

import pandas as pd
import io

def build_csv_bytes(export_data_horizontal: dict) -> bytes:
    """
    Construiește fișier CSV din datele orizontale.
    export_data_horizontal: dicționar cu cheile "headers" și "values"
    """
    df = pd.DataFrame([export_data_horizontal["values"]], columns=export_data_horizontal["headers"])
    return df.to_csv(index=False).encode("utf-8-sig")

def build_excel_bytes(export_data_horizontal: dict) -> bytes:
    """
    Construiește fișier Excel (.xlsx) din datele orizontale.
    export_data_horizontal: dicționar cu cheile "headers" și "values"
    """
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df = pd.DataFrame([export_data_horizontal["values"]], columns=export_data_horizontal["headers"])
        df.to_excel(writer, index=False, sheet_name="Fisa completa")
    buf.seek(0)
    return buf.getvalue()
