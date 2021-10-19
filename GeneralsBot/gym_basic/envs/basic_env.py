import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np


class BasicEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.action_space = spaces.Discrete(28**2 * 4)
        self.observation_space = spaces.Box(np.full((28, 28), -4), np.full((28, 28), 7))

    def step(self, action):

        # if we took an action, we were in state 1
        state = 1

        if action == 2:
            reward = 1
        else:
            reward = -1

        # regardless of the action, game is done after a single step
        done = True

        info = {}

        return state, reward, done, info

    def reset(self):
        state = 0
        return state

    def render(self, mode='human'):
        pass

    def close(self):
        pass
