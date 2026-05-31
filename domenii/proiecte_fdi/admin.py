# =========================================================
# IDBDC/domenii/proiecte_fdi/admin.py
# VERSIUNE: 1.0
# STATUS: NOU — Admin Proiecte FDI
# DATA: 2026.05.31
# =========================================================
# CONȚINUT:
#   Fațadă pentru Calea2 (Administrare).
#   Expune cele 4 funcții de render așteptate de motor.py:
#     render_date_de_baza()
#     render_date_financiare()
#     render_echipa()
#     render_aspecte_tehnice()
#
#   Fiecare apelează modulul corespunzător din același pachet
#   sau din domenii/_baza/ (echipa este generică).
# =========================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from domenii.proiecte_fdi.baza      import render as _render_baza
from domenii.proiecte_fdi.financiar import render as _render_financiar
from domenii.proiecte_fdi.tehnic    import render as _render_tehnic
from domenii._baza.echipa           import render as _render_echipa
from domenii.proiecte_fdi.definitie import (
    TIP_LABEL, CAT_LABEL, BASE_TABLE,
)


def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex):
    return _render_baza(
        supabase      = supabase,
        cod_introdus  = cod_introdus,
        cat_sel       = cat_sel,
        tip_label     = TIP_LABEL,
        tabela_nume   = BASE_TABLE,
        is_new        = is_new,
        date_existente= date_baza_ex,
    )


def render_date_financiare(supabase, cod_introdus, is_new, date_fin_ex):
    return _render_financiar(supabase, cod_introdus, is_new, date_fin_ex)


def render_echipa(supabase, cod_introdus, is_new, date_echipa_ex):
    return _render_echipa(supabase, cod_introdus, is_new, date_echipa_ex)


def render_aspecte_tehnice(supabase, cod_introdus, is_new, date_teh_ex):
    return _render_tehnic(supabase, cod_introdus, is_new, date_teh_ex)
