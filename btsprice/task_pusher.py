# -*- coding: utf-8 -*-

import asyncio
from btspusher import Pusher
import time


class TaskPusher(object):
    def __init__(self, data={}):
        self.expired = 150
        self.topic = "bts.exchanges"
        data_type = ["orderbook", "ticker", "rate"]
        for _type in data_type:
            if _type not in data:
                data[_type] = {}
        self.data = data

    def run_tasks(self, loop, login_info=None):
        def onData(_type, _name, _data, *args, **kwargs):
            if not _type or not _name or not _data:
                return
            if _type not in self.data:
                return
            _time = int(time.time())
            # only update the data which is expired
            if _name in self.data[_type] and \
                    _time - self.data[_type][_name]["time"] < self.expired:
                return
            # print("use:", _type, _name)
            self.data[_type][_name] = _data
        self.pusher = Pusher(loop, login_info)
        self.pusher.sync_subscribe(onData, self.topic)

    def set_expired(self, sec):
        self.expired = sec


if __name__ == "__main__":
    exchange_data = {}
    task_pusher = TaskPusher(exchange_data)
    topic = "public.exchanges"

    def publish_data(_type, _name, _data):
        print("publish: %s %s" % (_type, _name))
        task_pusher.pusher.publish(topic, _type, _name, _data)

    from btsprice.task_exchanges import TaskExchanges
    task_exchanges = TaskExchanges(exchange_data)
    task_exchanges.handler = publish_data
    task_exchanges.set_period(20)

    loop = asyncio.get_event_loop()

    task_pusher.topic = topic
    task_pusher.run_tasks(loop)
    task_exchanges.run_tasks(loop)

    loop.run_forever()
    loop.close()
