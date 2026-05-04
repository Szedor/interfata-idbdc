
# =========================================================
# admin/fise/proiecte_fdi.py
# VERSIUNE: 1.0
# STATUS: STABIL - Fațadă Admin pentru Proiecte FDI
# DATA: 2026.05.04
# =========================================================
# CONȚINUT:
#   Fațadă pentru Calea2 (Admin) — expune cele 4 metode
#   de randare/colectare date pentru proiectele FDI:
#       render_date_de_baza      → utils/sectiuni/date_baza_proiect.py
#       render_date_financiare   → utils/sectiuni/date_financiare_fdi.py
#       render_echipa            → utils/sectiuni/echipa.py (comun, neatins)
#       render_aspecte_tehnice   → utils/sectiuni/aspecte_tehnice.py
#
#   Diferențe față de contracte_cep.py:
#   - 4 metode în loc de 3 (adăugată render_aspecte_tehnice)
#   - Importuri din modulele specifice proiectelor
#   - tip_label="FDI", tabela_nume="base_contracte_cep"
#
# MODIFICĂRI VERSIUNEA 1.0:
#   - Creare inițială.
# =========================================================

from utils.sectiuni.date_baza_proiect import render_date_de_baza_proiect as _render_baza
from utils.sectiuni.date_financiare_fdi import render_date_financiare_fdi as _render_fin
from utils.sectiuni.echipa import render_echipa as _render_echipa
from utils.sectiuni.aspecte_tehnice import render_aspecte_tehnice as _render_teh


def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex):
    return _render_baza(
        supabase=supabase,
        cod_introdus=cod_introdus,
        cat_sel=cat_sel,
        tip_label="FDI",
        tabela_nume="base_contracte_cep",
        is_new=is_new,
        date_existente=date_baza_ex,
    )


def render_date_financiare(supabase, cod_introdus, is_new, date_fin_ex):
    return _render_fin(supabase, cod_introdus, is_new, date_fin_ex)


def render_echipa(supabase, cod_introdus, is_new, date_echipa_ex):
    return _render_echipa(supabase, cod_introdus, is_new, date_echipa_ex)


def render_aspecte_tehnice(supabase, cod_introdus, is_new, date_teh_ex):
    return _render_teh(supabase, cod_introdus, is_new, date_teh_ex)
