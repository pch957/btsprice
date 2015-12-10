# -*- coding: utf-8 -*-
from btsprice.exchanges import Exchanges
import time
from math import fabs
# from pprint import pprint


def get_median(prices):
    lenth = len(prices)
    if lenth == 0:
        return None
    _index = int(lenth / 2)
    if lenth % 2 == 0:
        median_price = float((prices[_index - 1] + prices[_index])) / 2
    else:
        median_price = prices[_index]
    return median_price


class BTSPriceAfterMatch(object):

    def __init__(self, bts_market=None, exchanges=None):
        self.bts_market = bts_market
        if exchanges:
            self.exchanges = exchanges
        else:
            self.exchanges = Exchanges()
        self.order_book = {}
        self.timeout = 300  # order book can't use after 300 seconds
        self.timestamp_rate_yahoo = 0
        self.timestamp = 0
        self.rate_yahoo = {}
        self.rate_btc = {"BTC": 1.0}
        self.order_types = ["bids", "asks"]
        self.need_cover_order = True

    def set_orderbook_timeout(self, timeout):
        self.timeout = timeout

    def get_rate_from_yahoo(self):
        _rate_yahoo = self.exchanges.fetch_from_yahoo()
        if _rate_yahoo:
            self.timestamp_rate_yahoo = self.timestamp
            self.rate_yahoo = _rate_yahoo

    def change_order_with_rate(self, _order_book, rate):
        for order_type in self.order_types:
            for order in _order_book[order_type]:
                order[0] = order[0] * rate
        return True

    def set_need_cover(self, need_cover):
        self.need_cover_order = need_cover

    def get_order_book_from_wallet(self):
        if self.bts_market is None:
            return
        need_cover = self.need_cover_order
        _order_book = self.bts_market.get_order_book(
            "CNY", "BTS", cover=need_cover)
        if _order_book:
            self.change_order_with_rate(_order_book, self.rate_btc["CNY"])
            self.order_book["wallet_cny"] = _order_book
            self.order_book["wallet_cny"]["asset"] = "CNY"
            self.order_book["wallet_cny"]["timestamp"] = self.timestamp
        _order_book = self.bts_market.get_order_book(
            "USD", "BTS", cover=need_cover)
        if _order_book:
            self.change_order_with_rate(_order_book, self.rate_btc["USD"])
            self.order_book["wallet_usd"] = _order_book
            self.order_book["wallet_usd"]["asset"] = "USD"
            self.order_book["wallet_usd"]["timestamp"] = self.timestamp

    def get_order_book_from_exchanges(self):
        _order_book = self.exchanges.fetch_from_poloniex("btc", "bts")
        if _order_book:
            self.order_book["poloniex_btc"] = _order_book
            self.order_book["poloniex_btc"]["asset"] = "BTC"
            self.order_book["poloniex_btc"]["timestamp"] = self.timestamp
        _order_book = self.exchanges.fetch_from_btc38()
        if _order_book:
            self.change_order_with_rate(_order_book, self.rate_btc["CNY"])
            self.order_book["btc38_cny"] = _order_book
            self.order_book["btc38_cny"]["asset"] = "CNY"
            self.order_book["btc38_cny"]["timestamp"] = self.timestamp
        _order_book = self.exchanges.fetch_from_btc38("btc", "bts")
        if _order_book:
            self.order_book["btc38_btc"] = _order_book
            self.order_book["btc38_btc"]["asset"] = "BTC"
            self.order_book["btc38_btc"]["timestamp"] = self.timestamp

        _order_book = self.exchanges.fetch_from_yunbi()
        if _order_book:
            self.change_order_with_rate(_order_book, self.rate_btc["CNY"])
            self.order_book["yunbi_cny"] = _order_book
            self.order_book["yunbi_cny"]["asset"] = "CNY"
            self.order_book["yunbi_cny"]["timestamp"] = self.timestamp
        _order_book = self.exchanges.fetch_from_bter()
        if _order_book:
            self.change_order_with_rate(_order_book, self.rate_btc["CNY"])
            self.order_book["bter_cny"] = _order_book
            self.order_book["bter_cny"]["asset"] = "CNY"
            self.order_book["bter_cny"]["timestamp"] = self.timestamp

    def test_valid(self):
        valid_price_queue = []
        valid_price_dict = {}
        for market in self.order_book:
            _price = (
                self.order_book[market]["bids"][0][0] + self.
                order_book[market]["asks"][0][0])/2
            valid_price_queue.append(_price)
            valid_price_dict[market] = _price
        valid_price = get_median(valid_price_queue)
        for market in self.order_book:
            change = fabs((valid_price_dict[market] - valid_price)/valid_price)
            # if offset more than 10%, this market is invalid
            if change > 0.1:
                self.order_book[market]["valid"] = False
            else:
                self.order_book[market]["valid"] = True

    def get_rate_btc(self):
        _order_book = self.exchanges.fetch_from_poloniex("USDT", "btc")
        if _order_book:
            _price_btc = (
                _order_book["bids"][0][0] + _order_book["asks"][0][0]) / 2.0
            # print("price of BTC %.3f(USD)" % _price_btc)
            for asset in self.rate_yahoo["USD"]:
                self.rate_btc[asset] = \
                    self.rate_yahoo["USD"][asset] / _price_btc
        _order_book = self.exchanges.fetch_from_btc38("cny", "btc")
        if _order_book:
            _price_btc = (
                _order_book["bids"][0][0] + _order_book["asks"][0][0]) / 2.0
            # print("price of BTC %.3f(CNY)" % _price_btc)
            for asset in self.rate_yahoo["CNY"]:
                self.rate_btc[asset] = \
                    self.rate_yahoo["CNY"][asset] / _price_btc

    def get_order_book_all(self):
        self.timestamp = time.time()
        self.order_book_all = {"bids": [], "asks": []}
        if self.timestamp_rate_yahoo == 0:
            self.get_rate_from_yahoo()
        self.get_rate_btc()
        self.get_order_book_from_exchanges()
        self.get_order_book_from_wallet()
        self.test_valid()
        for market in self.order_book:
            if self.timestamp - self.order_book[market]["timestamp"] \
                    >= self.timeout:
                continue
            if not self.order_book[market]["valid"]:
                continue
            for order_type in self.order_types:
                self.order_book_all[order_type].extend(
                    self.order_book[market][order_type])
        self.order_book_all["bids"] = sorted(
            self.order_book_all["bids"], reverse=True)
        self.order_book_all["asks"] = sorted(self.order_book_all["asks"])

    def get_spread_order_book(self, spread=0.0):
        order_bids = []
        order_asks = []
        for order in self.order_book_all["bids"]:
            order_bids.append([order[0]*(1 + spread), order[1]])
        for order in self.order_book_all["asks"]:
            order_asks.append([order[0]*(1 - spread), order[1]])
        return order_bids, order_asks

    def get_price_list(self, order_bids, order_asks):
        price_list = []
        for order in order_bids:
            if order[0] < order_asks[0][0]:
                break
            if len(price_list) == 0 or order[0] != price_list[-1]:
                price_list.append(order[0])
        for order in order_asks:
            if order[0] < order_bids[0][0]:
                break
            if len(price_list) == 0 or order[0] != price_list[-1]:
                price_list.append(order[0])
        price_list = sorted(price_list)
        return price_list

    def get_match_result(self, order_bids, order_asks, price_list):
        bid_volume = ask_volume = 0
        median_price = get_median(price_list)
        for order in order_bids:
            if order[0] < median_price:
                break
            bid_volume += order[1]
        for order in order_asks:
            if order[0] > median_price:
                break
            ask_volume += order[1]
        return ([bid_volume, ask_volume, median_price])

    def get_real_price(self, spread=0.0):
        order_bids, order_asks = self.get_spread_order_book(spread)
        price_list = self.get_price_list(order_bids, order_asks)
        if len(price_list) < 1:
            return [0.0, (order_bids[0][0] + order_asks[0][0]) / 2]
        match_result = []
        while True:
            bid_volume, ask_volume, median_price = self.get_match_result(
                order_bids, order_asks, price_list)
            # we need to find a price, which can match the max volume
            match_result.append([min(bid_volume, ask_volume),
                                 -(bid_volume+ask_volume), median_price])
            if len(price_list) <= 1:
                break
            if(bid_volume <= ask_volume):
                price_list = price_list[:int(len(price_list) / 2)]
            else:
                price_list = price_list[int(len(price_list) / 2):]

        match_result = sorted(match_result, reverse=True)
        # pprint(match_result)
        return match_result[0]

    def get_valid_depth(self, price, spread=0.0):
        valid_depth = {}
        bid_price = price / (1+spread)
        ask_price = price / (1-spread)
        for market in self.order_book:
            if self.timestamp - self.order_book[market]["timestamp"] \
                    >= self.timeout:
                continue
            if not self.order_book[market]["valid"]:
                continue
            quote = self.order_book[market]["asset"]
            valid_depth[market] = {
                "bid_price": bid_price / self.rate_btc[quote], "bid_volume": 0,
                "ask_price": ask_price / self.rate_btc[quote], "ask_volume": 0}
            for order in sorted(self.order_book[market]["bids"], reverse=True):
                if order[0] < bid_price:
                    break
                # valid_depth[market]["bid_price"] = \
                #     order[0] * self.rate_btc[quote]
                valid_depth[market]["bid_volume"] += order[1]
            for order in sorted(self.order_book[market]["asks"]):
                if order[0] > ask_price:
                    break
                # valid_depth[market]["ask_price"] = \
                #     order[0] * self.rate_btc[quote]
                valid_depth[market]["ask_volume"] += order[1]
        return valid_depth

if __name__ == "__main__":
    bts_price = BTSPriceAfterMatch()
    # updat rate cny
    bts_price.get_rate_from_yahoo()

    # get all order book
    bts_price.get_order_book_all()
    volume, volume_sum, real_price = bts_price.get_real_price(
        spread=0.01)
    valid_depth = bts_price.get_valid_depth(
        price=real_price,
        spread=0.01)
    price_cny = real_price / bts_price.rate_btc["CNY"]
    print(
        "price is %.5f CNY/BTS, volume is %.3f" % (price_cny, volume))
    print("efficent depth : %s" % valid_depth)
