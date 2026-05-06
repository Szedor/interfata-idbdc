
# =========================================================
# admin/fise/proiecte_pncdi.py
# VERSIUNE: 1.0
# STATUS: STABIL - Fațadă Admin pentru Proiecte PNCDI
# DATA: 2026.05.05
# =========================================================
# CONȚINUT:
#   Fațadă pentru Calea2 (Admin) — expune cele 4 metode
#   pentru proiectele PNCDI. Date financiare folosesc modulul
#   specific PNCDI (placeholder — ajustați coloanele după BD).
#
# MODIFICĂRI VERSIUNEA 1.0:
#   - Creare inițială.
# =========================================================

from utils.sectiuni.date_baza_proiect import render_date_de_baza_proiect as _render_baza
from utils.sectiuni.date_financiare_pncdi import render_date_financiare_pncdi as _render_fin
from utils.sectiuni.echipa import render_echipa as _render_echipa
from utils.sectiuni.aspecte_tehnice import render_aspecte_tehnice as _render_teh


def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex):
    return _render_baza(
        supabase=supabase,
        cod_introdus=cod_introdus,
        cat_sel=cat_sel,
        tip_label="PNCDI",
        tabela_nume="base_proiecte_pncdi",
        is_new=is_new,
        date_existente=date_baza_ex,
    )


def render_date_financiare(supabase, cod_introdus, is_new, date_fin_ex):
    return _render_fin(supabase, cod_introdus, is_new, date_fin_ex)


def render_echipa(supabase, cod_introdus, is_new, date_echipa_ex):
    return _render_echipa(supabase, cod_introdus, is_new, date_echipa_ex)


def render_aspecte_tehnice(supabase, cod_introdus, is_new, date_teh_ex):
    return _render_teh(supabase, cod_introdus, is_new, date_teh_ex)
