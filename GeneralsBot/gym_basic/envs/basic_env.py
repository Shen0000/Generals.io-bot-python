import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).parents[3]))
from GeneralsBot.make_map import create_map

"""
Tile Embedding:
Desirability - Mountain: -1, Our Tile: -0.75, Our City: -0.5, Our General: -0.25,
               Empty Tile: 0, Enemy Tile: 0.25, Empty City: 0.5, Enemy City: 0.75, Enemy General: 1
Is_Enemy - Mountain/Empty: 0, Our: 1, Enemy: -1, 
Army - Can be 0, magnitudes only, scale from 0 to 1
Signed_Army - Army * Is_Enemy

Tile Embedding:
Desirability - Mountain: -1, Our Tile: -0.75, Our City: -0.5, Our General: -0.25, Empty Tile: 0, Enemy Tile: 0.25, Empty City: 0.5, Enemy City: 0.75, Enemy General: 1
Is_Enemy - Mountain: 0, Our Tile: 1, Our City: 1, Empty Tile: 0, Enemy Tile: -1, Empty City: -1, Enemy City: -1, Enemy General: -1 
Visibility: -1 for fog, 1 for others
Army - Can be 0, same sign as Is_Enemy, scale from 0 to 1
Army * Is_Enemy

Features:
Ownership (-1, 0, 1)
Army values
Ownership * Army
City indicators
Fog indicators
Obstacle indicators
Mountain indicators
Empty indicator
Empty * City (to get city values)
General indicator (-1, 0, 1)
"""

OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

class BasicEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.SIZE = 28
        self.GRID_DIM = (self.SIZE, self.SIZE)
        self.EMBED_SIZE = 10
        self.action_space = spaces.Discrete(self.SIZE**2 * 4)
        self.observation_space = spaces.Box(np.full((self.GRID_DIM + (self.EMBED_SIZE,)), -1),
                                            np.full((self.GRID_DIM + (self.EMBED_SIZE,)), 1))

        tiles, cities, armies, generals = create_map([0.5, 0.5, 1, 0, 1, 2])
        self.state = {"tiles": tiles,
                      "armies": armies,
                      "cities": cities,
                      "turn": 0,
                      "total_land": [0, 0],
                      "total_army": [0, 0],
                      "generals": generals,  # TODO: generals, cities, tiles, armies should be generated
                      }
        self._state_to_obs()

    def step(self, action):
        assert self.action_space.contains(action)
        offset = OFFSETS[action % 4]
        tile = action // 4
        r, c = tile // self.SIZE, tile % self.SIZE
        adj_r, adj_c = r + offset[0], c + offset[1]

        if self.in_bounds(adj_r, adj_c):  # TODO: make sure (r, c) guaranteed to be in bounds
            self._update_states(r, c, adj_r, adj_c)

        return 0  # reward, done, info

    def _update_states(self, r, c, adj_r, adj_c):
        """
        Increment turn by 1
        Increment occupied cities by 1
        Every 25 turns, increase armies by 1
        To update:
            self.state["armies", "total_land", "total_army"]
            maybe also cities, tiles, and generals if new things are discovered


        Ideally also figure out how the action itself will work,
        but there will be a lot of edge cases (e.g. capture city) so I can do that
        """
        raise NotImplementedError  # TODO

    def _state_to_obs(self):
        _tile_to_owner = np.vectorize(lambda tile: 0 if tile < 0 else (1 if tile == 0 else -1))
        ownership = _tile_to_owner(self.state["tiles"])
        city_indicators = np.zeros(self.GRID_DIM, dtype=bool)
        for city_r, city_c in self.state["cities"]:
            city_indicators[city_r][city_c] = 1

        general_indicators = np.zeros(self.GRID_DIM, dtype=bool)
        for gen_r, gen_c in self.state["cities"]:
            general_indicators[gen_r][gen_c] = 1

        obstacle_indicators = self.state["tiles"] == -4
        fog_indicators = self.state["tiles"] <= -3
        mountain_indicators = self.state["tiles"] == -2
        empty_indicators = self.state["tiles"] == -1
        return np.stack([
            ownership, self.state["armies"], ownership * self.state["armies"],
            city_indicators, ownership * city_indicators, obstacle_indicators,
            fog_indicators, mountain_indicators, empty_indicators, general_indicators
        ])

    def get_states(self):
        return self.state

    def reset(self):
        state = 0
        return state

    def render(self, mode='human'):
        pass

    def close(self):
        pass

    def in_bounds(self, r=0, c=0):
        return 0 <= r < self.EMBED_SIZE and 0 <= c < self.EMBED_SIZE


if __name__ == "__main__":
    env = BasicEnv()