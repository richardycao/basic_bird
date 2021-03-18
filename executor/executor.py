import coinbasepro as cbp
from confluent_kafka import Consumer, KafkaException
from json import loads
import numpy as np
import sys
import datetime

class Executor(object):
  def __init__(self, topic_in, servers_in):
    self.client = cbp.PublicClient()

    self.topic_in = topic_in
    conf_in = {
      'bootstrap.servers': servers_in,
      'group.id': 'test1',
      'session.timeout.ms': 30000,
      'auto.offset.reset': 'earliest'
    }
    self.consumer = Consumer(conf_in)
    self.consumer.subscribe([topic_in])

  def run(self):
    try:
      while True:
        msg = self.consumer.poll(timeout=1.0)
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
      self.consumer.close()

if __name__ == "__main__":
    c = Executor(topic_in='q3', servers_in='kafka0:29092')
    c.run()
    