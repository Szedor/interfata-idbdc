# =========================================================
# utils/sectiuni/__init__.py
# VERSIUNE: 2.0
# STATUS: STABIL - Importuri automate eliminate
# DATA: 2026.05.04
# =========================================================
# CONȚINUT:
#   Pachet utils/sectiuni. Importurile explicite au fost
#   eliminate deoarece cauzau erori în lanț la startup:
#   orice problemă într-un modul de secțiune bloca întreaga
#   aplicație. Fiecare modul care necesită o funcție din
#   sectiuni o importă direct (ex:
#   from utils.sectiuni.date_baza import render_date_de_baza).
#
# MODIFICĂRI VERSIUNEA 2.0:
#   - Eliminate importurile automate ale tuturor secțiunilor.
# =========================================================
