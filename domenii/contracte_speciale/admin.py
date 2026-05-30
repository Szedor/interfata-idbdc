# =========================================================
# IDBDC/domenii/contracte_speciale/admin.py
# v.modul.1.0 - Admin Contracte SPECIALE
# =========================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from domenii._baza.baza import render as _baza_render_baza
from domenii.contracte_speciale.financiar import render as _baza_render_financiar
from domenii._baza.echipa import render as _baza_render_echipa
from domenii.contracte_speciale.definitie import TIP_LABEL, BASE_TABLE, FIELDS_BAZA


def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex):
    return _baza_render_baza(
        supabase=supabase,
        cod_introdus=cod_introdus,
        cat_sel=cat_sel,
        tip_label=TIP_LABEL,
        tabela_nume=BASE_TABLE,
        fields_map=FIELDS_BAZA,
        is_new=is_new,
        date_existente=date_baza_ex
    )


def render_date_financiare(supabase, cod_introdus, is_new, date_fin_ex):
    return _baza_render_financiar(supabase, cod_introdus, is_new, date_fin_ex)


def render_echipa(supabase, cod_introdus, is_new, date_echipa_ex):
    return _baza_render_echipa(supabase, cod_introdus, is_new, date_echipa_ex)
