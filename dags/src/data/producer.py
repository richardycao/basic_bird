from kafka import KafkaProducer
from json import dumps

def test_function():
  print('this is a test function')
  return 0

def generate_stream():
  print('Starting producer...')
  producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda x: dumps(x).encode('utf-8')
    )
  
  for i in range(10):
    print('producer:', i)
    producer.send('Topic1', value={'hello': i})
    
  producer.close()