from hummingbird import Module2
from sortedcontainers import SortedDict
import sys
from time import sleep
import datetime

"""
Documentation for CBPPositions

Description:

Parameters:
    durations: 

Message Format:
    Input: 
    Output: 

Command:

"""

class CBPPositions(Module2):
    def __init__(self):
        super().__init__()

        self.set_param("backtest", required=True, default=True)
        self.set_param("currencies", default=['BTC'])

    def msg_consume(self, message):
        return 0

    def run(self):
        try:
            while True:
                message = self.receive()

                if message != None:
                    data = self.msg_consume(message)
                    out_message = {
                      'type': 'test-strat-process',
                      'data': data
                    }
                    self.send(out_message)

        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            self.closeIO()

if __name__ == "__main__":
    c = CBPPositions()
    c.run()