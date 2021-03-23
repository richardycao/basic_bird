import coinbasepro as cbp
from confluent_kafka import Consumer, KafkaException
from json import loads
import numpy as np
import sys
import datetime

class Executor(object):
  def __init__(self, key, secret, passphrase, topic_in, servers_in):
    auth_client = cbp.AuthenticatedClient(key=key,
                                          secret=secret,
                                          passphrase=passphrase)

    self.topic_in = topic_in
    conf_in = {
      'bootstrap.servers': servers_in,
      'group.id': 'test1',
      'session.timeout.ms': 30000,
      'auto.offset.reset': 'earliest'
    }
    self.consumer = Consumer(conf_in)
    self.consumer.subscribe([topic_in])

  def construct_order(self, msg):
    return 0

  def execute_order(self, order):
    return 0

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

          order = self.construct_order(msg.value().decode("utf-8"))
          success = self.execute_order(order)
    except KeyboardInterrupt:
      sys.stderr.write('%% Aborted by user\n')
    finally:
      # Close down consumer to commit final offsets.
      self.consumer.close()

if __name__ == "__main__":
  if len(sys.argv) != 4:
    print('Please use the following format:')
    print('python3 executor.py <key> <secret> <passphrase>')

  key = sys.argv[1]
  secret = sys.argv[2]
  passphrase = sys.argv[3]

  client = cbp.PublicClient()
  

  #ex = Executor(key=key, secret=secret, passphrase=passphrase, topic_in='q3', servers_in='kafka0:29092')
  #ex.run()
    