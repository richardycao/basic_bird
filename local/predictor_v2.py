from confluent_kafka import Consumer, KafkaException
from json import loads
import numpy as np
import sys

class Predictor(object):
  def __init__(self, topic):
    self.topic = topic
    conf = {
      'bootstrap.servers': 'localhost:9092',
      'group.id': 'test1',
      'session.timeout.ms': 6000,
      'auto.offset.reset': 'earliest'
    }
    self.receiver = Consumer(conf)
    self.receiver.subscribe([topic])

  def run(self):
    try:
      while True:
        msg = self.receiver.poll(timeout=1.0)
        if msg is None:
          continue
        if msg.error():
          raise KafkaException(msg.error())
        else:
          print(msg.value().decode("utf-8"))
    except KeyboardInterrupt:
      sys.stderr.write('%% Aborted by user\n')
    finally:
      # Close down consumer to commit final offsets.
      self.receiver.close()

if __name__ == "__main__":
    c = Predictor(topic='processed2')
    c.run()
    
    
