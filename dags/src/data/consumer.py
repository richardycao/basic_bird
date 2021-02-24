from kafka import KafkaConsumer
from json import loads

def retrieve_stream():
  print('Starting consumer...')
  consumer = KafkaConsumer(
    'Topic1',
    bootstrap_servers=['kafka:9092'],
    consumer_timeout_ms=30000,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda x: loads(x.decode('utf-8'))
  )

  print('Consumer constructed')

  for message in consumer:
    print('consumer:', message.value)

  consumer.close()