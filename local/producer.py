from time import sleep
import json
from json import dumps
from kafka import KafkaProducer
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: dumps(x).encode('utf-8')
    )

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
    # bid_ask = {
    #     'id': data['product_id'],
    #     'bid': data['best_bid'],
    #     'ask': data['best_ask'],
    #     'action': data['side'],
    #     'volume': data['last_size']
    # }
    
    # price = {
    #     'id': data['product_id'],
    #     'price': data['price']
    # }

    # l2data = {
    #     'type': data['type'],
    #     'id': data['product_id'],
    #     'changes': data['changes'],
    #     'time': data['time']
    # }

    producer.send('raw', value=data)

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