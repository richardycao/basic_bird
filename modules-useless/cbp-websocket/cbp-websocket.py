from hummingbird import Module2
import websocket
import json
import sys, getopt
try:
    import thread
except ImportError:
    import _thread as thread

"""
TODO:
Do step 3 here:
https://github.com/binance-us/binance-official-api-docs/blob/master/web-socket-streams.md#how-to-manage-a-local-order-book-correctly

To get the existing bid/ask first. Currently I'm only getting the updates.
"""

class CBPWebsocket(Module2):
    def __init__(self):
        super().__init__()

        self.set_param('product_ids', required=True)
        self.set_param('channels', required=True)

        self.websocket_params = {
            'type': 'subscribe',
            'product_ids': self.params['product_ids'], # e.g. ['BTC-USD']
            'channels': self.params['channels']        # e.g. ['level2']
        }

        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("wss://ws-feed.pro.coinbase.com",
                                        on_open = self.on_open,
                                        on_message = self.on_message,
                                        on_error = self.on_error,
                                        on_close = self.on_close)
        self.ws.on_open = self.on_open

    def on_message(self, ws, message):
        self.send(message, encode=False)

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
    c = CBPWebsocket()
    c.run()