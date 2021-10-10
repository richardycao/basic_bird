from hummingbird import Module2
import datetime as dt
import numpy as np
import torch
from agent import JobAgent

import sys

class DogeJob(Module2):
  def __init__(self):
    super().__init__()

    self.max_price = 10 # dollars
    self.granularity = 10000 # 4 decimal places

    self.order_book = [0 for _ in range(self.max_price * self.granularity)]
    self.bid = 0
    self.ask = 0

    # Values to track
    self.cash = 1000
    self.account_value = 1000
    self.doge_owned = 0
    self.doge_cost_basis = 0

    # Values for agent and state
    self.agent = JobAgent(60, 3)
    self.cash_to_account_value = 1
    self.t = 0
    # ratio of the current mean of bid-ask to the doge_cost_basis

    self.avg_reward = []
  
  def _to_price(self, index) -> float:
    return index / self.granularity
  def _to_index(self, price) -> int:
    return int(price * self.granularity)

  def init_order_book(self, message):
    self.bid = message['bids'][0][0]
    self.ask = message['asks'][0][0]

    for bid in message['bids']:
      index = self._to_index(bid[0])
      self.order_book[index] = bid[1]
    for ask in message['asks']:
      index = self._to_index(ask[0])
      self.order_book[index] = ask[1]
  
  def on_order_fill(self, ts, side, price, volume): # `side` is the taker's side
    """
    1. I want to strip a section of the order book, 5% on each side of the mean.
    2. Then compress it. Compression can be done in 0.1 increments of each standard
    deviation, on each side, resulting in 60 sections.
    The compressed list should be of type torch.Tensor, which can be fed into the DQN.
    3. The 60-length array is fed into the DQN and gets an action.
    """

    # For now, I'll just use 30 prices on each side since the compression problem is tricky.
    bid_index = self._to_index(self.bid)
    ask_index = self._to_index(self.ask)
    mean_price = (self.bid + self.ask) / 2
    self.state = torch.tensor(self.order_book[bid_index-29:bid_index+1] + self.order_book[ask_index:ask_index+30] + [self.doge_owned, self.doge_cost_basis, mean_price])
    """
    Values to track:
    1. doge coin owned and cost basis are used to calculate the original value. When
    selling, bid * cost_basis is the new value, so the difference is the gain/loss.

    This is all I need.
    """

    self.action = self.agent.action(self.t, self.state)
    self.t += 1
    self.reward = 0
    if self.action == 0: # buy
      if self.doge_owned == 0: # if no position, then buy
        fee = self.account_value * 0.1 * 0.005
        doge_value = self.account_value * 0.1 * 0.995
        self.reward = -fee
        self.account_value -= fee

        self.doge_owned = doge_value / self.ask
        self.doge_cost_basis = self.ask
      else: # if has position, nothing happens
        pass
    elif self.action == 1: # sell
      if self.doge_owned != 0: # if has position, then sell
        doge_value = self.doge_cost_basis * self.doge_owned
        fee = doge_value * 0.005
        cash_back = doge_value * 0.995
        
        self.reward = cash_back
        self.account_value += cash_back

        self.doge_owned = 0
        self.doge_cost_basis = 0
      else: # if no position, nothing happens
        pass
    elif self.action == 2: # hold
      pass

    """
    This only hooks it up with the agent. I still need to include all the of the important
    variables in state. State includes:
    1. compressed order book
    2. cash
    3. total_account_value
    4. number of doge coin held
    5. cost basis of doge coin

    Rules:
    1. Exactly 10% of the account_value will be used in a buy.
    2. Sell will sell all doge coin.
    3. Can only sell if I have a position. Can only buy if I don't have a position.

    State should be invariant of:
    1. coin price
    2. account value
    3. number of coins held

    It simply needs to know:
    1. What is the percent gain or loss? This can be calculated using the current bid-ask and
    the cost basis of doge coin owned.

    Percent gain or loss isn't a good way. 50% gain -> 50% loss isn't breakeven.
    How about flat value? sure let's go that for now.
    This is a prototype anyway.
    """

    """
    If I think somthing is good to buy, I buy some.
    1. 10% of account_value is converted into doge coin and fees. account_value
    decreases by 0.5% * 10%. doge_owned increases by the number of doge equivalent
    to 10% * 99.5% of the original account value. And cost basis is adjusted for the
    new coins.
    """

  def after_order_fill(self):
    bid_index = self._to_index(self.bid)
    ask_index = self._to_index(self.ask)
    mean_price = (self.bid + self.ask) / 2
    next_state = torch.tensor(self.order_book[bid_index-29:bid_index+1] + self.order_book[ask_index:ask_index+30] + [self.doge_owned, self.doge_cost_basis, mean_price])

    self.agent.optimize(self.state, self.action, next_state, torch.tensor(self.reward))

    if len(self.avg_reward) < 200:
      self.avg_reward.append(self.reward)
    else:
      print('Average reward over last 200 actions:', np.average(self.avg_reward))
      self.avg_reward = []

  def update_order_book(self, message):
    for order in message['changes']:
      ts, side, price, new_vol = message['time'], order[0], float(order[1]), float(order[2])
      index = self._to_index(price)
      if index >= len(self.order_book):
        continue

      volume = np.abs(new_vol - self.order_book[self._to_index(price)])
      """
      if volume increases, then someone has placed a limit order.
      if volume decreases, 
          if it's on the bid or ask, then a limit order has been filled by a taker
          otherwise, it's a limit order cancelled by the maker.
      """
      old_vol = self.order_book[index]
      self.order_book[index] = new_vol
      if side == 'buy':
        if new_vol < old_vol: # volume decreased
          if price == self.bid: # buy limit order has been filled
            self.on_order_fill(ts, side, price, volume)

            if new_vol == 0: # if buy limit order is completely filled, then update the bid to be the next smallest one.
              bid_index = self._to_index(self.bid)
              while self.order_book[bid_index] == 0:
                bid_index -= 1
              self.bid = self._to_price(bid_index)
          else: # buy limit order has been cancelled
            pass
        else: # volume increased
          # someone has placed a limit order on the buy side
          if price > self.bid: # if price greater than the current bid, then update the bid
            self.bid = price
      elif side == 'sell':
        if new_vol < old_vol: # volume decreased
          if price == self.ask: # sell limit order has been filled
            self.on_order_fill(ts, side, price, volume)

            if new_vol == 0: # if sell limit order is completely filled, then update the ask to be the next largest one.
              ask_index = self._to_index(self.ask)
              while self.order_book[ask_index] == 0:
                ask_index += 1
              self.ask = self._to_price(ask_index)
          else: # sell limit order has been cancelled
              pass
        else: # volume increased
          # someone has placed a limit order on the sell side
          if price < self.ask: # if price less than the current ask, then update the ask
            self.ask = price
      self.after_order_fill()

  def on_message(self, message):
    if message['type'] == 'snapshot':
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
    j = DogeJob()
    j.run()