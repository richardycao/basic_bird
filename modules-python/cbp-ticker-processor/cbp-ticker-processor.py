from hummingbird import Module
import sys

"""
Documentation for CBPTickerProcessor

Description: 

Parameters:
    None yet.

Message Format:
    Input: See https://docs.pro.coinbase.com/?python#channels
    Output:

Command:
    python3 cbp-ticker-processor.py
    e.g. python3 cbp-ticker-processor.py

"""

class CBPTickerProcessor(Module):
    def __init__(self, args):
        super().__init__(args)

        self.setInput(True)
        self.setOutput(True)

        self.build()
    
    def msg_consume(self, message):
      pass

    def run(self):
        try:
            while True:
                message = self.receive()

                if message is not None:
                    print(message)
                    # should_produce = self.msg_consume(message)

                    # if should_produce:
                    #     data = self.process(1)
                    #     if data:
                    #         pass
                    #         # self.producer.produce(self.topic_out, value=dumps(str(self.highest_bid_price)+" | "+str(self.lowest_ask_price)).encode('utf-8'))
                    #         self.send(data)
        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            self.closeIO()

if __name__ == "__main__":
  c = CBPTickerProcessor(sys.argv[1:])
  c.run()
