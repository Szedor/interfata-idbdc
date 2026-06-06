# =========================================================
# IDBDC/domenii/proprietate_industriala/admin.py
# VERSIUNE: 2.0
# STATUS: CORECTAT - importuri aliniate cu fisierele existente
# DATA: 2026.06.06
# =========================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from domenii.proprietate_industriala.baza  import render_generale, render_suplimentare
from domenii._baza.echipa                  import render as _render_echipa
from domenii.proprietate_industriala.definitie import BASE_TABLE


def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex):
    """Tab 1 — Date de baza (vizibil si in Calea1)."""
    return render_generale(
        supabase=supabase,
        cod_introdus=cod_introdus,
        cat_sel=cat_sel,
        tabela_nume=BASE_TABLE,
        is_new=is_new,
        date_existente=date_baza_ex,
    )


def render_date_suplimentare(supabase, cod_introdus, is_new, date_baza_ex):
    """Tab 2 — Date suplimentare (NUMAI Calea2 / Admin)."""
    return render_suplimentare(
        supabase=supabase,
        cod_introdus=cod_introdus,
        tabela_nume=BASE_TABLE,
        is_new=is_new,
        date_existente=date_baza_ex,
    )


def render_echipa(supabase, cod_introdus, is_new, date_echipa_ex):
    """Tab 3 — Echipa."""
    return _render_echipa(supabase, cod_introdus, is_new, date_echipa_ex)
