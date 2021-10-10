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

class DQN(nn.Module):
    def __init__(self, input_size, outputs):
        super().__init__()
        
        self.conv1 = nn.Conv1d(1, 16, kernel_size=3) # 60x1 -> 58x16
        self.bn1 = nn.BatchNorm1d(16)
        self.conv2 = nn.Conv1d(16, 32, kernel_size=3) # 58x16 -> 56x32
        self.bn2 = nn.BatchNorm1d(32)

        # Calculates output size of convolutional operation
        def conv1d_size_out(size, kernel_size=3, stride=1, padding=0):
            return (size - (kernel_size - 1) - 1 + 2*padding) // stride + 1
        conv_size = conv1d_size_out(conv1d_size_out(input_size))
        linear_input_size = conv_size * 32 + 3 # total number of input nodes for fully-connected layer

        self.fc1 = nn.Linear(linear_input_size, 64)
        self.fc2 = nn.Linear(64, outputs)

    def forward(self, x):
        # print('forward:')
        # print(x.size())
        x = torch.reshape(x, (-1, 1, 63))
        # print(x.size())
        x, y = x[:,:,:-3], x[:,:,-3:]
        # print(x.size(), y.size())
        x = F.relu(self.bn1(self.conv1(x)))
        # print(x.size())
        x = F.relu(self.bn2(self.conv2(x)))
        # print(x.size())
        x = x.view(x.size(0), -1)
        # print(x.size())
        x = torch.cat((x, torch.reshape(y, (-1, 3))), 1)
        # print(x.size())
        x = self.fc1(x)
        # print(x.size())
        x = F.relu(x)
        # print(x.size())
        x = self.fc2(x)
        # print(x.size())
        return x

class JobAgent:
    def __init__(self, length, n_actions):
        self.length = 60
        self.n_actions = n_actions

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.policy_net = DQN(length, n_actions)
        self.target_net = DQN(length, n_actions)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=0.0001)
        self.memory = ReplayMemory(10000)
        
        self.BATCH_SIZE = 32
        self.GAMMA = 1
        self.EPS_START = 0.99
        self.EPS_END = 0.1
        self.EPS_DECAY = 3000
        self.TARGET_UPDATE = 100
        self.target_update_count = 0
    
    def get_memory(self):
      return self.memory

    def action(self, t, state):
        sample = random.random()
        eps_threshold = self.EPS_END + (self.EPS_START - self.EPS_END) * np.exp(-t / self.EPS_DECAY)

        if sample > eps_threshold: # greedy
            with torch.no_grad():
                return self.policy_net(state).max(1)[1].view(1, 1)
        else: # random
            return torch.tensor([[random.randrange(self.n_actions)]], device=self.device, dtype=torch.long)

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
        states_batch = torch.cat(batch.state, -1)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)

        # print('states_batch:', states_batch.size())
        # print('action_batch:', action_batch.size())
        # print('reward_batch:', reward_batch.size())
        state_action_values = self.policy_net(states_batch).gather(1, action_batch)

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
        for param in self.policy_net.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()

        # Copy policy net over to target net
        self.target_update_count = (self.target_update_count + 1) % self.TARGET_UPDATE
        if self.target_update_count == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())