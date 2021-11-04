import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
import pathlib, sys
import time

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


def valid_move(r, c, r2, c2):
    for o in OFFSETS:
        if (r + o[0], c + o[1]) == (r2, c2):
            return True
    return False


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
        # self._state_to_obs()

    def step(self, action):
        (r, c, adj_r, adj_c) = action
        # assert self.action_space.contains(action)
        # offset = OFFSETS[action % 4]
        # tile = action // 4
        # r, c = tile // self.SIZE, tile % self.SIZE
        # print(offset, r, c)
        # adj_r, adj_c = r + offset[0], c + offset[1]

        if self.in_bounds(adj_r, adj_c):  # TODO: make sure (r, c) guaranteed to be in bounds
            self._update_states(r, c, adj_r, adj_c)
            # print(self.state["armies"])

        time.sleep(0.05)
        return 0, 0, 0, 0  # obs, reward, done, info

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
        if valid_move(r, c, adj_r, adj_c) and self.state['armies'][r, c] > 1:
            if self.state['tiles'][adj_r, adj_c] == 0:  # moving to own tile
                self.state['armies'][adj_r, adj_c] += self.state['armies'][r, c] - 1
                self.state['armies'][r, c] = 1
            elif self.state['tiles'][adj_r, adj_c] == 1:  # moving onto enemy tile
                self.state['total_army'][0] -= min(self.state['armies'][adj_r, adj_c], self.state['armies'][r, c]-1)  # update total army for both players
                self.state['total_army'][1] -= min(self.state['armies'][adj_r, adj_c], self.state['armies'][r, c]-1)
                self.state['armies'][adj_r, adj_c] -= self.state['armies'][r, c] - 1
                self.state['armies'][r, c] = 1
                if self.state['armies'][adj_r, adj_c] < 0:
                    self.state['total_land'][0] += 1
                    self.state['total_land'][1] -= 1
                    self.state['tiles'][adj_r, adj_c] = 0
                    self.state['armies'][adj_r, adj_c] = abs(self.state['armies'][adj_r, adj_c])  # TODO: always < 0
            elif (adj_r, adj_c) in self.state['cities']:  # moving to a neutral city tile
                self.state['total_army'][0] -= min(self.state['armies'][adj_r, adj_c], self.state['armies'][r, c]-1)  # update total army after using troops to capture city
                self.state['armies'][adj_r, adj_c] -= self.state['armies'][r, c] - 1
                self.state['armies'][r, c] = 1
                if self.state['armies'][adj_r, adj_c] < 0:
                    self.state['total_land'][0] += 1
                    self.state['tiles'][adj_r, adj_c] = 0
                    self.state['armies'][adj_r, adj_c] = abs(self.state['armies'][adj_r, adj_c])
            elif self.state['tiles'][adj_r, adj_c] == -1: # moving to an empty tile
                self.state['tiles'][adj_r, adj_c] = 0
                self.state['total_land'][0] += 1
                self.state['armies'][adj_r, adj_c] += self.state['armies'][r, c] - 1
                self.state['armies'][r, c] = 1

        # Increment turn and armies
        self.state['turn'] += 1
        g1, g2 = self.state['generals']
        self.state["total_army"][0] += 1
        self.state["total_army"][1] += 1
        self.state['armies'][g1[0], g1[1]] += 1
        self.state['armies'][g2[0], g2[1]] += 1
        if self.state['turn'] % 25 == 0: # every 25 turns all land is increased by 1
            for row in range(self.SIZE):
                for col in range(self.SIZE):
                    if self.state['tiles'][row][col] > -1:
                        self.state['armies'][row][col]+=1
                        self.state['total_army'][self.state['tiles'][row][col]] += 1
        for (a, b) in self.state['cities']:
            if self.state['tiles'][a, b] > -1:
                self.state['total_army'][self.state['tiles'][a, b]] += 1
                self.state['armies'][a, b] += 1

        # raise NotImplementedError  # TODO

    def _state_to_obs(self):
        _tile_to_owner = np.vectorize(lambda tile: 0 if tile < 0 else (1 if tile == 0 else -1))
        ownership = _tile_to_owner(self.state["tiles"])
        city_indicators = np.zeros(self.GRID_DIM, dtype=bool)
        for city_r, city_c in self.state["cities"]:
            city_indicators[city_r][city_c] = 1

        general_indicators = np.zeros(self.GRID_DIM, dtype=bool)
        for gen_r, gen_c in self.state["cities"]:
            general_indicators[gen_r][gen_c] = 1

        visible_indicators = self._calc_visible()
        fog_indicators = np.invert(visible_indicators)
        mountain_indicators = self.state["tiles"] == -2
        empty_indicators = self.state["tiles"] == -1
        obstacle_indicators = (city_indicators + mountain_indicators) * fog_indicators
        ownership *= fog_indicators
        city_indicators *= visible_indicators
        general_indicators *= visible_indicators
        empty_indicators *= visible_indicators
        mountain_indicators *= visible_indicators
        out = np.stack([
            ownership, self.state["armies"] * visible_indicators, ownership * self.state["armies"],
            city_indicators, ownership * city_indicators, obstacle_indicators,
            fog_indicators, mountain_indicators, empty_indicators, general_indicators
        ])
        return out

    def _calc_visible(self):  # aka farthest6
        visited = [[False for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        queue = []
        fringe = []
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                if self.state["tiles"][row][col] == 0:
                    queue.append((row, col))

        while len(queue) > 0 or len(fringe) > 0:
            a, b = queue.pop(0) if len(queue) > 0 else fringe.pop(0)
            if visited[a][b]:
                continue

            visited[a][b] = True

            if self.state["tiles"][a][b] != 0:
                continue

            if len(queue) == 0 and len(fringe) != 0:
                continue

            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    if (dr, dc) == (0, 0):
                        continue
                    if self.in_bounds(a + dr, b + dc) and not visited[a + dr][b + dc]:
                        fringe.append((a + dr, b + dc))

        return np.array(visited)

    def update_state(self, state):
        self.state = state

    def reset(self):
        pass

    def render(self, mode='human'):
        pass

    def close(self):
        pass

    def in_bounds(self, r=0, c=0):
        return 0 <= r < self.SIZE and 0 <= c < self.SIZE


if __name__ == "__main__":
    env = BasicEnv()