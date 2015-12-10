# -*- coding: utf-8 -*-
import requests
import json
import logging
from btsprice.yahoo import Yahoo


class Exchanges():
    # ------------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------------
    def __init__(self):
        self.header = {'content-type': 'application/json',
                       'User-Agent': 'Mozilla/5.0 Gecko/20100101 Firefox/22.0'}
        self.log = logging.getLogger('bts')
        self.order_types = ["bids", "asks"]
        self.yahoo = Yahoo()

    # ------------------------------------------------------------------------
    # Fetch data
    # ------------------------------------------------------------------------
    #
    def fetch_from_btc38(self, quote="cny", base="bts"):
        try:
            url = "http://api.btc38.com/v1/depth.php"
            params = {'c': base, 'mk_type': quote}
            response = requests.get(
                url=url, params=params, headers=self.header, timeout=3)
            result = json.loads(vars(response)['_content'].decode("utf-8-sig"))
            for order_type in self.order_types:
                for order in result[order_type]:
                    order[0] = float(order[0])
                    order[1] = float(order[1])
            order_book_ask = sorted(result["asks"])
            order_book_bid = sorted(result["bids"], reverse=True)
            return {"bids": order_book_bid, "asks": order_book_ask}
        except:
            self.log.error("Error fetching results from btc38!")
            return

    def fetch_from_bter(self, quote="cny", base="bts"):
        try:
            url = "http://data.bter.com/api/1/depth/%s_%s" % (base, quote)
            result = requests.get(
                url=url, headers=self.header, timeout=3).json()
            for order_type in self.order_types:
                for order in result[order_type]:
                    order[0] = float(order[0])
                    order[1] = float(order[1])
            order_book_ask = sorted(result["asks"])
            order_book_bid = sorted(result["bids"], reverse=True)
            for bid_order in result["bids"]:
                order_book_bid.append(
                    [float(bid_order[0]), float(bid_order[1])])
            return {"bids": order_book_bid, "asks": order_book_ask}
        except:
            self.log.error("Error fetching results from bter!")
            return

    def fetch_from_yunbi(self, quote="cny", base="bts"):
        try:
            url = "https://yunbi.com/api/v2/depth.json"
            params = {'market': base+quote}
            result = requests.get(
                url=url, params=params, headers=self.header, timeout=3).json()
            for order_type in self.order_types:
                for order in result[order_type]:
                    order[0] = float(order[0])
                    order[1] = float(order[1])
            order_book_ask = sorted(result["asks"])
            order_book_bid = sorted(result["bids"], reverse=True)
            return {"bids": order_book_bid, "asks": order_book_ask}
        except:
            self.log.error("Error fetching results from yunbi!")
            return

    def fetch_from_poloniex(self, quote="btc", base="bts"):
        try:
            quote = quote.upper()
            base = base.upper()
            url = "http://poloniex.com/public?command=\
returnOrderBook&currencyPair=%s_%s" % (quote, base)

            result = requests.get(
                url=url, headers=self.header, timeout=3).json()
            for order_type in self.order_types:
                for order in result[order_type]:
                    order[0] = float(order[0])
                    order[1] = float(order[1])
            order_book_ask = sorted(result["asks"])
            order_book_bid = sorted(result["bids"], reverse=True)
            for bid_order in result["bids"]:
                order_book_bid.append(
                    [float(bid_order[0]), float(bid_order[1])])
            return {"bids": order_book_bid, "asks": order_book_ask}
        except:
            self.log.error("Error fetching results from bter!")
            return

    def fetch_from_yahoo(self, assets=None):
        return(self.yahoo.fetch_price())
