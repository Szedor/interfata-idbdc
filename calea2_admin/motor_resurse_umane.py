# =========================================================
# IDBDC/calea2_admin/motor_resurse_umane.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.06.11
# =========================================================
# Motor dedicat pentru gestionarea RESURSE UMANE în Calea2.
# Diferență față de motor.py:
#   - Cheie primară: nr_crt (bigint, autogenerat de BD)
#   - Listare persoane cu căutare după nume
#   - Operațiuni CRUD: Adăugare, Modificare, Ștergere
#   - Fără secțiuni Financiar / Tehnic / Echipă
# =========================================================

import streamlit as st
from domenii.resurse_umane.baza import render as _render_baza


_TABLE = "det_resurse_umane"

_TAB_CSS = """
<style>
[data-testid="stSidebar"] {
    min-width: 320px !important;
    max-width: 320px !important;
    width: 320px !important;
    overflow: hidden !important;
}
[data-testid="stSidebar"] > div:first-child {
    min-width: 320px !important;
    max-width: 320px !important;
    width: 320px !important;
}
</style>
"""


# ── Helpers Supabase ───────────────────────────────────────────────────

def _fetch_all(supabase) -> list:
    """Încarcă toate persoanele, ordonate după nume."""
    try:
        res = (
            supabase.table(_TABLE)
            .select("nr_crt,nume_prenume,email,acronim_functie_upt,acronim_departament")
            .order("nume_prenume")
            .limit(2000)
            .execute()
        )
        return res.data or []
    except Exception:
        return []


