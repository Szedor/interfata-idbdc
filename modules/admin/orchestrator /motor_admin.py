from __future__ import annotations

from datetime import date, datetime
import math

import pandas as pd
import streamlit as st

from modules.admin.admin_helpers import (
    append_observatii,
    cleanup_payload,
    is_row_effectively_empty,
    now_iso,
)
from modules.admin.contract_proiect_like.contract_proiect_like_builder import (
    ContractProiectLikeBuilder,
    build_contract_proiect_like,
)


def porneste_motorul(supabase):
    ADMIN_ONLY_COLS = {
        "responsabil_idbdc",
        "observatii_idbdc",
        "status_confirmare",
        "data_ultimei_modificari",
        "validat_idbdc",
        "creat_de",
        "creat_la",
        "modificat_de",
        "modificat_la",
    }

    is_admin = st.session_state.get("operator_rol") == "ADMIN"

    def get_table_columns(table_name: str) -> list[str]:
        try:
            res = supabase.rpc(
                "idbdc_get_columns",
                {"p_table": table_name},
            ).execute()
            return [r["column_name"] for r in (res.data or []) if r.get("column_name")]
        except Exception:
            return []

    def hide_control_cols(df: pd.DataFrame) -> pd.DataFrame:
        if is_admin:
            return df
        cols = [c for c in df.columns if c not in ADMIN_ONLY_COLS]
        return df[cols] if cols else df

    def _is_missing(v) -> bool:
        if v is None:
            return True

        try:
            if pd.isna(v):
                return True
        except Exception:
            pass

        if isinstance(v, str) and v.strip().lower() in ("", "nan", "nat", "none"):
            return True

        return False

    def _json_safe_value(v):
        if v is None:
            return None

        try:
            if pd.isna(v):
                return None
        except Exception:
            pass

        if hasattr(v, "item"):
            try:
                v = v.item()
            except Exception:
                pass

        if isinstance(v, pd.Timestamp):
            if pd.isna(v):
                return None
            return v.strftime("%Y-%m-%d")

        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d")

        if isinstance(v, date):
            return v.strftime("%Y-%m-%d")

        try:
            import numpy as np

            if isinstance(v, np.integer):
                return int(v)

            if isinstance(v, np.floating):
                v = float(v)
        except Exception:
            pass

        if isinstance(v, float):
            if math.isnan(v) or math.isinf(v):
                return None
            return v

        if isinstance(v, str):
            s = v.strip()
            if s.lower() in ("nan", "nat", "none", ""):
                return None
            return s

        return v

    def _sanitize_payload(payload: dict) -> dict:
        out = {}
        for k, v in (payload or {}).items():
            out[k] = _json_safe_value(v)
        return out

    def _has_meaningful_data(payload: dict, *, ignore_fields: set[str] | None = None) -> bool:
        ignore_fields = ignore_fields or set()

        for k, v in (payload or {}).items():
            if k in ignore_fields:
                continue
            if not _is_missing(v):
                return True

        return False

    def direct_upsert_single_row(table_name: str, payload: dict, cod: str):
        try:
            check = (
                supabase.table(table_name)
                .select("cod_identificare")
                .eq("cod_identificare", cod)
                .limit(1)
                .execute()
            )
            exists = bool(check.data)
        except Exception:
            exists = False

        if exists:
            try:
                supabase.table(table_name).update(payload).eq(
                    "cod_identificare",
                    cod,
                ).execute()
                return
            except Exception as e:
                raise Exception(f"Update eșuat pe {table_name}: {e}") from e
        else:
            try:
                supabase.table(table_name).insert(payload).execute()
                return
            except Exception as e:
                raise Exception(f"Insert eșuat pe {table_name}: {e}") from e

    def direct_save_all_tables(items: list, operator: str) -> tuple[bool, str]:
        if not items:
            return False, "Nu există date de salvat."

        by_table: dict[str, list[dict]] = {}
        for it in items:
            t = it.get("table")
            p = it.get("payload") or {}
            if not t or not isinstance(p, dict):
                continue
            by_table.setdefault(t, [])
            by_table[t].append(p)

        errors = []
        ok_any = False
        edit_msg = f"Editat de {operator} @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        ignore_fields_common = {
            "cod_identificare",
            "id_proiect_contract_sursa",
            "nr_crt",
            "observatii_idbdc",
            "data_ultimei_modificari",
            "validat_idbdc",
            "status_confirmare",
            "responsabil_idbdc",
            "creat_de",
            "creat_la",
            "modificat_de",
            "modificat_la",
        }

        for table_name, payloads in by_table.items():
            try:
                cols_real = set(get_table_columns(table_name))
                if "cod_identificare" not in cols_real:
                    continue

                clean_payloads = []

                for p in payloads:
                    cod_local = str(p.get("cod_identificare", "")).strip()
                    if not cod_local:
                        continue

                    cp = {k: p.get(k) for k in cols_real if k in p}
                    cp["cod_identificare"] = cod_local

                    if "data_ultimei_modificari" in cols_real:
                        cp["data_ultimei_modificari"] = now_iso()

                    if "observatii_idbdc" in cols_real:
                        cp["observatii_idbdc"] = append_observatii(
                            cp.get("observatii_idbdc"),
                            edit_msg,
                        )

                    cp = cleanup_payload(cp)
                    cp = _sanitize_payload(cp)

                    cp = {
                        k: v
                        for k, v in cp.items()
                        if not (
                            isinstance(v, str)
                            and v.strip().lower() in ("nan", "nat", "none")
                        )
                    }

                    if table_name == "com_date_financiare":
                        financial_fields = {
                            k: v
                            for k, v in cp.items()
                            if k not in ignore_fields_common | {"valuta"}
                        }

                        has_real_financial_data = any(
                            v is not None and str(v).strip() not in ("", "nan", "None")
                            for v in financial_fields.values()
                        )

                        if not has_real_financial_data:
                            continue

                        if "valuta" in cols_real:
                            valuta_curenta = cp.get("valuta")
                            if valuta_curenta is None or str(valuta_curenta).strip() in ("", "nan", "None"):
                                cp["valuta"] = "LEI"

                    elif table_name == "com_aspecte_tehnice":
                        if not _has_meaningful_data(cp, ignore_fields=ignore_fields_common):
                            continue

                    elif table_name == "com_echipe_proiect":
                        team_ignore = ignore_fields_common | {"persoana_contact", "functie_upt"}
                        if not _has_meaningful_data(cp, ignore_fields=team_ignore):
                            continue

                    else:
                        if is_row_effectively_empty(cp):
                            continue

                    if is_row_effectively_empty(cp) and not _has_meaningful_data(
                        cp,
                        ignore_fields=ignore_fields_common,
                    ):
                        continue

                    clean_payloads.append(cp)

                if not clean_payloads:
                    continue

                cod0 = str(clean_payloads[0].get("cod_identificare", "")).strip()

                if len(clean_payloads) > 1:
                    try:
                        supabase.table(table_name).delete().eq(
                            "cod_identificare",
                            cod0,
                        ).execute()
                    except Exception:
                        pass

                    supabase.table(table_name).insert(clean_payloads).execute()
                    ok_any = True
                    continue

                direct_upsert_single_row(table_name, clean_payloads[0], cod0)
                ok_any = True

            except Exception as e:
                errors.append(f"{table_name}: {e}")

        if not ok_any and errors:
            return False, " | ".join(errors)
        if not ok_any:
            return False, "Nu s-a putut salva (nicio operație aplicată)."
        if errors:
            return True, f"Salvare parțială: {' | '.join(errors)}"
        return True, "Salvarea realizată cu succes."

    def direct_validate_all_tables(cod: str, table_names: list[str], operator: str) -> tuple[bool, str]:
        ok_any = False
        errors = []
        msg = f"Validat de {operator} @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        for t in table_names:
            try:
                cols = set(get_table_columns(t))
                if "cod_identificare" not in cols:
                    continue

                payload = {}

                if "validat_idbdc" in cols:
                    payload["validat_idbdc"] = True
                if "data_ultimei_modificari" in cols:
                    payload["data_ultimei_modificari"] = now_iso()
                if "observatii_idbdc" in cols:
                    try:
                        cur = (
                            supabase.table(t)
                            .select("observatii_idbdc")
                            .eq("cod_identificare", cod)
                            .limit(1)
                            .execute()
                        )
                        existing = ""
                        if cur.data and isinstance(cur.data, list) and len(cur.data) > 0:
                            existing = cur.data[0].get("observatii_idbdc") or ""
                        payload["observatii_idbdc"] = append_observatii(existing, msg)
                    except Exception:
                        payload["observatii_idbdc"] = msg

                payload = cleanup_payload(payload)
                payload = _sanitize_payload(payload)

                if not payload:
                    continue

                supabase.table(t).update(payload).eq("cod_identificare", cod).execute()
                ok_any = True

            except Exception as e:
                errors.append(f"{t}: {e}")

        if not ok_any and errors:
            return False, " | ".join(errors)
        if not ok_any:
            return False, "Nu s-a putut valida (nu există coloane compatibile în tabelele selectate)."
        if errors:
            return True, f"Validare parțială: {' | '.join(errors)}"
        return True, "Validare realizată."

    def direct_delete_all_tables(cod: str, table_names: list[str]) -> tuple[bool, str]:
        ok_any = False
        errors = []

        for t in table_names:
            try:
                cols = set(get_table_columns(t))
                if "cod_identificare" not in cols:
                    continue
                supabase.table(t).delete().eq("cod_identificare", cod).execute()
                ok_any = True
            except Exception as e:
                errors.append(f"{t}: {e}")

        if not ok_any and errors:
            return False, " | ".join(errors)
        if not ok_any:
            return False, "Nu s-a șters nimic."
        if errors:
            return True, f"Ștergere parțială: {' | '.join(errors)}"
        return True, "Fișa a fost ștearsă."

    st.markdown(
        """
        <style>
          [data-testid="stSidebar"] {
            background: #0b2a52 !important;
            border-right: 2px solid rgba(255,255,255,0.20);
          }
          [data-testid="stSidebar"] .stMarkdown,
          [data-testid="stSidebar"] label,
          [data-testid="stSidebar"] p,
          [data-testid="stSidebar"] h1,
          [data-testid="stSidebar"] h2,
          [data-testid="stSidebar"] h3 {
            color: #ffffff !important;
          }
          div.block-container { padding-top: 1.0rem; padding-bottom: 1.0rem; }
          .stRadio, .stToggle { margin-bottom: 0.2rem; }
          .stButton { margin-top: 0.2rem; margin-bottom: 0.2rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<h3 style='text-align: center;'> 🛠️ Administrare IDBDC: {st.session_state.operator_identificat}</h3>",
        unsafe_allow_html=True,
    )

    st.divider()

    _filtru_categorii = st.session_state.get("operator_filtru_categorie") or []
    _filtru_tipuri = st.session_state.get("operator_filtru_tipuri") or []

    _toate_cat = [
        "Contracte",
        "Proiecte",
        "Evenimente stiintifice",
        "Proprietate intelectuala",
    ]
    _cat_disponibile = [""] + [
        c for c in _toate_cat
        if not _filtru_categorii or c in _filtru_categorii
    ]

    c1, c2, c3 = st.columns(3)

    with c1:
        cat_admin = st.selectbox("Categoria de date", _cat_disponibile)

    with c2:
        if cat_admin == "Contracte":
            _toate_contracte = ["CEP", "TERTI", "SPECIALE"]
            _tip_disponibile = [""] + [
                t for t in _toate_contracte
                if not _filtru_tipuri or t in _filtru_tipuri
            ]
            tip_admin = st.selectbox("Tipul de contract", _tip_disponibile)
        elif cat_admin == "Proiecte":
            _toate_proiecte = [
                "FDI",
                "PNRR",
                "PNCDI",
                "INTERNATIONALE",
                "INTERREG",
                "NONEU",
                "SEE",
            ]
            _tip_disponibile = [""] + [
                t for t in _toate_proiecte
                if not _filtru_tipuri or t in _filtru_tipuri
            ]
            tip_admin = st.selectbox("Tipul de proiect", _tip_disponibile)
        else:
            tip_admin = ""

    with c3:
        if cat_admin == "Contracte":
            id_admin = st.text_input("Filtru număr contract")
        else:
            id_admin = st.text_input("Filtru număr contract sau ID proiect")

    if id_admin and str(id_admin).strip():
        if not cat_admin:
            st.warning("Nu ati selectat categoria de date.")
        elif cat_admin in ("Contracte", "Proiecte") and not tip_admin:
            if cat_admin == "Contracte":
                st.warning("Nu ati selectat tipul de contract.")
            else:
                st.warning("Nu ati selectat tipul de proiect.")

    st.divider()

    map_baze = {
        "CEP": "base_contracte_cep",
        "TERTI": "base_contracte_terti",
        "SPECIALE": "base_contracte_speciale",
        "FDI": "base_proiecte_fdi",
        "PNRR": "base_proiecte_pnrr",
        "PNCDI": "base_proiecte_pncdi",
        "INTERNATIONALE": "base_proiecte_internationale",
        "INTERREG": "base_proiecte_interreg",
        "NONEU": "base_proiecte_noneu",
        "SEE": "base_proiecte_see",
    }

    if cat_admin in ("Contracte", "Proiecte"):
        tabela_baza = map_baze.get(tip_admin)
    elif cat_admin == "Evenimente stiintifice":
        tabela_baza = "base_evenimente_stiintifice"
    elif cat_admin == "Proprietate intelectuala":
        tabela_baza = "base_prop_intelect"
    else:
        tabela_baza = None

    if not tabela_baza:
        st.info("Selecteaza categoria si (daca este cazul) tipul.")
        return

    if not id_admin or str(id_admin).strip() == "":
        st.info("Introdu filtrul pentru a deschide fisa.")
        return

    cod = str(id_admin).strip()

    st.markdown("**Acțiune**")
    actiune = st.radio(
        label="",
        options=["Modificare / completare fișă existentă", "Fișă nouă"],
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    contract_proiect_like_types = {
        "CEP": "cep",
        "TERTI": "terti",
        "SPECIALE": "speciale",
        "FDI": "fdi",
        "INTERNATIONALE": "internationale",
        "INTERREG": "interreg",
        "NONEU": "noneu",
        "SEE": "see",
    }

    if tip_admin not in contract_proiect_like_types:
        st.info(
            "În acest motor nou este activă doar familia contract_proiect_like "
            "(CEP, TERTI, SPECIALE, FDI, INTERNATIONALE, INTERREG, NONEU, SEE). "
            "PNCDI, PNRR, evenimentele și proprietatea industrială rămân pentru etapele următoare."
        )
        return

    try:
        result = build_contract_proiect_like(
            supabase=supabase,
            cod=cod,
            actiune=actiune,
            entity_type=contract_proiect_like_types[tip_admin],
            cat_admin=cat_admin,
            tip_admin=tip_admin,
        )
    except Exception as e:
        st.error(f"Eroare la inițializarea builderului contract_proiect_like: {e}")
        return

    tabele = result["tabele"]
    table_names = result["table_names"]
    tabela_baza = result["tabela_baza"]

    state_key = lambda t: f"df_admin__{t}"
    state_key_raw = lambda t: f"df_admin_raw__{t}"

    _prev_cod_key = "admin_prev_cod"
    _prev_tabela_key = "admin_prev_tabela"

    prev_cod = st.session_state.get(_prev_cod_key)
    prev_tabela = st.session_state.get(_prev_tabela_key)

    if prev_cod != cod or prev_tabela != tabela_baza:
        for _, tn in tabele:
            for k in (
                f"df_admin__{tn}",
                f"df_admin_raw__{tn}",
                f"editor_{tn}_{prev_cod}",
                f"editor_echipa_rep_{prev_cod}",
                f"editor_echipa_rest_{prev_cod}",
                f"toggle_deblocat_{prev_cod}",
                f"echipa_reunited_{prev_cod}",
            ):
                if k in st.session_state:
                    del st.session_state[k]

        st.session_state[_prev_cod_key] = cod
        st.session_state[_prev_tabela_key] = tabela_baza

    builder = ContractProiectLikeBuilder(supabase)

    try:
        builder.seed_session_state(
            result=result,
            state_key=state_key,
            state_key_raw=state_key_raw,
            hide_control_cols_callable=hide_control_cols,
        )
    except Exception as e:
        st.error(f"Eroare la popularea session_state: {e}")
        return

    admin_msg = st.session_state.pop("admin_msg", None)
    if admin_msg and isinstance(admin_msg, tuple) and len(admin_msg) == 2:
        level, text = admin_msg
        if level == "success":
            st.success(text)
        elif level == "warning":
            st.warning(text)
        else:
            st.error(text)

    tab_labels = [label for label, _ in tabele]
    tabs_ui = st.tabs(tab_labels)

    edited_data: dict[str, pd.DataFrame] = {}

    for idx, (_, table_name) in enumerate(tabele):
        with tabs_ui[idx]:
            prepared_entry = result["prepared"][table_name]
            df_visible = st.session_state[state_key(table_name)].copy()
            column_config = prepared_entry["column_config"]

            edited_df = st.data_editor(
                df_visible,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                column_config=column_config,
                key=f"editor_{table_name}_{cod}",
            )

            edited_data[table_name] = edited_df.copy()
            st.session_state[state_key(table_name)] = edited_df.copy()

            if table_name == "com_echipe_proiect":
                st.session_state[f"echipa_reunited_{cod}"] = edited_df.copy()

    st.divider()

    bc1, bc2, bc3 = st.columns(3)

    with bc1:
        btn_save = st.button("💾 Salvează", use_container_width=True)

    with bc2:
        btn_validate = st.button("✅ Validează", use_container_width=True)

    with bc3:
        btn_delete = st.button("🗑️ Șterge", use_container_width=True)

    operator = st.session_state.get("operator_identificat", "necunoscut")

    if btn_save:
        try:
            items = builder.collect_items_for_save_from_session(
                result=result,
                state_key=state_key,
                state_key_raw=state_key_raw,
                edited_data=edited_data,
            )

            ok, msg = direct_save_all_tables(items, operator)

            if ok and "parțial" in msg.lower():
                st.session_state["admin_msg"] = ("warning", msg)
            elif ok:
                st.session_state["admin_msg"] = ("success", msg)
            else:
                st.session_state["admin_msg"] = ("error", f"Fișa nu a putut fi salvată: {msg}")

            st.rerun()

        except Exception as e:
            st.session_state["admin_msg"] = ("error", f"Fișa nu a putut fi salvată: {e}")
            st.rerun()

    if btn_validate:
        try:
            ok, msg = direct_validate_all_tables(cod, table_names, operator)

            if ok and "parțial" in msg.lower():
                st.session_state["admin_msg"] = ("warning", msg)
            elif ok:
                st.session_state["admin_msg"] = ("success", msg)
            else:
                st.session_state["admin_msg"] = ("error", msg)

            st.rerun()

        except Exception as e:
            st.session_state["admin_msg"] = ("error", f"Eroare la validare: {e}")
            st.rerun()

    if btn_delete:
        st.warning("Ștergerea este definitivă.")
        confirm = st.checkbox(
            "Confirm că vreau să șterg definitiv fișa (din toate tabelele)."
        )
        typed = st.text_input(
            "Reintrodu cod_identificare pentru confirmare:",
            value="",
        )

        if confirm and typed.strip() == cod:
            try:
                ok, msg = direct_delete_all_tables(cod, table_names)

                if ok and "parțial" in msg.lower():
                    st.session_state["admin_msg"] = ("warning", msg)
                elif ok:
                    for _, table_name in tabele:
                        for k in (state_key(table_name), state_key_raw(table_name)):
                            if k in st.session_state:
                                del st.session_state[k]

                    echipa_key = f"echipa_reunited_{cod}"
                    if echipa_key in st.session_state:
                        del st.session_state[echipa_key]

                    st.session_state["admin_msg"] = ("success", msg)
                else:
                    st.session_state["admin_msg"] = ("error", f"Eroare la ștergere: {msg}")

                st.rerun()

            except Exception as e:
                st.session_state["admin_msg"] = ("error", f"Eroare la ștergere: {e}")
                st.rerun()
