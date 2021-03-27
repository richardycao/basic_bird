from hummingbird import Module
import numpy as np
from sortedcontainers import SortedDict
import sys

"""
Documentation for CBPLevel2Processor

Description: Short for "Coinbase Pro Websocket Processor". Reads load-balanced
             websocket data for the level2 channel. Maintains a real-time order
             book. Sends a message of the 10 highest bids and 10 lowest asks.

Parameters:
    None yet.

Message Format:
    Input: See https://docs.pro.coinbase.com/?python#channels
    Output:
        {
            TODO
        }

Command:
    python3 cbp-level2-processor.py
    e.g. python3 cbp-level2-processor.py

"""

class CBPLevel2Processor(Module):
    def __init__(self, args):
        super().__init__(args)

        self.setInput(True)
        self.setOutput(True)
        self.build()

        self.bids = SortedDict({})
        self.asks = SortedDict({})

        self.highest_bid_price = 0
        self.highest_bid_size = 0
        self.lowest_ask_price = 0
        self.lowest_ask_size = 0

    def init_order_book(self, message):
        print('Initializing order book.')
        self.bids = SortedDict(map(lambda x: [float(x[0]), float(x[1])], message['bids']))
        self.asks = SortedDict(map(lambda x: [float(x[0]), float(x[1])], message['asks']))

        self.highest_bid_price = self.bids.peekitem(-1)[0]
        self.highest_bid_size = self.bids.peekitem(-1)[1]
        self.lowest_ask_price = self.asks.peekitem(0)[0]
        self.lowest_ask_size = self.asks.peekitem(0)[1]

    def update_order_book(self, message):
        send = False
        for c in message['changes']:
            price = float(c[1])
            size = float(c[2])
            if c[0] == 'buy':
                if price in self.bids:
                    if size == 0.0:
                        self.bids.pop(price, 0)
                    else:
                        self.bids[price] = size
                elif size != 0:
                    self.bids[price] = size
            if c[0] == 'sell':
                if price in self.asks:
                    if size == 0.0:
                        self.asks.pop(price, 0)
                    else:
                        self.asks[price] = size
                elif size != 0:
                    self.asks[price] = size
        
        if len(self.bids) != 0 and len(self.asks) != 0:
            if (self.highest_bid_price != self.bids.peekitem(-1)[0] or 
            self.highest_bid_size != self.bids.peekitem(-1)[1] or 
            self.lowest_ask_price != self.asks.peekitem(0)[0] or 
            self.lowest_ask_size != self.asks.peekitem(0)[1]):
                self.highest_bid_price = self.bids.peekitem(-1)[0]
                self.highest_bid_size = self.bids.peekitem(-1)[1]
                self.lowest_ask_price = self.asks.peekitem(0)[0]
                self.lowest_ask_size = self.asks.peekitem(0)[1]

                send = True

        return send

    def process(self, size=10):
        if len(self.bids) < size or len(self.asks) < size:
            return 
        midpoint = (self.bids.peekitem(-1)[0] + self.asks.peekitem(0)[0]) / 2

        scaled_bids = np.array([[self.bids.peekitem(-1-i)[0]/midpoint, self.bids.peekitem(-1-i)[1]] for i in range(size)])
        scaled_asks = np.array([[self.asks.peekitem(i)[0]/midpoint,    self.asks.peekitem(i)[1]]    for i in range(size)])

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
                message = self.receive()

                if message is not None:
                    print(message)
                    # should_produce = self.msg_consume(message)

                    # if should_produce:
                    #     data = self.process(1)
                    #     if data:
                    #         pass
                    #         # self.producer.produce(self.topic_out, value=dumps(str(self.highest_bid_price)+" | "+str(self.lowest_ask_price)).encode('utf-8'))
                    #         self.send(data)
        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            self.closeIO()

if __name__ == "__main__":
    c = CBPLevel2Processor(sys.argv[1:])
    c.run()