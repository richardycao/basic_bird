from hummingbird import Module
import json
import sys

"""
Documentation for CBPTickerProcessor

Description: Constructs records of bars (tick, time, volume, dollar). Outputs data 
             in a feature vector for the next module to train on immediately.

Parameters:
    type: comma-separated list of 'tick', 'time', 'volume', 'dollar'

Message Format:
    Input: See https://docs.pro.coinbase.com/?python#channels
    Output: May not contain all of {tick, time, volume, dollar} at once. It depends 
            on when they are each ready to be produced. The message will only contain what's
            being produced.
    {
        'tick': {
            'price': 0,
            'best_bid': 0,
            'best_ask': 0,
            'last_size': 0
        },
        'time': {

        },
        'volume': {

        },
        'dollar': {

        }
    }

Command:
    python3 cbp-ticker-processor.py --type <comma-separated bar types>
    e.g. python3 cbp-ticker-processor.py --type tick

"""

class CBPTickerProcessor(Module):
    def __init__(self, args):
        super().__init__(args)

        self.setInput(True)
        self.setOutput(True)
        self.add_argument('type', lambda x: x.split(','))
        self.build()

        self.previous = {
            'price': 0,
            'best_bid': 0,
            'best_ask': 0,
            'time': "", # Find out how to convert time from the message to something else
            'last_size': 0
        }
        
    def ready_produce_tick_bar(self):
        return True
    
    def ready_produce_time_bar(self):
        # Need to include an argument for duration of each bar
        return False

    def ready_produce_volume_bar(self):
        # Need to include an argument for volume of each bar
        return False
    
    def ready_produce_dollar_bar(self):
        # Need to include an argument for dollar value of each bar
        return False
    
    def msg_consume(self, message):
        # if message['type'] == 'snapshot':
        #     self.init_order_book(message)
        #     return True
        # elif message['type'] == 'l2update':
        #     should_produce = self.update_order_book(message)
        #     return should_produce
        msg = {}
        if self.ready_produce_tick_bar():
            msg['tick'] = {
                'price': float(message['price']),
                'best_bid': float(message['best_bid']),
                'best_ask': float(message['best_ask']),
                'change': float(message['price']) - self.previous['price'],
                'last_size': float(message['last_size'])
            }
        if self.ready_produce_time_bar():
            pass
        if self.ready_produce_volume_bar():
            pass
        if self.ready_produce_dollar_bar():
            pass

        self.previous = {
            'price': float(message['price']),
            'best_bid': float(message['best_bid']),
            'best_ask': float(message['best_ask']),
            'time': message['time'],
            'last_size': float(message['last_size'])
        }

        return msg

    def run(self):
        try:
            while True:
                message = self.receive()

                if message != None:
                    if message['type'] == 'ticker':
                        print("1:",message)
                        print("1.5:", message['type'])
                        # msg = json.loads(message)
                        # print("2:", msg)
                        # print("3:", msg['price'])
                        data = self.msg_consume(message)
                        self.send(data)
        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            self.closeIO()

if __name__ == "__main__":
  c = CBPTickerProcessor(sys.argv[1:])
  c.run()
