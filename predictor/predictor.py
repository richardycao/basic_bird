from confluent_kafka import Producer, Consumer, KafkaException
from json import loads
import numpy as np
import sys
import datetime

class Predictor(object):
  def __init__(self, topic_in, topic_out, servers_in, servers_out):
    self.topic_in = topic_in
    self.topic_out = topic_out

    conf_in = {
      'bootstrap.servers': servers_in,
      'group.id': 'test1',
      'session.timeout.ms': 30000,
      'auto.offset.reset': 'earliest'
    }
    self.consumer = Consumer(conf_in)
    self.consumer.subscribe([topic_in])

    conf_out = { 'bootstrap.servers': servers_out }
    self.producer = Producer(**conf_out)

  def delivery_callback(self, err, msg):
    if err:
      print('Delivery_callback failed delivery:', err)
      print(loads(msg))

  def run(self):
    try:
      while True:
        msg = self.consumer.poll(timeout=1.0)
        if msg is None:
          continue
        if msg.error():
          raise KafkaException(msg.error())
        else:
          #print(datetime.datetime.now(), "====predictor=====")
          print(msg.value().decode("utf-8"))
          decision = 0

          self.producer.produce(self.topic_out, value=dumps(decision).encode('utf-8'), callback=self.delivery_callback)
          self.producer.poll(0)
    except KeyboardInterrupt:
      sys.stderr.write('%% Aborted by user\n')
    finally:
      # Close down consumer to commit final offsets.
      self.consumer.close()

if __name__ == "__main__":
    c = Predictor(topic_in='q2', topic_out='q3', servers_in='kafka0:29092', servers_out='kafka0:29092')
    c.run()
    
    
