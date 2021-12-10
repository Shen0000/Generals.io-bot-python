from collections import namedtuple
import gym
import logging
import numpy as np
import random
import torch
import time
import threading
import wx

from flood_fill import GeneralUtils
from gym_basic.models.first import Net

logging.basicConfig(level=logging.DEBUG)

from gym.envs.registration import register
register(
    id='basic-v0',
    entry_point='gym_basic.envs:BasicEnv',
)

env = gym.make("gym_basic:basic-v0")
env.reset()
env.step(0)

OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
ARROW_OFFSETS = {"shaft": [-0.25, 0.25], "head": [(-0.1, -0.1), (0.1, -0.1)]}
PLAYER_COLORS = ['#ea3323', '#4363d8', '#027f00', '#008080', '#f58231', '#f032e6', '#800080', '#800001', '#b09f30', '#9a6324', '#0000ff', '#483d8a']
TILE_SIZE = 30
FPS = 3
SavedAction = namedtuple('SavedAction', ['log_prob', 'value'])
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 800))
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour("#E6E6E6")
        self.panel.Bind(wx.EVT_PAINT, self.repaint)
        self.state = None
        self.info = {"source": (-1, -1), "button": True}

        self.Centre()
        self.Show()

    def repaint(self, event):
        dc = wx.PaintDC(self.panel)
        if self.state is not None:
            tiles, armies, alives, cities, generals_list, army_size, land_size, all_cities, all_generals = \
                self.state['tiles'], self.state['armies'], [True] * 2, \
                self.state['cities'], self.state['generals'], \
                self.state['total_army'], self.state['total_land'], self.state['cities'], self.state['generals']

            self.state["usernames"] = ["test"] * 2
            for i, username in enumerate(self.state["usernames"]):
                dc.DrawText(f"{username}'s Army: {army_size[i]}", 100, 700 + i * 20)
                dc.DrawText(f"{username}'s Land: {land_size[i]}", 400, 700 + i * 20)

            dc.SetPen(wx.Pen('#000000', width=1))
            for r in range(len(tiles)):
                for c in range(len(tiles[0])):
                    if tiles[r][c] == -3:
                        dc.SetBrush(wx.Brush('#393939'))
                    elif tiles[r][c] in (-4, -2):
                        dc.SetPen(wx.Pen('#000000', width=1))
                        dc.SetBrush(wx.Brush('#bbbbbb' if tiles[r][c] == -2 else '#393939'))
                        dc.DrawRectangle(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                        if (r, c) not in all_cities:
                            mountains = [(11, 8, 3, 24), (11, 8, 18, 22), (16, 18, 20, 12), (20, 12, 27, 24)]
                            for mountain in mountains:
                                dc.DrawLine(mountain[0] + c * TILE_SIZE, mountain[1] + r * TILE_SIZE,
                                            mountain[2] + c * TILE_SIZE, mountain[3] + r * TILE_SIZE)
                        dc.SetBrush(wx.Brush("black", wx.TRANSPARENT))
                    elif tiles[r][c] == -1:
                        if (r, c) in cities:
                            dc.SetBrush(wx.Brush('#bbbbbb'))
                        else:
                            dc.SetBrush(wx.Brush('#dcdcdc'))
                    elif tiles[r][c] >= 0:
                        dc.SetBrush(wx.Brush(PLAYER_COLORS[int(tiles[r][c])]))
                    else:
                        dc.SetBrush(wx.Brush('#00c56c'))

                    if tiles[r][c] <= -3:
                        dc.SetPen(wx.Pen('#393939', width=1))
                    else:
                        dc.SetPen(wx.Pen('#000000', width=1))
                    dc.DrawRectangle(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                    if (r, c) in all_generals:
                        dc.SetPen(wx.Pen('#000000', width=3))
                        dc.SetBrush(wx.Brush("black", wx.TRANSPARENT))
                        dc.DrawCircle(c * TILE_SIZE + int(TILE_SIZE // 2), r * TILE_SIZE + int(TILE_SIZE // 2),
                                      int(TILE_SIZE * 0.4))
                        dc.SetPen(wx.Pen('#000000', width=1))

                    if (r, c) in all_cities:
                        dc.SetPen(wx.Pen('#000000', width=2))
                        dc.SetBrush(wx.Brush("black", wx.TRANSPARENT))
                        points = [
                        (c * TILE_SIZE + int(TILE_SIZE/6), r * TILE_SIZE + int(TILE_SIZE/3)),
                        (c * TILE_SIZE + int(TILE_SIZE*5/6), r * TILE_SIZE + int(TILE_SIZE/3)),
                        (c * TILE_SIZE + int(TILE_SIZE/2), r * TILE_SIZE + int(TILE_SIZE/8))
                        ]
                        dc.DrawPolygon(points)
                        dc.DrawRectangle(c * TILE_SIZE + int(TILE_SIZE*7/24), r * TILE_SIZE + int(TILE_SIZE/3), int(TILE_SIZE/2), int(TILE_SIZE/2))
                        dc.SetPen(wx.Pen('#000000', width=1))

                    if tiles[r][c] >= 0 or ((r, c) in all_cities and tiles[r][c] >= -1):
                        dc.SetTextForeground((255, 255, 255))
                        temp = str(int(armies[r][c]))
                        if len(temp) > 3:
                            temp = f"{temp[:3]}..."

                        tw, th = dc.GetTextExtent(temp)
                        dc.DrawText(temp, TILE_SIZE * c + (TILE_SIZE - tw) // 2,
                                    TILE_SIZE * r + (TILE_SIZE - th) // 2)

                if self.info["source"] != (-1, -1):
                    dc.SetPen(wx.Pen('#ffffff', width=2))
                    dc.SetBrush(wx.Brush("black", wx.TRANSPARENT))
                    dc.DrawRectangle(self.info["source"][1] * TILE_SIZE, self.info["source"][0] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    dc.SetPen(wx.Pen('#000000', width=1))

                dc.SetPen(wx.Pen('#000000', width=1))

        self.Show(True)


def tuple_to_action(a, b, c, d):
    """ Going from (a, b) to (c, d) """
    mag = (a * env.SIZE + b)
    delta = c - a, d - b
    assert delta in OFFSETS
    dir = OFFSETS.index(delta)
    return mag * 4 + dir


def select_action(model, state):
    with torch.no_grad():
        actions = model((state[0].to(device), [state[1]]))
        order = torch.argsort(actions, dim=1)[0]
        for action_ind in order:
            if env.is_good_move(action_ind.item(), collect=False):
                return action_ind.view(1, 1)

        return torch.tensor([[random.randrange(env.SIZE ** 2 * 4)]], device=device, dtype=torch.long)


def main(frame):
    model = Net()
    model.load_state_dict(torch.load("gym_basic/models/test1.pt", map_location="cpu"))
    while True:
        obs = env.get_obs()
        action = select_action(model, obs).item()
        # action_probs = select_action(model, obs)
        # action = torch.multinomial(action_probs, num_samples=1).item()
        # action = torch.distributions.Categorical(logits=action_probs).sample().item()
        obs, reward, done, _ = env.step(action)
        frame.state = env.denoise()
        # frame.probs = action_probs

        wx.CallAfter(frame.Refresh)

    time.sleep(1)
    wx.CallAfter(frame.Refresh)
    cnt = 0
    while True:
        time.sleep(1)
        print(cnt)
        cnt += 1

    wx.CallAfter(frame.Destroy)


if __name__ == "__main__":
    app = wx.App()
    f = MyFrame(None, "Bot Visualizer")
    thread = threading.Thread(target=main, args=[f])
    thread.setDaemon(True)
    thread.start()
    app.MainLoop()