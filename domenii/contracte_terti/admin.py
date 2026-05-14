# =========================================================
# IDBDC/domenii/contracte_terti/admin.py
# VERSIUNE: 1.0
# STATUS: NOU - ecran administrare Contracte TERȚI
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Orchestrare secțiuni editabile pentru Contracte TERȚI
#   în Calea2. Apelează componentele din domenii/_baza/.
#   Câmpul în plus față de CEP (DERULAT PRIN) este gestionat
#   de sectiune_baza_contracte prin date_existente.
# =========================================================

from domenii.contracte_terti.definitie              import TIP_LABEL, BASE_TABLE
from domenii._baza.sectiune_baza_contracte          import render as _baza_render_baza
from domenii._baza.sectiune_financiar_contracte     import render as _baza_render_financiar
from domenii._baza.sectiune_echipa                  import render as _baza_render_echipa


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
