# =========================================================
# ADMIN DATA OPS — operatii comune pentru c2
# =========================================================

import pandas as pd
from datetime import datetime


# ---------------------------------------------------------
# HELPERI GENERALI
# ---------------------------------------------------------

def now_iso() -> str:
    return datetime.now().isoformat()


def current_year() -> int:
    return datetime.now().year


def append_observatii(existing: str, msg: str) -> str:
    base = (existing or "").strip()

    if not base:
        return msg

    return base + "\n" + msg


# ---------------------------------------------------------
# NUMERIC / IDENTIFICATOR
# ---------------------------------------------------------

def normalize_identifier_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Forteaza cod_identificare sa fie tratat ca text.
    """

    if "cod_identificare" not in df.columns:
        return df

    def _normalize_code(v):
        if v is None:
            return None

        if isinstance(v, float):
            if pd.isna(v):
                return None

            if v.is_integer():
                return str(int(v))

            return str(v)

        if isinstance(v, int):
            return str(v)

        s = str(v).strip()

        if s == "" or s.lower() in ("none", "nan"):
            return None

        return s

    out = df.copy()
    out["cod_identificare"] = (
        out["cod_identificare"]
        .apply(_normalize_code)
        .astype("object")
    )

    return out


# ---------------------------------------------------------
# RAND GOL
# ---------------------------------------------------------

def empty_row(columns: list[str]) -> dict:
    row = {c: None for c in columns}

    if "status_confirmare" in row:
        row["status_confirmare"] = False

    if "validat_idbdc" in row:
        row["validat_idbdc"] = False

    if "persoana_contact" in row:
        row["persoana_contact"] = False

    y = current_year()

    for c in columns:
        if c == "an" or c.startswith("an_"):
            row[c] = y

    return row


def prepare_empty_single_row(columns: list[str], cod: str) -> pd.DataFrame:
    if not columns:
        return pd.DataFrame()

    row = empty_row(columns)

    if "cod_identificare" in row:
        row["cod_identificare"] = cod

    df = pd.DataFrame([row], columns=columns)
    df = normalize_identifier_column(df)

    return df


# ---------------------------------------------------------
# PAYLOAD
# ---------------------------------------------------------

def cleanup_payload(payload: dict) -> dict:
    out = {}

    for k, v in (payload or {}).items():
        if k == "nr_crt":
            if v is None:
                continue

            if isinstance(v, str) and v.strip() == "":
                continue

            out[k] = v
            continue

        if k == "cod_identificare":
            if v is not None and str(v).strip():
                out[k] = str(v).strip()
            continue

        if v is None:
            continue

        if isinstance(v, str) and v.strip() == "":
            continue

        out[k] = v

    return out


def is_row_effectively_empty(payload: dict) -> bool:
    cod = payload.get("cod_identificare")

    if cod is None:
        return True

    if isinstance(cod, str) and cod.strip() == "":
        return True

    return False


# ---------------------------------------------------------
# SALVARE / VALIDARE / STERGERE
# ---------------------------------------------------------

def direct_upsert_single_row(supabase, table_name: str, payload: dict, cod: str):
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
        supabase.table(table_name) \
            .update(payload) \
            .eq("cod_identificare", cod) \
            .execute()
    else:
        supabase.table(table_name) \
            .insert(payload) \
            .execute()


def direct_delete_all_tables(supabase, cod: str, table_names: list[str]) -> tuple[bool, str]:
    ok_any = False
    errors = []

    for table_name in table_names:
        try:
            supabase.table(table_name) \
                .delete() \
                .eq("cod_identificare", cod) \
                .execute()

            ok_any = True

        except Exception as e:
            errors.append(f"{table_name}: {e}")

    if not ok_any and errors:
        return False, " | ".join(errors)

    if not ok_any:
        return False, "Nu s-a sters nimic."

    if errors:
        return True, "Stergere partiala."

    return True, "Fisa a fost stearsa."


def direct_validate_all_tables(
    supabase,
    cod: str,
    table_names: list[str],
    operator: str
) -> tuple[bool, str]:

    ok_any = False
    errors = []

    msg = (
        f"Validat de {operator} @ "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    for table_name in table_names:
        try:
            payload = {
                "validat_idbdc": True,
                "data_ultimei_modificari": now_iso(),
                "observatii_idbdc": msg,
            }

            supabase.table(table_name) \
                .update(payload) \
                .eq("cod_identificare", cod) \
                .execute()

            ok_any = True

        except Exception as e:
            errors.append(f"{table_name}: {e}")

    if not ok_any and errors:
        return False, " | ".join(errors)

    if not ok_any:
        return False, "Nu s-a putut valida."

    if errors:
        return True, "Validare partiala."

    return True, "Validare realizata."
```

