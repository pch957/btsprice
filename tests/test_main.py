# -*- coding: utf-8 -*-

# The parametrize function is generated, so this doesn't work:
#
#     from pytest.mark import parametrize
#
import pytest
parametrize = pytest.mark.parametrize

from btsprice.exchanges import Exchanges
from btsprice.bts_price_after_match import BTSPriceAfterMatch
from btsprice.bts_price_after_match import get_median
from pprint import pprint


class TestMain(object):
    logfile = open("/tmp/test-btsprice.log", 'a')

    def test_get_median(self):
        assert get_median([1, 2, 3, 4]) == 2.5
        assert get_median([1, 2, 3]) == 2
        assert get_median([1]) == 1
        assert get_median([]) is None

    def test_exchanges_yahoo(self):
        exchanges = Exchanges()
        rate_cny = exchanges.fetch_from_yahoo()
        pprint("======= test_exchanges_yahoo =========", self.logfile)
        pprint(rate_cny, self.logfile)
        assert rate_cny["USD"] > 0

    def test_exchanges_yunbi(self):
        exchanges = Exchanges()
        order_book = exchanges.fetch_from_yunbi()
        pprint("======= test_exchanges_yunbi =========", self.logfile)
        pprint(order_book, self.logfile)
        assert len(order_book["bids"]) > 0

    def test_exchanges_poloniex(self):
        exchanges = Exchanges()
        order_book = exchanges.fetch_from_poloniex()
        pprint("======= test_exchanges_poloniex =========", self.logfile)
        pprint(order_book, self.logfile)
        assert len(order_book["bids"]) > 0

    def test_exchanges_btc38(self):
        exchanges = Exchanges()
        order_book = exchanges.fetch_from_btc38()
        pprint("======= test_exchanges_btc38 =========", self.logfile)
        pprint(order_book, self.logfile)
        assert len(order_book["bids"]) > 0

    def test_exchanges_bter(self):
        exchanges = Exchanges()
        order_book = exchanges.fetch_from_bter()
        pprint("======= test_exchanges_bter =========", self.logfile)
        pprint(order_book, self.logfile)
        assert len(order_book["bids"]) > 0

    def test_bts_price_after_match(self):
        bts_price = BTSPriceAfterMatch()
        bts_price.set_need_cover(False)
        bts_price.get_rate_from_yahoo()

        # get all order book
        bts_price.get_order_book_all()

        # can add weight here
        for order_type in bts_price.order_types:
            for _order in bts_price.order_book["btc38_btc"][order_type]:
                _order[1] *= 0.1

        # calculate real price
        volume, volume2, real_price = bts_price.get_real_price(spread=0.01)
        valid_depth = bts_price.get_valid_depth(price=real_price, spread=0.01)
        pprint("======= test_bts_price_after_match =========", self.logfile)
        pprint([volume, real_price,
                real_price/1.01, real_price/0.99], self.logfile)
        pprint(valid_depth, self.logfile)
        # pprint(bts_price.order_book, self.logfile)
        assert volume > 0
