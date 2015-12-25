# -*- coding: utf-8 -*-


def get_median(prices):
    lenth = len(prices)
    if lenth == 0:
        return None
    prices = sorted(prices)
    _index = int(lenth / 2)
    if lenth % 2 == 0:
        median_price = float((prices[_index - 1] + prices[_index])) / 2
    else:
        median_price = prices[_index]
    return median_price
