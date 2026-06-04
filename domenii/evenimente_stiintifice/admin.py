# =========================================================
# IDBDC/domenii/evenimente_stiintifice/admin.py
# VERSIUNE: 1.0 | DATA: 2026.06.02
# =========================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from domenii.evenimente_stiintifice.baza import render as _render_baza
from domenii._baza.echipa                import render as _render_echipa
from domenii.evenimente_stiintifice.definitie import TIP_LABEL, CAT_LABEL, BASE_TABLE


def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex):
    return _render_baza(
        supabase=supabase, cod_introdus=cod_introdus, cat_sel=cat_sel,
        tip_label=TIP_LABEL, tabela_nume=BASE_TABLE,
        is_new=is_new, date_existente=date_baza_ex,
    )

def render_echipa(supabase, cod_introdus, is_new, date_echipa_ex):
    return _render_echipa(supabase, cod_introdus, is_new, date_echipa_ex)
