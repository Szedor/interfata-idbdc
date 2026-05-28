# =========================================================
# core/auth.py
# v.modul.1.0 - Autentificare gate și operator
# =========================================================

import streamlit as st


def check_gate_password(supabase, gate: str, password: str) -> bool:
    """
    Verifică parola de acces pentru un gate (admin, explorator).
    Folosește funcția RPC idbdc_check_gate_password din Supabase.
    """
    try:
        res = supabase.rpc(
            "idbdc_check_gate_password",
            {"p_gate": gate, "p_password": password},
        ).execute()
        return bool(res.data)
    except Exception:
        return False


def identify_operator(supabase, cod: str) -> bool:
    """
    Caută operatorul după cod_operatori în tabela com_operatori.
    Dacă îl găsește, populează session_state și returnează True.
    
    Populează:
        operator_identificat  : nume_prenume
        operator_rol          : ADMIN / OPERATOR
        operator_username     : username_sistem
        operator_filtru_categorie : listă categorii permise
        operator_filtru_tipuri    : listă tipuri permise
    """
    try:
        res = (
            supabase
            .table("com_operatori")
            .select("username_sistem, nume_prenume, rol, filtru_categorie, filtru_proiect")
            .eq("cod_operatori", cod)
            .execute()
        )
        if res.data:
            d = res.data[0]
            st.session_state.operator_identificat = d.get("nume_prenume")
            st.session_state.operator_rol = (d.get("rol") or "OPERATOR").strip()
            st.session_state.operator_username = (d.get("username_sistem") or "").strip()
            raw_cat = d.get("filtru_categorie") or ""
            raw_tip = d.get("filtru_proiect") or ""
            st.session_state.operator_filtru_categorie = [x.strip() for x in raw_cat.split(",") if x.strip()]
            st.session_state.operator_filtru_tipuri = [x.strip() for x in raw_tip.split(",") if x.strip()]
            return True
        return False
    except Exception as e:
        st.sidebar.error(f"Eroare la verificarea operatorului: {e}")
        return False
