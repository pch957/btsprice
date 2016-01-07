# -*- coding: utf-8 -*-
import json
import asyncio
import aiohttp


class Exchanges():
    def __init__(self):
        header = {
            'User-Agent': 'curl/7.35.0',
            'Accept': '*/*'}

        self.session = aiohttp.ClientSession(headers=header)
        self.order_types = ["bids", "asks"]

    @asyncio.coroutine
    def orderbook_btc38(self, quote="cny", base="bts"):
        try:
            url = "http://api.btc38.com/v1/depth.php"
            params = {'c': base, 'mk_type': quote}
            response = yield from asyncio.wait_for(self.session.get(
                url, params=params), 120)
            response = yield from response.read()
            result = json.loads(response.decode("utf-8-sig"))
            for order_type in self.order_types:
                for order in result[order_type]:
                    order[0] = float(order[0])
                    order[1] = float(order[1])
            order_book_ask = sorted(result["asks"])
            order_book_bid = sorted(result["bids"], reverse=True)
            return {"bids": order_book_bid, "asks": order_book_ask}
        except:
            print("Error fetching book from btc38!")

    @asyncio.coroutine
    def orderbook_bter(self, quote="cny", base="bts"):
        try:
            url = "http://data.bter.com/api/1/depth/%s_%s" % (base, quote)
            response = yield from asyncio.wait_for(self.session.get(
                url), 120)
            result = yield from response.json()
            for order_type in self.order_types:
                for order in result[order_type]:
                    order[0] = float(order[0])
                    order[1] = float(order[1])
            order_book_ask = sorted(result["asks"])
            order_book_bid = sorted(result["bids"], reverse=True)
            return {"bids": order_book_bid, "asks": order_book_ask}
        except:
            print("Error fetching book from bter!")

    @asyncio.coroutine
    def orderbook_yunbi(self, quote="cny", base="bts"):
        try:
            url = "https://yunbi.com/api/v2/depth.json"
            params = {'market': base+quote, 'limit': 20}
            response = yield from asyncio.wait_for(self.session.get(
                url, params=params), 120)
            result = yield from response.json()
            for order_type in self.order_types:
                for order in result[order_type]:
                    order[0] = float(order[0])
                    order[1] = float(order[1])
            order_book_ask = sorted(result["asks"])
            order_book_bid = sorted(result["bids"], reverse=True)
            time = int(result["timestamp"])
            return {
                "bids": order_book_bid, "asks": order_book_ask, "time": time}
        except:
            print("Error fetching book from yunbi!")

    @asyncio.coroutine
    def orderbook_poloniex(self, quote="btc", base="bts"):
        try:
            quote = quote.upper()
            base = base.upper()
            url = "http://poloniex.com/public"
            params = {
                "command": "returnOrderBook",
                "currencyPair": "%s_%s" % (quote, base),
                "depth": 50
                }

            response = yield from asyncio.wait_for(self.session.get(
                url, params=params), 120)
            result = yield from response.json()
            for order_type in self.order_types:
                for order in result[order_type]:
                    order[0] = float(order[0])
                    order[1] = float(order[1])
            order_book_ask = sorted(result["asks"])
            order_book_bid = sorted(result["bids"], reverse=True)
            return {"bids": order_book_bid, "asks": order_book_ask}
        except:
            print("Error fetching book from poloniex!")

    @asyncio.coroutine
    def ticker_btc38(self, quote="cny", base="bts"):
        try:
            url = "http://api.btc38.com/v1/ticker.php?c=%s&mk_type=%s" % (
                base, quote)
            response = yield from asyncio.wait_for(self.session.get(url), 120)
            response = yield from response.read()
            result = json.loads(response.decode("utf-8-sig"))
            _ticker = result["ticker"]
            for key in _ticker:
                _ticker[key] = float(_ticker[key])
            return _ticker
        except:
            print("Error fetching ticker from btc38!")

    @asyncio.coroutine
    def ticker_poloniex(self, quote="USDT", base="BTC"):
        try:

            url = "https://poloniex.com/public?command=returnTicker"
            response = yield from asyncio.wait_for(self.session.get(url), 120)
            response = yield from response.read()
            result = json.loads(
                response.decode("utf-8-sig"))["%s_%s" % (quote, base)]
            _ticker = {}
            _ticker["last"] = result["last"]
            _ticker["vol"] = result["baseVolume"]
            _ticker["buy"] = result["highestBid"]
            _ticker["sell"] = result["lowestAsk"]
            _ticker["low"] = result["low24hr"]
            _ticker["high"] = result["high24hr"]
            for key in _ticker:
                _ticker[key] = float(_ticker[key])
            return _ticker
        except:
            print("Error fetching ticker from btc38!")

    @asyncio.coroutine
    def ticker_btcchina(self, quote="cny", base="btc"):
        try:
            url = "https://data.btcchina.com/data/ticker?market=%s%s" % (
                base, quote)
            response = yield from asyncio.wait_for(self.session.get(url), 120)
            response = yield from response.read()
            result = json.loads(response.decode("utf-8-sig"))
            _ticker = result["ticker"]
            for key in _ticker:
                _ticker[key] = float(_ticker[key])
            _ticker["time"] = int(_ticker["date"])
            return _ticker
        except:
            print("Error fetching ticker from btcchina!")

    @asyncio.coroutine
    def ticker_huobi(self, base="btc"):
        try:
            url = "http://api.huobi.com/staticmarket/ticker_%s_json.js" % base
            response = yield from asyncio.wait_for(self.session.get(url), 120)
            response = yield from response.read()
            result = json.loads(response.decode("utf-8-sig"))
            _ticker = result["ticker"]
            for key in _ticker:
                _ticker[key] = float(_ticker[key])
            _ticker["time"] = int(result['time'])
            return _ticker
        except:
            print("Error fetching ticker from huobi!")

    @asyncio.coroutine
    def ticker_okcoin_cn(self, quote="cny", base="btc"):
        try:
            url = "https://www.okcoin.cn/api/ticker.do?symbol=%s_%s" % (
                base, quote)
            response = yield from asyncio.wait_for(self.session.get(url), 120)
            response = yield from response.read()
            result = json.loads(response.decode("utf-8-sig"))
            _ticker = result["ticker"]
            for key in _ticker:
                _ticker[key] = float(_ticker[key])
            _ticker["time"] = int(result['date'])
            return _ticker
        except:
            print("Error fetching ticker from okcoin cn!")

    @asyncio.coroutine
    def ticker_okcoin_com(self, quote="usd", base="btc"):
        try:
            url = "https://www.okcoin.com/api/v1/ticker.do?symbol=%s_%s" % (
                base, quote)
            response = yield from asyncio.wait_for(self.session.get(url), 120)
            response = yield from response.read()
            result = json.loads(response.decode("utf-8-sig"))
            _ticker = result["ticker"]
            for key in _ticker:
                _ticker[key] = float(_ticker[key])
            _ticker["time"] = int(result['date'])
            return _ticker
        except:
            print("Error fetching ticker from okcoin com!")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    exchanges = Exchanges()

    @asyncio.coroutine
    def run_task(coro, *args):
        while True:
            result = yield from coro(*args)
            print(result)
            yield from asyncio.sleep(120)

    tasks = [
        loop.create_task(run_task(exchanges.orderbook_btc38)),
        loop.create_task(run_task(exchanges.orderbook_btc38, "cny", "btc")),
        loop.create_task(run_task(exchanges.orderbook_bter)),
        loop.create_task(run_task(exchanges.orderbook_yunbi)),
        loop.create_task(run_task(exchanges.orderbook_poloniex)),
        loop.create_task(run_task(exchanges.ticker_btc38)),
        loop.create_task(run_task(exchanges.ticker_poloniex)),
        loop.create_task(run_task(exchanges.ticker_btcchina)),
        loop.create_task(run_task(exchanges.ticker_huobi)),
        loop.create_task(run_task(exchanges.ticker_okcoin_cn)),
        loop.create_task(run_task(exchanges.ticker_okcoin_com))
        ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.run_forever()
