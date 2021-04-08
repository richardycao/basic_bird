from hummingbird import Module
import coinbasepro as cbp
import sys
from time import sleep

"""
Documentation for CBPHistoricRates

Description: 

Parameters:
    None yet.

Message Format:
    Input: 
    Output:

Command:

"""

class CBPHistoricRates(Module):
    def __init__(self, args):
        super().__init__(args)

        self.setInput(False)
        self.setOutput(False)

        self.add_argument("product-id", parser=lambda x: x, default="BTC-USD")
        self.add_argument("start", parser=lambda x: x, default="2016-01-01T04:00:00.000Z")
        self.add_argument("stop", parser=lambda x: x, default="2021-01-01T04:00:00.000Z")
        self.add_argument("granularity", parser=lambda x: x, default="60")
        self.build()

        self.client = cbp.PublicClient()

    def run(self):
        try:
            #while True:
            data = self.client.get_product_historic_rates(
                "BTC-USD",
                start="2016-01-01T04:00:00.000Z",
                stop="2016-01-01T09:00:00.000Z",
                granularity="60"
            )
            print(data)

            # limit of 3 requests per second
            sleep(0.334)
        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            self.closeIO()

if __name__ == "__main__":
    c = CBPHistoricRates(sys.argv[1:])
    c.run()