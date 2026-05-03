# =========================================================
# IDBDC/utils/contracte_common.py
# VERSIUNE: 2.0
# STATUS: CORECTAT - adăugat câmpul observatii în Date de bază
# DATA: 2026.05.03
# =========================================================
# CONȚINUT:
#   Orchestrator comun pentru toate tipurile de contracte
#   (CEP, TERȚI, SPECIALE). Conține logica comună pentru
#   cele trei secțiuni: Date de bază, Date financiare, Echipă.
#   Importă funcțiile de randare din modulele dedicate din
#   utils/sectiuni/ și le expune ca interfață unică pentru
#   modulele din admin/fise/.
#
# MODIFICĂRI VERSIUNEA 2.0:
#   - Funcția render_date_de_baza acum include câmpul
#     `observatii` în datele returnate pentru salvare,
#     prin delegare către utils/sectiuni/date_baza.py v3.0.
#   - Eliminată definiția locală duplicată a render_date_de_baza
#     (care nu includea observatii) — acum se folosește exclusiv
#     importul din utils/sectiuni/date_baza.py.
#   - Corectat cache-ul pentru _get_status_list (prefix _supabase).
# =========================================================

import streamlit as st
import pandas as pd
from utils.date_helpers import to_date, calc_durata, add_months, sub_months
from utils.supabase_helpers import safe_select_eq

# =========================================================
# Importuri din modulele dedicate
# ADĂUGAT v2.0: render_date_de_baza vine exclusiv din
# utils/sectiuni/date_baza.py care include coloana OBSERVAȚII.
# Definiția locală anterioară a fost eliminată pentru a evita
# duplicarea codului și inconsistențele între versiuni.
# =========================================================
from utils.sectiuni.date_baza import render_date_de_baza
from utils.sectiuni.date_financiare import render_date_financiare
from utils.sectiuni.echipa import render_echipa
from utils.sectiuni.aspecte_tehnice import render_aspecte_tehnice


# =========================================================
# FIȘA 2 — DATE FINANCIARE (comună pentru CEP, TERȚI, SPECIALE)
# =========================================================
def render_date_financiare(supabase, cod_introdus, is_new, date_existente):
    """
    Randare și salvare date financiare.
    Parametri:
        supabase: clientul Supabase
        cod_introdus: codul identificator
        is_new: boolean - dacă este înregistrare nouă
        date_existente: listă cu datele existente
    """
    VALUTE = ["LEI", "EURO", "USD"]
    if is_new or not date_existente:
        row_ex = {"valuta": "LEI", "valoare_contract_cep_terti_speciale": 0.0}
    else:
        row_ex = date_existente[0]

    try:
        val_ex = float(row_ex.get("valoare_contract_cep_terti_speciale") or 0)
    except Exception:
        val_ex = 0.0
    valuta_ex = row_ex.get("valuta", "LEI")
    if valuta_ex not in VALUTE:
        valuta_ex = "LEI"

    df = pd.DataFrame([{
        "VALUTA": valuta_ex,
        "VALOARE CONTRACT": val_ex,
    }])

    col_cfg = {
        "VALUTA": st.column_config.SelectboxColumn("💱 VALUTA", options=VALUTE, required=True),
        "VALOARE CONTRACT": st.column_config.NumberColumn("💰 VALOARE CONTRACT", format="%,.2f", min_value=0.0),
    }

    df_edit = st.data_editor(
        df,
        column_config=col_cfg,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"fin_editor_{cod_introdus}",
    )
    row = df_edit.iloc[0]
    return [{
        "cod_identificare": cod_introdus,
        "valuta": row["VALUTA"],
        "valoare_contract_cep_terti_speciale": float(row["VALOARE CONTRACT"] or 0),
    }]
