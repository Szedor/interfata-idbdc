# =========================================================
# utils/sectiuni/__init__.py
# VERSIUNE: 2.0
# STATUS: STABIL
# DATA: 2026.05.05
# =========================================================
# CONȚINUT:
#   Exportă funcțiile principale din toate secțiunile.
#   Importurile sunt opționale — fișierele individuale
#   pot fi importate direct acolo unde sunt necesare.
#
# MODIFICĂRI VERSIUNEA 2.0:
#   - Corectat: render_date_financiare → render_date_financiare_fdi
#     (numele real al funcției din date_financiare.py).
#   - Adăugat import pentru date_baza_proiect.
# =========================================================

from utils.sectiuni.date_baza import render_date_de_baza
from utils.sectiuni.date_baza_proiect import render_date_de_baza_proiect
from utils.sectiuni.date_financiare import render_date_financiare_fdi
from utils.sectiuni.echipa import render_echipa
from utils.sectiuni.aspecte_tehnice import render_aspecte_tehnice
