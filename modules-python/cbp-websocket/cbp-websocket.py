from hummingbird import Module
import websocket
import json
import sys, getopt
try:
    import thread
except ImportError:
    import _thread as thread

"""
Documentation for CBPWebsocket

Description: Short for "Coinbase Pro Websocket". Reads streamed data from the
             Coinbase Pro websocket for a variety of channels, such as level2,
             ticker, heartbeat, etc. Sends the data to a Kafka partition for
             load balancing before being serviced by the next module.

Parameters:
    product_ids: comma-separated product ids from Coinbase Pro API.
                 e.g. 'BTC-USD,XLM-USD'
    channels   : comma-separated channels from Coinbase Pro API

Message Format:
    Input: N/A
    Output: See https://docs.pro.coinbase.com/?python#channels

Command:
    python3 cbp-websocket.py --product_ids <product ids> --channels <channels>
    e.g. python3 cbp-websocket.py --product_ids BTC-USD,XLM-USD --channels level2,ticker

"""

class CBPWebsocket(Module):
    def __init__(self, args):
        super().__init__(args)

        self.setInput(False)
        self.setOutput(True)

        self.add_argument('product_ids', lambda x: x.split(','))
        self.add_argument('channels', lambda x: x.split(','))
        self.build()

        self.websocket_params = {
            'type': 'subscribe',
            'product_ids': self.args['product_ids'], # e.g. ['BTC-USD']
            'channels': self.args['channels']        # e.g. ['level2']
        }

        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("wss://ws-feed.pro.coinbase.com",
                                        on_open = self.on_open,
                                        on_message = self.on_message,
                                        on_error = self.on_error,
                                        on_close = self.on_close)
        self.ws.on_open = self.on_open

    def on_message(self, ws, message):
        #print(json.dumps(message).encode('utf-8'))
        self.send(message)

    def on_error(self, ws, error):
        self.closeIO()
        print(error)

    def on_close(self, ws):
        self.closeIO()
        print("### closed ###")

    def on_open(self, ws):
        def run(*args):
            self.ws.send(json.dumps(self.websocket_params))
        thread.start_new_thread(run, ())

    def run(self):
        print('run')
        self.ws.run_forever()

if __name__ == "__main__":
    c = CBPWebsocket(sys.argv[1:])
    c.run()