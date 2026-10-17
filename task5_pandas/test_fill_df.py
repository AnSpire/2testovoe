import pandas as pd
import pandas.testing as pdt

from fill_df import df1, df3


def test_df3_values():
    expected = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
    pdt.assert_frame_equal(df3, expected, check_dtype=False)


def test_df3_is_integer():
    assert all(pd.api.types.is_integer_dtype(dtype) for dtype in df3.dtypes)


def test_df1_not_modified():
    assert df1.isna().sum().sum() == 2
