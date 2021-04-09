from hummingbird import Module2
import tensorflow as tf
import sys
from time import sleep
import datetime

"""
Documentation for TestStratPredict

Description:

Parameters:
    currency: can be one of "BTC", "USD", etc. (any single currency)

Message Format:
    Input: 
    Output: 

Command:

"""

class TestStratPredict(Module2):
    def __init__(self):
        super().__init__()

        self.initial_price = -1

    def msg_consume(self, message):
        if self.initial_price == -1:
            self.initial_price = message[0]

        features = tf.reshape(tf.constant(message[1:]), [1, -1])
        features /= message[0]
        print(features)
        
        return 0

    def run(self):
        try:
            while True:
                message = self.receive()

                if message != None:
                    data = self.msg_consume(message)
                    # self.send(data)

        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            self.closeIO()

if __name__ == "__main__":
    c = TestStratPredict()
    c.run()
