# =========================================================
# utils/contracte_common.py
# v.modul.2.0 - Orchestrator care folosește noile module secționate
# =========================================================

# Acest fișier devine un simplu orchestrator care importă și expune funcțiile din sectiuni
# Pentru compatibilitate cu codul existent, păstrăm aceleași nume de funcții.

from utils.sectiuni.date_baza import render_date_de_baza
from utils.sectiuni.date_financiare import render_date_financiare
from utils.sectiuni.echipa import render_echipa
from utils.sectiuni.aspecte_tehnice import render_aspecte_tehnice

# Toate funcțiile sunt deja disponibile prin importurile de mai sus
