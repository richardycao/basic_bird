from hummingbird import Module
import coinbasepro as cbp
import sys
from time import sleep
import datetime

"""
Documentation for CBPHistoricRates

Description: 

Parameters:
    product-id: See Coinbase Pro API
    start: See Coinbase Pro API
    stop: See Coinbase Pro API
    granularity: See Coinbase Pro API

Message Format:
    Input: None
    Output:
        {
           'low': xxx,
           'high': xxx,
           'open': xxx,
           'close': xxx,
           'volume': xxx
        }

Command:

"""

class CBPHistoricRates(Module):
    def __init__(self, args):
        super().__init__(args)

        self.setInput(False)
        self.setOutput(True)

        self.add_argument("product-id", parser=lambda x: x, default="BTC-USD")
        # Default start is chosen to be 2017 since ~2017-01-02T00:00:00 is when data loss is nearly gone.
        self.add_argument("start", parser=lambda x: self.__str2iso(x), default="2017-01-01T00:00:00.000Z")
        self.add_argument("stop", parser=lambda x: self.__str2iso(x), default="2021-01-01T00:00:00.000Z")
        self.add_argument("granularity", parser=lambda x: x, default="60")
        self.build()

        self.client = cbp.PublicClient()

    def __str2iso(self, date):
      return datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))

    def __iso2str(self, date):
      d = date.isoformat()
      return d[:d.find('+')] + "Z"

    def run(self):
        interval_start = self.args['start']
        interval_stop = interval_start + datetime.timedelta(hours=5)
        try:
            while interval_stop < self.args['stop']:
                data = self.client.get_product_historic_rates(
                    self.args['product-id'],
                    start=self.__iso2str(interval_start),
                    stop=self.__iso2str(interval_stop),
                    granularity="60"
                )
                for bar in data:
                    self.send({
                        'low': float(bar['low']),
                        'high': float(bar['high']),
                        'open': float(bar['open']),
                        'close': float(bar['close']),
                        'volume': float(bar['volume']),
                    })

                interval_start += datetime.timedelta(hours=5)
                interval_stop = interval_start + datetime.timedelta(hours=5)
                sleep(0.334)
        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            self.closeIO()

if __name__ == "__main__":
    c = CBPHistoricRates(sys.argv[1:])
    c.run()