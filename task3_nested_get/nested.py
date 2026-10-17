from typing import Any

_MISSING = object()


def get_by_path(obj: Any, path: str, default: Any = None) -> Any:
    current = obj
    for key in path.split("."):
        if isinstance(current, dict):
            current = current.get(key, _MISSING)
        elif isinstance(current, (list, tuple)):
            try:
                current = current[int(key)]
            except (ValueError, IndexError):
                current = _MISSING
        else:
            current = _MISSING
        if current is _MISSING:
            return default
    return current


if __name__ == "__main__":
    data = {
        "a": {
            "b": {
                "c": "+++",
            },
        },
    }
    print(get_by_path(data, "a.b.c"))
    print(get_by_path(data, "a.b"))
    print(get_by_path(data, "a.x.c"))
