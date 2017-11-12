# -*- coding: utf-8 -*-
from btsprice.exchanges import Exchanges
from btsprice.yahoo import Yahoo
from btsprice.sina import Sina
import time
import asyncio


class TaskExchanges(object):
    def __init__(self, data={}):
        self.period = 120
        self.exchanges = Exchanges()
        self.yahoo = Yahoo()
        self.sina = Sina()
        self.handler = None
        data_type = ["orderbook", "ticker", "rate"]
        for _type in data_type:
            if _type not in data:
                data[_type] = {}
        self.data = data

    def set_period(self, sec):
        self.period = sec

    @asyncio.coroutine
    def fetch_orderbook(self, name, quote, coro, *args):
        time_end = int(time.time())
        orderbook = self.data["orderbook"]
        while True:
            time_begin = time_end
            _orderbook = yield from coro(*args)
            time_end = int(time.time())
            if _orderbook:
                orderbook[name] = _orderbook
                orderbook[name]["quote"] = quote
                if "time" not in _orderbook:
                    orderbook[name]["time"] = time_end
                if self.handler:
                    self.handler("orderbook", name, orderbook[name])
            time_left = self.period - (time_end - time_begin)
            if time_left <= 1:
                time_left = 1
            time_end += time_left
            yield from asyncio.sleep(time_left)

    @asyncio.coroutine
    def fetch_ticker(self, name, quote, coro, *args):
        time_end = int(time.time())
        ticker = self.data["ticker"]
        while True:
            time_begin = time_end
            _ticker = yield from coro(*args)
            time_end = int(time.time())
            if _ticker:
                _ticker["quote"] = quote
                if "time" not in _ticker:
                    _ticker["time"] = time_end
                ticker[name] = _ticker
                if self.handler:
                    self.handler("ticker", name, _ticker)
            time_left = self.period - (time_end - time_begin)
            if time_left <= 1:
                time_left = 1
            time_end += time_left
            yield from asyncio.sleep(time_left)

    @asyncio.coroutine
    def fetch_yahoo_rate(self):
        time_end = int(time.time())
        rate = self.data["rate"]
        while True:
            time_begin = time_end
            _rate = yield from self.yahoo.fetch_price()
            time_end = int(time.time())
            if _rate:
                _rate["time"] = time_end
                rate["yahoo"] = _rate
                if self.handler:
                    self.handler("rate", "yahoo", _rate)
            time_left = self.period - (time_end - time_begin)
            if time_left <= 1:
                time_left = 1
            time_end += time_left
            yield from asyncio.sleep(time_left)

    @asyncio.coroutine
    def fetch_sina_rate(self):
        time_end = int(time.time())
        rate = self.data["rate"]
        while True:
            time_begin = time_end
            _rate = yield from self.sina.fetch_price()
            time_end = int(time.time())
            if _rate:
                _rate["time"] = time_end
                rate["Sina"] = _rate
                if self.handler:
                    self.handler("rate", "Sina", _rate)
            time_left = self.period - (time_end - time_begin)
            if time_left <= 1:
                time_left = 1
            time_end += time_left
            yield from asyncio.sleep(time_left)

    def run_tasks_ticker(self, loop):
        return [
            loop.create_task(self.fetch_ticker(
                "poloniex", "USD",
                self.exchanges.ticker_poloniex, "USDT", "BTC")),
            # loop.create_task(self.fetch_ticker(
            #     "btce", "USD",
            #     self.exchanges.ticker_btce, "usd", "btc")),
            loop.create_task(self.fetch_ticker(
                "bitstamp", "USD",
                self.exchanges.ticker_bitstamp, "usd", "btc")),
            loop.create_task(self.fetch_ticker(
                "gdax", "USD",
                self.exchanges.ticker_gdax, "usd", "btc")),
            # loop.create_task(self.fetch_ticker(
            #     "btcchina", "CNY",
            #     self.exchanges.ticker_btcchina, "cny", "btc")),
            # loop.create_task(self.fetch_ticker(
            #     "huobi", "CNY",
            #     self.exchanges.ticker_huobi, "btc")),
            # loop.create_task(self.fetch_ticker(
            #     "okcoin_cn", "CNY",
            #     self.exchanges.ticker_okcoin_cn, "cny", "btc")),
            loop.create_task(self.fetch_ticker(
                 "okcoin_com", "USD",
                 self.exchanges.ticker_okcoin_com, "usd", "btc")),
            loop.create_task(self.fetch_ticker(
                 "bitfinex", "USD",
                 self.exchanges.ticker_bitfinex, "usd", "btc")),
            loop.create_task(self.fetch_ticker(
                 "kraken", "EUR",
                 self.exchanges.ticker_kraken, "eur", "btc")),
            loop.create_task(self.fetch_ticker(
                 "bitflyer_usd", "USD",
                 self.exchanges.ticker_bitflyer, "usd", "btc")),
            loop.create_task(self.fetch_ticker(
                 "bitflyer_jpy", "JPY",
                 self.exchanges.ticker_bitflyer, "jpy", "btc")),
            ]

    def run_tasks_orderbook(self, loop):
        return [
            loop.create_task(self.fetch_orderbook(
                "btsbots_cny", "CNY",
                self.exchanges.orderbook_btsbots, "CNY", "BTS")),
            loop.create_task(self.fetch_orderbook(
                "btsbots_usd", "USD",
                self.exchanges.orderbook_btsbots, "USD", "BTS")),
            loop.create_task(self.fetch_orderbook(
                "btsbots_open.btc", "BTC",
                self.exchanges.orderbook_btsbots, "OPEN.BTC", "BTS")),
            loop.create_task(self.fetch_orderbook(
                "aex_btc", "BTC",
                self.exchanges.orderbook_aex, "btc", "bts")),
            loop.create_task(self.fetch_orderbook(
                "zb_btc", "BTC",
                self.exchanges.orderbook_zb, "btc", "bts")),
            loop.create_task(self.fetch_orderbook(
                "zb_usdt", "USD",
                self.exchanges.orderbook_zb, "usdt", "bts")),
            loop.create_task(self.fetch_orderbook(
                "poloniex_btc", "BTC",
                self.exchanges.orderbook_poloniex, "btc", "bts"))
            # loop.create_task(self.fetch_orderbook(
            #     "yunbi_cny", "CNY",
            #     self.exchanges.orderbook_yunbi, "cny", "bts")),
            # loop.create_task(self.fetch_orderbook(
            #     "jubi_cny", "CNY",
            #     self.exchanges.orderbook_jubi, "cny", "bts")),
            # loop.create_task(self.fetch_orderbook(
            #     "19800_cny", "CNY",
            #     self.exchanges.orderbook_19800, "cny", "bts")),
            # loop.create_task(self.fetch_orderbook(
            #     "bittrex_btc", "BTC",
            #     self.exchanges.orderbook_bittrex, "btc", "bts")),
            ]

    def run_tasks(self, loop):
        return [
                loop.create_task(self.fetch_yahoo_rate()),
                loop.create_task(self.fetch_sina_rate())
                ] + \
            self.run_tasks_orderbook(loop) + \
            self.run_tasks_ticker(loop)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    task_exchanges = TaskExchanges()
    task_exchanges.set_period(20)
    tasks = task_exchanges.run_tasks(loop)

    @asyncio.coroutine
    def task_display():
        my_data = task_exchanges.data
        while True:
            for _type in my_data:
                for _name in my_data[_type]:
                    if "done" not in my_data[_type][_name]:
                        print("got %s: %s" % (_type, _name))
                        my_data[_type][_name]["done"] = None
            yield from asyncio.sleep(1)
    tasks += [loop.create_task(task_display())]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.run_forever()
    loop.close()
