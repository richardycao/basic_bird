from time import sleep
import json
from json import dumps
from confluent_kafka import Producer
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time

class Fetcher(object):
    def __init__(self, topic_out, servers_out):
        self.topic_out = topic_out

        conf = { 'bootstrap.servers': servers_out }
        self.producer = Producer(**conf)

        self.params = {
            'type': 'subscribe',
            'product_ids': [
                'BTC-USD'
            ],
            'channels': [
                'level2'
            ]
        }

        self.ws = websocket.WebSocketApp("wss://ws-feed.pro.coinbase.com",
                                         on_open = self.on_open,
                                         on_message = self.on_message,
                                         on_error = self.on_error,
                                         on_close = self.on_close)
        self.ws.on_open = self.on_open
    
    def delivery_callback(self, err, msg):
        if err:
            print('Delivery_callback failed delivery:', err)
            print(json.loads(msg))

    def on_message(self, ws, message):
        self.producer.produce('q1', value=message, callback=self.delivery_callback)
        self.producer.poll(0)

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
    websocket.enableTrace(True)
    f = Fetcher(topic_out='q1', servers_out='kafka0:29092')
    f.run()