from kafka import KafkaProducer, KafkaConsumer
from json import loads, dumps
import numpy as np
from sortedcontainers import SortedDict, SortedList

class Consumer(object):
    def __init__(self, topic, bid_breakpoints, ask_breakpoints, max_width=0.001):
        self.topic = topic
        self.sender = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda x: dumps(x).encode('utf-8')
        )
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='test1',
            value_deserializer=lambda x: loads(x.decode('utf-8'))
        )
        self.bid_breakpoints = bid_breakpoints
        self.ask_breakpoints = ask_breakpoints
        self.max_width = max_width
        self.t = 0
    
    def init_order_book(self, message):
        self.bids = SortedDict(map(lambda x: [float(x[0]), float(x[1])], message['bids']))
        self.asks = SortedDict(map(lambda x: [float(x[0]), float(x[1])], message['asks']))

    def update_order_book(self, message):
        for c in message['changes']:
            price = float(c[1])
            size = float(c[2])
            if c[0] == 'buy':
                if size == 0.0:
                    self.bids.pop(price, 0)
                self.bids[price] = size
            if c[0] == 'sell':
                if size == 0.0:
                    self.asks.pop(price, 0)
                self.asks[price] = size

    def find_div(self, arr, val):
        return np.argmin(np.abs(np.asarray(arr) - val))#.argmin()

    def preprocess(self):
        midpoint = (self.bids.peekitem(-1)[0] + self.asks.peekitem(0)[0]) / 2
        
        # Convert bids/asks dicts to SortedLists and scale them around 0
        scaled_bids = list(filter(lambda y: y > -self.max_width, map(lambda x: x[0] / midpoint - 1, self.bids.items())))
        scaled_asks = list(filter(lambda y: y <  self.max_width, map(lambda x: x[0] / midpoint - 1, self.asks.items())))

        # Find breakpoint indices at which to divide the bids and asks into buckets
        bid_dividers = [_ for _ in map(lambda x: self.find_div(scaled_bids, x), self.bid_breakpoints)]
        ask_dividers = [_ for _ in map(lambda x: self.find_div(scaled_asks, x), self.ask_breakpoints)]

        bid_dividers.append(len(scaled_bids))
        ask_dividers.insert(0, 0)

        # Bucketize them, divided by the breakpoints
        bid_vals = [_ for _ in self.bids.values()]
        ask_vals = [_ for _ in self.asks.values()]

        bid_volumes = [0 for _ in range(len(self.bid_breakpoints))]
        for i in range(len(bid_dividers)-1):
            bid_volumes[i] = np.sum(bid_vals[bid_dividers[i]:bid_dividers[i+1]])

        ask_volumes = [0 for _ in range(len(self.ask_breakpoints))]
        for i in range(len(ask_dividers)-1):
            ask_volumes[i] = np.sum(ask_vals[ask_dividers[i]:ask_dividers[i+1]])

        return bid_volumes, ask_volumes

    def run(self):
        for msg in self.consumer:
            message = msg.value
            if message['type'] == 'snapshot':
                self.init_order_book(message)
            elif message['type'] == 'l2update':
                self.update_order_book(message)

                # 100: consumer reaches 14000 when limit is 16000
                # 200: works
                # see log about 2 queues and C++
                # the bucketizing process seems very slow
                if self.t % 200 == 0:
                    bv, av = self.preprocess()
                    #print(bv, av)
                    self.sender.send('processed', value={'bids': bv, 'asks': av})
                self.t += 1

if __name__ == "__main__":
    c = Consumer(topic='raw', bid_breakpoints=[-0.008, -0.006, -0.004, -0.002], ask_breakpoints=[0.002, 0.004, 0.006, 0.008], max_width=0.01)
    c.run()
    
    
