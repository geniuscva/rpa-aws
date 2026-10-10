from typing import Any
def _first(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return rows[0] if rows else {}

row = _first([])
print(type(row))
def g(*keys: str) -> str:
    for k in keys:
        if row.get(k) not in (None, ""):
            return str(row.get(k))
    return ""

print(g("A", "B"))
