from hummingbird import Module2
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

class CBPHistoricRates(Module2):
    def __init__(self):
        super().__init__()

        self.set_param("product-id", required=True)
        self.set_param("start", default="2017-01-01T00:00:00.000Z")
        self.set_param("stop", default="2021-01-09T00:00:00.000Z")
        self.set_param("granularity", default="60")

        self.client = cbp.PublicClient()

    def __str2iso(self, date):
      return datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))

    def __iso2str(self, date):
      d = date.isoformat()
      return d[:d.find('+')] + "Z"

    def run(self):
        interval_start = self.__str2iso(self.params['start'])
        interval_stop = interval_start + datetime.timedelta(hours=5)
        final_stop = self.__str2iso(self.params['stop'])
        try:
            while interval_stop < final_stop:
                data = self.client.get_product_historic_rates(
                    self.params['product-id'],
                    start=self.__iso2str(interval_start),
                    stop=self.__iso2str(interval_stop),
                    granularity=self.params['granularity']
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
    c = CBPHistoricRates()
    c.run()