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
            value_deserializer=lambda x: loads(x.decode('utf-8'))
        )

    def run(self):
        for msg in self.receiver:
            message = msg.value
            print(message)

if __name__ == "__main__":
    c = Predictor(topic='processed')
    c.run()
    
    
