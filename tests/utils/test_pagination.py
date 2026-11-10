from app.utils.pagination import calc_total_pages


# 0 件の場合は 0 ページ
def test_calc_total_pages_zero():
    assert calc_total_pages(0, 10) == 0


# 割り切れる場合
def test_calc_total_pages_divisible():
    assert calc_total_pages(20, 10) == 2


# 端数がある場合は切り上げ
def test_calc_total_pages_with_remainder():
    assert calc_total_pages(21, 10) == 3
    assert calc_total_pages(1, 10) == 1
