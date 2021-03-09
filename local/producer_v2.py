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

bootstrap_servers = "localhost:9092"
topic = 'confluent-kafka-topic'
conf = {
  'bootstrap.servers': 'localhost:9092'
}
producer = Producer(**conf)

params = {
    'type': 'subscribe',
    'product_ids': [
        'BTC-USD'
    ],
    'channels': [
        'level2'
    ]
}

def on_message(ws, message):
    global producer
    data = json.loads(message)

    producer.produce('test', value=message)
    producer.poll(0)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

# reference: https://pypi.org/project/websocket_client/
def on_open(ws):
    def run(*args):
        ws.send(json.dumps(params))
    thread.start_new_thread(run, ())

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://ws-feed.pro.coinbase.com",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()