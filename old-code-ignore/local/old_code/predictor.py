from kafka import KafkaConsumer
from json import loads
import numpy as np

class Predictor(object):
    def __init__(self, topic):
        self.topic = topic
        self.receiver = KafkaConsumer(
            topic,
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='test1',
            value_deserializer=lambda x: x
        )

    def run(self):
        for msg in self.receiver:
            print(msg.value.decode("utf-8"))
            #message = msg.value
            #print(message)

if __name__ == "__main__":
    c = Predictor(topic='processed2')
    c.run()
    
    
