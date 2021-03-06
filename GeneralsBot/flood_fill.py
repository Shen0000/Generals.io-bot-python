OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
OBSTACLES = [-2, -4]


class GeneralUtils:

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def closest(self, r, c, our_flag, tiles, armies, cities):
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        queue = [(r, c, 0)]
        while len(queue):
            curr = queue.pop(0)
            a, b = curr[:2]
            dist = curr[2] + 1
            if vis[a][b] or tiles[a][b] in OBSTACLES or (a, b) in cities:
                continue
            vis[a][b] = True
            if armies[a][b] > 1 and tiles[a][b] == our_flag:
                return a, b, dist
            else:
                for offset in OFFSETS:
                    if self.in_bounds(a + offset[0], b + offset[1]) and tiles[a + offset[0]][b + offset[1]] not in OBSTACLES and not vis[a + offset[0]][b + offset[1]]:
                        queue.append((a+offset[0], b+offset[1], dist))

        return -1, -1, -1

    def farthest5(self, r, c, state, enemy_r=None, enemy_c=None):
        our_flag, tiles, armies, cities = state["player_index"], state['tile_grid'], state["army_grid"], state['cities']
        prev_tile = [[(-1, -1) for _ in range(self.cols)] for _ in range(self.rows)]
        fringe_lvls = [[-1 for _ in range(self.cols)] for _ in range(self.rows)]
        fringe_lvls[r][c] = 0
        fringe_level = 1

        queue = []
        fringe = []

        for offset in OFFSETS:
            adj_r = r + offset[0]
            adj_c = c + offset[1]
            if self.in_bounds(adj_r, adj_c) and not (tiles[adj_r][adj_c] in OBSTACLES or (adj_r, adj_c) in cities):
                queue.append((adj_r, adj_c))

        while len(queue) > 0:
            a, b = queue.pop(0)
            if fringe_lvls[a][b] > -1 or tiles[a][b] in OBSTACLES or (a, b) in cities:
                if len(queue) == 0 and len(fringe) > 0:
                    queue = fringe
                    fringe = []
                    fringe_level += 1
                continue

            fringe_lvls[a][b] = fringe_level

            max_army = -1
            adj_tile = (-1, -1)
            for offset in OFFSETS:
                adj_r = a + offset[0]
                adj_c = b + offset[1]
                if self.in_bounds(adj_r, adj_c) and not (tiles[adj_r][adj_c] in OBSTACLES):
                    if fringe_lvls[adj_r][adj_c] == -1:
                        fringe.append((adj_r, adj_c))
                    elif fringe_lvls[adj_r][adj_c] - fringe_level == -1 and max_army < armies[adj_r][adj_c]:
                        max_army = armies[adj_r][adj_c]
                        adj_tile = (adj_r, adj_c)

            assert adj_tile != (-1, -1), "ffff"
            prev_tile[a][b] = adj_tile

            if len(queue) == 0 and len(fringe) > 0:
                queue = fringe
                fringe = []
                fringe_level += 1

        if enemy_r is None:
            max_path = [(self.farthest(our_flag, tiles, cities))]
            a, b = max_path[0]
        else:
            assert enemy_c is not None
            max_path = [(enemy_r, enemy_c)]
            a, b = max_path[0]

        while (a, b) != (r, c):
            a, b = prev_tile[a][b]
            max_path.append((a, b))

        return max_path[::-1]

    def farthest4(self, r, c, state):
        our_flag, tiles, armies, cities = state["player_index"], state['tile_grid'], state["army_grid"], state['cities']
        dists = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        prev_tile = [[(-1, -1) for _ in range(self.cols)] for _ in range(self.rows)]
        fringe_lvls = [[-1 for _ in range(self.cols)] for _ in range(self.rows)]

        dists[r][c] = max(1, armies[r][c])
        fringe_lvls[r][c] = 0
        fringe_level = 1

        queue = []
        fringe = []

        for offset in OFFSETS:
            adj_r = r + offset[0]
            adj_c = c + offset[1]
            if self.in_bounds(adj_r, adj_c) and not (tiles[adj_r][adj_c] in OBSTACLES or (adj_r, adj_c) in cities):
                queue.append((adj_r, adj_c))

        while len(queue) > 0:
            a, b = queue.pop(0)
            if fringe_lvls[a][b] > -1 or tiles[a][b] in OBSTACLES or (a, b) in cities:
                if len(queue) == 0 and len(fringe) > 0:
                    queue = fringe
                    fringe = []
                    fringe_level += 1
                continue

            fringe_lvls[a][b] = fringe_level

            max_dist = 0
            adj_tile = (-1, -1)
            for offset in OFFSETS:
                adj_r = a + offset[0]
                adj_c = b + offset[1]
                if self.in_bounds(adj_r, adj_c) and not (tiles[adj_r][adj_c] in OBSTACLES or (adj_r, adj_c) in cities):
                    if fringe_lvls[adj_r][adj_c] == -1:
                        fringe.append((adj_r, adj_c))
                    elif fringe_lvls[adj_r][adj_c] - fringe_level == -1 and max_dist < dists[adj_r][adj_c]:
                        max_dist = dists[adj_r][adj_c]
                        adj_tile = (adj_r, adj_c)

            if tiles[a][b] == our_flag:
                max_dist += armies[a][b] - 1
            elif tiles[a][b] >= 0 and tiles[a][b] != our_flag:
                max_dist -= (armies[a][b] + 1)

            dists[a][b] = max_dist

            prev_tile[a][b] = adj_tile

            if len(queue) == 0 and len(fringe) > 0:
                queue = fringe
                fringe = []
                fringe_level += 1

        max_dist = -1
        max_r, max_c = -1, -1
        for a in range(self.rows):
            for b in range(self.cols):
                if tiles[a][b] == our_flag and dists[a][b] > max_dist:
                    max_r = a
                    max_c = b
                    max_dist = dists[a][b]

        max_path = [(max_r, max_c)]
        a = max_r
        b = max_c

        while (a, b) != (r, c):
            a, b = prev_tile[a][b]
            max_path.append((a, b))

        return max_path

    def farthest(self, our_flag, tiles, cities):
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        queue = []
        fringe = []
        for row in range(self.rows):
            for col in range(self.cols):
                if tiles[row][col] == our_flag:
                    queue.append((row, col))

                elif tiles[row][col] in OBSTACLES or (row, col) in cities:
                    vis[row][col] = True

        while True:
            a, b = queue.pop(0)

            if vis[a][b] or tiles[a][b] in OBSTACLES or (a, b) in cities:
                if len(queue) == 0:
                    if len(fringe) == 0:
                        return a, b

                    queue = fringe
                    fringe = []
                continue

            vis[a][b] = True

            for offset in OFFSETS:
                if self.in_bounds(a + offset[0], b + offset[1]) and tiles[a + offset[0]][b + offset[1]] not in OBSTACLES and not vis[a + offset[0]][b + offset[1]]:
                    fringe.append((a+offset[0], b+offset[1]))

            if len(queue) == 0:
                if len(fringe) == 0:
                    return a, b

                queue = fringe
                fringe = []

        return -1, -1

    def manhattan_dist(self, r, c, tr, tc, state, attack=False):
        tiles, cities, our_flag = state['tile_grid'], state['cities'], state["player_index"]
        if ((not attack) and (tiles[r][c] not in (-1, our_flag) or (r, c) in cities)) or (
                attack and (tiles[r][c] in OBSTACLES or (r, c) in cities)):
            return 1e6

        queue = [(r, c, 0)]
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        while len(queue):
            curr = queue.pop(0)
            a, b = curr[:2]
            dist = curr[2] + 1
            if vis[a][b] or tiles[a][b] in OBSTACLES or (a, b) in cities:
                continue

            if a == tr and b == tc:
                return dist

            vis[a][b] = True
            for offset in OFFSETS:
                adj_r = a + offset[0]
                adj_c = b + offset[1]
                if self.in_bounds(adj_r, adj_c) and tiles[adj_r][adj_c] not in OBSTACLES:
                    queue.append((adj_r, adj_c, dist))

        return 1e6

    def city_dist(self, r, c, tr, tc, tiles, cities):
        if tiles[r][c] in OBSTACLES:
            return 1000000
        queue = [(r, c, 0)]
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        while len(queue):
            curr = queue.pop(0)
            dist = curr[2] + 1
            a , b = curr[:2]
            if a == tr and b == tc:
                return dist
            if vis[a][b] or tiles[a][b] in OBSTACLES or (a, b) in cities:
                continue
            else:
                vis[a][b]=True
                for offset in OFFSETS:
                    if self.in_bounds(a + offset[0], b + offset[1]) and tiles[a + offset[0]][b + offset[1]] not in OBSTACLES and not vis[a + offset[0]][b + offset[1]]:
                        queue.append((a+offset[0], b+offset[1], dist))

        return 1000000

    def nearest_city(self, r, c, tr, tc, tiles, cities):
        queue = [(r, c, 0)]
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        while len(queue):
            curr = queue.pop(0)
            dist = curr[2] + 1
            a , b = curr[:2]
            if vis[a][b] or tiles[a][b] in OBSTACLES or ((a, b) in cities and (a, b) != (r, c)):
                continue
            vis[a][b] = True
            if a == tr and b == tc:
                return dist
            else:
                for offset in OFFSETS:
                    if self.in_bounds(a + offset[0], b + offset[1]) and tiles[a + offset[0]][b + offset[1]] not in OBSTACLES and not vis[a + offset[0]][b + offset[1]]:
                        queue.append((a+offset[0], b+offset[1], dist))

        return 1000000

    def find_main(self, tiles, armies, id):
        vis = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        max_r=-1
        max_c=-1
        max=0
        for r in range(self.rows):
            for c in range(self.cols):
                if tiles[r][c]==id:
                    if armies[r][c]>max:
                        max_r=r
                        max_c=c
                        max=armies[r][c]
        return max_r, max_c

    def in_bounds(self, r=0, c=0):
        return 0 <= r < self.rows and 0 <= c < self.cols
