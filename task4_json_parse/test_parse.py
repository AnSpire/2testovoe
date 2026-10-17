from parse import outData


def test_out_data():
    assert outData == {"one": ["http", "yandex.ru"], "two": ["https", "google.com"]}
    assert isinstance(outData, dict)
