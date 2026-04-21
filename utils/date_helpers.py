# =========================================================
# utils/date_helpers.py
# v.modul.1.1 - Funcții ajutătoare pentru date (extrase din codul validat)
# =========================================================

import pandas as pd
import calendar as cal_lib
from datetime import date

def to_date(val):
    """Convertește o valoare în obiect date, dacă este posibil."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    try:
        return pd.to_datetime(val).date()
    except Exception:
        return None

def calc_durata(d1, d2) -> int:
    """Calculează durata în luni între două date."""
    try:
        luni = (d2.year - d1.year) * 12 + (d2.month - d1.month)
        if d2.day >= d1.day:
            luni += 1
        return max(0, luni)
    except Exception:
        return 0

def add_months(d, luni) -> date:
    """Adaugă un număr de luni la o dată."""
    try:
        m = d.month - 1 + int(luni)
        an = d.year + m // 12
        luna = m % 12 + 1
        zi = min(d.day, cal_lib.monthrange(an, luna)[1])
        return date(an, luna, zi)
    except Exception:
        return None

def sub_months(d, luni) -> date:
    """Scade un număr de luni dintr-o dată."""
    return add_months(d, -int(luni))
