# =========================================================
# IDBDC/domenii/contracte_cep/admin.py
# VERSIUNE: 1.1
# STATUS: CORECTAT - RecursionError la render_echipa eliminat
# DATA: 2026.05.09
# =========================================================
# CONȚINUT:
#   Randează toate secțiunile editabile pentru Contracte CEP
#   în Calea2 (Administrare). Apelează exclusiv componentele
#   din domenii/_baza/ și constantele din definitie.py.
#
# MODIFICĂRI VERSIUNEA 1.1:
#   - CORECȚIE: importurile din _baza redenumite cu prefix
#     _baza_ pentru a evita conflictul de nume între funcția
#     locală render_echipa și cea importată din _baza,
#     care provoca RecursionError (apel infinit pe sine).
# =========================================================

from domenii.contracte_cep.definitie             import TIP_LABEL, BASE_TABLE
from domenii._baza.sectiune_baza_contracte       import render as _baza_render_baza
from domenii._baza.sectiune_financiar_contracte  import render as _baza_render_financiar
from domenii._baza.sectiune_echipa               import render as _baza_render_echipa


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
