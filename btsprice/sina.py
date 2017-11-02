# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import re


def is_float_try(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


class Sina(object):
    def __init__(self):
        header = {
            'content-type': 'application/json',
            'User-Agent': 'Mozilla/5.0 Gecko/20100101 Firefox/22.0'}
        self.session = aiohttp.ClientSession(headers=header)
        self.param_s = {}
        self.quote = {}
        self.scale = {}
        self.init_param_dict1()
        self.init_param_dict2()
        self.rate = {'CNY': {'CNY': 1.0}, 'USD': {'USD': 1.0}}

    def init_param_dict1(self):
        assets = ["CNY", "KRW", "TRY", "SGD", "HKD", "RUB", "SEK", "NZD",
                  "MXN", "CAD", "CHF", "AUD", "GBP", "JPY", "EUR", "ARS"]
        for asset in assets:
            self.param_s[asset] = "fx_s%susd" % asset.lower()

        self.param_s["GOLD"] = "hf_XAU"
        self.param_s["SILVER"] = "hf_XAG"
        for asset in self.param_s:
            self.quote[asset] = "USD"

    def init_param_dict2(self):
        # todo:"OIL", GAS", "DIESEL"
        self.param_s["SHENZHEN"] = 'sz399106'
        self.quote["SHENZHEN"] = "CNY"
        self.param_s["SHANGHAI"] = 'sh000001'
        self.quote["SHANGHAI"] = "CNY"

    def get_query_param(self, assets):
        query_string = ','.join(
            '%s' % (self.param_s[asset]) for asset in assets)
        return query_string

    @asyncio.coroutine
    def fetch_price(self, assets=None):
        if assets is None:
            assets = self.param_s.keys()
        url = "http://hq.sinajs.cn/list="
        try:
            params = self.get_query_param(assets)
            response = yield from asyncio.wait_for(self.session.get(
                url+params), 120)
            response = yield from response.read()
            # print(response)
            price_info = dict(zip(assets, response.decode("gbk").splitlines()))
            price = {}
            for asset in assets:
                pattern = re.compile(r'"(.*)"')
                # print(price_info[asset])
                data = pattern.findall(price_info[asset])[0]
                if self.param_s[asset][:3] == "hf_":
                    price[asset] = data.split(',')[0]
                elif self.param_s[asset][:3] == "fx_":
                    price[asset] = data.split(',')[1]
                else:
                    price[asset] = data.split(',')[3]
                if is_float_try(price[asset]) and float(price[asset]) > 0.0:
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
                # need throw a exception is not float
                else:
                    raise
        except Exception as e:
            print("Error fetching results from sina!", e)
        # print(self.rate)
        return self.rate

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    sina = Sina()
    loop.run_until_complete(sina.fetch_price())
    loop.run_forever()
