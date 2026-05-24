# =========================================================
# IDBDC/domenii/evenimente_stiintifice/admin.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.05.23
# =========================================================

from domenii.evenimente_stiintifice.definitie          import BASE_TABLE
from domenii._baza.sectiune_baza_evenimente_stiintifice import render as _baza_render_baza
from domenii._baza.sectiune_echipa                     import render as _baza_render_echipa


def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex):
    return _baza_render_baza(
        supabase=supabase,
        cod_introdus=cod_introdus,
        cat_sel=cat_sel,
        tabela_nume=BASE_TABLE,
        is_new=is_new,
        date_existente=date_baza_ex,
    )

def render_echipa(supabase, cod_introdus, is_new, date_echipa_ex):
    return _baza_render_echipa(supabase, cod_introdus, is_new, date_echipa_ex)
