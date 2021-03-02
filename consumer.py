from kafka import KafkaConsumer
from json import loads
import numpy as np
from sortedcontainers import SortedDict

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
        self.i = 0
    
    def init_order_book(self, message):
        self.bids = SortedDict(map(lambda x: [float(x[0]), float(x[1])], message['bids']))
        self.asks = SortedDict(map(lambda x: [float(x[0]), float(x[1])], message['asks']))

    def update_order_book(self, message):
        for c in message['changes']:
            if c[0] == 'buy':
                self.bids[float(c[1])] = float(c[2])
            if c[0] == 'sell':
                self.asks[float(c[1])] = float(c[2])

    def run(self):
        for msg in self.consumer:
            message = msg.value
            if message['type'] == 'snapshot':
                self.init_order_book(message)
            elif message['type'] == 'l2update':
                self.update_order_book(message)

            print(self.i)
            self.i += 1

if __name__ == "__main__":
    c = Consumer(topic='Topic1')
    c.run()
    
    
