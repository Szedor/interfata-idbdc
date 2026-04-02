from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
import streamlit as st

from modules.admin.admin_helpers import (
    autofill_functie_upt,
    merge_back_control_cols,
    prepare_empty_single_row,
)
from modules.admin.contract_proiect_like.contract_proiect_like_column_config import (
    build_contract_proiect_like_column_config,
    prepare_contract_proiect_like_df_for_editor,
)
from modules.admin.contract_proiect_like.contract_proiect_like_config import (
    CONTRACT_PROIECT_LIKE_TYPES,
)
from modules.admin.contract_proiect_like.contract_proiect_like_financiar import (
    FDI_FINANCIAL_FIELDS,
    build_contract_proiect_like_financial_df,
)
from modules.admin.contract_proiect_like.contract_proiect_like_tehnic import (
    prepare_contract_proiect_like_tehnic_for_editor,
)


@dataclass(frozen=True)
class ContractProiectLikeContext:
    supabase: Any
    cod: str
    actiune: str
    entity_type: str
    cat_admin: str
    tip_admin: str


class ContractProiectLikeBuilder:
    """
    Builder generic pentru familia:
      - CEP
      - TERTI
      - SPECIALE
      - FDI
      - INTERNATIONALE
      - INTERREG
      - NONEU
      - SEE
    """

    def __init__(self, supabase: Any):
        self.supabase = supabase

    def build(
        self,
        *,
        cod: str,
        actiune: str,
        entity_type: str,
        cat_admin: str,
        tip_admin: str,
    ) -> dict[str, Any]:
        ctx = ContractProiectLikeContext(
            supabase=self.supabase,
            cod=str(cod).strip(),
            actiune=actiune,
            entity_type=self._normalize_entity_type(entity_type),
            cat_admin=cat_admin,
            tip_admin=tip_admin,
        )

        config = self._resolve_config(ctx.entity_type)
        tabela_baza = config["base_table"]
        tabele = self._resolve_tabs(config)
        table_names = [table_name for _, table_name in tabele]

        loaded, exists_map = self._load_all_tables(
            cod=ctx.cod,
            tabele=tabele,
        )

        self._assert_action_is_valid(
            actiune=ctx.actiune,
            tabela_baza=tabela_baza,
            exists_map=exists_map,
        )

        prepared = self._prepare_all_tables_for_editing(
            cod=ctx.cod,
            tabele=tabele,
            tabela_baza=tabela_baza,
            cat_admin=ctx.cat_admin,
            tip_admin=ctx.tip_admin,
            loaded=loaded,
            config=config,
        )

        return {
            "entity_type": ctx.entity_type,
            "config": config,
            "cod": ctx.cod,
            "actiune": ctx.actiune,
            "cat_admin": ctx.cat_admin,
            "tip_admin": ctx.tip_admin,
            "tabela_baza": tabela_baza,
            "tabele": tabele,
            "table_names": table_names,
            "loaded": loaded,
            "exists_map": exists_map,
            "prepared": prepared,
            "base_exists": exists_map.get(tabela_baza, False),
        }

    def seed_session_state(
        self,
        *,
        result: dict[str, Any],
        state_key,
        state_key_raw,
        hide_control_cols_callable,
    ) -> None:
        cod = result["cod"]

        for _, table_name in result["tabele"]:
            prepared_entry = result["prepared"][table_name]
            df_full = prepared_entry["df"].copy()

            raw_key = state_key_raw(table_name)
            visible_key = state_key(table_name)

            if raw_key not in st.session_state:
                st.session_state[raw_key] = df_full.copy()

            if visible_key not in st.session_state:
                st.session_state[visible_key] = hide_control_cols_callable(
                    st.session_state[raw_key].copy()
                )

            if table_name == "com_echipe_proiect":
                echipa_key = f"echipa_reunited_{cod}"
                if echipa_key not in st.session_state:
                    df_echipa_init = st.session_state[visible_key].copy()

                    if "cod_identificare" in df_echipa_init.columns:
                        df_echipa_init["cod_identificare"] = cod
                    else:
                        df_echipa_init.insert(0, "cod_identificare", cod)

                    if "id_proiect_contract_sursa" in df_echipa_init.columns:
                        df_echipa_init["id_proiect_contract_sursa"] = cod

                    if "persoana_contact" in df_echipa_init.columns:
                        df_echipa_init["persoana_contact"] = df_echipa_init["persoana_contact"].apply(
                            lambda v: True
                            if v is True or str(v).strip().upper() in ("TRUE", "DA", "1")
                            else False
                        )

                    st.session_state[echipa_key] = df_echipa_init

    def collect_items_for_save_from_session(
        self,
        *,
        result: dict[str, Any],
        state_key,
        state_key_raw,
        edited_data: dict[str, pd.DataFrame],
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []

        cod = result["cod"]
        tabela_baza = result["tabela_baza"]
        config = result["config"]
        tabele = result["tabele"]

        for _, table_name in tabele:
            df_edit_visible = edited_data.get(table_name)

            if df_edit_visible is None:
                df_edit_visible = st.session_state.get(state_key(table_name))

            if df_edit_visible is None:
                continue

            df_edit_visible = df_edit_visible.copy()

            if table_name == "com_echipe_proiect":
                echipa_key = f"echipa_reunited_{cod}"
                df_edit_visible = st.session_state.get(echipa_key, df_edit_visible).copy()

            # Nu sărim peste tabel dacă are rânduri cu cod_identificare valid
            # (rânduri nou introduse de utilizator)
            if df_edit_visible.empty:
                # Verificăm și în session_state dacă nu cumva există date salvate
                _sk = state_key(table_name)
                _df_state = st.session_state.get(_sk)
                if _df_state is None or _df_state.empty:
                    continue
                df_edit_visible = _df_state.copy()

            if table_name == "com_date_financiare" and config.get("uses_fdi_financial", False):
                df_for_save = st.session_state.get(
                    state_key_raw(tabela_baza),
                    pd.DataFrame(),
                ).copy()

                if df_for_save.empty:
                    base_cols = self._get_table_columns(tabela_baza)
                    if base_cols:
                        df_for_save = prepare_empty_single_row(base_cols, cod)
                    else:
                        df_for_save = pd.DataFrame([{"cod_identificare": cod}])

                if len(df_for_save) == 0:
                    df_for_save = pd.DataFrame([{"cod_identificare": cod}])

                if len(df_edit_visible) == 0:
                    continue

                for c in FDI_FINANCIAL_FIELDS:
                    if c in df_edit_visible.columns:
                        if c not in df_for_save.columns:
                            df_for_save[c] = None
                        df_for_save.at[df_for_save.index[0], c] = df_edit_visible.iloc[0].get(c)

                df_for_save = self._assign_link_fields(df_for_save, cod)

                df_for_save = df_for_save.drop(columns=["total_buget"], errors="ignore")
                table_name_for_save = tabela_baza
                cols_real = self._get_table_columns(tabela_baza)

            elif table_name == "com_echipe_proiect":
                df_for_save = df_edit_visible.copy()
                df_for_save = self._assign_link_fields(df_for_save, cod)
                df_for_save = autofill_functie_upt(df_for_save)
                table_name_for_save = table_name
                cols_real = self._get_table_columns(table_name_for_save)

            else:
                df_raw_original = st.session_state.get(state_key_raw(table_name))

                if isinstance(df_raw_original, pd.DataFrame) and not df_raw_original.empty:
                    try:
                        df_for_save = merge_back_control_cols(
                            df_edit_visible.copy(),
                            df_raw_original.copy(),
                        )
                    except Exception:
                        df_for_save = df_edit_visible.copy()
                else:
                    df_for_save = df_edit_visible.copy()

                df_for_save = self._assign_link_fields(df_for_save, cod)

                table_name_for_save = table_name
                cols_real = self._get_table_columns(table_name_for_save)

            if not cols_real:
                continue

            for _, row in df_for_save.iterrows():
                data = row.to_dict()
                cod_row = str(data.get("cod_identificare", "") or "").strip()

                if not cod_row:
                    continue

                payload = {
                    k: data.get(k)
                    for k in cols_real
                    if k in data
                }

                if "cod_identificare" in cols_real:
                    payload["cod_identificare"] = cod_row

                if "id_proiect_contract_sursa" in cols_real:
                    payload["id_proiect_contract_sursa"] = cod

                items.append(
                    {
                        "table": table_name_for_save,
                        "payload": payload,
                    }
                )

        return items

    def _normalize_entity_type(self, entity_type: str) -> str:
        value = (entity_type or "").strip().lower()

        aliases = {
            "cep": "cep",
            "terti": "terti",
            "speciale": "speciale",
            "fdi": "fdi",
            "internationale": "internationale",
            "interreg": "interreg",
            "noneu": "noneu",
            "see": "see",
        }

        if value not in aliases:
            raise ValueError(
                f"Entity type invalid pentru ContractProiectLikeBuilder: {entity_type}"
            )

        return aliases[value]

    def _resolve_config(self, entity_type: str) -> dict[str, Any]:
        if entity_type not in CONTRACT_PROIECT_LIKE_TYPES:
            raise KeyError(f"Nu există config pentru entity_type={entity_type}")
        return CONTRACT_PROIECT_LIKE_TYPES[entity_type]

    def _resolve_tabs(self, config: dict[str, Any]) -> list[tuple[str, str]]:
        tabs = config.get("tabs") or []
        if not tabs:
            raise ValueError(
                "Config invalid: lipsesc tab-urile pentru contract_proiect_like"
            )
        return tabs

    def _get_table_columns(self, table_name: str) -> list[str]:
        try:
            res = self.supabase.rpc(
                "idbdc_get_columns",
                {"p_table": table_name},
            ).execute()

            return [
                r["column_name"]
                for r in (res.data or [])
                if r.get("column_name")
            ]
        except Exception:
            return []

    def _load_single_row(
        self,
        table_name: str,
        cod: str,
    ) -> tuple[pd.DataFrame, list[str], bool]:
        cols = self._get_table_columns(table_name)

        if not cols:
            return pd.DataFrame(), [], False

        data = []

        try:
            if "cod_identificare" in cols:
                res = (
                    self.supabase.table(table_name)
                    .select("*")
                    .eq("cod_identificare", cod)
                    .execute()
                )
                data = res.data or []
        except Exception:
            data = []

        if not data:
            try:
                if "id_proiect_contract_sursa" in cols:
                    res = (
                        self.supabase.table(table_name)
                        .select("*")
                        .eq("id_proiect_contract_sursa", cod)
                        .execute()
                    )
                    data = res.data or []
            except Exception:
                data = []

        df = pd.DataFrame(data)

        if df.empty:
            df = pd.DataFrame(columns=cols)
            return df, cols, False

        for c in cols:
            if c not in df.columns:
                df[c] = None

        df = df[cols]

        return df, cols, True

    def _load_all_tables(
        self,
        *,
        cod: str,
        tabele: list[tuple[str, str]],
    ) -> tuple[dict[str, tuple[pd.DataFrame, list[str]]], dict[str, bool]]:
        loaded: dict[str, tuple[pd.DataFrame, list[str]]] = {}
        exists_map: dict[str, bool] = {}

        for _, table_name in tabele:
            df, cols, exista = self._load_single_row(table_name, cod)
            loaded[table_name] = (df, cols)
            exists_map[table_name] = exista

        return loaded, exists_map

    def _assert_action_is_valid(
        self,
        *,
        actiune: str,
        tabela_baza: str,
        exists_map: dict[str, bool],
    ) -> None:
        base_exists = exists_map.get(tabela_baza, False)

        if actiune == "Modificare / completare fișă existentă" and not base_exists:
            raise ValueError(
                "Nu există fișă pentru acest cod în baza de date. "
                "Alege «Fișă nouă» dacă vrei să creezi."
            )

        if actiune == "Fișă nouă" and base_exists:
            raise ValueError(
                "Există deja o fișă pentru acest cod în baza de date. "
                "Alege «Modificare / completare fișă existentă» dacă vrei să o editezi."
            )

    def _prepare_all_tables_for_editing(
        self,
        *,
        cod: str,
        tabele: list[tuple[str, str]],
        tabela_baza: str,
        cat_admin: str,
        tip_admin: str,
        loaded: dict[str, tuple[pd.DataFrame, list[str]]],
        config: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        prepared: dict[str, dict[str, Any]] = {}

        for _, table_name in tabele:
            df, cols = loaded[table_name]

            if table_name == "com_date_financiare":
                df_full = self._prepare_financial_df(
                    cod=cod,
                    tabela_baza=tabela_baza,
                    loaded=loaded,
                    config=config,
                )
            elif table_name == "com_aspecte_tehnice":
                df_full = self._prepare_tehnic_df(
                    cod=cod,
                    loaded=loaded,
                    config=config,
                )
            else:
                if df.empty and cols:
                    df_full = prepare_empty_single_row(cols, cod)
                elif df.empty:
                    df_full = pd.DataFrame([{"cod_identificare": cod}])
                else:
                    df_full = df.copy()

                if table_name == tabela_baza:
                    df_full = self._autofill_base_table_fields(
                        df=df_full,
                        cat_admin=cat_admin,
                        tip_admin=tip_admin,
                    )
                else:
                    df_full = self._assign_link_fields(df_full, cod)

            df_for_editor = prepare_contract_proiect_like_df_for_editor(
                table_name=table_name,
                df=df_full,
            )

            column_config = build_contract_proiect_like_column_config(
                table_name=table_name,
                df=df_for_editor,
                tabela_baza_ctx=tabela_baza,
                load_dropdown_options_callable=self._load_dropdown_options,
            )

            prepared[table_name] = {
                "df": df_for_editor,
                "column_config": column_config,
            }

        return prepared

    def _prepare_financial_df(
        self,
        *,
        cod: str,
        tabela_baza: str,
        loaded: dict[str, tuple[pd.DataFrame, list[str]]],
        config: dict[str, Any],
    ) -> pd.DataFrame:
        df_fin, cols_fin = loaded.get(
            "com_date_financiare",
            (pd.DataFrame(), []),
        )

        df_base, cols_base = loaded.get(
            tabela_baza,
            (pd.DataFrame(), []),
        )

        if config.get("uses_fdi_financial", False):
            if df_base.empty and cols_base:
                df_base = prepare_empty_single_row(cols_base, cod)
            elif df_base.empty:
                df_base = pd.DataFrame([{"cod_identificare": cod}])

            return build_contract_proiect_like_financial_df(
                df_fin_source=df_fin,
                df_base_source=df_base,
                cod=cod,
                tabela_baza=tabela_baza,
                config=config,
            )

        if df_fin.empty and cols_fin:
            df_out = prepare_empty_single_row(cols_fin, cod)
        elif df_fin.empty:
            df_out = pd.DataFrame([{"cod_identificare": cod}])
        else:
            df_out = df_fin.copy()

        return self._assign_link_fields(df_out, cod)

    def _prepare_tehnic_df(
        self,
        *,
        cod: str,
        loaded: dict[str, tuple[pd.DataFrame, list[str]]],
        config: dict[str, Any],
    ) -> pd.DataFrame:
        df_tehnic, cols_tehnic = loaded.get(
            "com_aspecte_tehnice",
            (pd.DataFrame(), []),
        )

        df_out = prepare_contract_proiect_like_tehnic_for_editor(
            df_tehnic_source=df_tehnic,
            cols_tehnic=cols_tehnic,
            cod=cod,
            config=config,
        )

        return self._assign_link_fields(df_out, cod)

    def _autofill_base_table_fields(
        self,
        *,
        df: pd.DataFrame,
        cat_admin: str,
        tip_admin: str,
    ) -> pd.DataFrame:
        out = df.copy()

        if "denumire_categorie" in out.columns and cat_admin:
            out["denumire_categorie"] = cat_admin

        if "acronim_contracte_proiecte" in out.columns and tip_admin:
            out["acronim_contracte_proiecte"] = tip_admin

        if "cod_identificare" in out.columns:
            out["cod_identificare"] = (
                out["cod_identificare"]
                .fillna("")
                .astype(str)
            )

        return out

    def _assign_link_fields(
        self,
        df: pd.DataFrame,
        cod: str,
    ) -> pd.DataFrame:
        out = df.copy()

        if "cod_identificare" in out.columns:
            out["cod_identificare"] = (
                out["cod_identificare"]
                .fillna(cod)
                .astype(str)
            )
            out.loc[out["cod_identificare"].str.strip() == "", "cod_identificare"] = cod
        else:
            out.insert(0, "cod_identificare", cod)

        if "id_proiect_contract_sursa" in out.columns:
            out["id_proiect_contract_sursa"] = cod

        return out

    def _load_dropdown_options(
        self,
        source_table: str,
        source_col: str,
    ) -> list[str]:
        try:
            res = self.supabase.table(source_table).select(source_col).execute()
            rows = res.data or []

            values = []

            for row in rows:
                value = row.get(source_col)

                if value is None:
                    continue

                value_str = str(value).strip()

                if value_str:
                    values.append(value_str)

            return sorted(list(set(values)))

        except Exception:
            return []

    def build_items_for_save(
        self,
        *,
        cod: str,
        tabela_baza: str,
        edited_data: dict[str, pd.DataFrame],
        loaded_raw: dict[str, tuple[pd.DataFrame, list[str]]],
        config: dict[str, Any],
    ) -> list[dict[str, Any]]:
        _ = loaded_raw
        result_like = {
            "cod": cod,
            "tabela_baza": tabela_baza,
            "config": config,
            "tabele": [(k, k) for k in edited_data.keys()],
        }

        return self.collect_items_for_save_from_session(
            result=result_like,
            state_key=lambda t: f"df_admin__{t}",
            state_key_raw=lambda t: f"df_admin_raw__{t}",
            edited_data=edited_data,
        )


def build_contract_proiect_like(
    *,
    supabase: Any,
    cod: str,
    actiune: str,
    entity_type: str,
    cat_admin: str,
    tip_admin: str,
) -> dict[str, Any]:
    builder = ContractProiectLikeBuilder(supabase)

    return builder.build(
        cod=cod,
        actiune=actiune,
        entity_type=entity_type,
        cat_admin=cat_admin,
        tip_admin=tip_admin,
    )
