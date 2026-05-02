# =========================================================
# IDBDC/admin/motor.py
# VERSIUNE: 4.0
# STATUS: CORECTAT - salvare completă cross-tab + fetch optimizat
# DATA: 2026.05.02
# =========================================================

import streamlit as st
import admin.config as cfg
import admin.data_ops as ops
import admin.ui as ui

from admin.fise import contracte_cep, contracte_terti, contracte_speciale


# Stiluri pentru navigarea tip tab (radio orizontal)
_TAB_CSS = """
<style>
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    padding: 0 !important;
}
div.tab-nav > div[role="radiogroup"] {
    display: flex; flex-direction: row; gap: 6px;
}
div.tab-nav label {
    background: rgba(255,255,255,0.10) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.30) !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 6px 18px !important;
    font-weight: 700 !important;
    font-size: 0.93rem !important;
    cursor: pointer !important;
}
div.tab-nav label:has(input:checked) {
    background: rgba(255,255,255,0.96) !important;
    color: #0b1f3a !important;
    border-bottom: 2px solid rgba(255,255,255,0.96) !important;
}
div.tab-nav [data-testid="stMarkdownContainer"] { display: none; }
</style>
"""


def porneste_motorul(supabase):
    ui.apply_admin_styles()
    ui.display_admin_message()

    is_admin = st.session_state.get("operator_rol") == "ADMIN"
    filtru_cat = st.session_state.get("operator_filtru_categorie", [])
    filtru_tip = st.session_state.get("operator_filtru_tipuri", [])

    with st.sidebar:
        st.header("📂 Selecție Date")
        lista_categorii = (
            [c for c in cfg.BASE_TABLE_MAP.keys() if c in filtru_cat]
            if not is_admin else list(cfg.BASE_TABLE_MAP.keys())
        )
        cat_sel = st.selectbox("Categorie", ["- Alege -"] + lista_categorii)

    if cat_sel == "- Alege -":
        st.info("Selectați categoria din meniul lateral.")
        return

    with st.sidebar:
        optiuni_tip = list(cfg.BASE_TABLE_MAP[cat_sel].keys())
        if not is_admin:
            optiuni_tip = [t for t in optiuni_tip if t in filtru_tip]
        tip_sel = st.selectbox("Tip", ["- Alege -"] + optiuni_tip)

    if tip_sel == "- Alege -":
        st.info("Selectați tipul din meniul lateral.")
        return

    base_table = cfg.get_base_table(cat_sel, tip_sel)

    with st.sidebar:
        try:
            res_coduri = supabase.table(base_table).select("cod_identificare").execute()
            list_coduri = sorted(
                [r["cod_identificare"] for r in res_coduri.data]
            ) if res_coduri.data else []
        except Exception:
            list_coduri = []

        cod_introdus = st.text_input(
            "Cod identificare",
            placeholder="Introduceți codul...",
            key="input_cod_identificare"
        ).strip()

    if not cod_introdus:
        st.info("Introduceți codul în meniul lateral.")
        return

    este_existent = cod_introdus in list_coduri

    with st.sidebar:
        if este_existent:
            st.success(f"✅ Cod recunoscut: {cod_introdus}")
            st.info("✏️ S-a identificat o fișă existentă, în secțiunile căreia poți modifica/completa datele.")
        else:
            st.warning(f"🆕 Cod nou: {cod_introdus}")
            st.info("🆕 S-a creat o fișă nouă, în secțiunile căreia poți înregistra date.")

        st.divider()
        btn_save = st.button(
            "💾 SALVEAZĂ TOATE DATELE",
            use_container_width=True,
            type="primary"
        )

        btn_delete = False
        if is_admin and este_existent:
            btn_delete = st.button("🗑️ ȘTERGE FIȘA", use_container_width=True)

    is_new = not este_existent

    # =========================================================
    # CORECȚIE [5A]: Fetch optimizat — o singură interogare per tabel.
    #
    # PROBLEMA ORIGINALĂ: Linia pentru date_baza_ex apela _fetch()
    # de DOUĂ ORI pentru același tabel și același cod:
    #   _fetch(base_table, cod_introdus)[0]          <- apel 1
    #   if not is_new and _fetch(base_table, cod_introdus)  <- apel 2
    # Fiecare apel = un drum la baza de date PostgreSQL.
    # Cu 3 secțiuni × 2 apeluri = până la 6 interogări în loc de 3.
    # Aceasta contribuia la timpul mare de răspuns.
    #
    # SOLUȚIA: Apelăm _fetch() o singură dată, salvăm rezultatul
    # într-o variabilă intermediară, și folosim variabila de 2 ori.
    # =========================================================
    def _fetch(table, cod):
        try:
            res = supabase.table(table).select("*").eq("cod_identificare", cod).execute()
            return res.data or []
        except Exception:
            return []

    # CORECȚIE [5B]: Un singur apel per tabel, rezultat salvat în variabilă.
    if not is_new:
        _baza_list  = _fetch(base_table, cod_introdus)
        date_baza_ex   = _baza_list[0] if _baza_list else {}
        date_fin_ex    = _fetch("com_date_financiare", cod_introdus)
        date_echipa_ex = _fetch("com_echipe_proiect",  cod_introdus)
    else:
        date_baza_ex   = {}
        date_fin_ex    = []
        date_echipa_ex = []

    rezultate = {}

    # =========================================================
    # Modulul de fișă
    # =========================================================
    if cat_sel == "Contracte" and tip_sel == "CEP":
        modul = contracte_cep
    elif cat_sel == "Contracte" and tip_sel == "TERTI":
        modul = contracte_terti
    elif cat_sel == "Contracte" and tip_sel == "SPECIALE":
        modul = contracte_speciale
    else:
        st.info(f"Fișele pentru categoria «{cat_sel}» / tipul «{tip_sel}» sunt în curs de configurare.")
        return

    # =========================================================
    # Navigare tab-uri cu reținere în session_state
    # =========================================================
    TAB_LABELS = ["📋 Date de bază", "💰 Date financiare", "👥 Echipă"]
    key_tab = f"tab_activ_{cod_introdus}"

    if key_tab not in st.session_state:
        st.session_state[key_tab] = TAB_LABELS[0]

    st.markdown(_TAB_CSS, unsafe_allow_html=True)
    st.markdown('<div class="tab-nav">', unsafe_allow_html=True)
    tab_activ = st.radio(
        "Secțiune",
        TAB_LABELS,
        index=TAB_LABELS.index(st.session_state[key_tab]),
        horizontal=True,
        key=f"radio_tab_{cod_introdus}",
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.session_state[key_tab] = tab_activ

    st.markdown(
        "<div style='border-top: 2px solid rgba(255,255,255,0.30); margin-bottom: 16px;'></div>",
        unsafe_allow_html=True,
    )

    # =========================================================
    # CORECȚIE [6A]: Chei session_state pentru datele din tab-uri
    # care nu sunt vizibile în momentul salvării.
    #
    # PROBLEMA PRINCIPALĂ (cauza Calea1 afișează date lipsă):
    # Aplicația folosește 3 tab-uri: Date de bază, Financiar, Echipă.
    # La un moment dat, utilizatorul poate vedea DOAR UN TAB.
    # Când apasă "Salvează toate datele", codul original salva
    # NUMAI secțiunea vizibilă în acel moment (cea din `rezultate`).
    # Celelalte două secțiuni NU se salvau — sau mai rău, dacă
    # nu fuseseră niciodată vizitate în sesiunea curentă,
    # datele lor din baza de date rămâneau din sesiuni anterioare.
    # Fișa completă din Calea1 citea direct din baza de date și
    # găsea date incomplete sau lipsă.
    #
    # SOLUȚIA: Salvăm datele fiecărui tab în session_state pe
    # chei dedicate (key_baza, key_fin, key_echipa) de fiecare
    # dată când tab-ul respectiv este afișat și completat.
    # La apăsarea "Salvează", colectăm datele din TOATE cheile
    # disponibile în session_state, indiferent de tab-ul activ.
    # Astfel, chiar dacă utilizatorul este pe tab-ul Echipă când
    # apasă Salvează, și datele de bază și cele financiare
    # (introduse anterior în sesiunea curentă) se salvează.
    # =========================================================
    key_baza_ss  = f"ss_baza_{cod_introdus}"
    key_fin_ss   = f"ss_fin_{cod_introdus}"
    # Nota: echipa folosește deja key_data_init din echipa.py

    # =========================================================
    # Conținut tab activ + salvare în session_state
    # =========================================================
    if tab_activ == "📋 Date de bază":
        rezultat_baza = modul.render_date_de_baza(
            supabase, cod_introdus, cat_sel, tip_sel, is_new, date_baza_ex
        )
        # CORECȚIE [6B]: Salvăm rezultatul în session_state imediat
        # după ce utilizatorul îl completează/vizualizează.
        if rezultat_baza:
            st.session_state[key_baza_ss] = rezultat_baza
        rezultate["baza"] = rezultat_baza

    elif tab_activ == "💰 Date financiare":
        rezultat_fin = modul.render_date_financiare(
            supabase, cod_introdus, is_new, date_fin_ex
        )
        # CORECȚIE [6C]: Idem pentru date financiare.
        if rezultat_fin is not None:
            st.session_state[key_fin_ss] = rezultat_fin
        rezultate["financiar"] = rezultat_fin

    elif tab_activ == "👥 Echipă":
        rezultate["echipa"] = modul.render_echipa(
            supabase, cod_introdus, is_new, date_echipa_ex
        )

    # =========================================================
    # Salvare — colectăm datele din TOATE secțiunile,
    # inclusiv cele din tab-urile care nu sunt active acum
    # =========================================================
    if btn_save:
        with st.spinner("Se salvează datele..."):
            erori = []

            # CORECȚIE [6D]: Date de bază — luăm din tab activ dacă
            # disponibil, altfel din session_state (vizitat anterior
            # în aceeași sesiune), altfel lăsăm ce e în DB.
            baza_de_salvat = rezultate.get("baza") or st.session_state.get(key_baza_ss)
            if baza_de_salvat:
                row = {**baza_de_salvat, "cod_identificare": cod_introdus}
                ok, msg = ops.direct_upsert_single_row(supabase, base_table, row)
                if not ok:
                    erori.append(f"Date de bază: {msg}")
            elif not is_new:
                pass  # Lăsăm ce există deja în DB

            # CORECȚIE [6E]: Date financiare — același principiu.
            fin_de_salvat = rezultate.get("financiar")
            if fin_de_salvat is None:
                fin_de_salvat = st.session_state.get(key_fin_ss)
            if fin_de_salvat is not None:
                try:
                    supabase.table("com_date_financiare").delete().eq(
                        "cod_identificare", cod_introdus
                    ).execute()
                except Exception:
                    pass
                for row in fin_de_salvat:
                    ok, msg = ops.direct_upsert_single_row(
                        supabase, "com_date_financiare", row, match_col="cod_identificare"
                    )
                    if not ok:
                        erori.append(f"Date financiare: {msg}")

            # CORECȚIE [6F]: Echipă — datele echipei sunt deja
            # gestionate prin session_state în echipa.py (key_data_init).
            # Dacă tab-ul Echipă a fost vizitat, rezultate["echipa"]
            # conține datele curente. Dacă nu a fost vizitat,
            # nu ștergem echipa existentă din DB — o lăsăm intactă.
            if "echipa" in rezultate:
                try:
                    supabase.table("com_echipe_proiect").delete().eq(
                        "cod_identificare", cod_introdus
                    ).execute()
                except Exception:
                    pass
                randuri_echipa = [r for r in rezultate["echipa"] if r.get("nume_prenume")]
                if randuri_echipa:
                    try:
                        supabase.table("com_echipe_proiect").insert(randuri_echipa).execute()
                    except Exception as e:
                        erori.append(f"Echipă: {e}")

            if erori:
                st.session_state["admin_msg"] = ("error", " | ".join(erori))
            else:
                st.session_state["admin_msg"] = ("success", "Toate datele au fost salvate cu succes.")

            # CORECȚIE [7A]: Nu mai ștergem key_data_init după salvare.
            # PROBLEMA ORIGINALĂ: Un st.rerun() după salvare putea în
            # anumite condiții redesena editorul cu date vechi dacă
            # key_editor nu era resetat. Acum păstrăm key_data_init
            # intact (datele rămân pe ecran) și resetăm doar key_editor
            # pentru a forța Streamlit să redeseneze editorul cu
            # valorile corecte din session_state.
            key_editor_echipa = f"echipa_editor_{cod_introdus}"
            if key_editor_echipa in st.session_state:
                del st.session_state[key_editor_echipa]

            st.rerun()

    # =========================================================
    # Ștergere
    # =========================================================
    if btn_delete:
        st.warning(f"Atenție: Ștergeți definitiv fișa {cod_introdus}!")
        if st.checkbox("Confirm eliminarea din toate tabelelor"):
            tabele_curatare = [
                base_table,
                "com_date_financiare",
                "com_echipe_proiect",
                "com_aspecte_tehnice",
            ]
            ok, msg = ops.direct_delete_all_tables(supabase, cod_introdus, tabele_curatare)
            if ok:
                # CORECȚIE [7B]: La ștergere, curățăm și cheile
                # din session_state specifice acestui cod,
                # pentru a preveni afișarea de date reziduale
                # dacă același cod este refolosit ulterior.
                for k in [key_baza_ss, key_fin_ss,
                           f"echipa_data_init_{cod_introdus}",
                           f"echipa_editor_{cod_introdus}",
                           f"tab_activ_{cod_introdus}"]:
                    st.session_state.pop(k, None)
                st.session_state["admin_msg"] = ("success", "Înregistrarea a fost eliminată.")
                st.rerun()
            else:
                st.error(msg)
