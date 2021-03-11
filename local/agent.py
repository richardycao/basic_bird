import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T

from collections import namedtuple
import random

Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward'))

class ReplayMemory(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, *args):
        if len(self.memory) < self.capacity:
            self.memory.append(None)
            self.memory[self.position] = Transition(*args)
            self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

class ValueNet(nn.Module):
    def __init__(self, inputs, outputs):
        super().__init__()

        self.fc1 = nn.Linear(inputs, 64)
        self.fc2 = nn.Linear(64, 16)
        self.fc3 = nn.Linear(16, outputs)

    def forward(self, x):
        x = self.fc2(x)
        x = self.fc2(x)
        x = self.fc3(x)
        return x

class Critic:
    def __init__(self, inputs, n_actions):
        self.inputs = inputs
        self.n_actions = n_actions

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.value_net = ValueNet(inputs, n_actions)
        self.target_net = ValueNet(inputs, n_actions)
        self.target_net.load_state_dict(self.value_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.value_net.parameters(), lr=0.0001)
        self.memory = ReplayMemory(1000000)
        
        self.BATCH_SIZE = 64
        self.GAMMA = 0.95
        self.TARGET_UPDATE = 1000
        self.target_update_count = 0

    def optimize(self):
        if len(self.memory) < self.BATCH_SIZE:
            return
        transitions = self.memory.sample(self.BATCH_SIZE)
        batch = Transition(*zip(*transitions))

        # Creates a list (mask) of true/false corresponding to whether or not the next state is terminal      
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None, batch.next_state)), device=self.device, dtype=torch.bool)
        if len([s[0] for s in batch.next_state if s is not None]) == 0:
            return
        non_final_next_states = torch.cat([s for s in batch.next_state if s is not None])

        # Get data batches
        states_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)

        state_action_values = self.value_net(states_batch).gather(1, action_batch)

        # state value or 0 in case the state was final.
        next_state_values = torch.zeros(self.BATCH_SIZE, device=self.device)
        next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1)[0].detach()

        # Compute the expected Q values
        expected_state_action_values = (next_state_values * self.GAMMA).view(-1, 1) + reward_batch

        # Compute the loss
        loss = F.mse_loss(state_action_values, expected_state_action_values)

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.value_net.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()

        # Copy value net over to target net
        self.target_update_count = (self.target_update_count + 1) % self.TARGET_UPDATE
        if self.target_update_count == 0:
            self.target_net.load_state_dict(self.value_net.state_dict())

class PolicyNet(nn.Module):
    def __init__(self, inputs, outputs):
        super().__init__()

        self.fc1 = nn.Linear(inputs, 64)
        self.fc2 = nn.Linear(64, 16)
        self.fc3 = nn.Linear(16, outputs)

    def forward(self, x):
        x = self.fc1(x)
        x = self.fc2(x)
        x = F.softmax(self.fc3(x), dim=1)
        return x

class Actor:
    def __init__(self, inputs, n_actions):
        self.inputs = inputs
        self.n_actions = n_actions

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.policy = PolicyNet(inputs, n_actions)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=0.0001)
        self.GAMMA = 0.95

    def action(self, state):
        return torch.multinomial(self.policy(state), 1)

    def optimize(self, state_action_value, expected_state_action_value):
        # Compute the loss
        loss = F.cross_entropy(state_action_value, expected_state_action_value)

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.policy.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()

class Agent:
    def __init__(self, inputs, n_actions):
        self.actor = Actor(inputs, n_actions)
        self.critic = Critic(inputs, n_actions)

        self.GAMMA = 0.95

    def action(self, state):
        return self.actor.action(state)

    def optimize(self, state, action, next_state, reward):
        self.critic.memory.push(state, action, next_state, reward)
        self.critic.optimize()

        # Critic evaluates Q(s,a) for each a, given input s
        state_action_value = self.critic.value_net(state)
        expected_state_action_value = reward + self.GAMMA * self.critic.value_net(next_state) if next_state != None else 0

        self.actor.optimize(state_action_value, expected_state_action_value.argmax().view(1))
