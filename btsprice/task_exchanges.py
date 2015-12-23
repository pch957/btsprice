# -*- coding: utf-8 -*-
from btsprice.exchanges import Exchanges
from btsprice.yahoo import Yahoo
import time
import asyncio


class TaskExchanges(object):
    def __init__(self):
        self.order_types = ["bids", "asks"]
        self.exchanges = Exchanges()
        self.orderbook = {}
        self.ticker = {}
        self.yahoo = Yahoo()
        self.yahoo_rate = {}
        self.handler = None

        self.period = 120

    def set_period(self, sec):
        self.period = sec

    @asyncio.coroutine
    def fetch_orderbook(self, name, quote, coro, *args):
        time_end = int(time.time())
        while True:
            time_begin = time_end
            _orderbook = yield from coro(*args)
            time_end = int(time.time())
            if _orderbook:
                self.orderbook[name] = _orderbook
                self.orderbook[name]["quote"] = quote
                if "time" not in _orderbook:
                    self.orderbook[name]["time"] = time_end
                if self.handler:
                    self.handler("ticker", name, self.orderbook[name])
            time_left = self.period - (time_end - time_begin)
            if time_left <= 1:
                time_left = 1
            time_end += time_left
            yield from asyncio.sleep(time_left)

    @asyncio.coroutine
    def fetch_ticker(self, name, quote, coro, *args):
        time_end = int(time.time())
        while True:
            time_begin = time_end
            _ticker = yield from coro(*args)
            time_end = int(time.time())
            if _ticker:
                _ticker["quote"] = quote
                if "time" not in _ticker:
                    _ticker["time"] = time_end
                self.ticker[name] = _ticker
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
        while True:
            time_begin = time_end
            _yahoo_rate = yield from self.yahoo.fetch_price()
            time_end = int(time.time())
            if _yahoo_rate:
                del _yahoo_rate["USD"]["BTC"]
                del _yahoo_rate["USD"]["CNY"]
                self.yahoo_rate["time"] = time_end
                self.yahoo_rate["rate"] = _yahoo_rate
                if self.handler:
                    self.handler("yahoo_rate", None, self.yahoo_rate)
            time_left = self.period - (time_end - time_begin)
            if time_left <= 1:
                time_left = 1
            time_end += time_left
            yield from asyncio.sleep(time_left)

    def run_tasks_ticker(self, loop):
        return [
            loop.create_task(self.fetch_ticker(
                "btc38", "CNY",
                self.exchanges.ticker_btc38, "cny", "btc")),
            loop.create_task(self.fetch_ticker(
                "poloniex", "USD",
                self.exchanges.ticker_poloniex, "USDT", "BTC")),
            loop.create_task(self.fetch_ticker(
                "btcchina", "CNY",
                self.exchanges.ticker_btcchina, "cny", "btc")),
            loop.create_task(self.fetch_ticker(
                "huobi", "CNY",
                self.exchanges.ticker_huobi, "btc")),
            loop.create_task(self.fetch_ticker(
                "okcoin_cn", "CNY",
                self.exchanges.ticker_okcoin_cn, "cny", "btc")),
            loop.create_task(self.fetch_ticker(
                "okcoin_com", "USD",
                self.exchanges.ticker_okcoin_com, "usd", "btc")),
            ]

    def run_tasks_orderbook(self, loop):
        return [
            loop.create_task(self.fetch_orderbook(
                "btc38_cny", "CNY",
                self.exchanges.orderbook_btc38, "cny", "bts")),
            loop.create_task(self.fetch_orderbook(
                "btc38_btc", "BTC",
                self.exchanges.orderbook_btc38, "btc", "bts")),
            loop.create_task(self.fetch_orderbook(
                "poloniex_btc", "BTC",
                self.exchanges.orderbook_poloniex, "btc", "bts")),
            loop.create_task(self.fetch_orderbook(
                "yunbi_cny", "CNY",
                self.exchanges.orderbook_yunbi, "cny", "bts")),
            loop.create_task(self.fetch_orderbook(
                "bter_cny", "CNY",
                self.exchanges.orderbook_bter, "cny", "bts")),
            ]

    def run_tasks(self, loop):
        return [loop.create_task(self.fetch_yahoo_rate())] + \
            self.run_tasks_orderbook(loop) + \
            self.run_tasks_ticker(loop)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    task_exchanges = TaskExchanges()
    task_exchanges.set_period(10)
    tasks = task_exchanges.run_tasks(loop)

    @asyncio.coroutine
    def task_display():
        datas = [
            task_exchanges.ticker,
            task_exchanges.orderbook]
        while True:
            for _data in datas:
                for name in _data:
                    if "done" not in _data[name]:
                        print("got %s: %s" % (name, _data[name].keys()))
                        _data[name]["done"] = None
            yield from asyncio.sleep(1)
    tasks += [loop.create_task(task_display())]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.run_forever()
    loop.close()
