from app.utils.format_utils import format_extensions


# 拡張子をソートして「.ext」形式で連結する
def test_format_extensions():
    assert format_extensions({"png", "jpg", "heic"}) == "「.heic」,「.jpg」,「.png」"


# 空集合は空文字
def test_format_extensions_empty():
    assert format_extensions(set()) == ""
