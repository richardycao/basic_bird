from kafka import KafkaConsumer
from json import loads
import numpy as np
from sortedcontainers import SortedDict, SortedList

class Consumer(object):
    def __init__(self, topic):
        self.topic = topic
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='test1',
            value_deserializer=lambda x: loads(x.decode('utf-8'))
        )
        self.bid_breakpoints = [-0.01, -0.005, 0]
        self.ask_breakpoints = [0, 0.005, 0.01]
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

    def binary_search(self, arr, l, r, x): 
        if r >= l: 
            mid = l + (r - l) // 2
            if arr[mid] == x: 
                return mid 
            elif arr[mid] > x: 
                return self.binary_search(arr, l, mid-1, x) 
            else: 
                return self.binary_search(arr, mid + 1, r, x) 
        else: 
            return np.clip(l + (r - l) // 2, 0, len(arr) - 1)

    def find_div(self, arr, val):
        return self.binary_search(arr, 0, len(arr)-1, val)

    def preprocess(self):
        midpoint = (self.bids.peekitem(-1)[0] + self.asks.peekitem(0)[0]) / 2
        
        # Convert bids/asks dicts to SortedLists and scale them around 0
        scaled_bids = SortedList(map(lambda x: x[0] / midpoint - 1, self.bids.items()))
        scaled_asks = SortedList(map(lambda x: x[0] / midpoint - 1, self.asks.items()))

        # Find breakpoint indices at which to divide the bids and asks into buckets
        bid_dividers = [_ for _ in map(lambda x: self.find_div(scaled_bids, x), self.bid_breakpoints)]
        ask_dividers = [_ for _ in map(lambda x: self.find_div(scaled_asks, x), self.ask_breakpoints)]

        bid_dividers.insert(0, 0)
        bid_dividers.append(len(scaled_bids))
        ask_dividers.insert(0, 0)
        ask_dividers.append(len(scaled_asks))

        # Bucketize them, divided by the breakpoints
        bid_volumes = [0 for _ in range(len(self.bid_breakpoints)+1)]
        for i in range(len(bid_dividers)-1):
            bid_vals = [_ for _ in self.bids.values()]
            bid_volumes[i] = np.sum(bid_vals[bid_dividers[i]:bid_dividers[i+1]])

        ask_volumes = [0 for _ in range(len(self.ask_breakpoints)+1)]
        for i in range(len(ask_dividers)-1):
            ask_vals = [_ for _ in self.asks.values()]
            ask_volumes[i] = np.sum(ask_vals[ask_dividers[i]:ask_dividers[i+1]])

        return bid_volumes, ask_volumes

    def run(self):
        for msg in self.consumer:
            message = msg.value
            if message['type'] == 'snapshot':
                self.init_order_book(message)
            elif message['type'] == 'l2update':
                self.update_order_book(message)

                print(self.t)
                if self.t % 1000 == 0:
                    bv, av = self.preprocess()
                    print(bv, av)
                self.t += 1

if __name__ == "__main__":
    c = Consumer(topic='Topic1')
    c.run()
    
    
