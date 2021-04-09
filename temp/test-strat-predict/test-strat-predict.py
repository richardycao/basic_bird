from hummingbird import Module
#import coinbasepro as cbp
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

class TestStratPredict(Module):
    def __init__(self, args):
        super().__init__(args)

        self.setInput(True)
        self.setOutput(False)
        self.add_argument('currency', lambda x: x, default="BTC")
        self.build()

        self.initial_price = -1
        
        """
        Maybe the client isn't necessary here.
        All I need is the starting price, and each subsequent price, which
          comes from the queue.
        Reward is calculated using the starting price as reference.
        """

        # with open('./cbp-creds.txt', 'r') as f:
        #     api = f.readline().strip()
        #     self._KEY = api[api.find('=')+1:]
        #     secret = f.readline().strip()
        #     self._SECRET = secret[secret.find('=')+1:]
        #     passphrase = f.readline().strip()
        #     self._PASSPHRASE = passphrase[passphrase.find('=')+1:]

        # self.client = cbp.AuthenticatedClient(
        #     key=self._KEY,
        #     secret=self._SECRET,
        #     passphrase=self._PASSPHRASE
        # )

        # x = self.client.get_accounts()
        # print(x)

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
    c = TestStratPredict(sys.argv[1:])
    c.run()
