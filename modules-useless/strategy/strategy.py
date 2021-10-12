from hummingbird import Module2
import datetime as dt
import numpy as np
import torch
from agent import JobAgent

import sys

class Strategy(Module2):
  def __init__(self):
    super().__init__()
    # Training
    self.agent = JobAgent(60, additional_features=4, n_actions=3)
    self.account_value = 10000
    self.doge_owned = 0
    self.doge_cost_basis = 0
    self.position_size = 0.01
    self.t = 0

    # Stats
    self.stats_limit = 1000
    self.avg_reward = []
    self.buys = 0
    self.sells = 0
    self.holds = 0
    self.wins = 0
    self.trades = 0
  
  def _to_price(self, index) -> float:
    return index / self.granularity
  def _to_index(self, price) -> int:
    return int(price * self.granularity)
  
  def update_stats(self):
    if len(self.avg_reward) >= self.stats_limit:
      print('Average reward over last ' + str(self.stats_limit) + ' actions:', np.average(self.avg_reward))
      print('Buys / sells / holds:', self.buys, self.sells, self.holds)
      print('Winrate:', self.wins / self.stats_limit, ', Account value:', self.account_value)
      self.avg_reward = []
      self.buys = 0
      self.sells = 0
      self.holds = 0
      self.wins = 0
      self.trades = 0
    self.avg_reward.append(self.reward)
    if self.action[0][0] == 0:
      self.buys += 1
    elif self.action[0][0] == 1:
      self.sells += 1
    elif self.action[0][0] == 2:
      self.holds += 1

  def on_message(self, message):
    bid, ask = message['bid'], message['ask']
    mean_price = (bid + ask) / 2
    self.state = torch.tensor(message['before'] + [self.doge_owned, self.doge_cost_basis, mean_price, message['market_buy_ratio']])

    self.action = self.agent.action(self.t, self.state)
    self.t += 1
    self.reward = 0
    if self.action == 0: # buy
      if self.doge_owned == 0: # if no position, then buy
        fee = self.account_value * self.position_size * 0.005
        doge_value = self.account_value * self.position_size * 0.995
        self.reward = -fee
        # self.account_value -= fee

        self.doge_owned = doge_value / ask
        self.doge_cost_basis = ask
      else: # if has position, nothing happens. huge neagtive reward to disincentive it
        self.reward = -1000 # -self.account_value
    elif self.action == 1: # sell
      if self.doge_owned != 0: # if has position, then sell
        original_doge_value = self.doge_cost_basis * self.doge_owned
        current_doge_value = bid * self.doge_owned
        fee = current_doge_value * 0.005
        cash_back = current_doge_value * 0.995
        
        self.reward = cash_back - original_doge_value
        if self.reward > 0:
          self.wins += 1
        self.trades += 1
        # self.account_value -= fee

        self.doge_owned = 0
        self.doge_cost_basis = 0
      else: # if no position, nothing happens. huge negative reward to disincentive it
        self.reward = -1000 # -self.account_value
    elif self.action == 2: # hold
      pass

    next_state = torch.tensor(message['after'] + [self.doge_owned, self.doge_cost_basis, mean_price, message['market_buy_ratio']])
    self.agent.get_memory().push(self.state, self.action, next_state, torch.tensor([self.reward]))

    self.agent.optimize()

    self.update_stats()

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
    s = Strategy()
    s.run()