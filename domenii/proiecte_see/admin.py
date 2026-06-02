# =========================================================
# IDBDC/domenii/proiecte_see/admin.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.06.02
# =========================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from domenii.proiecte_see.baza      import render as _render_baza
from domenii.proiecte_see.financiar import render as _render_financiar
from domenii.proiecte_see.tehnic    import render as _render_tehnic
from domenii._baza.echipa           import render as _render_echipa
from domenii.proiecte_see.definitie import TIP_LABEL, CAT_LABEL, BASE_TABLE


def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex):
    return _render_baza(
        supabase       = supabase,
        cod_introdus   = cod_introdus,
        cat_sel        = cat_sel,
        tip_label      = TIP_LABEL,
        tabela_nume    = BASE_TABLE,
        is_new         = is_new,
        date_existente = date_baza_ex,
    )


def render_date_financiare(supabase, cod_introdus, is_new, date_fin_ex):
    return _render_financiar(supabase, cod_introdus, is_new, date_fin_ex)


def render_echipa(supabase, cod_introdus, is_new, date_echipa_ex):
    return _render_echipa(supabase, cod_introdus, is_new, date_echipa_ex)


def render_aspecte_tehnice(supabase, cod_introdus, is_new, date_teh_ex):
    return _render_tehnic(supabase, cod_introdus, is_new, date_teh_ex)
