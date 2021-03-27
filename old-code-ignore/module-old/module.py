from confluent_kafka import Producer, Consumer, KafkaException
import sys
import getopt
import json

class Module(object):
  def __init__(self, args):
    self.topic_in, self.topic_out, self.servers_in, self.servers_out = "", "", "", ""
    self.extract_args(args)
    
    if self.topic_in != "" and self.servers_in != "":
      print('Creating consumer')
      conf_in = {
        'bootstrap.servers': self.servers_in,
        'group.id': 'test1',
        'session.timeout.ms': 30000,
        'auto.offset.reset': 'earliest'
      }
      self.consumer = Consumer(conf_in)
      self.consumer.subscribe([self.topic_in])

    if self.topic_out != "" and self.servers_out != "":
      print('Creating producer')
      conf_out = { 'bootstrap.servers': self.servers_out }
      self.producer = Producer(**conf_out)
  
  def extract_args(self, args):
    arguments = sys.argv[1:]
    options = "i:o:s:t:"
    
    long_options = ["input-stream", "output-stream", "input-host-port", "output-host-port"]

    try:
      arguments, _ = getopt.getopt(arguments, options, long_options)
      
      for currentArgument, currentValue in arguments:
        if currentArgument in ("-i", "--input-stream"):
          self.topic_in = currentValue
        elif currentArgument in ("-o", "--output-stream"):
          self.topic_out = currentValue
        elif currentArgument in ("-s", "--input-host-port"):
          self.servers_in = currentValue
        elif currentArgument in ("-t", "--output-host-port"):
          self.servers_out = currentValue
                
    except getopt.error as err:
      print(str(err))
  
  def delivery_callback(self, err, msg):
    if err:
      print('Delivery_callback failed delivery:', err)
      print(json.loads(msg))

  def run(self):
    pass