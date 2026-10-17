import pytest

from wrap import MAX_WIDTH, format_text

LONG_TEXT = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod "
    "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim "
    "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea "
    "commodo consequat."
)


def test_lines_not_longer_than_width():
    for line in format_text(LONG_TEXT).splitlines():
        assert len(line) <= MAX_WIDTH


def test_words_are_not_broken():
    result = format_text(LONG_TEXT)
    assert result.split() == LONG_TEXT.split()


def test_lines_are_filled_greedily():
    lines = format_text(LONG_TEXT).splitlines()
    for prev, nxt in zip(lines, lines[1:]):
        assert len(prev) + 1 + len(nxt.split()[0]) > MAX_WIDTH


def test_short_text_unchanged():
    assert format_text("короткий текст") == "короткий текст"


def test_exact_width_fits_on_one_line():
    text = "a" * 35 + " " + "b" * 34
    assert format_text(text) == text


def test_word_longer_than_width_stays_whole():
    long_word = "x" * 100
    assert format_text(f"a {long_word} b").splitlines() == ["a", long_word, "b"]


def test_paragraphs_are_preserved():
    assert format_text("первый\nвторой") == "первый\nвторой"


def test_custom_width():
    assert format_text("aa bb cc", width=5) == "aa bb\ncc"


def test_extra_spaces_collapsed():
    assert format_text("  a   b  ") == "a b"


def test_invalid_width():
    with pytest.raises(ValueError):
        format_text("text", width=0)
