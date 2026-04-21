# =========================================================
# admin/fise/contracte_terti.py
# v.modul.1.0 - Fațadă pentru Contracte TERTI
# =========================================================
# Acest fișier este un adaptor subțire care folosește funcțiile comune.
# Nu conține logică duplicată.
# =========================================================

from utils.contracte_common import render_date_de_baza, render_date_financiare, render_echipa

def render(supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex, date_fin_ex, date_echipa_ex):
    baza = render_date_de_baza(
        supabase=supabase,
        cod_introdus=cod_introdus,
        cat_sel=cat_sel,
        tip_label="TERȚI",
        tabela_nume="base_contracte_terti",
        is_new=is_new,
        date_existente=date_baza_ex
    )
    financiar = render_date_financiare(supabase, cod_introdus, is_new, date_fin_ex)
    echipa = render_echipa(supabase, cod_introdus, is_new, date_echipa_ex)
    return {"baza": baza, "financiar": financiar, "echipa": echipa}
