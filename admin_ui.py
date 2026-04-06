# =========================================================
# ADMIN UI — helperi de afisare pentru c2
# =========================================================

import streamlit as st

from admin_rules import (
    get_hidden_tabs,
    get_financial_mode,
    is_multiyear_financial_type,
    tab_is_visible,
)


# ---------------------------------------------------------
# TAB-URI VIZIBILE
# ---------------------------------------------------------

def get_visible_tabs(category: str, tabs: list[str]) -> list[str]:
    hidden = get_hidden_tabs(category)
    return [t for t in tabs if t not in hidden]


# ---------------------------------------------------------
# NUMAR RANDURI AFISATE
# ---------------------------------------------------------

def get_editor_height(table_name: str) -> int:
    """
    Returneaza inaltimea editorului in pixeli.
    """

    table_name = (table_name or "").strip().lower()

    if table_name == "com_echipe_proiect":
        return 245

    if table_name == "com_aspecte_tehnice":
        return 320

    if table_name == "com_date_financiare":
        return 320

    return 360


# ---------------------------------------------------------
# TITLURI TAB-URI
# ---------------------------------------------------------

def get_tab_title(tab_name: str, category: str = "", tip: str = "") -> str:
    """
    Returneaza titlul afisat pentru tab.
    """

    if tab_name == "Date de baza":
        return "📄 Date de baza"

    if tab_name == "Date financiare":
        if is_multiyear_financial_type(tip):
            return "💰 Date financiare multianuale"
        return "💰 Date financiare"

    if tab_name == "Echipa":
        return "👥 Echipa"

    if tab_name == "Aspecte tehnice":
        return "🧪 Aspecte tehnice"

    return tab_name


# ---------------------------------------------------------
# MESAJE AJUTATOARE
# ---------------------------------------------------------

def render_financial_info_box(project_type: str):
    """
    Afiseaza un mesaj explicativ pentru proiectele multianuale.
    """

    mode = get_financial_mode(project_type)

    if mode != "multianual":
        return

    st.info(
        "Pentru acest tip de proiect se recomanda completarea atat a "
        "valorilor totale, cat si a valorilor anuale."
    )


def render_team_info_box():
    st.caption(
        "Pentru echipe mai mari de 5 persoane poti adauga randuri noi "
        "prin scroll sau PgDn."
    )


def render_light_category_info(category: str):
    """
    Mesaj simplu pentru categoriile fara Echipa si Aspecte tehnice.
    """

    if category not in [
        "Evenimente stiintifice",
        "Proprietate intelectuala",
    ]:
        return

    st.caption(
        "Pentru aceasta categorie sunt necesare doar Date de baza "
        "si Date financiare."
    )


# ---------------------------------------------------------
# TAB-URI
# ---------------------------------------------------------

def create_tabs(category: str, tab_names: list[str]):
    """
    Creeaza doar tab-urile vizibile.
    """

    visible_tabs = get_visible_tabs(category, tab_names)

    if not visible_tabs:
        return [], []

    streamlit_tabs = st.tabs(visible_tabs)

    return visible_tabs, streamlit_tabs
