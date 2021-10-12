from hummingbird import Module2
import numpy as np
import sys
from collections import deque

class OrderBookFeatures(Module2):
  def __init__(self):
    super().__init__()

    self.set_param('max_non_decimal_digits',required=True)
    self.set_param('max_decimal_digits', required=True)
    self.max_non_decimal_digits = self.params['max_non_decimal_digits']
    self.granularity = 10 ** self.params['max_decimal_digits']

    self.has_seen_snapshot = False

    self.order_book = [0 for _ in range((10 ** self.max_non_decimal_digits) * self.granularity)]
    self.bid = 0
    self.ask = 0

    self.market_orders_buys = 0
    self.market_orders_sells = 0
    self.market_orders_buy_volume = 0
    self.market_orders_sell_volume = 0
    self.market_orders_queue_limit = 10000
    self.market_orders_queue = deque()
  
  def _to_price(self, index) -> float:
    return index / self.granularity
  def _to_index(self, price) -> int:
    return int(price * self.granularity)

  def init_order_book(self, message):
    self.bid = float(message['bids'][0][0])
    self.ask = float(message['asks'][0][0])

    for bid in message['bids']:
      index = self._to_index(float(bid[0]))
      self.order_book[index] = float(bid[1])
    for ask in message['asks']:
      index = self._to_index(float(ask[0]))
      if index < len(self.order_book):
        self.order_book[index] = float(ask[1])

  def get_features(self):
    bid_index = self._to_index(self.bid)
    ask_index = self._to_index(self.ask)
    return self.order_book[bid_index-29:bid_index+1] + self.order_book[ask_index:ask_index+30]
  
  """
  Tracks the ratio of buys to sells in the last `self.market_orders_queue_limit` trades.
  Also tracks the volume of each market order.
  """
  def on_market_order(self, ts, side, price, old_vol, new_vol):
    order_volume = old_vol - new_vol
    if side == 'buy':
      self.market_orders_buys += 1
      self.market_orders_buy_volume += order_volume
    if side == 'sell':
      self.market_orders_sells += 1
      self.market_orders_sell_volume += order_volume
    self.market_orders_queue.append((side, order_volume))
    
    if len(self.market_orders_queue) > self.market_orders_queue_limit:
      removal = self.market_orders_queue.popleft()
      if removal[0] == 'buy':
        self.market_orders_buys -= 1
        self.market_orders_buy_volume -= removal[1]
      if removal[0] == 'sell':
        self.market_orders_sells -= 1
        self.market_orders_sell_volume -= removal[1]

  def on_limit_order(self, ts, side, price, old_vol, new_vol):
    pass

  def on_cancel_order(self, ts, side, price, old_vol, new_vol):
    pass

  def update_order_book(self, message):
    for order in message['changes']:
      ts, side, price, new_vol = message['time'], order[0], float(order[1]), float(order[2])
      index = self._to_index(price)
      if index >= len(self.order_book):
        continue

      """
      if volume increases, then someone has placed a limit order.
      if volume decreases, 
          if it's on the bid or ask, then a limit order has been filled by a taker.
          otherwise, it's a limit order cancelled by the maker.
      """
      before, after = [], []
      before = self.get_features()
      old_vol = self.order_book[index]
      self.order_book[index] = new_vol
      if side == 'buy':
        if new_vol < old_vol: # volume decreased
          if price == self.bid: # buy limit order has been filled
            self.on_market_order(ts, side, price, old_vol, new_vol)

            if new_vol == 0: # if buy limit order is completely filled, then update the bid to be the next smallest one.
              bid_index = self._to_index(self.bid)
              while self.order_book[bid_index] == 0:
                bid_index -= 1
              self.bid = self._to_price(bid_index)
          else: # buy limit order has been cancelled
            self.on_cancel_order(ts, side, price, old_vol, new_vol)
        else: # volume increased
          # someone has placed a limit order on the buy side
          if price > self.bid: # if price greater than the current bid, then update the bid
            self.bid = price
          self.on_limit_order(ts, side, price, old_vol, new_vol)
      elif side == 'sell':
        if new_vol < old_vol: # volume decreased
          if price == self.ask: # sell limit order has been filled
            self.on_market_order(ts, side, price, old_vol, new_vol)

            if new_vol == 0: # if sell limit order is completely filled, then update the ask to be the next largest one.
              ask_index = self._to_index(self.ask)
              while self.order_book[ask_index] == 0:
                ask_index += 1
              self.ask = self._to_price(ask_index)
          else: # sell limit order has been cancelled
            self.on_cancel_order(ts, side, price, old_vol, new_vol)
        else: # volume increased
          # someone has placed a limit order on the sell side
          if price < self.ask: # if price less than the current ask, then update the ask
            self.ask = price
          self.on_limit_order(ts, side, price, old_vol, new_vol)

      after = self.get_features()

      self.send({
        'bid': self.bid,
        'ask': self.ask,
        'before': before,
        'after': after,
        'market_buy_ratio': self.market_orders_buy_volume / (self.market_orders_buy_volume + self.market_orders_sell_volume + 1)
      })

  def on_message(self, message):
    if not self.has_seen_snapshot and message['type'] != 'snapshot':
      return

    if message['type'] == 'snapshot':
      self.has_seen_snapshot = True
      self.init_order_book(message)
    elif message['type'] == 'l2update':
      self.update_order_book(message)

  def run(self):
    try:
      while True:
        message = self.receive()

        if message is not None:
          self.on_message(message)
    except KeyboardInterrupt:
      sys.stderr.write('%% Aborted by user\n')
    finally:
      self.closeIO()

if __name__ == "__main__":
    o = OrderBookFeatures()
    o.run()