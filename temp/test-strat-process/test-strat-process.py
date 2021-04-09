from hummingbird import Module
from sortedcontainers import SortedDict
import sys
from time import sleep
import datetime

"""
Documentation for TestStratProcess

Description:
    Holding position?: y/n
    Current vs 30-day: h/l
    Current vs 5-day: h/l
    5-day vs 30-day: h/l

    If I have a position:
        If current < 5-day < 30-day:
        If current < 30-day < 5-day:
        If 30-day < current < 5-day:
        If 30-day < 5-day < current:
        If 5-day < current < 30-day:
        If 5-day < 30-day < current:
    If I don't have a position:
        If current < 5-day < 30-day:
        If current < 30-day < 5-day:
        If 30-day < current < 5-day: 
        If 30-day < 5-day < current:
        If 5-day < current < 30-day:
        If 5-day < 30-day < current:

    Another approach is using parameters:
        Current/30-day ratio
        Current/5-day ratio

Parameters:

Message Format:
    Input: 
    Output: 

Command:

"""

class TestStratProcess(Module):
    def __init__(self, args):
        super().__init__(args)

        self.setInput(True)
        self.setOutput(True)

        self.add_argument("durations", parser=lambda x: [int(i) for i in x.split(",")], default="5,90")
        self.build()

        self.queues = SortedDict({})
        for d in self.args['durations']:
            self.queues[d] = [[], 0] # (queue, moving average)

        #self.initial_price = -1

    def msg_consume(self, message):
        val = message['low'] + (message['high'] - message['low']) / 2
        # if self.initial_price == -1:
        #     self.initial_price = val

        for length, pair in self.queues.items():
            if len(pair[0]) >= length:
                removed = pair[0].pop(0)
                pair[1] -= removed
            pair[0].append(val)
            pair[1] += val

        #print([str(k)+"-day: "+str(v[1]/k) for k,v in self.queues.items()])
        return [val] + [v[1]/k for k,v in self.queues.items()]

    def run(self):
        try:
            while True:
                message = self.receive()

                if message != None:
                    data = self.msg_consume(message)
                    self.send(data)

        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            self.closeIO()

if __name__ == "__main__":
    c = TestStratProcess(sys.argv[1:])
    c.run()