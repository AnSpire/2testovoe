"""Задание 5: заполнить пропуски df1 значениями из df2, результат в int."""

import pandas as pd

d1 = {"a": [1, 2, 3], "b": [None, 5, 6], "c": [7, None, 9]}
d2 = {"b": [4, 89, 87], "c": [54, 8, 35], "d": [10, 11, 12]}

df1 = pd.DataFrame(d1)
df2 = pd.DataFrame(d2)


def fill_from(target: pd.DataFrame, source: pd.DataFrame) -> pd.DataFrame:
    """Заполняет NaN в target значениями source с тем же индексом и столбцом.

    Столбцы, которых нет в target (например, 'd'), в результат не попадают.
    """
    return target.fillna(source).astype(int)


df3 = fill_from(df1, df2)

if __name__ == "__main__":
    print(df3)
    print(df3.dtypes)
