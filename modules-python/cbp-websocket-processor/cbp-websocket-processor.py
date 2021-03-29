from hummingbird import Module
import json
import sys

"""
Documentation for CBPWebsocketProcessor

Description: Processes data for each type of websocket channel.
    Type:
        ticker: Constructs records of bars (tick, time, volume, dollar). Outputs data 
                in a feature vector for the next module to train on immediately.
        level2: Not supported yet.

Parameters:
    type: 'ticker' or 'level2' (for now)
    bar-type: comma-separated list of 'tick', 'time', 'volume', 'dollar'
    ...

Message Format:
    Input: See https://docs.pro.coinbase.com/?python#channels
    Output: Produces data depending on the channel type.
        ticker: Contains some or all of {tick, time, volume, dollar}. It depends on when 
                they are each ready to be produced. The message will only contain what's
                being produced.
            {
                type: 'ticker',
                data: {
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
            }
        level2: {
            'type': 'l2update',
            'data': {

            }
        }

Command:
    ...

"""

class CBPWebsocketProcessor(Module):
    def __init__(self, args):
        super().__init__(args)

        self.setInput(True)
        self.setOutput(True)
        self.add_argument('type', lambda x: x)
        self.add_argument('bar-type', lambda x: x.split(','))
        self.build()

        self.previous = {
            'price': 0,
            'best_bid': 0,
            'best_ask': 0,
            'time': "", # Find out how to convert time from the message to something else
            'last_size': 0
        }
        
    def ready_produce_tick_bar(self):
        return 'tick' in self.args['bar-type']
    
    def ready_produce_time_bar(self):
        # Need to include an argument for duration of each bar
        return False

    def ready_produce_volume_bar(self):
        # Need to include an argument for volume of each bar
        return False
    
    def ready_produce_dollar_bar(self):
        # Need to include an argument for dollar value of each bar
        return False
    
    def consume_ticker(self, message):
        msg = {
          'type': 'ticker',
          'data': {}
        }
        if self.ready_produce_tick_bar():
            msg['data']['tick'] = {
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

    def msg_consume(self, message):
        if message['type'] == 'subscriptions':
            pass
        elif message['type'] == 'ticker':
            return self.consume_ticker(message)
        elif message['type'] == 'snapshot':
            pass #self.init_order_book(message)
        elif message['type'] == 'l2update':
            pass #self.update_order_book(message)

    def run(self):
        try:
            while True:
                message = self.receive()

                if message != None:
                    data = self.msg_consume(message)
                    self.send(data)
        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            self.closeIO()

if __name__ == "__main__":
  c = CBPWebsocketProcessor(sys.argv[1:])
  c.run()
