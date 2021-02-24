from kafka import KafkaConsumer
from json import loads
import numpy as np

consumer = KafkaConsumer(
    'Topic1',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)

print('hi')

for message in consumer:
    print('mes')
    message = message.value
    print('Received.. {}'.format(message))