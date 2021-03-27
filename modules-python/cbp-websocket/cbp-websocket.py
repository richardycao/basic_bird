# python3.7 cbp-websocket.py --product_ids BTC-USD --channels ticker --servers-out kafka:29092 --group-id asdf

from hummingbird import Module
import websocket
import json
import sys, getopt
try:
    import thread
except ImportError:
    import _thread as thread

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
        #print(message)
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