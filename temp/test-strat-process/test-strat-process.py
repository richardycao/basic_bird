from hummingbird import Module
from sortedcontainers import SortedDict
import sys
from time import sleep
import datetime

"""
Documentation for TestStratProcess

Description:

Parameters:
    durations: comma-separated list of durations

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