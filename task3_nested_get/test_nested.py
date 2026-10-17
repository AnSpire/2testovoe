import pytest

from nested import get_by_path

DATA = {
    "a": {
        "b": {
            "c": "+++",
        },
    },
}


def test_example_from_task():
    assert get_by_path(DATA, "a.b.c") == "+++"


def test_intermediate_level():
    assert get_by_path(DATA, "a.b") == {"c": "+++"}
    assert get_by_path(DATA, "a") == {"b": {"c": "+++"}}


@pytest.mark.parametrize("path", ["x", "a.x", "a.b.c.d", "a.b.x"])
def test_missing_path_returns_none(path):
    assert get_by_path(DATA, path) is None


def test_default_value():
    assert get_by_path(DATA, "a.x", default="нет") == "нет"


def test_falsy_values_are_returned():
    data = {"a": {"zero": 0, "empty": "", "none": None}}
    assert get_by_path(data, "a.zero", default="d") == 0
    assert get_by_path(data, "a.empty", default="d") == ""
    assert get_by_path(data, "a.none", default="d") is None


def test_lists_by_index():
    data = {"a": [{"b": "first"}, {"b": "second"}]}
    assert get_by_path(data, "a.1.b") == "second"
    assert get_by_path(data, "a.5.b") is None
    assert get_by_path(data, "a.x") is None


def test_deep_nesting():
    data = current = {}
    keys = [f"k{i}" for i in range(50)]
    for key in keys[:-1]:
        current[key] = {}
        current = current[key]
    current[keys[-1]] = "deep"
    assert get_by_path(data, ".".join(keys)) == "deep"
