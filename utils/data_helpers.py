# IDBDC - Utilitare pentru date
from datetime import date
import calendar as cal_lib
import pandas as pd

def to_date(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    try:
        return pd.to_datetime(val).date()
    except Exception:
        return None

def calc_durata(d1, d2) -> int:
    try:
        luni = (d2.year - d1.year) * 12 + (d2.month - d1.month)
        if d2.day >= d1.day:
            luni += 1
        return max(0, luni)
    except Exception:
        return 0

def add_months(d, luni) -> date:
    try:
        m = d.month - 1 + int(luni)
        an = d.year + m // 12
        luna = m % 12 + 1
        zi = min(d.day, cal_lib.monthrange(an, luna)[1])
        return date(an, luna, zi)
    except Exception:
        return None

def sub_months(d, luni) -> date:
    return add_months(d, -int(luni))
