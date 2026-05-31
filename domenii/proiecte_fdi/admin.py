# =========================================================
# IDBDC/domenii/proiecte_fdi/admin.py
# v.modul.1.0 - Admin Proiecte FDI
# =========================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from domenii._baza.baza import render as _baza_render_baza
from domenii.proiecte_fdi.financiar import render as _baza_render_financiar
from domenii._baza.echipa import render as _baza_render_echipa
from domenii.proiecte_fdi.tehnic import render as _baza_render_tehnic
from domenii.proiecte_fdi.definitie import TIP_LABEL, BASE_TABLE, FIELDS_BAZA


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


def render_aspecte_tehnice(supabase, cod_introdus, is_new, date_teh_ex):
    return _baza_render_tehnic(supabase, cod_introdus, is_new, date_teh_ex)
