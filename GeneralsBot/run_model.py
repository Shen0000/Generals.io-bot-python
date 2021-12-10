import torch
import torch.nn as nn

from gym_basic.models.first import Net

model = Net()
model.load_state_dict(torch.load("gym_basic/models/test1.pt", map_location="cpu"))