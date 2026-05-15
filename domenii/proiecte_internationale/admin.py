# =========================================================
# IDBDC/domenii/proiecte_internationale/admin.py
# VERSIUNE: 1.0
# STATUS: NOU - ecran administrare Proiecte INTERNATIONALE
# DATA: 2026.05.09
# =========================================================

from domenii.proiecte_internationale.definitie              import TIP_LABEL, BASE_TABLE
from domenii._baza.sectiune_baza_proiecte_internationale    import render as _baza_render_baza
from domenii._baza.sectiune_financiar_internationale        import render as _baza_render_financiar
from domenii._baza.sectiune_echipa                          import render as _baza_render_echipa
from domenii._baza.sectiune_tehnic                          import render as _baza_render_tehnic


def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex):
    return _baza_render_baza(
        supabase=supabase,
        cod_introdus=cod_introdus,
        cat_sel=cat_sel,
        tip_label=TIP_LABEL,
        tabela_nume=BASE_TABLE,
        is_new=is_new,
        date_existente=date_baza_ex,
    )


def render_date_financiare(supabase, cod_introdus, is_new, date_fin_ex):
    return _baza_render_financiar(supabase, cod_introdus, is_new, date_fin_ex)


def render_echipa(supabase, cod_introdus, is_new, date_echipa_ex):
    return _baza_render_echipa(supabase, cod_introdus, is_new, date_echipa_ex)


def render_aspecte_tehnice(supabase, cod_introdus, is_new, date_teh_ex):
    return _baza_render_tehnic(supabase, cod_introdus, is_new, date_teh_ex)
