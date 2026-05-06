
# =========================================================
# admin/fise/proprietate_industriala.py
# VERSIUNE: 1.0
# STATUS: STABIL - Fațadă Admin pentru Proprietate Industrială
# DATA: 2026.05.05
# =========================================================
# CONȚINUT:
#   Fațadă pentru Calea2 (Admin) — expune 2 metode pentru
#   Proprietate Industrială:
#       render_date_de_baza  → utils/sectiuni/date_baza_proiect.py
#       render_echipa        → utils/sectiuni/echipa.py
#
#   Nu există secțiune Financiar sau Aspecte tehnice
#   pentru această categorie.
#
# MODIFICĂRI VERSIUNEA 1.0:
#   - Creare inițială.
# =========================================================

from utils.sectiuni.date_baza_proiect import render_date_de_baza_proiect as _render_baza
from utils.sectiuni.echipa import render_echipa as _render_echipa


def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex):
    return _render_baza(
        supabase=supabase,
        cod_introdus=cod_introdus,
        cat_sel=cat_sel,
        tip_label="PROPRIETATE INDUSTRIALĂ",
        tabela_nume="base_proprietate_industriala",
        is_new=is_new,
        date_existente=date_baza_ex,
    )


def render_echipa(supabase, cod_introdus, is_new, date_echipa_ex):
    return _render_echipa(supabase, cod_introdus, is_new, date_echipa_ex)
