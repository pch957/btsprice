# -*- coding: utf-8 -*-
import requests


def is_float_try(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


class Yahoo(object):
    def __init__(self):
        self.header = {'content-type': 'application/json',
                       'User-Agent': 'Mozilla/5.0 Gecko/20100101 Firefox/22.0'}
        self.param_s = {}
        self.quote = {}
        self.scale = {}
        self.init_param_dict1()
        self.init_param_dict2()
        self.init_param_dict3()
        self.rate = {'CNY': {'CNY': 1.0}, 'USD': {'USD': 1.0}}

    def init_param_dict1(self):
        assets = ["CNY", "KRW", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD",
                  "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "BTC"]
        for asset in assets:
            self.param_s[asset] = asset + "USD=X"

        self.param_s["GOLD"] = "XAUUSD=X"
        self.param_s["SILVER"] = "XAGUSD=X"
        for asset in self.param_s:
            self.quote[asset] = "USD"

    def init_param_dict2(self):
        # todo:"OIL", GAS", "DIESEL"
        self.param_s["SHENZHEN"] = '399106.SZ'
        self.quote["SHENZHEN"] = "CNY"
        self.param_s["SHANGHAI"] = '000001.SS'
        self.quote["SHANGHAI"] = "CNY"
        self.param_s["NASDAQC"] = '^IXIC'
        self.quote["NASDAQC"] = "USD"
        self.param_s["NIKKEI"] = '^N225'
        self.quote["NIKKEI"] = "JPY"
        self.param_s["HANGSENG"] = '^HSI'
        self.quote["HANGSENG"] = "HKD"

    def init_param_dict3(self):
        self.param_s["BDR.AAPL"] = 'AAPL'
        self.quote["BDR.AAPL"] = "USD"
        self.scale["BDR.AAPL"] = 0.001

    def get_query_param(self, assets):
        query_string = ','.join(
            '%s' % (self.param_s[asset]) for asset in assets)
        params = {'s': query_string, 'f': 'l1', 'e': '.csv'}
        return params

    def fetch_price(self, assets=None):
        if assets is None:
            assets = self.param_s.keys()
        url = "http://download.finance.yahoo.com/d/quotes.csv"
        try:
            params = self.get_query_param(assets)
            response = requests.get(
                url=url, headers=self.header, params=params, timeout=3)

            price = dict(zip(assets, response.text.split()))
            for asset in assets:
                if is_float_try(price[asset]):
                    scale = 1.0
                    if asset in self.scale:
                        scale = self.scale[asset]
                    if self.quote[asset] == "CNY":
                        self.rate["CNY"][asset] = float(price[asset])
                    elif self.quote[asset] == "USD":
                        self.rate["USD"][asset] = float(price[asset])
                    else:
                        self.rate["USD"][asset] = float(price[asset]) * \
                            float(price[self.quote[asset]]) * scale
        except:
            print("Error fetching results from yahoo!")
        return self.rate

if __name__ == "__main__":
    yahoo = Yahoo()
    rate = yahoo.fetch_price()
    print(rate)
