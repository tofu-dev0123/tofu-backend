import math


def calc_total_pages(total_count: int, limit: int) -> int:
    """総件数と 1 ページあたりの件数から総ページ数を計算する（0 件なら 0）"""
    return math.ceil(total_count / limit) if total_count > 0 else 0
