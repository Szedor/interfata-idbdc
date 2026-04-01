from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from modules.admin.admin_helpers import prepare_empty_single_row
from modules.admin.contract_proiect_like.contract_proiect_like_column_config import (
    build_contract_proiect_like_column_config,
    prepare_contract_proiect_like_df_for_editor,
)
from modules.admin.contract_proiect_like.contract_proiect_like_config import (
    CONTRACT_PROIECT_LIKE_TYPES,
)
from modules.admin.contract_proiect_like.contract_proiect_like_financiar import (
    build_contract_proiect_like_financial_df,
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

    Etapa 4:
      - nu schimbă payload-urile;
      - nu schimbă numele câmpurilor;
      - nu schimbă schema DB;
      - mută într-un loc comun logica de selecție / încărcare / pregătire.
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
        """
        Returnează o structură intermediară pentru orchestrator / UI.

        Builderul NU face render Streamlit.
        El pregătește:
          - config-ul rezolvat
          - tabelele active
          - datele încărcate
          - dataframes pregătite pentru editare
          - column_config pentru fiecare tabel
          - metadate pentru save/validate
        """
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
            res = self.supabase.rpc("idbdc_get_columns", {"p_table": table_name}).execute()
            return [r["column_name"] for r in (res.data or []) if r.get("column_name")]
        except Exception:
            return []

    def _load_single_row(self, table_name: str, cod: str) -> tuple[pd.DataFrame, list[str], bool]:
        cols = self._get_table_columns(table_name)
        if not cols:
            return pd.DataFrame(), [], False

        res = self.supabase.table(table_name).select("*").eq("cod_identificare", cod).execute()
        data = res.data or []
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
        df_fin, cols_fin = loaded.get("com_date_financiare", (pd.DataFrame(), []))
        df_base, cols_base = loaded.get(tabela_baza, (pd.DataFrame(), []))

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
            return prepare_empty_single_row(cols_fin, cod)
        if df_fin.empty:
            return pd.DataFrame([{"cod_identificare": cod}])

        return df_fin.copy()

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
            out["cod_identificare"] = out["cod_identificare"].fillna("").astype(str)

        return out

    def _load_dropdown_options(self, source_table: str, source_col: str) -> list[str]:
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
        """
        Pregătește payload-urile brute pentru direct_save_all_tables(...) din motor.

        În Etapa 4 îl lăsăm minimal:
          - pentru FDI, financiarul se salvează în tabela de bază;
          - pentru restul, fiecare tab se salvează în tabela lui.
        """
        items: list[dict[str, Any]] = []

        for table_name, df_edit_visible in edited_data.items():
            if df_edit_visible is None or len(df_edit_visible) == 0:
                continue

            if table_name == "com_date_financiare" and config.get("uses_fdi_financial", False):
                target_table = tabela_baza
                cols_real = self._get_table_columns(tabela_baza)
                df_for_save = df_edit_visible.copy()
                df_for_save["cod_identificare"] = cod
                df_for_save = df_for_save.drop(columns=["total_buget"], errors="ignore")
            else:
                target_table = table_name
                cols_real = self._get_table_columns(table_name)
                df_for_save = df_edit_visible.copy()
                if "cod_identificare" in df_for_save.columns:
                    df_for_save["cod_identificare"] = cod

            for _, row in df_for_save.iterrows():
                data = row.to_dict()
                payload = {k: data.get(k) for k in cols_real if k in data}
                payload["cod_identificare"] = cod
                items.append({"table": target_table, "payload": payload})

        return items


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
