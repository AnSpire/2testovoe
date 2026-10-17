"""Задание 1: перенос текста по словам, не более 70 символов в строке."""

MAX_WIDTH = 70


def wrap_paragraph(paragraph: str, width: int = MAX_WIDTH) -> list[str]:
    """Разбивает один абзац на строки длиной не более width символов.

    Слова не разрываются. Если слово само длиннее width, оно
    помещается на отдельную строку целиком.
    """
    lines: list[str] = []
    current = ""
    for word in paragraph.split():
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= width:
            current += " " + word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def format_text(text: str, width: int = MAX_WIDTH) -> str:
    """Форматирует текст, сохраняя исходное деление на абзацы."""
    if width < 1:
        raise ValueError("width должен быть положительным")
    return "\n".join(
        "\n".join(wrap_paragraph(paragraph, width)) for paragraph in text.split("\n")
    )


if __name__ == "__main__":
    sample = (
        "Дан текст. Напишите программу, которая отформатирует этот текст так, "
        "чтобы в строке текста было не более 70 символов, а потом шел перенос "
        "строки. Слова при этом не должны разбиваться."
    )
    result = format_text(sample)
    print(result)
    print()
    print("Длины строк:", [len(line) for line in result.splitlines()])
