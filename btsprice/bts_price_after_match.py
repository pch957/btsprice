# -*- coding: utf-8 -*-
import time
import copy
from math import fabs
from btsprice.misc import get_median
# from pprint import pprint


class BTSPriceAfterMatch(object):

    def __init__(self, data):
        self.data = data
        self.timeout = 600  # order book can't use after 300 seconds
        self.order_types = ["bids", "asks"]
        self.orderbook = {}
        self.global_orderbook = {"bids": [], "asks": []}
        self.rate_cny = {}
        self.callback = None

    def set_weight(self, _market_weight):
        self.market_weight = _market_weight

    def set_timeout(self, timeout):
        self.timeout = timeout

    def change_order_with_rate(self, _orderbook, rate):
        for order_type in self.order_types:
            for order in _orderbook[order_type]:
                order[0] = order[0] * rate

    def remove_timeout(self, data):
        for name in list(data.keys()):
            if self.timestamp - data[name]["time"] >= self.timeout:
                del data[name]

    def test_valid(self):
        valid_price_queue = []
        valid_price_dict = {}
        for market in self.market_weight:
            if market not in self.orderbook:
                continue
            _price = (
                self.orderbook[market]["bids"][0][0] + self.
                orderbook[market]["asks"][0][0])/2
            if self.market_weight[market]:
                valid_price_queue.append(_price)
            valid_price_dict[market] = _price
        valid_price = get_median(valid_price_queue)
        for market in list(self.orderbook.keys()):
            change = fabs((valid_price_dict[market] - valid_price)/valid_price)
            # if offset more than 10%, this market is invalid
            if change > 0.1:
                del self.orderbook[market]
        # all market is invalid if we got valid market less than 2
        if len(self.orderbook) < 2:
            return False
        else:
            return True

    def compute_rate_cny(self):
        btc_ticker = self.data["ticker"].copy()
        self.remove_timeout(btc_ticker)
        price_btc_queue = {"CNY": [], "USD": []}
        price_btc = {}
        for name in btc_ticker:
            quote = btc_ticker[name]["quote"]
            price_btc_queue[quote].append(btc_ticker[name]["last"])
        for asset in price_btc_queue:
            if len(price_btc_queue[asset]) == 0:
                return
            price_btc[asset] = get_median(price_btc_queue[asset])
        rate_cny = {"CNY": 1.0}
        rate_cny["BTC"] = price_btc["CNY"]
        rate_cny["USD"] = price_btc["CNY"] / price_btc["USD"]
        rate = self.data["rate"]
        if len(rate) == 0:
            return
        rate_yahoo = rate["yahoo"]

        _change = fabs(price_btc["USD"] - rate_yahoo["USD"]["BTC"]) / \
            rate_yahoo["USD"]["BTC"]
        if _change >= 0.1:  # BTC price different more than 10%
            return
        _change = fabs(rate_cny["USD"] - 1/rate_yahoo["USD"]["CNY"]) / \
            rate_cny["USD"]
        if _change >= 0.1:  # rate USD/CNY different more than 10%
            return
        for quote in ["CNY", "USD"]:
            for base in rate_yahoo[quote]:
                if base not in rate_cny:
                    rate_cny[base] = rate_cny[quote] * rate_yahoo[quote][base]

        rate_cny["TCNY"] = rate_cny["CNY"]
        rate_cny["TUSD"] = rate_cny["USD"]
        self.rate_cny = rate_cny

    def update_orderbook(self):
        if not self.rate_cny:
            return
        self.global_orderbook = {"bids": [], "asks": []}
        self.orderbook = copy.deepcopy(self.data["orderbook"])
        self.remove_timeout(self.orderbook)
        for market in self.orderbook:
            change_rate = self.rate_cny[self.orderbook[market]["quote"]]
            self.change_order_with_rate(self.orderbook[market], change_rate)
        if not self.test_valid():
            return
        if self.callback:
            self.callback(self.orderbook)
        for market in self.orderbook:
            for order_type in self.order_types:
                self.global_orderbook[order_type].extend(
                    self.orderbook[market][order_type])
        self.global_orderbook["bids"] = sorted(
            self.global_orderbook["bids"], reverse=True)
        self.global_orderbook["asks"] = sorted(self.global_orderbook["asks"])

    def get_spread_orderbook(self, spread=0.01):
        order_bids = []
        order_asks = []
        for order in self.global_orderbook["bids"]:
            order_bids.append([order[0]*(1 + spread), order[1]])
        for order in self.global_orderbook["asks"]:
            order_asks.append([order[0]/(1 + spread), order[1]])
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

    def compute_price(self, spread=0.01):
        self.timestamp = int(time.time())
        self.compute_rate_cny()
        self.update_orderbook()
        if len(self.global_orderbook["bids"]) == 0 or \
                len(self.global_orderbook["asks"]) == 0:
            return [0.0, 0.0, None]
        order_bids, order_asks = self.get_spread_orderbook(spread)
        price_list = self.get_price_list(order_bids, order_asks)
        if len(price_list) < 1:
            return [0.0, 0.0, (order_bids[0][0] + order_asks[0][0]) / 2]
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

    def get_valid_depth(self, price, spread=0.01):
        valid_depth = {}
        bid_price = price / (1+spread)
        ask_price = price * (1+spread)
        for market in self.orderbook:
            quote = self.orderbook[market]["quote"]
            valid_depth[market] = {
                "bid_price": bid_price / self.rate_cny[quote], "bid_volume": 0,
                "ask_price": ask_price / self.rate_cny[quote], "ask_volume": 0}
            for order in sorted(self.orderbook[market]["bids"], reverse=True):
                if order[0] < bid_price:
                    break
                # valid_depth[market]["bid_price"] = \
                #     order[0] * self.rate_cny[quote]
                valid_depth[market]["bid_volume"] += order[1]
            for order in sorted(self.orderbook[market]["asks"]):
                if order[0] > ask_price:
                    break
                # valid_depth[market]["ask_price"] = \
                #     order[0] * self.rate_cny[quote]
                valid_depth[market]["ask_volume"] += order[1]
        return valid_depth

if __name__ == "__main__":
    import asyncio
    from btsprice.task_exchanges import TaskExchanges
    exchange_data = {}
    task_exchanges = TaskExchanges(exchange_data)
    task_exchanges.set_period(20)
    loop = asyncio.get_event_loop()
    task_exchanges.run_tasks(loop)

    bts_price = BTSPriceAfterMatch(exchange_data)

    @asyncio.coroutine
    def task_compute_price():
        yield from asyncio.sleep(1)
        while True:
            volume, volume_sum, real_price = bts_price.compute_price(
                spread=0.01)
            if real_price:
                valid_depth = bts_price.get_valid_depth(
                    price=real_price,
                    spread=0.01)
                print(
                    "price:%.5f CNY/BTS, volume:%.3f" % (real_price, volume))
                print("efficent depth : %s" % valid_depth)
            else:
                print("can't get valid market order")
            yield from asyncio.sleep(20)
    loop.create_task(task_compute_price())
    loop.run_forever()
    loop.close()
