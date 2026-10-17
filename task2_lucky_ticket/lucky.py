"""Задание 2: можно ли из шести цифр собрать счастливый билет.

Билет счастливый, если сумма первых трёх цифр равна сумме последних трёх.
Цифры можно переставлять, поэтому задача сводится к вопросу: можно ли
разбить шесть цифр на две тройки с равными суммами.
"""

from itertools import combinations


def can_be_lucky(digits: tuple[int, ...]) -> bool:
    if len(digits) != 6:
        raise ValueError("Нужно ровно шесть цифр")
    if not all(isinstance(d, int) and 0 <= d <= 9 for d in digits):
        raise ValueError("Каждый элемент должен быть цифрой от 0 до 9")

    total = sum(digits)
    if total % 2:
        return False
    half = total // 2
    return any(
        sum(digits[i] for i in triple) == half for triple in combinations(range(6), 3)
    )


def make_lucky(digits: tuple[int, ...]) -> tuple[int, ...] | None:
    """Возвращает пример счастливого билета из этих цифр или None."""
    if not can_be_lucky(digits):
        return None
    half = sum(digits) // 2
    for triple in combinations(range(6), 3):
        if sum(digits[i] for i in triple) == half:
            rest = [i for i in range(6) if i not in triple]
            return tuple(digits[i] for i in (*triple, *rest))
    return None  # недостижимо


if __name__ == "__main__":
    for ticket in [(1, 2, 3, 3, 2, 1), (1, 1, 1, 1, 1, 2), (0, 0, 0, 0, 0, 0), (9, 1, 1, 1, 1, 7)]:
        print(ticket, can_be_lucky(ticket), make_lucky(ticket))
