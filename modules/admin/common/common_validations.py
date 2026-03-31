from __future__ import annotations

from datetime import date, datetime
from typing import Any


def is_missing(value: Any) -> bool:
    """
    Consideră lipsă:
    - None
    - string gol / doar whitespace
    """
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def validate_required(value: Any) -> bool:
    """
    True dacă valoarea este prezentă.
    """
    return not is_missing(value)


def to_float_safe(value: Any) -> float | None:
    """
    Conversie tolerantă la float.
    Acceptă:
    - 1234
    - 1234.56
    - 1234,56
    - 1.234,56
    """
    if value is None:
        return None

    if isinstance(value, str):
        s = value.strip()
        if s == "":
            return None

        try:
            if "," in s and "." in s:
                s = s.replace(".", "").replace(",", ".")
            else:
                s = s.replace(",", ".")
            return float(s)
        except Exception:
            return None

    try:
        return float(value)
    except Exception:
        return None


def validate_number(value: Any) -> bool:
    """
    True dacă valoarea poate fi interpretată numeric.
    """
    return to_float_safe(value) is not None


def validate_non_negative_number(value: Any) -> bool:
    """
    True dacă valoarea este numerică și >= 0.
    """
    num = to_float_safe(value)
    return num is not None and num >= 0


def validate_positive_number(value: Any) -> bool:
    """
    True dacă valoarea este numerică și > 0.
    """
    num = to_float_safe(value)
    return num is not None and num > 0


def validate_percentage(value: Any) -> bool:
    """
    True dacă valoarea este numerică și în intervalul [0, 100].
    """
    num = to_float_safe(value)
    return num is not None and 0 <= num <= 100


def validate_year(value: Any) -> bool:
    """
    True dacă valoarea reprezintă un an valid în format rezonabil.
    """
    num = to_float_safe(value)
    if num is None:
        return False

    if int(num) != num:
        return False

    year = int(num)
    return 1900 <= year <= 2100


def parse_date_safe(value: Any) -> date | None:
    """
    Conversie tolerantă la date calendaristice.
    Acceptă:
    - obiecte date/datetime
    - stringuri în formatele uzuale:
      YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY
    """
    if value is None:
        return None

    if isinstance(value, date) and not isinstance(value, datetime):
        return value

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None

        patterns = (
            "%Y-%m-%d",
            "%d.%m.%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
        )

        for pattern in patterns:
            try:
                return datetime.strptime(s, pattern).date()
            except ValueError:
                continue

    return None


def validate_date(value: Any) -> bool:
    """
    True dacă valoarea poate fi interpretată ca dată.
    """
    return parse_date_safe(value) is not None


def validate_date_interval(start_value: Any, end_value: Any) -> bool:
    """
    True dacă ambele date sunt valide și start <= end.
    """
    start_date = parse_date_safe(start_value)
    end_date = parse_date_safe(end_value)

    if start_date is None or end_date is None:
        return False

    return start_date <= end_date


def validate_max_length(value: Any, max_length: int) -> bool:
    """
    True dacă valoarea text nu depășește lungimea permisă.
    """
    if value is None:
        return True

    return len(str(value)) <= max_length


def validate_one_of(value: Any, allowed_values: list[Any] | tuple[Any, ...] | set[Any]) -> bool:
    """
    True dacă valoarea este în colecția permisă.
    """
    return value in allowed_values


def validate_sum_equals(total: Any, components: list[Any], tolerance: float = 0.01) -> bool:
    """
    True dacă totalul este egal cu suma componentelor în limita unei toleranțe.
    """
    total_num = to_float_safe(total)
    if total_num is None:
        return False

    parts = []
    for value in components:
        num = to_float_safe(value)
        if num is None:
            return False
        parts.append(num)

    return abs(total_num - sum(parts)) <= tolerance


def validate_boolean_like(value: Any) -> bool:
    """
    True pentru:
    - bool
    - 0 / 1
    - 'true' / 'false'
    - 'da' / 'nu'
    """
    if isinstance(value, bool):
        return True

    if value in (0, 1):
        return True

    if isinstance(value, str):
        normalized = value.strip().lower()
        return normalized in {"true", "false", "da", "nu", "0", "1"}

    return False
