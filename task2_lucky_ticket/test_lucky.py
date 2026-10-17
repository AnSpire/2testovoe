from itertools import permutations, product

import pytest

from lucky import can_be_lucky, make_lucky


def brute_force(digits):
    return any(sum(p[:3]) == sum(p[3:]) for p in permutations(digits))


@pytest.mark.parametrize(
    "digits, expected",
    [
        ((1, 2, 3, 3, 2, 1), True),
        ((0, 0, 0, 0, 0, 0), True),
        ((9, 0, 0, 3, 3, 3), True),
        ((1, 1, 1, 1, 1, 2), False),
        ((9, 9, 9, 0, 0, 0), False),
        ((9, 1, 1, 1, 1, 1), False),
    ],
)
def test_examples(digits, expected):
    assert can_be_lucky(digits) is expected


def test_matches_brute_force():
    for digits in product((0, 1, 5, 9), repeat=6):
        assert can_be_lucky(digits) == brute_force(digits)


def test_make_lucky_returns_permutation():
    digits = (3, 9, 0, 3, 3, 0)
    ticket = make_lucky(digits)
    assert sorted(ticket) == sorted(digits)
    assert sum(ticket[:3]) == sum(ticket[3:])


def test_make_lucky_none():
    assert make_lucky((1, 1, 1, 1, 1, 2)) is None


@pytest.mark.parametrize("bad", [(1, 2, 3), (1, 2, 3, 4, 5, 6, 7), (1, 2, 3, 4, 5, 10), (1, 2, 3, 4, 5, -1)])
def test_invalid_input(bad):
    with pytest.raises(ValueError):
        can_be_lucky(bad)
