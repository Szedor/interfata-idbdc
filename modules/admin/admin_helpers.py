from typing import Any

import pandas as pd

NO_DECIMAL_FIELDS = {
"cod_identificare",
"numar_contract",
"nr_contract",
"nr_contract_achizitie",
"nr_contract_subsecvent",
"numar_oficial_acordare",
"numar_publicare_cerere",
"numar_data_notificare_intern",
"telefon_mobil",
"telefon_upt",
"cod_depunere",
"cod_temporar",
"an_referinta",
"durata_luni",
"numar_autori_total",
"numar_autori_upt",
"numar_participanti",
"pozitie_clasament",
}

DATE_FIELDS = {
"data_contract",
"data_inceput",
"data_sfarsit",
"data_semnare",
"data_depunere",
"data_acordare",
"data_eveniment",
"data_inceput_rol",
"data_sfarsit_rol",
"data_depozit_cerere",
"data_oficiala_acordare",
"data_inceput_valabilitate",
"data_sfarsit_valabilitate",
"data_apel",
}

NUMERIC_PREFIXES = (
"valoare_",
"suma_",
"cost_",
"buget_",
"cofinantare_",
"contributie_",
"numar_",
"nr_",
"punctaj",
"scor_",
"interval_",
"total_",
"pozitie_",
"perioada_valabilitate_ani",
)

FINANCIAL_PREFIXES = (
"valoare_",
"suma_",
"cost_",
"buget_",
"cofinantare_",
"contributie_",
)

def normalize_string(value: Any) -> str:
if value is None:
return ""
return str(value).strip()

def is_empty_value(value: Any) -> bool:
if value is None:
return True

```
if isinstance(value, float) and pd.isna(value):
    return True

return normalize_string(value) == ""
```

def is_date_col(col_name: str) -> bool:
return (col_name or "").lower().strip() in DATE_FIELDS

def is_numeric_col(col_name: str, df: pd.DataFrame | None = None) -> bool:
col = (col_name or "").lower().strip()

```
if col in NO_DECIMAL_FIELDS:
    return False

if any(col.startswith(prefix) for prefix in NUMERIC_PREFIXES):
    return True

if df is not None and col_name in df.columns:
    return pd.api.types.is_numeric_dtype(df[col_name])

return False
```

def is_financial_col(col_name: str) -> bool:
col = (col_name or "").lower().strip()
return any(col.startswith(prefix) for prefix in FINANCIAL_PREFIXES)

def format_numeric_value(value: Any, col_name: str = "") -> str:
if is_empty_value(value):
return ""

```
raw = normalize_string(value)
col = (col_name or "").lower().strip()

try:
    number = float(raw.replace(",", "."))
except Exception:
    return raw

if col in NO_DECIMAL_FIELDS:
    return str(int(round(number)))

if is_financial_col(col):
    return f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

if number.is_integer():
    return str(int(number))

return f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
```

def ensure_identifier_columns_are_text(df: pd.DataFrame) -> pd.DataFrame:
if df is None or df.empty:
return df

```
cols_to_force_text = [
    "cod_identificare",
    "numar_contract",
    "nr_contract",
    "nr_contract_achizitie",
    "nr_contract_subsecvent",
    "numar_oficial_acordare",
    "numar_publicare_cerere",
    "telefon_mobil",
    "telefon_upt",
    "cod_depunere",
    "cod_temporar",
]

for col in cols_to_force_text:
    if col in df.columns:
        df[col] = (
            df[col]
            .fillna("")
            .apply(lambda x: "" if str(x).strip() == "" else str(int(float(x))) if str(x).replace(".", "", 1).isdigit() else str(x))
        )

return df
```

