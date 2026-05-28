# =========================================================
# domenii/contracte_cep/admin.py
# v.modul.1.0 - Admin Contracte CEP
# =========================================================

from domenii._baza.sectiune_baza import render_date_de_baza
from domenii._baza.sectiune_financiar import render_date_financiare
from domenii._baza.sectiune_echipa import render_echipa
from domenii.contracte_cep.definitie import TIP_LABEL, BASE_TABLE, get_label

def render_date_de_baza(supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex):
    return render_date_de_baza(
        supabase=supabase,
        cod_introdus=cod_introdus,
        cat_sel=cat_sel,
        tip_label=TIP_LABEL,
        tabela_nume=BASE_TABLE,
        fields=FIELDS_BAZA,
        is_new=is_new,
        date_existente=date_baza_ex
    )

def render_date_financiare(supabase, cod_introdus, is_new, date_fin_ex):
    return render_date_financiare(supabase, cod_introdus, is_new, date_fin_ex)

def render_echipa(supabase, cod_introdus, is_new, date_echipa_ex):
    return render_echipa(supabase, cod_introdus, is_new, date_echipa_ex)
