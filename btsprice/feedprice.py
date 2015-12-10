#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from btsprice.bts_price_after_match import BTSPriceAfterMatch
from btsprice.feedapi import FeedApi
import time
import logging
import logging.handlers
import os
from prettytable import PrettyTable
from datetime import datetime
from math import fabs
import locale
locale.setlocale(locale.LC_ALL, '')


class FeedPrice(object):

    def __init__(self, config=None):
        self.init_config(config)
        self.init_bts_price()
        self.setup_log()
        self.init_mpa_info()
        self.sample = self.config["price_limit"]["filter_minute"] / \
            self.config["timer_minute"]
        if self.sample < 1:
            self.sample = 1
        self.feedapi = FeedApi(config)

    def init_config(self, config):
        if config:
            self.config = config
            return
        config = {}
        config["witness"] = None
        config["timer_minute"] = 3
        config["max_update_hours"] = 23.5
        config["price_limit"] = {
            "change_min": 0.5, "change_max": 50, "spread": 0.01,
            "filter_minute": 30}
        config["market_weight"] = {
            "poloniex_btc": 1, "yunbi_cny": 1, "btc38_cny": 1, "btc38_btc": 1}

        self.config = config

    def init_bts_price(self):
        self.bts_price = BTSPriceAfterMatch()
        # don't use cover order, because it's feed price related,
        # if there is a big order, feed price will down without stop
        self.bts_price.set_need_cover(False)

    def setup_log(self):
        # Setting up Logger
        self.logger = logging.getLogger('bts')
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s[%(levelname)s]: %(message)s')
        fh = logging.handlers.RotatingFileHandler("/tmp/bts_delegate_task.log")
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def init_mpa_info(self):
        peg_asset_list = ["KRW", "BTC", "SILVER", "GOLD", "TRY",
                          "SGD", "HKD", "RUB", "SEK", "NZD", "CNY",
                          "MXN", "CAD", "CHF", "AUD", "GBP", "JPY",
                          "EUR", "USD", "SHENZHEN", "NASDAQC", "NIKKEI",
                          "HANGSENG", "SHANGHAI", "TCNY"]
        self.price_queue = {}
        for asset in peg_asset_list:
            self.price_queue[asset] = []
        self.time_publish_feed = 0
        self.adjust_scale = 1.00

    def fetch_bts_price(self):
        # updat rate cny
        self.bts_price.get_rate_from_yahoo()

        # get all order book
        self.bts_price.get_order_book_all()

        self.bts_price.rate_btc["TCNY"] = self.bts_price.rate_btc["CNY"]
        # can add weight here
        for order_type in self.bts_price.order_types:
            for market in self.bts_price.order_book:
                if market not in self.config["market_weight"]:
                    _weight = 0.0
                else:
                    _weight = self.config["market_weight"][market]
                for _order in self.bts_price.order_book[market][order_type]:
                    _order[1] *= _weight

        # calculate real price
        volume, volume_sum, real_price = self.bts_price.get_real_price(
            spread=self.config["price_limit"]["spread"])
        self.valid_depth = self.bts_price.get_valid_depth(
            price=real_price,
            spread=self.config["price_limit"]["spread"])
        price_cny = real_price / self.bts_price.rate_btc["CNY"]
        self.logger.info("fetch price is %.5f CNY/BTS, volume is %.3f",
                         price_cny, volume)
        self.logger.info("efficent depth : %s" % self.valid_depth)
        return real_price, volume

    # these MPA's precision is 100, it's too small,
    # have to change the price
    # but we should fixed these at BTS2.0
    def patch_nasdaqc(self, price):
        if "SHENZHEN" in price:
            price["SHENZHEN"] /= price["CNY"]
        if "SHANGHAI" in price:
            price["SHANGHAI"] /= price["CNY"]
        if "NASDAQC" in price:
            price["NASDAQC"] /= price["USD"]
        if "NIKKEI" in price:
            price["NIKKEI"] /= price["JPY"]
        if "HANGSENG" in price:
            price["HANGSENG"] /= price["HKD"]

    def price_filter(self, bts_price_in_btc):
        self.filter_price = self.get_average_price(bts_price_in_btc)

    def get_median_price(self, bts_price_in_btc):
        median_price = {}
        for asset in self.price_queue:
            if asset not in self.bts_price.rate_btc or \
                    self.bts_price.rate_btc[asset] is None:
                continue
            self.price_queue[asset].append(bts_price_in_btc
                                           / self.bts_price.rate_btc[asset])
            if len(self.price_queue[asset]) > self.sample:
                self.price_queue[asset].pop(0)
            median_price[asset] = sorted(
                self.price_queue[asset])[int(len(self.price_queue[asset]) / 2)]
        self.patch_nasdaqc(median_price)
        return median_price

    def get_average_price(self, bts_price_in_btc):
        average_price = {}
        for asset in self.price_queue:
            if asset not in self.bts_price.rate_btc or \
                    self.bts_price.rate_btc[asset] is None:
                continue
            self.price_queue[asset].append(bts_price_in_btc
                                           / self.bts_price.rate_btc[asset])
            if len(self.price_queue[asset]) > self.sample:
                self.price_queue[asset].pop(0)
            average_price[asset] = sum(
                self.price_queue[asset])/len(self.price_queue[asset])
        self.patch_nasdaqc(average_price)
        return average_price

    def display_depth(self, volume):
        t = PrettyTable([
            "market", "bid price", "bid_volume", "ask price", "ask_volume"])
        t.align = 'r'
        t.border = True
        for market in sorted(self.valid_depth):
            _bid_price = "%.8f" % self.valid_depth[market]["bid_price"]
            _bid_volume = "{:,.0f}".format(
                self.valid_depth[market]["bid_volume"])
            _ask_price = "%.8f" % self.valid_depth[market]["ask_price"]
            _ask_volume = "{:,.0f}".format(
                self.valid_depth[market]["ask_volume"])
            t.add_row([
                market, _bid_price, _bid_volume, _ask_price, _ask_volume])
        print(t.get_string())

    def display_price(self):
        t = PrettyTable([
            "asset", "current(/BTC)", "current(/BTS)", "current(BTS/)",
            "median(/BTS)", "median(BTS/)", "my feed"])
        t.align = 'r'
        t.border = True
        for asset in sorted(self.filter_price):
            _price_btc = "%.3f" % (1/self.bts_price.rate_btc[asset])
            _price_bts1 = "%.8f" % self.price_queue[asset][-1]
            _price_bts2 = "%.3f" % (1/self.price_queue[asset][-1])
            _median_bts1 = "%.8f" % self.filter_price[asset]
            _median_bts2 = "%.3f" % (1/self.filter_price[asset])
            if self.feedapi.my_feeds and asset in self.feedapi.my_feeds:
                _my_feed = "%.8f" % self.feedapi.my_feeds[asset]["price"]
            else:
                _my_feed = 'x'
            t.add_row([
                asset, _price_btc, _price_bts1,
                _price_bts2, _median_bts1, _median_bts2, _my_feed])
        print(t.get_string())

    def task_get_price(self):
        bts_price_in_btc, volume = self.fetch_bts_price()
        self.price_filter(bts_price_in_btc)
        os.system("clear")
        cur_t = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time()))
        bts_price_in_cny = bts_price_in_btc / self.bts_price.rate_btc["CNY"]
        print("[%s] efficent price: %.5f CNY/BTS, depth: %s BTS" % (
            cur_t, bts_price_in_cny, "{:,.0f}".format(volume)))
        self.display_depth(volume)
        print()
        self.display_price()

    def check_publish(self, asset_list, my_feeds, real_price):
        need_publish = {}
        for asset in asset_list:
            if asset not in my_feeds:
                need_publish[asset] = real_price[asset]
                continue
            if (datetime.utcnow() - my_feeds[asset]["timestamp"]). \
                    total_seconds() > \
                    self.feedapi.asset_info[asset]["feed_lifetime_sec"] - 600:
                need_publish[asset] = real_price[asset]
                continue
            change = fabs(my_feeds[asset]["price"] - real_price[asset]) * \
                100.0 / my_feeds[asset]["price"]
            if change > self.config["price_limit"]["change_min"] and  \
                    change < self.config["price_limit"]["change_max"]:
                need_publish[asset] = real_price[asset]
                continue
        return need_publish

    def task_publish_price(self):
        if not self.config["witness"]:
            return
        self.feedapi.fetch_feed()
        feed_need_publish = self.check_publish(
            self.feedapi.asset_list, self.feedapi.my_feeds, self.filter_price)
        if feed_need_publish:
            self.logger.info("publish feeds: %s" % feed_need_publish)
            self.feedapi.publish_feed(feed_need_publish)

    def excute(self):
        while True:
            try:
                self.task_get_price()
                self.task_publish_price()
            except Exception as e:
                print(e)
                self.logger.exception(e)
            time.sleep(int(self.config["timer_minute"]*60))

if __name__ == '__main__':
    feedprice = FeedPrice()
    feedprice.excute()
