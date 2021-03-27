from confluent_kafka import Producer, Consumer, KafkaException
from json import loads, dumps
import numpy as np
from sortedcontainers import SortedDict, SortedList
import sys

class Preprocessor(object):
    def __init__(self, topic_in, topic_out):
        self.topic_in = topic_in
        self.topic_out = topic_out

        conf_in = {
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'test1',
            'session.timeout.ms': 6000,
            'auto.offset.reset': 'earliest'
        }
        self.consumer = Consumer(conf_in)
        self.consumer.subscribe([topic_in])

        conf_out = { 'bootstrap.servers': 'localhost:9092' }
        self.producer = Producer(**conf_out)
    
    def init_order_book(self, message):
        self.bids = SortedDict(map(lambda x: [float(x[0]), float(x[1])], message['bids']))
        self.asks = SortedDict(map(lambda x: [float(x[0]), float(x[1])], message['asks']))

        self.highest_bid_price = self.bids.peekitem(-1)[0]
        self.highest_bid_size = self.bids.peekitem(-1)[1]
        self.lowest_ask_price = self.asks.peekitem(0)[0]
        self.lowest_ask_size = self.asks.peekitem(0)[1]

    def update_order_book(self, message):
        ok = False
        for c in message['changes']:
            price = float(c[1])
            size = float(c[2])
            if c[0] == 'buy':
                if size == 0.0:
                    self.bids.pop(price, 0)
                else:
                    self.bids[price] = size
            if c[0] == 'sell':
                if size == 0.0:
                    self.asks.pop(price, 0)
                else:
                    self.asks[price] = size
        
        if (self.highest_bid_price != self.bids.peekitem(-1)[0] or 
        self.highest_bid_size != self.bids.peekitem(-1)[1] or 
        self.lowest_ask_price != self.asks.peekitem(0)[0] or 
        self.lowest_ask_size != self.asks.peekitem(0)[1]):
            self.highest_bid_price = self.bids.peekitem(-1)[0]
            self.highest_bid_size = self.bids.peekitem(-1)[1]
            self.lowest_ask_price = self.asks.peekitem(0)[0]
            self.lowest_ask_size = self.asks.peekitem(0)[1]

            ok = True

        return ok

    def preprocess(self):
        midpoint = (self.bids.peekitem(-1)[0] + self.asks.peekitem(0)[0]) / 2

        scaled_bids = np.array([[self.bids.peekitem(-1-i)[0]/midpoint, self.bids.peekitem(-1-i)[1]] for i in range(10)])
        scaled_asks = np.array([[self.asks.peekitem(i)[0]/midpoint,    self.asks.peekitem(i)[1]]    for i in range(10)])

        return np.concatenate([np.ravel(scaled_bids), np.ravel(scaled_asks)]).tolist()

    def msg_consume(self, message):
        if message['type'] == 'snapshot':
            self.init_order_book(message)
            return True
        elif message['type'] == 'l2update':
            should_produce = self.update_order_book(message)
            return should_produce

    def run(self):
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())
                else:
                    message = loads(msg.value().decode("utf-8"))
                    should_produce = self.msg_consume(message)

                    if should_produce:
                        data = self.preprocess()
                        self.producer.produce(self.topic_out, value=dumps(data).encode('utf-8'))
                        self.producer.poll(0)
        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            # Close down consumer to commit final offsets.
            self.consumer.close()

if __name__ == "__main__":
    p = Preprocessor(topic_in='test', topic_out='processed2')
    p.run()