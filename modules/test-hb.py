from hummingbird import Module

# python3.7 cbp-websocket.py -o cbp-websocket-data -t kafka0:29092

import websocket
import json
import sys
try:
    import thread
except ImportError:
    import _thread as thread

class CBPWebsocket(Module):
    def __init__(self, args):
        super().__init__(args)

        self.params = {
                'type': 'subscribe',
                'product_ids': [
                    'BTC-USD'
                ],
                'channels': [
                    'level2'
                ]
            }

        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("wss://ws-feed.pro.coinbase.com",
                                        on_open = self.on_open,
                                        on_message = self.on_message,
                                        on_error = self.on_error,
                                        on_close = self.on_close)
        self.ws.on_open = self.on_open

    def on_message(self, ws, message):
        print(message)
        # self.producer.produce(self.args['topics_out'][0], value=message, callback=self.delivery_callback)
        # self.producer.poll(0)

    def on_error(self, ws, error):
        self.producer.flush()
        print(error)

    def on_close(self, ws):
        self.producer.flush()
        print("### closed ###")

    def on_open(self, ws):
        def run(*args):
            self.ws.send(json.dumps(self.params))
        thread.start_new_thread(run, ())

    def run(self):
        self.ws.run_forever()

if __name__ == "__main__":
    c = CBPWebsocket(sys.argv[1:])
    c.run()