from hummingbird import Module2
from sortedcontainers import SortedDict
import sys
from time import sleep
import datetime

"""
Documentation for TestStratProcess

Description:

Parameters:
    durations: 

Message Format:
    Input: 
    Output: 

Command:

"""

class TestStratProcess(Module2):
    def __init__(self):
        super().__init__()

        self.set_param("durations", default=[5,30])

        self.queues = SortedDict({})
        for d in self.params['durations']:
            self.queues[d] = [[], 0] # queue-size: [[queue], moving average]

    def msg_consume(self, message):
        # Use opening price to avoid getting future data into the calculations
        val = message['open']

        for length, pair in self.queues.items():
            if len(pair[0]) >= length:
                removed = pair[0].pop(0)
                pair[1] -= removed
            pair[0].append(val)
            pair[1] += val

        return [val] + [v[1]/(len(v[0]) if len(v[0]) != 0 else 1) for k,v in self.queues.items()]

    def run(self):
        try:
            while True:
                message = self.receive()

                if message != None:
                    data = self.msg_consume(message)
                    # out_message = {
                    #   'type': 'test-strat-process',
                    #   'data': data
                    # }
                    self.send(data)

        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            self.closeIO()

if __name__ == "__main__":
    c = TestStratProcess()
    c.run()