import math
import numpy as np
import random
import sys

MIN, MAX = 24, 28
# MIN = 28
# MIN, MAX = 10, 10
CMIN, CMAX = 40, 50
sys.setrecursionlimit(10000)

'''
tiles = arr
armies = arr
turn = 0
lands = [0, 0]
armies [0, 0]
generals = [(), (-1, -1)]
'''


def flood(grid, flag, generalloc):
    components, map = [], []
    vis = [[False for _ in range(len(grid[0]))] for __ in range(len(grid))]
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            size=0
            if grid[r][c] == flag and not vis[r][c]:
                queue = []
                queue.append((r, c))
                while (len(queue)):
                    curr = queue.pop(0)
                    a, b = curr
                    if a<0 or a>=len(grid) or b<0 or b>=len(grid[0]):
                        continue
                    if vis[a][b] or grid[a][b] != flag:
                        continue
                    for gl in generalloc:
                        if (gl[0], gl[1]) == (a, b):
                            map.append(len(components))

                    vis[a][b] = True
                    size+=1
                    queue.append((a+1, b))
                    queue.append((a-1, b))
                    queue.append((a, b+1))
                    queue.append((a, b-1))
                components.append(size)
    return components, map


def create_map(data, seed=82):
    # random.seed(seed)
    length, width, city_density, swamp_density, mountain_density, num_players = data
    assert num_players > 1, "can't play with only one player"
    grid, armies, cities, generalloc = [], [], [], []
    rows, cols = 0, 0
    rows = MIN #+ int(MIN*length) + random.randint(-2, 2)
    cols = MIN #+ int(MIN*width) + random.randint(-2, 2)
    rows = min(max(rows, MIN), MAX) # make sure everything is in bounds
    cols = min(max(cols, MIN), MAX)
    for i in range(rows):
        grid.append([-1 for j in range(cols)])
        armies.append([0 for j in range(cols)])
    num_mountains = int(100 * mountain_density) + int((length + width)/2 * 40) + random.randint(-5, 5)
    num_cities = int(10 * city_density) * num_players + random.randint(0, num_players)
    filled = set()
    cnt = 0
    while cnt < num_mountains:
        rand = random.randint(0, rows*cols-1)
        if rand not in filled:
            filled.add(rand)
            grid[rand // cols][rand % cols] = -2
            cnt += 1

    cnt = 0
    while cnt < num_cities:
        rand = random.randint(0, rows*cols-1)
        if rand not in filled:
            filled.add(rand)
            cities.append((rand // cols, rand % cols))
            armies[rand//cols][rand%cols] = random.randint(CMIN, CMAX)
            cnt += 1
    cnt = 0
    while cnt < num_players:
        rand = random.randint(0, rows*cols-1)
        if rand not in filled:
            filled.add(rand)
            generalloc.append((rand // cols, rand % cols))
            cnt += 1

    if valid(grid, generalloc):
        gen_r, gen_c = generalloc[0]
        grid[gen_r][gen_c] = 0
        armies[gen_r][gen_c] = 1
        return np.array(grid), cities, np.array(armies), generalloc
    else:
        return create_map(data)
        # raise ValueError
        # return


def valid(grid, generalloc):
    components, map = flood(grid, -1, generalloc)
    # print(map, generalloc)
    assert len(map) == len(generalloc), "not all general locations were found while flood filling"
    components.sort(reverse=True)
    num = -1
    valid = True
    for loc in map:
        if num == -1:
            num = loc
        elif loc != num:
            valid = False
    if not valid:
        print("Generals are not in the same component, remaking map")
        return False
    empty_tiles = 0
    for component in components:
        empty_tiles += component

    largest = components[0]
    frac = largest / empty_tiles
    n = len(generalloc)
    for i in range(n):
        x = generalloc[i]
        for j in range(i + 1, n):
            y = generalloc[j]
            dist = math.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)
            if dist <= 12:
                print("distance invalid, remaking map")
                return False

    if frac < .90:
        print("remaking map")

    return frac >= .90


def pad_map(tiles, cities, armies, generals, GRID_DIM):  # TODO: flip to normal order
    """
    Pads tiles and armies to same dimensions as GRID_DIM
    Tiles are padded with mountains, while armies are padded with 0s
    cities and generals are shifted
    Args:
        tiles, armies - np.array()
        GRID_DIM - tuple of (num_rows, num_cols)
    """
    # random.seed(2)
    assert tiles.shape == armies.shape
    padded_tiles = np.full(GRID_DIM, -2, dtype=int)
    padded_armies = np.zeros(GRID_DIM, dtype=int)
    num_rows, num_cols = tiles.shape
    dr = GRID_DIM[0] - num_rows
    dc = GRID_DIM[1] - num_cols
    r0 = random.randint(0, dr)  if dr > 0 else 0
    c0 = random.randint(0, dc) if dc > 0 else 0
    padded_tiles[r0:r0+num_rows, c0:c0+num_cols] = tiles
    padded_armies[r0:r0+num_rows, c0:c0+num_cols] = armies
    shifted_cities = []
    for r, c in cities:
        shifted_cities.append((r + r0, c + c0))

    shifted_generals = []
    for r, c in generals:
        shifted_generals.append((r + r0, c + c0))

    shifted_generals[1] = (-1, -1)
    return padded_tiles, padded_armies, shifted_cities, shifted_generals


if __name__ == "__main__":
    for i in range(100):
        print(i)
        create_map([0.5, 0.5, 0.1, 0, 0.1, 2], seed=i)
    # print(grid, cities, armies, generalslocations)

'''
Testing:
135 mountains for 1x mountains and 1 x 1 board
112 mountains for 1x mountains and 0.75 x 0.75 board
108 mountains for 1x mountains and 0.5 x 0.5 board
103 mountains for 1x mountains and 0 x 0 board
Result:
num_mountains is approximately 100 + (mountain_density) * 40

Testing:
20 cities for 1x cities and 0 x 0 board
20 cities for 1x cities and 0.25 x 0.25 board
all others were about 20 as well
Result:
num_cities is approximately (10 * city_density) x the number of players

'''
