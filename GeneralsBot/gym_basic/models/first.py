import torch
import torch.nn as nn
import torch.nn.functional as F


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(10, 16, 3)  # TODO: don't hardcode
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(16, 32, 3)
        self.fc = nn.Linear(32 * 11 * 11 + 4, 3136)

    def forward(self, x):
        # x is tuple of (observation, [turn, more, game, parameters])
        x, info = x
        x = self.pool(F.relu(self.conv1(x)))
        x = F.relu(self.conv2(x))
        x = torch.flatten(x, 1)  # flatten all dimensions except batch
        x = torch.cat([x, torch.tensor(info).to(x.device).unsqueeze(1)], dim=0)
        x = self.fc(x)
        return x


# net = Net()