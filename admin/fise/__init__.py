# =========================================================
# admin/fise/__init__.py
# VERSIUNE: 2.0
# STATUS: STABIL
# DATA: 2026.05.05
# =========================================================
# CONȚINUT:
#   Înregistrează toate modulele din admin/fise/ ca pachet
#   Python. Fără acest fișier completat, importurile din
#   admin/motor.py eșuează.
#
# MODIFICĂRI VERSIUNEA 2.0:
#   - Adăugat importuri explicite pentru toate modulele fise.
# =========================================================

from admin.fise import contracte_cep
from admin.fise import contracte_terti
from admin.fise import contracte_speciale
from admin.fise import proiecte_fdi
from admin.fise import proiecte_pncdi
from admin.fise import proiecte_pnrr
from admin.fise import proiecte_internationale
from admin.fise import proiecte_interreg
from admin.fise import proiecte_noneu
from admin.fise import proiecte_see
from admin.fise import proiecte_structurale
from admin.fise import evenimente_stiintifice
from admin.fise import proprietate_industriala
