from hummingbird import Module2
import tensorflow as tf
from tensorflow import keras
import coinbasepro as cbp
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

        self.set_param("backtest", required=True, default=False)
        self.set_param("currencies", default=['BTC'])

        self.initial_price = -1
        self.initial_funds = 0
        self.funds = 0
        self.positions = {}
        
        """
        It's best to set up the backtesting position tracker locally because there's
        delay if I send trades to another module to handle tracking mock positions.

        Because of that, I might as well include the CBP client here too.
        """

        if self.params['backtest']:
            self.initial_funds = 10000
            self.funds = self.initial_funds
            for c in self.params['currencies']:
                self.positions[c] = {
                    "price": -1,
                    "size": 0
                }

        else: # This part is not really supported yet.
            with open('./cbp-creds.txt', 'r') as f:
                api = f.readline()
                self._KEY = api[api.find('=')+1:].strip()
                secret = f.readline()
                self._SECRET = secret[secret.find('=')+1:].strip()
                passphrase = f.readline()
                self._PASSPHRASE = passphrase[passphrase.find('=')+1:].strip()

                self.client = cbp.AuthenticatedClient(
                    key=self._KEY,
                    secret=self._SECRET,
                    passphrase=self._PASSPHRASE
                )
        
        # init list of states, replace each one and train in batches
        self.init_model()
        self.action = tf.random.uniform(shape=(1,1), minval=0, maxval=2, dtype=tf.int32, seed=10)

    def init_model(self):
        self.model = keras.Sequential([
            keras.layers.Dense(units=16, activation='relu'),
            keras.layers.Dense(units=3, activation='softmax')
        ])

        self.model.compile(optimizer='adam', 
                           loss=tf.losses.CategoricalCrossentropy(from_logits=True),
                           metrics=['accuracy'])

    def msg_consume(self, message):
        cur = message[0]
        if self.initial_price == -1:
            self.initial_price = cur
        
        # Only calculate when a sell happens
        # alpha = (self.funds - self.initial_funds) / self.initial_funds
        # beta = (cur - self.initial_price) / self.initial_price

        # Get current position (temporary)
        position = [[v] for k,v in self.positions['BTC'].items()]
        position[0][0] /= cur
        ### end temporary ###

        self.state = tf.reshape(tf.constant(message[1:]), [-1, 1])
        self.state = (self.state - cur) / cur
        state_action = tf.concat([self.action, position, self.state], 0)

        history = self.model.fit(
            state_action,
            epochs=1,
            
        )


        self.action = 0

        
        
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
