# =========================================================
# admin/fise/contracte_speciale.py
# v.modul.1.1 - Fațadă pentru Contracte SPECIALE
# =========================================================

from utils.contracte_common import (
    render_date_de_baza as _render_date_de_baza,
    render_date_financiare as _render_date_financiare,
    render_echipa as _render_echipa
)

def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex):
    return _render_date_de_baza(
        supabase=supabase,
        cod_introdus=cod_introdus,
        cat_sel=cat_sel,
        tip_label="SPECIALE",
        tabela_nume="base_contracte_speciale",
        is_new=is_new,
        date_existente=date_baza_ex
    )

def render_date_financiare(supabase, cod_introdus, is_new, date_fin_ex):
    return _render_date_financiare(supabase, cod_introdus, is_new, date_fin_ex)

def render_echipa(supabase, cod_introdus, is_new, date_echipa_ex):
    return _render_echipa(supabase, cod_introdus, is_new, date_echipa_ex)