def _fetch_one(supabase, nr_crt: int) -> dict:
    """Încarcă o singură persoană după nr_crt."""
    try:
        res = (
            supabase.table(_TABLE)
            .select("*")
            .eq("nr_crt", nr_crt)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else {}
    except Exception:
        return {}


def _save_new(supabase, payload: dict, operator: str) -> tuple:
    """Inserare persoană nouă. Returnează (True, nr_crt) sau (False, mesaj_eroare)."""
    try:
        # nr_crt este autogenerat de BD (bigint serial/identity)
        data = {k: v for k, v in payload.items() if v is not None}
        data["creat_de"]    = operator
        data["modificat_de"] = operator
        res = supabase.table(_TABLE).insert(data).execute()
        if res.data:
            return True, res.data[0].get("nr_crt")
        return False, "Inserarea nu a returnat date."
    except Exception as e:
        return False, str(e)


def _save_update(supabase, nr_crt: int, payload: dict, operator: str) -> tuple:
    """Actualizare persoană existentă. Returnează (True, "Succes") sau (False, mesaj_eroare)."""
    try:
        data = {k: v for k, v in payload.items() if v is not None}
        data["modificat_de"] = operator
        supabase.table(_TABLE).update(data).eq("nr_crt", nr_crt).execute()
        return True, "Succes"
    except Exception as e:
        return False, str(e)


def _delete_person(supabase, nr_crt: int) -> tuple:
    """Ștergere persoană. Returnează (True, "Succes") sau (False, mesaj_eroare)."""
    try:
        supabase.table(_TABLE).delete().eq("nr_crt", nr_crt).execute()
        return True, "Succes"
    except Exception as e:
        return False, str(e)


# ── Motor principal ────────────────────────────────────────────────────

def porneste_motorul_ru(supabase):
    """Punct de intrare pentru modulul Resurse Umane în Calea2."""
    st.markdown(_TAB_CSS, unsafe_allow_html=True)

    is_admin   = st.session_state.get("operator_rol") == "ADMIN"
    operator   = st.session_state.get("operator_username") or "necunoscut"

    # ── Sidebar: mod de lucru ──────────────────────────────────────────
    with st.sidebar:
        st.header("👤 Resurse Umane")
        mod = st.radio(
            "Acțiune",
            ["📋 Listă persoane", "➕ Adaugă persoană", "✏️ Modifică persoană", "🗑️ Șterge persoană"],
            key="ru_mod",
        )

    # ──────────────────────────────────────────────────────────────────
    # MOD 1 — LISTĂ PERSOANE
    # ──────────────────────────────────────────────────────────────────
    if mod == "📋 Listă persoane":
        st.markdown("## 👥 Lista persoanelor înregistrate")

        with st.sidebar:
            cauta = st.text_input("🔍 Caută după nume", key="ru_cauta").strip().lower()

        persoane = _fetch_all(supabase)

        if cauta:
            persoane = [p for p in persoane if cauta in (p.get("nume_prenume") or "").lower()]

        if not persoane:
            st.info("Nu există persoane înregistrate sau nicio potrivire pentru căutare.")
            return

        # Afișare tabel
        st.markdown(
            f"<div style='color:rgba(255,255,255,0.70);font-size:0.88rem;"
            f"margin-bottom:10px;'>Total: <b>{len(persoane)}</b> persoane</div>",
            unsafe_allow_html=True,
        )

        rows_html = ""
        for p in persoane:
            nr       = p.get("nr_crt", "")
            nume     = p.get("nume_prenume", "") or "—"
            email    = p.get("email", "") or "—"
            functie  = p.get("acronim_functie_upt", "") or "—"
            dep      = p.get("acronim_departament", "") or "—"
            rows_html += (
                f"<tr>"
                f"<td style='padding:5px 10px;color:rgba(255,255,255,0.50);font-size:0.80rem;'>{nr}</td>"
                f"<td style='padding:5px 10px;color:#ffffff;font-weight:700;font-size:0.92rem;'>{nume}</td>"
                f"<td style='padding:5px 10px;color:rgba(255,255,255,0.80);font-size:0.88rem;'>{email}</td>"
                f"<td style='padding:5px 10px;color:rgba(255,255,255,0.70);font-size:0.86rem;'>{functie}</td>"
                f"<td style='padding:5px 10px;color:rgba(255,255,255,0.70);font-size:0.86rem;'>{dep}</td>"
                f"</tr>"
            )

        st.markdown(
            f"""
            <table style='width:100%;border-collapse:collapse;'>
            <thead>
            <tr style='background:rgba(255,255,255,0.12);'>
            <th style='padding:6px 10px;text-align:left;color:rgba(255,255,255,0.60);
                font-size:0.76rem;text-transform:uppercase;'>NR</th>
            <th style='padding:6px 10px;text-align:left;color:rgba(255,255,255,0.60);
                font-size:0.76rem;text-transform:uppercase;'>NUME ȘI PRENUME</th>
            <th style='padding:6px 10px;text-align:left;color:rgba(255,255,255,0.60);
                font-size:0.76rem;text-transform:uppercase;'>EMAIL</th>
            <th style='padding:6px 10px;text-align:left;color:rgba(255,255,255,0.60);
                font-size:0.76rem;text-transform:uppercase;'>FUNCȚIE</th>
            <th style='padding:6px 10px;text-align:left;color:rgba(255,255,255,0.60);
                font-size:0.76rem;text-transform:uppercase;'>DEPARTAMENT</th>
            </tr>
            </thead>
            <tbody>{rows_html}</tbody>
            </table>
            """,
            unsafe_allow_html=True,
        )

    # ──────────────────────────────────────────────────────────────────
    # MOD 2 — ADAUGĂ PERSOANĂ
    # ──────────────────────────────────────────────────────────────────
    elif mod == "➕ Adaugă persoană":
        st.markdown("## ➕ Adaugă persoană nouă")

        with st.sidebar:
            btn_save = st.button("💾 SALVEAZĂ", use_container_width=True, type="primary", key="ru_btn_add")

        # Marker unic pentru câmpuri noi (nu are nr_crt încă)
        _KEY = "RU_NOU"

        payload = _render_baza(
            supabase       = supabase,
            nr_crt         = _KEY,
            is_new         = True,
            date_existente = {},
        )

        if btn_save:
            if not payload.get("nume_prenume"):
                st.error("Numele și prenumele sunt obligatorii.")
            else:
                ok, rezultat = _save_new(supabase, payload, operator)
                if ok:
                    st.session_state["ru_msg"] = ("success", f"Persoană adăugată cu succes. Nr.crt: {rezultat}")
                    # Resetăm câmpurile ștergând cheile din session_state
                    for k in list(st.session_state.keys()):
                        if k.startswith(f"ru_") and k.endswith(f"_{_KEY}"):
                            del st.session_state[k]
                    st.rerun()
                else:
                    st.error(f"Eroare la salvare: {rezultat}")

    # ──────────────────────────────────────────────────────────────────
    # MOD 3 — MODIFICĂ PERSOANĂ
    # ──────────────────────────────────────────────────────────────────
    elif mod == "✏️ Modifică persoană":
        st.markdown("## ✏️ Modifică datele unei persoane")

        persoane = _fetch_all(supabase)
        optiuni  = {f"{p['nr_crt']} — {p.get('nume_prenume', '')}": p["nr_crt"] for p in persoane}

        with st.sidebar:
            sel = st.selectbox(
                "Selectează persoana",
                options=["— alege —"] + list(optiuni.keys()),
                key="ru_sel_mod",
            )
            btn_save = st.button("💾 SALVEAZĂ MODIFICĂRILE", use_container_width=True,
                                 type="primary", key="ru_btn_mod")

        if sel == "— alege —":
            st.info("Selectează persoana din meniul lateral.")
            return

        nr_crt     = optiuni[sel]
        date_ex    = _fetch_one(supabase, nr_crt)

        if not date_ex:
            st.warning("Persoana nu a fost găsită în baza de date.")
            return

        payload = _render_baza(
            supabase       = supabase,
            nr_crt         = nr_crt,
            is_new         = False,
            date_existente = date_ex,
        )

        if btn_save:
            if not payload.get("nume_prenume"):
                st.error("Numele și prenumele sunt obligatorii.")
            else:
                ok, msg = _save_update(supabase, nr_crt, payload, operator)
                if ok:
                    st.session_state["ru_msg"] = ("success", f"Datele pentru «{payload.get('nume_prenume')}» au fost actualizate.")
                    st.rerun()
                else:
                    st.error(f"Eroare la salvare: {msg}")

    # ──────────────────────────────────────────────────────────────────
    # MOD 4 — ȘTERGE PERSOANĂ
    # ──────────────────────────────────────────────────────────────────
    elif mod == "🗑️ Șterge persoană":
        if not is_admin:
            st.warning("⚠️ Ștergerea este permisă exclusiv operatorilor cu rol ADMIN.")
            return

        st.markdown("## 🗑️ Șterge persoană")

        persoane = _fetch_all(supabase)
        optiuni  = {f"{p['nr_crt']} — {p.get('nume_prenume', '')}": p["nr_crt"] for p in persoane}

        with st.sidebar:
            sel = st.selectbox(
                "Selectează persoana",
                options=["— alege —"] + list(optiuni.keys()),
                key="ru_sel_del",
            )

        if sel == "— alege —":
            st.info("Selectează persoana din meniul lateral.")
            return

        nr_crt  = optiuni[sel]
        date_ex = _fetch_one(supabase, nr_crt)
        nume    = date_ex.get("nume_prenume", str(nr_crt))

        st.markdown(
            f"<div style='background:rgba(255,80,80,0.12);border:1px solid rgba(255,80,80,0.50);"
            f"border-radius:10px;padding:12px 18px;margin-bottom:12px;'>"
            f"<span style='color:#ff8888;font-weight:700;font-size:0.97rem;'>"
            f"⚠️ Atenție: urmează ștergerea definitivă a persoanei:<br>"
            f"<span style='font-size:1.05rem;color:#ffffff;'>{nome}</span>"
            f"</span></div>".replace("nome", nome),
            unsafe_allow_html=True,
        )

        confirmare = st.checkbox(
            f"Confirm ștergerea definitivă a lui {nume} din baza de date",
            key="ru_confirm_del",
        )

        if confirmare:
            if st.button("🗑️ ȘTERGE DEFINITIV", type="primary", key="ru_btn_del"):
                ok, msg = _delete_person(supabase, nr_crt)
                if ok:
                    st.session_state["ru_msg"] = ("success", f"Persoana «{nume}» a fost ștearsă.")
                    st.rerun()
                else:
                    st.error(f"Eroare la ștergere: {msg}")

    # ── Mesaje de feedback ─────────────────────────────────────────────
    if "ru_msg" in st.session_state:
        tip, text = st.session_state.pop("ru_msg")
        if tip == "success":
            st.markdown(
                f"<div style='background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.45);"
                f"border-radius:10px;padding:10px 16px;margin-top:12px;display:inline-block;'>"
                f"<span style='color:#4ade80;font-weight:700;font-size:0.95rem;'>✅ {text}</span></div>",
                unsafe_allow_html=True,
            )
        else:
            st.error(text)
